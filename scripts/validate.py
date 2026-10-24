#!/usr/bin/env python3
"""Assemble maintained examples and check behavior, contracts, and links.

Requires MADS (MADS environment variable or mads on PATH) and py65==1.2.0.
No ROM downloads or network access. Build products live in a temporary folder.
"""
from pathlib import Path
import itertools
import json
import os
import re
import random
import subprocess
import tempfile
import unittest

from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[1]
STOP = 0x0700


def load_xex(path):
    data = path.read_bytes()
    memory = [0] * 65536
    pos = 0
    while pos < len(data):
        if data[pos:pos + 2] == b'\xff\xff':
            pos += 2
        if pos == len(data):
            break
        if pos + 4 > len(data):
            raise ValueError('Truncated XEX header')
        start = int.from_bytes(data[pos:pos + 2], 'little')
        end = int.from_bytes(data[pos + 2:pos + 4], 'little')
        pos += 4
        size = end - start + 1
        if size <= 0 or pos + size > len(data):
            raise ValueError('Invalid XEX segment')
        memory[start:end + 1] = data[pos:pos + size]
        pos += size
    return memory


def labels_from(path):
    return {name.lower(): int(address, 16)
            for address, name in re.findall(
                r'^00\s+([0-9A-Fa-f]{4})\s+(\S+)\s*$', path.read_text(), re.M)}


def run_until(cpu, target=STOP, limit=20000, hook=None):
    for _ in range(limit):
        if cpu.pc == target:
            return
        if hook:
            hook(cpu)
        cpu.step()
    raise AssertionError(f'Execution did not reach ${target:04X}; PC=${cpu.pc:04X}')


def call(cpu, address):
    cpu.pc = address
    cpu.sp = 0xff
    cpu.stPushWord(STOP - 1)


class BankedMemory(list):
    """XL/XE OS overlay sufficient to test the bridge, not a chipset model."""
    def __init__(self, ram, rom):
        super().__init__(ram)
        self.rom = rom

    def __getitem__(self, address):
        if isinstance(address, int) and super().__getitem__(0xd301) & 1:
            if 0xc000 <= address <= 0xcfff or 0xd800 <= address <= 0xffff:
                return self.rom[address]
        return super().__getitem__(address)


class Validation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='atari-skills-check-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.build = Path(cls.temp.name)
        cls.programs = {}
        for source in sorted((ROOT / 'examples').glob('*.asm')):
            cls.programs[source.stem] = cls.assemble(source)
        for name in ('quarter-square', 'multiplication', 'find-free-iocb', 'os-nmi-bridge'):
            source = cls.build / f'{name}.asm'
            origin = '$1800' if name == 'os-nmi-bridge' else '$2000'
            source.write_text(
                f"        icl '{ROOT / 'examples/atari.inc'}'\n"
                f"        org {origin}\n"
                f"        icl '{ROOT / 'examples/routines' / (name + '.asm')}'\n")
            cls.programs[name] = cls.assemble(source)
        cls.programs['interrupt-stub'] = cls.assemble(ROOT / 'tests/interrupt-stub.asm')

    @classmethod
    def assemble(cls, source):
        binary = cls.build / f'{source.stem}.xex'
        labels = cls.build / f'{source.stem}.lab'
        result = subprocess.run(
            [os.environ.get('MADS', 'mads'), str(source), f'-o:{binary}', f'-t:{labels}'],
            capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return load_xex(binary), labels_from(labels)

    def test_all_starters_have_run_vectors(self):
        for source in (ROOT / 'examples').glob('*.asm'):
            memory, labels = self.programs[source.stem]
            self.assertEqual(memory[0x2e0] | memory[0x2e1] << 8, labels['start'])

    def test_quarter_square_all_unsigned_byte_pairs(self):
        memory, labels = self.programs['quarter-square']
        cpu = MPU(memory=memory.copy())
        for a, b in itertools.product(range(256), repeat=2):
            call(cpu, labels['qs_mul8'])
            cpu.p = cpu.UNUSED  # D=0; routine establishes carry itself
            cpu.a, cpu.x = a, b
            run_until(cpu, limit=80)
            actual = cpu.memory[labels['prod_lo']] | cpu.memory[labels['prod_hi']] << 8
            self.assertEqual(actual, a * b, (a, b))
            self.assertEqual(cpu.sp, 0xff)

    def test_table_free_multiplication(self):
        memory, labels = self.programs['multiplication']
        cpu = MPU(memory=memory.copy())

        def multiply(entry, a, b=0, size=2):
            call(cpu, labels[entry])
            cpu.p = cpu.UNUSED
            cpu.a, cpu.x, cpu.y = a & 255, b & 255, 0x5a
            for name, value in (('mul_a', a), ('mul_b', b)):
                address = labels[name]
                cpu.memory[address:address + 2] = [value & 255, value >> 8]
            run_until(cpu, limit=1000)
            self.assertEqual(cpu.sp, 0xff)
            self.assertEqual(cpu.y, 0x5a)
            result = labels['mul_result']
            return int.from_bytes(bytes(cpu.memory[result:result + size]), 'little')

        for a, b in itertools.product(range(256), repeat=2):
            self.assertEqual(multiply('mul8_u16', a, b), a * b, (a, b))
        for a in range(65536):
            self.assertEqual(multiply('mul3_u16', a), (a * 3) & 65535, a)
            self.assertEqual(multiply('mul10_u16', a), (a * 10) & 65535, a)
        for a in range(256):
            self.assertEqual(multiply('mul96_u8', a), a * 96, a)
        boundaries = (0, 1, 2, 255, 256, 32767, 32768, 65534, 65535)
        pairs = list(itertools.product(boundaries, repeat=2))
        rng = random.Random(6502)
        pairs += [(rng.randrange(65536), rng.randrange(65536)) for _ in range(512)]
        for a, b in pairs:
            self.assertEqual(multiply('mul16_u32', a, b, size=4), a * b, (a, b))

    def test_iocb_search_all_occupancy_patterns(self):
        memory, labels = self.programs['find-free-iocb']
        for occupied in range(128):
            cpu = MPU(memory=memory.copy())
            cpu.memory[0x340] = 0xff  # IOCB0 must still be skipped
            free = []
            for n in range(1, 8):
                cpu.memory[0x340 + n * 16] = 0 if occupied & (1 << (n - 1)) else 0xff
                if cpu.memory[0x340 + n * 16] == 0xff:
                    free.append(n * 16)
            before = cpu.memory[0x340:0x3c0]
            call(cpu, labels['find_free_iocb'])
            cpu.y = 0x5a
            cpu.p |= cpu.CARRY
            run_until(cpu)
            self.assertEqual(bool(cpu.p & cpu.CARRY), not bool(free))
            if free:
                self.assertEqual(cpu.x, free[0])
            self.assertEqual(cpu.y, 0x5a)
            self.assertEqual(cpu.memory[0x340:0x3c0], before)

    def test_documented_keyboard_polling(self):
        document = (ROOT / 'system/input.md').read_text()
        blocks = re.findall(r'```asm\n(.*?)```', document, re.S)
        os_poll = next(b for b in blocks if b.startswith('poll_keyboard'))
        hardware = next(b for b in blocks if b.startswith('init_keyboard_hardware'))
        init, raw = hardware.split('poll_key_hardware\n', 1)
        for name, body in (('keyboard-init', init), ('keyboard-os', os_poll),
                           ('keyboard-raw', 'poll_key_hardware\n' + raw)):
            source = self.build / f'{name}.asm'
            source.write_text(f"        icl '{ROOT / 'examples/atari.inc'}'\n"
                              f"        org $2000\n{body}")
            self.programs[name] = self.assemble(source)
        for status, code in itertools.product((0xff, 0xfb, 0xf7, 0xf3), range(256)):
            memory, _ = self.programs['keyboard-raw']
            cpu = MPU(memory=memory.copy())
            cpu.memory[0xd20f] = status
            cpu.memory[0xd209] = code
            call(cpu, 0x2000)
            run_until(cpu)
            held = not (status & 4)
            self.assertEqual(bool(cpu.p & cpu.CARRY), held)
            if held:
                self.assertEqual(cpu.a, code)  # includes legitimate code $FF
        for code in range(256):
            memory, _ = self.programs['keyboard-os']
            cpu = MPU(memory=memory.copy())
            cpu.memory[0x2fc] = code
            call(cpu, 0x2000)
            run_until(cpu)
            self.assertEqual(cpu.memory[0x2fc], 0xff)
            self.assertEqual(cpu.a, code)
        memory, _ = self.programs['keyboard-init']
        cpu = MPU(memory=memory.copy())
        call(cpu, 0x2000)
        run_until(cpu)
        self.assertEqual(cpu.memory[0xd20f], 3)

    def test_nmi_bridge_preserves_mapping_and_interrupt_frame(self):
        bridge, labels = self.programs['os-nmi-bridge']
        rom, _ = self.programs['interrupt-stub']
        bitmap, bitmap_labels = self.programs['bitmap-dli-vbi']
        for mapping, status, registers, irq_masked, stack in itertools.product(
                (0xfe, 0xfc, 0xbe, 0xbc, 0x7e, 0x7c), (0x40, 0x80),
                ((0, 0, 0), (0xff, 0x5a, 0xa5)), (False, True), (0xf0, 0x08)):
            # Use actual maintained VBI/DLI handlers at their assembled addresses.
            ram = bitmap.copy()
            ram[0x1800:0x1900] = bridge[0x1800:0x1900]
            vbi = bitmap_labels['my_vbi']
            dli = bitmap_labels['my_dli']
            ram[0x224:0x226] = [vbi & 255, vbi >> 8]
            ram[0x200:0x202] = [dli & 255, dli >> 8]
            ram[0xd301] = mapping
            ram[0xd40f] = status
            frame_count = bitmap_labels['frame_count']
            ram[frame_count] = 0
            memory = BankedMemory(ram, rom)
            cpu = MPU(memory=memory)
            cpu.a, cpu.x, cpu.y = registers
            cpu.p = cpu.UNUSED | cpu.DECIMAL | cpu.CARRY
            if irq_masked:
                cpu.p |= cpu.INTERRUPT
            old_p = cpu.p
            cpu.pc = STOP
            cpu.sp = stack
            cpu.stPushWord(STOP)
            cpu.stPush(old_p & ~cpu.BREAK)
            cpu.p |= cpu.INTERRUPT
            cpu.pc = labels['os_nmi_bridge']
            run_until(cpu)
            self.assertEqual((cpu.a, cpu.x, cpu.y), registers)
            self.assertEqual(cpu.sp, stack)
            self.assertEqual(cpu.p & ~cpu.BREAK, old_p)
            self.assertEqual(memory[0xd301], mapping)
            self.assertEqual(memory[frame_count], int(status == 0x40 and not irq_masked))

    def test_display_list_and_dma_blocks(self):
        memory, labels = self.programs['bitmap-dli-vbi']
        pc = labels['display_list']
        self.assertEqual(pc // 1024, (labels['display_list_end'] - 1) // 1024)
        lines, bitmap_rows, dlis, address = 0, 0, 0, None
        while True:
            opcode = memory[pc]
            pc += 1
            mode = opcode & 15
            if mode == 0:
                lines += ((opcode >> 4) & 7) + 1
            elif mode == 1:
                self.assertEqual(opcode, 0x41)
                self.assertEqual(memory[pc] | memory[pc + 1] << 8, labels['display_list'])
                break
            else:
                self.assertEqual(mode, 14)
                if opcode & 0x40:
                    address = memory[pc] | memory[pc + 1] << 8
                    pc += 2
                self.assertIsNotNone(address)
                self.assertEqual(address // 4096, (address + 39) // 4096)
                self.assertTrue(all(x == 0x55 for x in memory[address:address + 40]))
                address += 40
                bitmap_rows += 1
                lines += 1
                dlis += bool(opcode & 0x80)
        self.assertEqual((lines, bitmap_rows, dlis), (216, 192, 1))

    def test_pmg_initializes_all_dma_memory(self):
        memory, labels = self.programs['pmg']
        cpu = MPU(memory=memory.copy())
        cpu.memory[0x4000:0x4800] = [0xa5] * 2048
        cpu.memory[0x22f] = 0x22
        call(cpu, labels['start'])
        run_until(cpu, target=labels['frame'])
        expected = [0] * 2048
        shape = labels['player0'] + 80 - 0x4000
        expected[shape:shape + 32] = [0xff] * 32
        self.assertEqual(cpu.memory[0x4000:0x4800], expected)
        self.assertEqual(cpu.memory[0xd01d], 2)
        self.assertEqual(cpu.memory[0x22f], 0x3a)

    def test_text_io_success_and_cleanup_errors(self):
        memory, labels = self.programs['text-io']
        # Failure keys are call numbers: prompt, OPEN, GET, echo, CLOSE.
        scenarios = (({}, 1), ({1: 0x8a}, 0x8a), ({2: 0x85}, 0x85),
                     ({3: 0x80}, 0x80), ({4: 0x86}, 0x86), ({5: 0x88}, 0x88),
                     ({3: 0x80, 4: 0x88}, 0x80), ({4: 0x86, 5: 0x88}, 0x86))
        for failures, expected_status in scenarios:
            cpu = MPU(memory=memory.copy())
            for n in range(1, 8):
                cpu.memory[0x340 + n * 16] = 0xff
            operations = []

            def cio_hook(m):
                if m.pc != 0xe456:
                    return
                x = m.x
                command = m.memory[0x342 + x]
                buffer = m.memory[0x344 + x] | m.memory[0x345 + x] << 8
                length = m.memory[0x348 + x] | m.memory[0x349 + x] << 8
                operations.append((x, command))
                self.assertIn(command, (3, 7, 11, 12))
                if command == 3:
                    self.assertEqual(m.memory[buffer:buffer + 3], [ord('K'), ord(':'), 0])
                    self.assertEqual(m.memory[0x34a + x], 4)
                elif command == 7:
                    self.assertEqual(length, 1)
                    m.memory[buffer] = ord('A')
                elif command == 11:
                    self.assertGreater(length, 0)
                    if x == 0 and len(operations) > 1:
                        self.assertEqual(m.memory[buffer], ord('A'))
                m.y = failures.get(len(operations), 1)
                # CIO returns Y and corresponding N/Z; use an RTS at the vector.
                m.p = (m.p & ~(m.NEGATIVE | m.ZERO)) | (m.y & m.NEGATIVE)
                m.memory[0xe456] = 0x60

            call(cpu, labels['start'])
            run_until(cpu, hook=cio_hook)
            self.assertEqual(cpu.memory[labels['example_status']], expected_status)
            if not (1 in failures or 2 in failures):
                self.assertEqual(operations[-1][1], 12)
                self.assertEqual(sum(command == 12 for _, command in operations), 1)
            else:
                self.assertNotIn(12, [command for _, command in operations])

    def test_disk_read_dcb_and_status(self):
        memory, labels = self.programs['disk-read']
        for result in (1, 0x8a):
            cpu = MPU(memory=memory.copy())

            def sio_hook(m):
                if m.pc != 0xe459:
                    return
                buf = labels['sector_buffer']
                self.assertEqual(m.memory[0x300:0x30c],
                                 [0x31, 1, 0x52, 0x40, buf & 255, buf >> 8, 7, 0, 128, 0, 1, 0])
                m.y = result
                m.memory[0x303] = result
                m.memory[0xe459] = 0x60

            call(cpu, labels['start'])
            run_until(cpu, hook=sio_hook)
            self.assertEqual(cpu.memory[labels['example_status']], result)

    def test_equates_and_keyboard_against_pinned_reference(self):
        reference = json.loads((ROOT / 'tests/fixtures/atari-equates.json').read_text())
        _, labels = self.programs['text-io']
        for name, value in reference['equates'].items():
            self.assertIn(name.lower(), labels, name)
            self.assertEqual(labels[name.lower()], value, name)
        section = (ROOT / 'system/input.md').read_text().split('### 6.3.3')[1]
        pairs = re.findall(r'`\$([0-9A-F]{2})` \| ([^|\n]+)', section)
        self.assertEqual(len(pairs), 64)
        matrix = {int(code, 16): key.strip().split(' (')[0] for code, key in pairs}
        self.assertEqual(set(matrix), set(range(64)))
        aliases = {'COMMA': ',', 'PERIOD': '.', 'SLASH': '/', 'SEMICOLON': ';',
                   'PLUS': '+', 'ASTERISK': '*', 'DASH': '-', 'EQUALS': '=',
                   'LESSTHAN': '<', 'GREATERTHAN': '>', 'ESC': 'ESCAPE', 'DELETE': 'BACKSPACE'}
        for name, code in reference['keys'].items():
            self.assertEqual(matrix[code], aliases.get(name, name), name)
        self.assertEqual({code for code, key in matrix.items() if key == 'Unused'},
                         {0x09, 0x19, 0x24, 0x29, 0x31, 0x3b})

    def test_local_markdown_links(self):
        broken = []
        for source in ROOT.rglob('*.md'):
            if '.git' in source.parts:
                continue
            for target in re.findall(r'\]\(([^)]+)\)', source.read_text()):
                path = target.split('#')[0]
                if path and ':' not in path and not (source.parent / path).exists():
                    broken.append((str(source.relative_to(ROOT)), target))
        self.assertEqual(broken, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
