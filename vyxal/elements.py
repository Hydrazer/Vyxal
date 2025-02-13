"""This is where the element functions are stored

(that is, functions directly corresponding to Vyxal elements). It's also where
the python equivalent of command is stored
"""

import itertools
import math
import string
import types
from typing import Union

import sympy

from vyxal.helpers import *
from vyxal.LazyList import LazyList

NUMBER_TYPE = "number"
SCALAR_TYPE = "scalar"


def process_element(
    expr: Union[str, types.FunctionType], arity: int
) -> tuple[str, int]:
    """Take a python expression and adds boilerplate for element functions to it

    expr can be a string, which will be added verbatim to the transpiled output,
    or a function, for which a function call will be generated.

    See documents/specs/Transpilation.md for information on what happens here.
    """
    if arity:
        arguments = ["third", "rhs", "lhs"][-arity:]
    else:
        arguments = "_"

    if isinstance(expr, types.FunctionType):
        pushed = f"{expr.__name__}({', '.join(arguments[::-1])}, ctx)"
    else:
        pushed = expr
    py_code = (
        f"{', '.join(arguments)} = pop(stack, {arity}, ctx); "
        f"stack.append({pushed})"
    )
    return py_code, arity


def add(lhs, rhs, ctx):
    """Element +
    (num, num) -> lhs + rhs
    (num, str) -> str(lhs) + rhs
    (str, num) -> lhs + str(rhs)
    (str, str) -> lhs + rhs
    """

    ts = vy_type(lhs, rhs)
    return {
        (NUMBER_TYPE, NUMBER_TYPE): lambda: lhs + rhs,
        (NUMBER_TYPE, str): lambda: str(lhs) + rhs,
        (str, NUMBER_TYPE): lambda: lhs + str(rhs),
        (str, str): lambda: lhs + rhs,
    }.get(ts, lambda: vectorise(add, lhs, rhs, ctx=ctx))()


def combinations_with_replacement(lhs, rhs, ctx):
    """Element ↔
    (any, num) -> combinations of lhs of length rhs with replacement
    (any, non-num) -> remove elements in lhs that are not in rhs
    (fun, any) -> apply lhs on rhs until the result does not change. Collects intermittent values
    (any, fun) -> apply rhs on lhs until the result does not change. Collects intermittent values
    """

    ts = vy_type(lhs, rhs)
    return {
        (NUMBER_TYPE, ts[1]): lambda: LazyList(
            itertools.product(iterable(rhs, ctx), repeat=lhs)
        ),
        (ts[0], NUMBER_TYPE): lambda: LazyList(
            itertools.product(iterable(lhs, ctx), repeat=rhs)
        ),
        (types.FunctionType, ts[1]): lambda: fixed_point(lhs, rhs),
        (ts[0], types.FunctionType): lambda: fixed_point(rhs, lhs),
    }.get(ts, lambda: keep(lhs, rhs))()


def complement(lhs, ctx):
    """Element ⌐
    (num) -> 1 - a
    (str) -> a.split(",")
    """
    ts = vy_type(lhs)
    return {NUMBER_TYPE: lambda: 1 - lhs, str: lambda: lhs.split(",")}.get(
        ts, lambda: vectorise(complement, lhs, ctx=ctx)
    )()


def exclusive_one_range(lhs, ctx):
    """Element ɽ
    (num) -> range(1, a)
    (str) -> a.lower()
    """

    ts = vy_type(lhs)
    return {
        NUMBER_TYPE: lambda: LazyList(range(1, int(lhs))),
        str: lambda: lhs.lower(),
    }.get(ts, lambda: vectorise(exclusive_one_range, lhs, ctx=ctx))


def exclusive_zero_range(lhs, ctx):
    """Element ʁ
    (num) -> range(0, a)
    (str) -> mirror(a)
    """
    ts = vy_type(lhs)
    return {
        NUMBER_TYPE: lambda: LazyList(range(0, int(lhs))),
        str: lambda: merge(lhs, reverse(lhs, ctx)[1:], ctx),
    }.get(ts, lambda: vectorise(exclusive_zero_range, lhs, ctx=ctx))()


def function_call(lhs, ctx):
    """Element †
    (fun) -> lhs()
    (num) -> count of prime factors
    (str) -> vyxal exec lhs
    (lst) -> vectorised not
    """

    # Modifies lhs, because lhs = stack

    top = pop(lhs, 1, ctx=ctx)
    ts = vy_type(top, simple=True)
    if isinstance(top, types.FunctionType):
        lhs += top(lhs, ctx=ctx)
        return None
    else:
        return {
            NUMBER_TYPE: lambda: len(prime_factors(top, ctx)),
            str: lambda: exec(lhs) or [],
            list: lambda: vectorised_not(top, ctx),
        }.get(ts)()


def halve(lhs, ctx):
    """Element ½
    (num) -> lhs / 2
    (str) -> a split into two strings of equal lengths (as close as possible)
    """
    ts = vy_type(lhs)
    return {
        NUMBER_TYPE: lambda: sympy.Rational(lhs, 2),
        str: lambda: wrap(lhs, math.ceil(len(lhs) / 2)),
    }.get(ts, lambda: vectorise(halve, lhs, ctx=ctx))()


def inclusive_one_range(lhs, ctx):
    """Element ɾ
    (num) -> range(1, a + 1)
    (str) -> a.uppercase()
    """

    ts = vy_type(lhs)
    return {
        NUMBER_TYPE: lambda: LazyList(range(1, int(lhs) + 1)),
        str: lambda: lhs.upper(),
    }.get(ts, lambda: vectorise(inclusive_one_range, lhs, ctx=ctx))()


def inclusive_zero_range(lhs, ctx):
    """Element ʀ
    (num) -> range(0, a + 1)
    (str) -> [char is alphabetical? for char in a]
    """
    ts = vy_type(lhs)
    return {
        NUMBER_TYPE: lambda: LazyList(range(0, int(lhs) + 1)),
        str: lambda: scalarify(
            [int(char in string.ascii_letters) for char in lhs]
        ),
    }.get(ts, lambda: vectorise(inclusive_zero_range, lhs, ctx=ctx))()


def infinite_replace(lhs, rhs, other, ctx):
    """Element ¢
    (any, any, any) -> replace b in a with c until a doesn't change
    """

    prev = deep_copy(lhs)
    while True:
        lhs = replace(lhs, rhs, other, ctx)
        if lhs == prev:
            break
        prev = deep_copy(lhs)

    return lhs


def is_prime(lhs, ctx):
    """Element æ
    (num) -> is a prime?
    (str) -> case of a (1 if all letters in a are uppercase,
             0 if all letters in a are lowercase,
            -1 if mixed case)
    """

    ts = vy_type(lhs)
    return {
        NUMBER_TYPE: lambda: int(sympy.ntheory.isprime(lhs)),
        str: lambda: case_of(lhs),
    }.get(ts, vectorise(is_prime, lhs, ctx=ctx))()


def log_mold_multi(lhs, rhs, ctx):
    """Element •
    (num, num) -> log_lhs(rhs)
    (num, str) -> [char * lhs for char in rhs]
    (str, num) -> [char * rhs for char in lhs]
    (str, str) -> lhs.with_capitalisation_of(rhs)
    (lst, lst) -> lhs molded to the shape of rhs
    """

    ts = vy_type(lhs, rhs, True)

    return {
        (NUMBER_TYPE, NUMBER_TYPE): lambda: sympy.Rational(math.log(lhs, rhs)),
        (NUMBER_TYPE, str): lambda: "".join([char * lhs for char in rhs]),
        (str, NUMBER_TYPE): lambda: "".join([char * rhs for char in lhs]),
        (str, str): lambda: transfer_capitalisation(rhs, lhs),
        (list, list): lambda: mold(lhs, rhs),
    }.get(ts, lambda: vectorise(log_mold_multi, lhs, rhs, ctx=ctx))()


def merge(lhs, rhs, ctx):
    """Element J
    (scl, scl) -> concatenate a and b
    (lst, scl) -> append b to a
    (scl, lst) -> prepend a to b
    (lst, lst) -> merged a and b
    """

    ts = vy_type(lhs, rhs, simple=True)
    return {
        (NUMBER_TYPE, NUMBER_TYPE): lambda: vy_eval(
            str(lhs) + str(rhs), ctx=ctx
        ),
        (NUMBER_TYPE, str): lambda: add(lhs, rhs),
        (str, NUMBER_TYPE): lambda: add(lhs, rhs),
        (str, str): lambda: lhs + rhs,
        (list, ts[1]): lambda: lhs + [rhs],
        (ts[0], list): lambda: [lhs] + rhs,
        (list, list): lambda: lhs + rhs,
    }.get(ts)()


def prime_factors(lhs, ctx):
    """Element Ǐ
    (num) -> prime factors
    (str) -> lhs + lhs[0]"""
    ts = vy_type(lhs)
    return {
        NUMBER_TYPE: lambda: sympy.ntheory.primefactors(int(lhs)),
        str: lambda: lhs + lhs[0],
    }.get(ts, lambda: vectorise(prime_factors, lhs, ctx=ctx))()


def replace(lhs, rhs, other, ctx):
    """Element V
    (any, any, any) -> a.replace(b, c)
    """

    if vy_type(lhs, simple=True) is not list:
        return str(lhs).replace(str(rhs), str(other))
    else:
        return [other if value == rhs else value for value in iterable(lhs)]


def reverse(lhs, ctx):
    """Element Ṙ
    (any) -> a reversed
    """

    ts = vy_type(lhs)
    return {
        NUMBER_TYPE: lambda: reverse_number(lhs),
        str: lambda: lhs[::-1],
        list: lambda: lhs[::-1],
        LazyList: lambda: lhs.reversed(),
    }.get(ts)()


def split_on(lhs, rhs, ctx):
    """
    Element €
    (num, num) -> str(lhs).split(rhs)
    (num, str) -> str(lhs).split(rhs)
    (str, num) -> lhs.split(str(rhs))
    (str, str) -> lhs.split(rhs)

    """
    if [primitive_type(lhs), primitive_type(rhs)] == [SCALAR_TYPE, SCALAR_TYPE]:
        return str(lhs).split(str(rhs))

    else:
        ret, temp = [], []
        for item in iterable(lhs, ctx=ctx):
            if item == rhs:
                ret.append(temp[::])
                temp = []
            else:
                temp.append(item)
        if temp:
            ret.append(temp)
        return ret


def subtract(lhs, rhs, ctx):
    """Element -
    (num, num) -> lhs - rhs
    (num, str) -> ("-" * lhs) + rhs
    (str, num) -> lhs + ("-" * rhs)
    (str, str) -> lhs.replace(rhs, "")
    """

    ts = vy_type(lhs, rhs)
    return {
        (NUMBER_TYPE, NUMBER_TYPE): lambda: lhs - rhs,
        (NUMBER_TYPE, str): lambda: ("-" * lhs) + rhs,
        (str, NUMBER_TYPE): lambda: lhs + ("-" * rhs),
        (str, str): lambda: lhs.replace(rhs, ""),
    }.get(ts, lambda: vectorise(subtract, lhs, rhs, ctx=ctx))()


def vectorise(function, lhs, rhs=None, other=None, explicit=False, ctx=None):
    """
    Maps a function over arguments
    Probably cursed but whatever.
    The explicit argument is mainly for stopping element-wise
    vectorisation happening.
    """

    if other is not None:
        # That is, three argument vectorisation
        # That is:

        ts = primitive_type(lhs), primitive_type(rhs), primitive_type(other)

        simple = {
            (SCALAR_TYPE, SCALAR_TYPE, SCALAR_TYPE): lambda: safe_apply(
                function, lhs, rhs, other, ctx=ctx
            ),
            (SCALAR_TYPE, SCALAR_TYPE, list): lambda: (
                safe_apply(function, lhs, rhs, x, ctx=ctx) for x in other
            ),
            (SCALAR_TYPE, list, SCALAR_TYPE): lambda: (
                safe_apply(function, lhs, x, other, ctx=ctx) for x in rhs
            ),
            (SCALAR_TYPE, list, list): lambda: (
                safe_apply(function, lhs, x, y, ctx=ctx)
                for x, y in vy_zip(rhs, other)
            ),
            (list, SCALAR_TYPE, SCALAR_TYPE): lambda: (
                safe_apply(function, x, rhs, other, ctx=ctx) for x in lhs
            ),
            (list, SCALAR_TYPE, list): lambda: (
                safe_apply(function, x, rhs, y, ctx=ctx)
                for x, y in vy_zip(lhs, other)
            ),
            (list, list, SCALAR_TYPE): lambda: (
                safe_apply(function, x, y, other, ctx=ctx)
                for x, y in vy_zip(lhs, rhs)
            ),
            (list, list, list): lambda: (
                safe_apply(function, x, y, z, ctx=ctx)
                for x, y, z in vy_zip(lhs, rhs, other)
            ),
        }

        if explicit:
            return LazyList(
                (safe_apply(x, rhs, other, ctx=ctx) for x in iterable(lhs))
            )
        else:
            return LazyList(simple.get(ts)())
    elif rhs is not None:
        # That is, two argument vectorisation
        ts = primitive_type(lhs), primitive_type(rhs)
        simple = {
            (SCALAR_TYPE, SCALAR_TYPE): lambda: safe_apply(
                function, lhs, rhs, ctx=ctx
            ),
            (SCALAR_TYPE, list): lambda: (
                safe_apply(function, lhs, x, ctx=ctx) for x in rhs
            ),
            (list, SCALAR_TYPE): lambda: (
                safe_apply(function, x, rhs, ctx=ctx) for x in lhs
            ),
            (list, list): lambda: (
                safe_apply(function, x, y, ctx=ctx) for x, y in vy_zip(lhs, rhs)
            ),
        }

        explicit_dict = {
            (SCALAR_TYPE, SCALAR_TYPE): lambda: (
                safe_apply(function, x, rhs, ctx=ctx) for x in iterable(lhs)
            ),
            (SCALAR_TYPE, list): lambda: (
                safe_apply(function, lhs, x, ctx=ctx) for x in rhs
            ),
            (list, SCALAR_TYPE): lambda: (
                safe_apply(function, x, rhs, ctx=ctx) for x in lhs
            ),
            (list, list): lambda: (
                safe_apply(function, x, rhs, ctx=ctx) for x in lhs
            ),
        }

        if explicit:
            return list(explicit_dict.get(ts)())
        else:
            return list(simple.get(ts)())
    else:
        # That is, single argument vectorisation
        if explicit:
            lhs = iterable(lhs, range, ctx=ctx)
        else:
            lhs = iterable(lhs, ctx=ctx)

        return LazyList((safe_apply(function, x, ctx=ctx) for x in lhs))


def vectorised_not(lhs, ctx):
    return {NUMBER_TYPE: lambda: int(not lhs), str: lambda: int(not lhs)}.get(
        vy_type(lhs), lambda: vectorise(vectorised_not, lhs, ctx=ctx)
    )()


def vy_print(lhs, end="\n", ctx=None):
    """Element ,
    (any) -> send to stdout
    """

    ctx.printed = True
    ts = vy_type(lhs)

    if ts is LazyList:
        lhs.output(end, ctx)
    elif ts is list:
        LazyList(lhs).output(end, ctx)
    else:
        if ctx.online:
            ctx.online_output += str(lhs)
            # TODO: use custom string func
        else:
            print(lhs, end=end)


def vy_type(item, other=None, simple=False):
    if other is not None:
        return (vy_type(item, simple=simple), vy_type(other, simple=simple))
    if (x := type(item)) in (int, sympy.Rational, complex):
        return NUMBER_TYPE
    elif simple and isinstance(item, LazyList):
        return list
    else:
        return x


elements: dict[str, tuple[str, int]] = {
    "¬": process_element("int(not lhs)", 1),
    "∧": process_element("lhs and rhs", 2),
    "⟑": process_element("rhs and lhs", 2),
    "∨": process_element("lhs or rhs", 2),
    "⟇": process_element("rhs or lhs", 2),
    "÷": (
        "lhs = pop(stack, 1, ctx); stack += iterable(lhs, ctx=ctx)",
        1,
    ),
    "×": process_element("'*'", 0),
    "•": process_element(log_mold_multi, 2),
    "†": (
        "top = function_call(stack, ctx)\n"
        + "if top is not None: stack.append(top)",
        1,
    ),
    "€": process_element(split_on, 2),
    "½": process_element(halve, 1),
    "↔": process_element(combinations_with_replacement, 2),
    "¢": process_element(infinite_replace, 3),
    "⌐": process_element(complement, 1),
    "æ": process_element(is_prime, 1),
    "ʀ": process_element(inclusive_zero_range, 1),
    "ʁ": process_element(exclusive_zero_range, 1),
    "ɾ": process_element(inclusive_one_range, 1),
    "ɽ": process_element(exclusive_one_range, 1),
    "+": process_element(add, 2),
    ",": process_element(vy_print, 1),
    "-": process_element(subtract, 2),
    "?": (
        "ctx.use_top_input = True; lhs = get_input(ctx); "
        "ctx.use_top_input = False; stack.append(lhs)",
        0,
    ),
    '"': process_element("[lhs, rhs]", 2),
    "J": process_element(merge, 2),
    "V": process_element(replace, 3),
}
modifiers = {
    "v": (
        "arguments = pop(stack, function_A.stored_arity, ctx=ctx)\n"
        + "if len(arguments) == 1: arguments = [arguments]\n"
        + "stack.append"
        + "(vectorise(function_A, *arguments[::-1], explicit=True, ctx=ctx))\n"
    )
}
