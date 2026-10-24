#!/usr/bin/env python3
"""Optional Atari800/Altirra-OS execution checks under PAL and NTSC.

Uses the installed Atari800 replacement ROM and SDL dummy drivers. This checks
execution/state, not screenshots, audio quality, or universal ROM compatibility.
"""
import os
import argparse
from pathlib import Path
import re
import subprocess
import struct
import tempfile

import pexpect

from validate import ROOT, labels_from


def require(condition, message):
    if not condition:
        raise AssertionError(message)


class Monitor:
    def __init__(self, binary, breakpoint, standard, config, rom=None, disk=None):
        # Atari800 classifies known images by checksum; forcing "custom" would
        # select the wrong slot when the supplied image is a recognized ROM.
        os_args = ['-xlxe_rom', str(rom)] if rom else ['-xl-rev', 'altirra']
        self.process = pexpect.spawn(
            os.environ.get('ATARI800', 'atari800'),
            ['-config', str(config), '-no-autosave-config',
             '-xl', *os_args, '-nobasic', '-nosound', '-nojoystick',
             '-windowed', '-no-video-accel', '-turbo', '-' + standard,
             '-run', str(binary), '-bpc', f'{breakpoint:04x}',
             *([str(disk)] if disk else [])],
            env={**os.environ, 'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy'},
            encoding='utf-8', timeout=20)
        try:
            self.process.expect('> ')
            self.state = self.process.before
            require(f'PC={breakpoint:04X}' in self.state, 'Wrong initial breakpoint')
        except BaseException:
            self.close()
            raise

    def command(self, command):
        self.process.sendline(command)
        self.process.expect('> ')
        return self.process.before

    def byte(self, address):
        return self.bytes(address, 1)[0]

    def bytes(self, address, size):
        require(0 < size <= 256 and address + size <= 65536, 'Invalid monitor read')
        output = self.command(f'M {address:04x}')
        data = {}
        for start, hex_data in re.findall(
                r'^([0-9A-F]{4}): ((?:[0-9A-F]{2} ){15}[0-9A-F]{2})', output, re.M):
            for offset, value in enumerate(bytes.fromhex(hex_data)):
                data[int(start, 16) + offset] = value
        require(all(address + n in data for n in range(size)), 'Cannot parse memory read')
        return bytes(data[address + n] for n in range(size))

    def word(self, address):
        return int.from_bytes(self.bytes(address, 2), 'little')

    def register(self, chip, name):
        match = re.search(fr'\b{re.escape(name)}=\s*([0-9A-F]{{2}})', self.command(chip))
        require(match is not None, f'Cannot parse {chip}/{name}')
        return int(match[1], 16)

    def breakpoint(self, address):
        self.command(f'BPC {address:04x}')

    def close(self):
        try:
            if self.process.isalive():
                self.process.sendline('QUIT')
                try:
                    self.process.expect(pexpect.EOF, timeout=2)
                except (pexpect.TIMEOUT, pexpect.EOF):
                    pass  # May still be running outside the monitor; force-close below.
        finally:
            self.process.close(force=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, help='Optional local XL/XE ROM instead of the replacement OS')
    options = parser.parse_args()
    if options.rom:
        require(options.rom.is_file() and options.rom.stat().st_size == 16384,
                'Expected a local 16K XL/XE OS ROM')
    programs = [('bitmap-dli-vbi', 'my_vbi'), ('pmg', 'frame'),
                ('pokey-tone', 'next_frame'), ('joystick', 'frame'),
                ('disk-read', 'done'), ('disk-read-image', 'done'),
                ('text-io', 'read_key'), ('os-off-vbi', 'done')]
    with tempfile.TemporaryDirectory(prefix='atari-skills-emulator-') as directory:
        build = Path(directory)
        config = build / 'atari800.cfg'
        config.write_text('Atari 800 Emulator, Version 6.0.0\n'
                          'MACHINE_TYPE=Atari XL/XE\nRAM_SIZE=64\nCFG_SAVE_ON_EXIT=0\n')
        sector = bytearray(128)
        sector[:8] = b'\x00\x01\x00\x07\x00\x07\x38\x60'
        sector[16:32] = b'ATARI TEST DATA!'
        require(len(sector) == 128, 'Fixture sector size changed')
        disk = build / 'read-only-fixture.atr'
        disk.write_bytes(struct.pack('<HHH', 0x296, 720 * 128 // 16, 128)
                         + bytes(10) + sector + bytes(719 * 128))
        for name in dict.fromkeys(name.removesuffix('-image') for name, _ in programs):
            result = subprocess.run(
                [os.environ.get('MADS', 'mads'), str(ROOT / 'examples' / f'{name}.asm'),
                 f'-o:{build / name}.xex', f'-t:{build / name}.lab'],
                capture_output=True, text=True, timeout=30)
            require(result.returncode == 0, result.stdout + result.stderr)
        for standard in ('pal', 'ntsc'):
            for name, stop in programs:
                source_name = name.removesuffix('-image')
                labels = labels_from(build / f'{source_name}.lab')
                monitor = Monitor(build / f'{source_name}.xex', labels[stop], standard, config,
                                  options.rom, disk if name.endswith('-image') else None)
                try:
                    if name == 'bitmap-dli-vbi':
                        initial_sp = re.search(r'S=([0-9A-F]{2})', monitor.state)[1]
                        for _ in range(3):
                            state = monitor.command('CONT')
                            require(f'PC={labels[stop]:04X}' in state, 'VBI stopped repeating')
                            require(re.search(r'S=([0-9A-F]{2})', state)[1] == initial_sp,
                                    'VBI stack drift')
                        require(monitor.byte(labels['frame_count']) == 3, 'Frame count drift')
                        require('NMIEN= C0' in monitor.command('ANTIC'), 'Interrupts disabled')
                        monitor.breakpoint(labels['my_dli'])
                        monitor.command('CONT')
                        require(monitor.register('GTIA', 'COLPF0') == 0x28, 'Upper color wrong')
                        monitor.breakpoint(labels['main'])
                        monitor.command('CONT')
                        require(monitor.register('GTIA', 'COLPF0') == 0x48, 'DLI color write missing')
                        saved_dl = monitor.word(labels['saved_dl'])
                        saved_vbi = monitor.word(labels['saved_vbi'])
                        saved_dli = monitor.word(labels['saved_dli'])
                        monitor.command('C D01F 09')  # Mask START low for the normal exit path.
                        monitor.breakpoint(labels['cleanup_return'])
                        monitor.command('CONT')
                        require(monitor.word(0x230) == saved_dl, 'Display pointer not restored')
                        require(monitor.word(0x224) == saved_vbi, 'VBI vector not restored')
                        require(monitor.word(0x200) == saved_dli, 'DLI vector not restored')
                        require('NMIEN= 40' in monitor.command('ANTIC'), 'NMI mask not restored')
                    elif name == 'pmg':
                        monitor.breakpoint(monitor.word(0x224))
                        monitor.command('CONT')
                        monitor.command('CONT')  # Allow a complete player-DMA frame.
                        require(monitor.register('ANTIC', 'DMACTL') == 0x3a, 'Player DMA off')
                        require(monitor.register('ANTIC', 'PMBASE') == 0x40, 'Wrong PMG base')
                        require(monitor.register('GTIA', 'HPOSP0') == 100, 'Player position wrong')
                        require(monitor.register('GTIA', 'GRACTL') == 2, 'Player output off')
                        monitor.breakpoint(labels['frame'])
                        monitor.command('CONT')  # Finish VBI before testing the main-loop exit.
                        monitor.command('C D01F 09')
                        monitor.breakpoint(labels['cleanup_return'])
                        monitor.command('CONT')
                        require(monitor.byte(0x22f) == monitor.byte(labels['saved_dma']), 'DMA shadow leaked')
                        require(monitor.byte(0x2c0) == monitor.byte(labels['saved_color']), 'Player color leaked')
                        require(monitor.register('GTIA', 'GRACTL') == 0, 'Player output left on')
                        require(monitor.register('GTIA', 'HPOSP0') == 0, 'Player position left active')
                    elif name == 'joystick':
                        monitor.breakpoint(labels['check_exit'])
                        monitor.command('CONT')
                        screen = monitor.word(0x58)
                        require(monitor.bytes(screen, 2) == b'\x26\x11', 'Neutral joystick display wrong')
                        monitor.command('C D01F 09')
                        monitor.breakpoint(labels['done'])
                        monitor.command('CONT')
                    elif name == 'pokey-tone':
                        require(monitor.register('POKEY', 'AUDF1') == 72, 'Tone frequency wrong')
                        require(monitor.register('POKEY', 'AUDC1') == 0xa8, 'Tone output off')
                        clock = monitor.byte(0x14)
                        monitor.breakpoint(labels['done'])
                        monitor.command('CONT')
                        ticks = (monitor.byte(0x14) - clock) & 255
                        require(ticks == (50 if standard == 'pal' else 60), 'Tone duration wrong')
                        require(monitor.register('POKEY', 'AUDC1') == 0, 'Tone left on')
                    elif name == 'disk-read':
                        # No disk attached: exercise the real OS timeout/error path.
                        require(monitor.byte(labels['example_status']) == 0x8a,
                                'Expected no-device timeout')
                    elif name == 'disk-read-image':
                        require(monitor.byte(labels['example_status']) == 1, 'ATR read failed')
                        actual = monitor.bytes(labels['sector_buffer'], 128)
                        require(actual == sector, f'ATR sector data wrong: {actual.hex()}')
                    elif name == 'text-io':
                        # Inject a pending raw A key after K: OPEN; run real CIO GET/PUT/CLOSE.
                        monitor.command('C 02FC 3F')
                        monitor.breakpoint(labels['done'])
                        monitor.command('CONT')
                        require(monitor.byte(labels['example_status']) == 1, 'CIO failed')
                        require(monitor.byte(labels['key_buffer']) == ord('A'), 'Key translation failed')
                        channel = monitor.byte(labels['channel'])
                        require(monitor.byte(0x340 + channel) == 0xff, 'K: channel leaked')
                    elif name == 'os-off-vbi':
                        saved_mapping = monitor.byte(labels['saved_portb'])
                        require(monitor.byte(0xd301) == saved_mapping, 'OS mapping not restored')
                        require(monitor.byte(labels['masked_ticks']) == 0,
                                'OS ran deferred VBI while interrupted I was set')
                        require(monitor.byte(labels['deferred_ticks']) >= 3,
                                'OS skipped deferred VBI while interrupted I was clear')
                        require(monitor.word(0x224) == monitor.word(labels['saved_vbi']),
                                'OS-off example leaked its deferred handler')
                        require('NMIEN= 40' in monitor.command('ANTIC'), 'NMI mask not restored')
                    print(f'PASS {standard.upper()}: {name}', flush=True)
                finally:
                    monitor.close()


if __name__ == '__main__':
    main()
