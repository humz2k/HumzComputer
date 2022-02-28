# HumzComputer
 
WIP!!!

I started this with the intention of writing an emulator for an architecture I came up with. I am realising now that the architecture is pretty dumb overall. However, I have written so much of it already that I figure I might as well complete it.

So, I'm going to use this as an exercise in bad architecture and compiler design. Trying to design a working compiler for an architecture that is pretty dumb.

### USAGE:
To run .hl programs without using the file system, run `python run_hl.py your_program.hl`

To save to file system, run `python save_hl.py your_program.hl`
This will print the file location that your program was stored in.

Then, run `python computer.py`
Input the location of your program, e.g. 2, to run your program.

### SYNTAX:
Two types, `int` and `unsigned_int`.

Declare a variable with `int a` or `unsigned_int a`.

For lists, `int a[length]`, e.g. `int a[5]`.

You can declare variable with starting value, e.g. `int a = 5`, `int a[4] = "test"`. This only works once.

To update variable, `a = 5`.

Math operations: `a = a + 5`, `b = a - c`, `b = 5 / 1`, `c = a * b`.

Push to screen: `push a`, `push "TEST"`

Flip screen: `flip`.

If statements: `if a == 5; { do stuff };`, `a != 5`, `a <= 5`, `a >= 5`, `a > 5`, `a < 4`.

While loops: `while a == 5; { do stuff };`

All lines end in `;`.

See `/programs` for examples.

### LIMITATIONS:
Assembly generated for program currently cant be bigger than 512 lines -> this will be fixed in future using some hacking magic.

Only one math operation per line.

If stuff doesnt work, run `python save_hl.py os.hl -o` to reset the os.

### TODO: 
Macros.

Fix variable declarations.

MALLOC.
