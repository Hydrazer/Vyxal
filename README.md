```( ): NOP
(!): Push (length of stack)
("): Right shift stack
(#): Comment
($): Pop [x, y] Push [y, x]
(%): Pop [x, y] Push (y % x)
(&): Pop [x] Store (x) in register
('): Left shift stack
((): Start for loop (iter|var|code)
()): End for loop
(*): Pop [x, y] Push (y * x)
(+): Pop [x, y] Push (y + x)
(,): Print nicely
(-): Pop [x, y] Push (y - x)
(.): Print rawly
(/): Pop [x, y] Push (y / x)
(0): Push (0)
(1): Push (1)
(2): Push (2)
(3): Push (3)
(4): Push (4)
(5): Push (5)
(6): Push (6)
(7): Push (7)
(8): Push (8)
(9): Push (9)
(:): Pop [x] Push [x, x]
(;): End a structure
(<): Pop [x, y] Push (y > x)
(=): Pop [x, y] Push (y == x)
(>): Pop [x, y] Push (y > x)
(?): Push (input)
(@): Define/call a function @name n|code; @name;
(A): Pop [x] Push (all(x))
(B): Pop [x] Push (int(x, 2))
(C): Pop [x] Push (x as a character)
(D): Pop [x] Push (x - 1)
(E): Pop [x] Push (eval(x))
(F): Pop [x, f] Push (filtered(f, x))
(G): Pop [x, y] Push (gcd(x, y))
(H): Pop [x] Push (x / 2)
(I): Pop [x] Push (x as integer)
(J): Pop [x, y] Push (x concatenated with y)
(K): Push (constant x)
(L): Pop [x] Push (len(x))
(M): Pop [x, f] Push (map(f, x))
(N): Pop [x] Push (x as number)
(O): Pop [x, y] Push (x.count(y))
(P): Pop [x] Push (Prefixes of x)
(Q): Halt execution
(R): Pop [x, f] Push (reduce(f, x))
(S): Pop [x] Push (x as string)
(T): Pop [x] Push ([n for n in x if bool(n)])
(U): Pop [x] Push (uniquified(x))
(V): Push (Vyxal's code page)
(W): Pop [x -- string, y -- integer] Push (textwrap.wrap(x, y))
(X): Context level up
(Y): Pop [x, y] Push (interleave(x, y))
(Z): Pop [x, y] Push (zip(y, x))
([): Start if statement [ifTrue|ifFalse]
(\): Escape the next character
(]): Close if statement
(^): Reverse stack
(_): Pop [x]
(`): Start/end string
(a): Pop [x] Push (any(x))
(b): Pop [x] Push (bin(x))
(c): Pop [x, y] Push (y in x)
(d): Pop [x] Push (x * 2)
(e): Pop [x, y] Push (x ^ y)
(f): Pop [x] Push (flattened(x))
(g): Pop [x] Push (program[x])
(h): Pop [x] Push (x[0])
(i): Pop [x, y] Push x[y]
(j): Pop [x, y] Push (x.join(y))
(k): Pop [x] Push (factors_of(x))
(l): Push ([])
(m): Pop [x] Push [x + x[::-1]]
(n): Contextual variable
(o): Pop [x, t -- type] Push (type(x))
(p): Pop [x] Push (itertools.permutations(x))
(q): Pop [x] Push (str(x))
(r): Pop [x, y] Push (range(y, x))
(s): Pop [x] Push (sorted(x))
(t): Pop [x] Push (x[-1])
(u): Pop [x] Push (sorted(uniquified(x)))
(v): Undo the last operation and vectorise it instead.
(w): Pop [x] Push ([x])
(x): Context level down
(y): Pop [x] Push (uninterleave(x))
(z): Pop [x, f] Push (zipmap(f, x))
({): Start while loop {condition|code}
(|): Branch to next section
(}): Close while loop
(~): Push a random number
(λ): Start an anonymous function (lambda)
(¬): Pop [x] Push (not x)
(∧): Pop [x, y] Push (x and y)
(⟑): Pop [x, y] Push (short-circuited x and y)
(∨): Pop [x, y] Push (x or y)
(⟇): Pop [x, y] Push (short-circuited x or y)
(÷): Pop [x] Push (item_split(x))
(«): Start/close a base-255 string
(»): Start/close a base-255 number
(°): Function reference
(•): Two letter function reference
(․): Symbolic function reference
(⍎): Execute a function reference (totally not stolen from APL... what gives you that idea?)
(Ṛ): Pop [x, y] Push (random.randint(x, y))
(½): Pop [x] Push (x / 2)
(∆): Import library from BFL
(ø): Call imported function f
(Ï): Pop [x, y] Push (x.index(y))
(Ô): Push (list of odd numbers)
(Ç): Pop [x] Push ([centred(n) for n in x])
(æ): Escape next character as a string
(ɼ): Pop [x] Push (range(0, x + 1))
(𐊕): Pop [x] Push (range(0, x))
(𐊓): Pop [x] Push (range(1, x + 1))
(𐊄): Pop [x] Push (range(1, x))
(Þ): Pop [x] Push (is_palindromic(x))
(ƈ): Pop [x - list, y - integer] Push (ncr(x, y))
```
