9/8/2012

You can start the program by running:

        python MayCalEditor.py README.md

Ctrl+Y will execute every line that starts with a semicolon.

; f := \x y -> x + y

; f(12, 24)

36

As you can see, Haskell style lambdas are supported,
although, you can also define functions as below:

; g(n) := 1 if n = 1 else n * g(n - 1)

; g(5)

120

As you can see Python style if - else expressions are
supported as well.

--------------------------------------------------------------

The language itself is implemented in MayCal.py, but the
editor is implemented in MayCalEditor.py. You can run MayCal.py
by itself -->

      python MayCal.py

will start a command line prompt, whereas

      python MayCal.py <filename>

will execute every line in the file.

--------------------------------------------------------------

The editor also exhibits a few neat features -->
You can check out the stuff under "File" and "Edit" in the menu--
It will show you the stuff you can do (e.g. save file using Ctrl-S)

However, the hotkey for decreasing fontsize (Ctrl-minus) doesn't
seem to work. On the other hand, increasing the font size (Ctrl-=)
seems to work ok.
 --------> Nevermind --- I got it fixed .

--------------------------------------------------------------

Rudimentary Haskell style (non-sugared) lists are supported as well.
However, unlike in Haskell, the lists may be heterogeneous.

; a := 1 : 2 : 3 : 4 : nil

; car(a)

1

; cdr(a)

[2, 3, 4]

; cons(5, a)

[5, 1, 2, 3, 4]

; cons(a : nil, a)
[[[1, 2, 3, 4]], 1, 2, 3, 4]

Note that internally, Python lists are used, and I did NOT flip the
list to make popping and pushing elements efficient. This means
that inserting an element takes linear time, i.e. list operations
are very slow.

However, considering this is a Toy language, I think it is pretty
productive work for a single Friday evening.
