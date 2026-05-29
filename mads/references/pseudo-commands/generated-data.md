# Generated Data

### SIN (centre,amp,size[,first,last])

```
centre     is a number which is added to every sine value
amp        is the sine amplitude
size       is the sine period
first,last define range of values in the table. They are optional.
           Default are 0,size-1.
```

```
   dta a(sin(0,1000,256,0,63))
```
defines table of 64 words representing a quarter of sine with amplitude of 1000.


<a name="cos"></a>

### COS (centre,amp,size[,first,last])

```
centre     is a number which is added to every cosine value
amp        is the cosine amplitude
size       is the cosine period
first,last define range of values in the table. They are optional.
           Default are 0,size-1.
```

```
   dta a(cos(0,1000,256,0,63))
```
defines table of 64 words representing a quarter of cosine with amplitude of 1000.


<a name="rnd"></a>

### RND (min,max,length)
This pseudo-command allows generating LENGTH random values within the range <MIN..MAX>.

```
   dta b(rnd(0,33,256))
```

<a name="ift"></a>
<a name="els"></a>
<a name="eli"></a>
<a name="eif"></a>
