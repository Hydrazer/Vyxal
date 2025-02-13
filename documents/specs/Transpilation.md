# Turning Bytes Into Code - the Guide to Transpiling Elements and Structures That I Wrote on a Tuesday Morning/Afternoon

When doing the actual code transpilation, there are templates that need to be followed in order to make transpiled code consistent and clear. This document relates
to what gets executed after transpilation, not the element functions. Note that this document doesn't account for any multi-branch extensions yet.

## Elements

There will be a function called `process_element` that will take a single expression (called `expr`) as a string (don't pass raw code). 
`expr` must be a python _expression_, not a _statement_; an easy way to think of this is that you must be able to put `expr` inside a 
lambda without syntax errors. The function wraps `expr` in one of the following templates:

### Nilads

```python
stack.append(expr)
```

### Monads

```python
lhs = pop(stack); stack.append(expr)
```

### Dyads

```python
rhs, lhs = pop(stack, 2); stack.append(expr)
```

### Triads

```python
third, rhs, lhs = pop(stack, 3); stack.append(expr)
```

If it is impractical to wrap an element's python equivalent inside of `process_element`, then
the protocol is to manually define it inside the command dictionary.

## Structures

These will all be in main.py

### If Statements

```python
"""transpiled code"""
condition = pop(stack)
context_values.append(condition)
if boolify(condition):
    """transpiled truthy branch"""
else:
    """transpiled falsey branch"""
context_values.pop()
```

Note that if no falsey branch is present, then there is no `else` block.

### For Loops

```python
"""transpiled code"""
for VAR_"""loop variable""" in iterable(pop(stack)):
    context_values.append("""loop variable""")
    """transpiled body code"""
    context_values.pop()
```

If no loop variable is provided, a loop variable is to be generated using `"LOOP" + secrets.token_hex(16)`

### While Loops

```python
"""transpiled condition branch"""
condition = pop(stack)
while boolify(condition):
    context_values.append(condition)
    """transpiled body branch"""
    context_values.pop()
    """transpiled condition branch"""
    condition = pop(stack)
```

If no condition is present, `1` is used as the code.


### Defined Functions

```python
def FN_"""function name"""(parameters, *, ctx):
    this = FN_"""function name"""
    context_values.append(parameters[-"""total sum of parameters""":])
    input_level += 1
    stack = []
    """processed parameters"""
    input_values[input_level] = [stack[::], 0]
    """transpiled function code"""
    context_values.pop()
    input_level -= 1
    return stack
```
    
### Lambdas

```python
def _lambda_"""(x := secrets.token_hex(16))"""(parameters, arity, self, *, ctx):
    this = _lambda_"""x"""
    overloaded_arity = False
    
    if "arity_overload" in dir(self): overloaded_arity = self.arity_overload
    
    if arity and arity != """defined arity""": stack = pop(parameters, arity)
    elif overloaded_arity: stack = pop(parameters, arity)
    else: stack = pop(parameters, """defined arity""")
    
    context_values.append(stack[::])
    input_level += 1
    input_values[input_level] = [stack[::], 0]
    
    """transpiled body code"""
    ret = pop(stack) 
    context_values.pop()
    input_level -= 1
    
    return ret
stack.append(_lambda_"""x""")
```
   
### Lists

```python
temporary_list = []

def list_item(s):
    stack = s[::]
    """list code"""

temporary_list.append(list_item(stack))

# continue this as much as needed

stack.append(temporary_list[::])
```

### Function Reference and Variables

- Fn ref: `stack.append(FN_"""name""")`
- Variable get: `stack.append(VAR_"""name""")`
- Variable set: `VAR_"""name""" = pop(stack)`


## Modifiers
These actually go in commmands.py

The transpiler in `main.py` will wrap each branch except for the modifier character in a lambda (if it already is a lambda, it stays as a lambda). This is so that the functions can be popped off the stack and put into variables. E.g.

```python
function_B, function_A = pop(stack, 2)
```

The things in commands.py don't need to follow the element template. They can just be strings.
