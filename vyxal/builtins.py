import itertools
import math
import os
import random
import string
import sys
import urllib.request
from datetime import date
from datetime import datetime as dt

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/.."
sys.path.insert(1, THIS_FOLDER)

import vyxal
from vyxal import array_builtins
from vyxal.factorials import FIRST_100_FACTORIALS
from vyxal.utilities import *

try:
    import numpy
    import pwn
    import regex
    import sympy
except:
    os.system("pip3 install -r requirements.txt --quiet --disable-pip-version-check")
    import numpy
    import pwn
    import regex
    import sympy


def tapp(x):
    typ = vy_type(x)
    if typ is Generator:
        print(x[:5])
    else:
        print(x)

    print(CTX.stack)
    return x


def add(lhs, rhs, context=None):
    """
    Returns lhs + rhs. Check command docs for type cohesion.
    """
    types = vy_type(lhs), vy_type(rhs)
    return {
        (Number, Number): lambda: lhs + rhs,
        (str, str): lambda: lhs + rhs,
        (str, Number): lambda: str(lhs) + str(rhs),
        (Number, str): lambda: str(lhs) + str(rhs),
    }.get(types, lambda: vectorise(add, lhs, rhs))()


def all_combinations(vector, context=None):
    ret = []
    for i in range(len(vector) + 1):
        ret = join(ret, combinations_replace_generate(vector, i))
    return ret


def all_prime_factors(item, context=None):
    if vy_type(item) == Number:
        m = sympy.ntheory.factorint(int(item))
        out = []
        for key in sorted(m.keys()):
            out += [key] * m[key]
        return out
    elif vy_type(item) is str:
        return item.title()
    return vectorise(all_prime_factors, item)


def apply_to_register(function, vector, context):
    vector.append(context.register)
    if function.stored_arity > 1:
        top, over = pop(context.stack, 2)
        context.stack.append(top)
        context.stack.append(over)
    vector += function_call(function, vector)
    context.register = pop(vector)


def assigned(vector, index, item, context=None):
    if type(vector) is str:
        vector = list(vector)
        vector[index] = item
        return "".join([str(x) for x in vector])
    else:
        temp = array_builtins.deref(vector, False)
        temp[index] = item
        return temp


def optimal_compress(word, context=None):
    DP = [" " * (len(word) + 1)] * (len(word) + 1)
    DP[0] = ""
    for index in range(1, len(word) + 1):
        for left in range(max(0, index - words.dictionary.max_word_len), index - 1):
            i = words.word_index(word[left:index])
            if i != -1:
                DP[index] = min([DP[index], DP[left] + i], key=len)
                break
        DP[index] = min([DP[index], DP[index - 1] + word[index - 1]], key=len)
    return DP[-1]


def bifurcate(item, context=None):
    t_item = vy_type(item)
    if t_item in (Number, list, str):
        return [item, reverse(item)]
    else:
        g = item._dereference()
        return [g, reverse(g)]


def bit_and(lhs, rhs, context=None):
    types = (vy_type(lhs), vy_type(rhs))
    return {
        (Number, Number): lambda: lhs & rhs,
        (Number, str): lambda: rhs.center(lhs),
        (str, Number): lambda: lhs.center(rhs),
        (str, str): lambda: lhs.center(len(rhs) - len(lhs)),
        (types[0], list): lambda: [bit_and(lhs, item) for item in rhs],
        (list, types[1]): lambda: [bit_and(item, rhs) for item in lhs],
        (list, list): lambda: list(map(lambda x: bit_and(*x), vy_zip(lhs, rhs))),
        (list, Generator): lambda: two_argument(bit_and, lhs, rhs),
        (Generator, list): lambda: two_argument(bit_and, lhs, rhs),
        (Generator, Generator): lambda: two_argument(bit_and, lhs, rhs),
    }.get(types, lambda: vectorise(bit_and, lhs, rhs))()


def bit_or(lhs, rhs, context=None):
    types = (vy_type(lhs), vy_type(rhs))
    if types == (str, str):
        suffixes = {lhs[-i:] for i in range(1, len(lhs) + 1)}
        prefixes = {rhs[:i] for i in range(1, len(rhs) + 1)}
        common = suffixes & prefixes
        if len(common) == 0:
            return lhs + rhs
        common = sorted(common, key=lambda x: len(x))[-1]
        return lhs[: -len(common)] + common + rhs[len(common) :]
    return {
        (Number, Number): lambda: lhs | rhs,
        (Number, str): lambda: lhs[:rhs] + lhs[rhs + 1 :],
        (str, Number): lambda: rhs[:lhs] + rhs[lhs + 1 :],
        (types[0], list): lambda: [bit_or(lhs, item) for item in rhs],
        (list, types[1]): lambda: [bit_or(item, rhs) for item in lhs],
        (list, list): lambda: list(map(lambda x: bit_or(*x), vy_zip(lhs, rhs))),
        (list, Generator): lambda: two_argument(bit_or, lhs, rhs),
        (Generator, list): lambda: two_argument(bit_or, lhs, rhs),
        (Generator, Generator): lambda: two_argument(bit_or, lhs, rhs),
    }.get(types, lambda: vectorise(bit_or, lhs, rhs))()


def bit_not(item, context=None):
    return {
        str: lambda: int(any(map(lambda x: x.isupper(), item))),
        Number: lambda: ~item,
    }.get(vy_type(item), lambda: vectorise(bit_not, item))()


def bit_xor(lhs, rhs, context=None):
    types = (vy_type(lhs), vy_type(rhs))
    return {
        (Number, Number): lambda: lhs ^ rhs,
        (Number, str): lambda: (" " * lhs) + rhs,
        (str, Number): lambda: lhs + (" " * rhs),
        (str, str): lambda: levenshtein_distance(lhs, rhs),
        (types[0], list): lambda: [bit_xor(lhs, item) for item in rhs],
        (list, types[1]): lambda: [bit_xor(item, rhs) for item in lhs],
        (list, list): lambda: list(map(lambda x: bit_xor(*x), vy_zip(lhs, rhs))),
        (list, Generator): lambda: two_argument(bit_xor, lhs, rhs),
        (Generator, list): lambda: two_argument(bit_xor, lhs, rhs),
        (Generator, Generator): lambda: two_argument(bit_xor, lhs, rhs),
    }.get(types, lambda: vectorise(bit_xor, lhs, rhs))()


def ceiling(item, context=None):
    return {Number: lambda: math.ceil(item), str: lambda: item.split(" ")}.get(
        vy_type(item), lambda: vectorise(ceiling, item)
    )()


def centre(vector, context=None):
    vector = array_builtins.deref(iterable(vector), True)
    focal = max(map(len, vector))

    @Generator
    def gen():
        for item in vector:
            yield item.center(focal)

    return gen()


def chrord(item, context=None):
    t_item = vy_type(item)
    if t_item is str and len(item) == 1:
        return ord(item)
    elif t_item == Number:
        return chr(int(item))
    else:
        return Generator(map(chrord, item))


def closest_prime(item, context=None):
    up, down = next_prime(item), prev_prime(item)
    if abs(item - down) < abs(item - up):
        return down
    return up


def compare(lhs, rhs, mode, context=None):
    op = ["==", "<", ">", "!=", "<=", ">="][mode]

    types = tuple(map(vy_type, [lhs, rhs]))
    boolean = {
        types: lambda lhs, rhs: eval(f"lhs {op} rhs"),
        (Number, str): lambda lhs, rhs: eval(f"str(lhs) {op} rhs"),
        (str, Number): lambda lhs, rhs: eval(f"lhs {op} str(rhs)"),
        (types[0], list): lambda *x: [compare(lhs, item, mode) for item in rhs],
        (list, types[1]): lambda *x: [compare(item, rhs, mode) for item in lhs],
        (Generator, types[1]): lambda *y: vectorise(
            lambda x: compare(x, rhs, mode), lhs
        ),
        (types[0], Generator): lambda *y: vectorise(
            lambda x: compare(lhs, x, mode), rhs
        ),
        (list, list): lambda *y: list(
            map(lambda x: compare(*x, mode), vy_zip(lhs, rhs))
        ),
        (list, Generator): lambda *y: Generator(
            map(lambda x: compare(*x, mode), vy_zip(lhs, rhs))
        ),
        (Generator, list): lambda *y: Generator(
            map(lambda x: compare(*x, mode), vy_zip(lhs, rhs))
        ),
        (Generator, Generator): lambda *y: Generator(
            map(lambda x: compare(*x, mode), vy_zip(lhs, rhs))
        ),
    }[types](lhs, rhs)
    if type(boolean) is bool:
        return int(boolean)
    else:
        return boolean


def complement(item, context=None):
    return {Number: lambda: 1 - item, str: lambda: item.split(",")}.get(
        vy_type(item), lambda: vectorise(complement, item)
    )()


def combinations_replace_generate(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)
    if Function not in types:
        ret = {
            (Number, types[1]): lambda: Generator(
                itertools.product(iterable(rhs), repeat=lhs)
            ),
            (types[0], Number): lambda: Generator(
                itertools.product(iterable(lhs), repeat=rhs)
            ),
        }.get(types, lambda: -1)()
        if ret != -1:
            return ret
        out = "" if type(lhs) is str else []
        for item in lhs:
            if item in rhs:
                if type(lhs) is str:
                    out += item
                else:
                    out.append(item)
        return out
    else:
        if vy_type(lhs) is Function:
            fn, init = lhs, rhs
        else:
            fn, init = rhs, lhs

        @Generator
        def gen():
            prev = None
            curr = init
            while prev != curr:
                yield curr
                prev = array_builtins.deref(curr)
                curr = fn([curr])[-1]

        return gen()


def const_divisibility(item, n, string_overload, context=None):
    def int_if_not_tuple():
        a = string_overload(item)
        if type(a) is tuple:
            return a
        else:
            return int(a)

    return {
        Number: lambda: int(item % n == 0),
        str: int_if_not_tuple,
        list: int_if_not_tuple,
    }.get(
        vy_type(item),
        lambda: vectorise(lambda x: const_divisibility(x, n, string_overload), item),
    )()


def counts(vector, context=None):
    ret = []
    vector = iterable(vector)
    for item in set(vector):
        ret.append([item, vector.count(item)])
    return ret


def decimalify(vector, context=None):
    if vy_type(vector) == Number:
        return iterable(vector)
    elif vy_type(vector) is str:
        return list(vector)
    else:
        return functools.reduce(lambda x, y: divide(x, y), vector)


def deltas(vector, context=None):
    ret = []
    vector = iterable(vector)
    for i in range(len(vector) - 1):
        ret.append(subtract(vector[i + 1], vector[i]))
    return ret


def dictionary_compress(item, context=None):
    return "`" + optimal_compress(vy_str(item)) + "`"


def distance_between(lhs, rhs, context=None):
    inner = Generator(
        map(lambda x: exponate(subtract(x[0], x[1]), 2), vy_zip(lhs, rhs))
    )
    inner = array_builtins.summate(inner)
    return exponate(inner, 0.5)


def distribute(vector, value, context=None):
    types = vy_type(vector), vy_type(value)
    if types == (Number, Number):
        return abs(vector - value)
    vector = iterable(vector)
    if vy_type(vector) is Generator:
        vector = vector._dereference()
    remaining = value
    index = 0
    while remaining > 0:
        vector[index % len(vector)] += 1
        index += 1
        remaining -= 1

    return vector


def divide(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)

    def handle_numbers(lhs, rhs):
        if rhs == 0:
            return 0
        normal, int_div = lhs / rhs, lhs // rhs
        return [normal, int_div][normal == int_div]

    return {
        (Number, Number): lambda: handle_numbers(lhs, rhs),
        (str, str): lambda: split(lhs, rhs),
        (str, Number): lambda: wrap(lhs, len(lhs) // rhs),
        (Number, str): lambda: wrap(rhs, len(rhs) // lhs),
        (list, types[1]): lambda: [divide(item, rhs) for item in lhs],
        (types[0], list): lambda: [divide(lhs, item) for item in rhs],
        (list, list): lambda: list(map(lambda x: divide(*x), vy_zip(lhs, rhs))),
        (list, Generator): lambda: two_argument(divide, lhs, rhs),
        (Generator, list): lambda: two_argument(divide, lhs, rhs),
        (Generator, Generator): lambda: two_argument(divide, lhs, rhs),
    }.get(types, lambda: vectorise(divide, lhs, rhs))()


def divisors_of(item, context=None):
    t_item = vy_type(item)
    if t_item in [list, Generator]:
        return Generator(array_builtins.prefixes(item))

    divisors = []
    if t_item == str:

        @Generator
        def gen():
            s = list(item)
            i = itertools.chain.from_iterable(
                itertools.combinations(s, r) for r in range(1, len(s) + 1)
            )

            for sub in i:
                sub = "".join(sub)
                if len(item.split(sub)) == 2:
                    yield sub

        return gen()

    for value in vy_range(item, 1, 1):
        if modulo(item, value) == 0:
            divisors.append(value)

    return divisors


def dont_pop(function, vector, context):
    if function.stored_arity == 1:
        vector.append(vy_filter(function, pop(vector)))
    else:
        context.retain_items = True
        args = pop(vector, function.stored_arity, context=context)
        vector.append(safe_apply(function, args[::-1]))
        context.retain_items = False


def escape(item, context=None):
    ret = ""
    escaped = False
    for char in item:
        if escaped:
            ret += "\\" + char
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            ret += '\\"'
        else:
            ret += char
    return ret


def exponate(lhs, rhs, context=None):
    types = (vy_type(lhs), vy_type(rhs))

    if types == (str, str):
        pobj = regex.compile(lhs)
        mobj = pobj.search(rhs)
        return list(mobj.span()) if mobj else []

    if types == (str, Number):
        factor = rhs
        if 0 < rhs < 1:
            factor = int(1 / rhs)
        return lhs[::factor]
    return {
        (Number, Number): lambda: lhs ** rhs,
        (types[0], list): lambda: [exponate(lhs, item) for item in rhs],
        (list, types[1]): lambda: [exponate(item, rhs) for item in lhs],
        (list, list): lambda: list(map(lambda x: exponate(*x), vy_zip(lhs, rhs))),
        (list, Generator): lambda: two_argument(exponate, lhs, rhs),
        (Generator, list): lambda: two_argument(exponate, lhs, rhs),
        (Generator, Generator): lambda: two_argument(exponate, lhs, rhs),
    }.get(types, lambda: vectorise(exponate, lhs, rhs))()


def factorial(item, context=None):
    t_item = vy_type(item)
    if t_item == Number:
        if item in FIRST_100_FACTORIALS:
            return FIRST_100_FACTORIALS[item]
        else:
            FIRST_100_FACTORIALS[item] = math.factorial(item)
        return FIRST_100_FACTORIALS[item]
    elif t_item == str:
        return sentence_case(item)
    else:
        return vectorise(factorial, item)


def factorials():
    # Different to factorial because this is a list of all factorials
    for i in range(1, 101):
        yield FIRST_100_FACTORIALS[i]

    temp = FIRST_100_FACTORIALS[100]
    n = 101

    while True:
        temp *= n
        FIRST_100_FACTORIALS[n] = temp
        n += 1
        yield temp


def fibonacci():
    # A generator of all the fibonacci numbers
    # Pro-tip: wrap in a generator before pushing to globals.stack

    yield 0
    yield 1

    memory = [0, 1]
    while True:
        temp = memory[-1] + memory[-2]
        memory.append(temp)
        yield temp


def find(haystack, needle, start=0, context=None):
    if type(needle) is Function:
        return array_builtins.indices_where(haystack, needle)

    # It looks like something from 2001
    index = 0
    haystack = iterable(haystack)
    if type(haystack) is str:
        needle = str(needle)
    if type(start) is int or (type(start) is str and start.isnumeric()):
        index = int(start)

    if (vy_type(haystack), vy_type(needle)) in (
        (Number, Number),
        (Number, str),
        (str, Number),
        (str, str),
    ):
        return str(haystack).find(str(needle), start=index)

    index = 0
    while True:
        try:
            temp = haystack[index]
            if array_builtins.deref(temp) == array_builtins.deref(needle):
                return index
        except:
            break
        index += 1
    return -1


def flatten(item, context=None):
    """
    Returns a deep-flattened (all sublists expanded) version of the input
    """
    t_item = vy_type(item)
    if t_item is Generator:
        return flatten(item._dereference())
    else:
        ret = []
        for x in item:
            if type(x) in [list, Generator]:
                ret += flatten(x)
            else:
                ret.append(x)
        return ret


def floor(item, context=None):
    return {
        Number: lambda: math.floor(item),
        str: lambda: int("".join(digit for digit in item if digit in "0123456789")),
    }.get(vy_type(item), lambda: vectorise(floor, item))()


def format_string(value, items, context=None):
    ret = ""
    index = 0
    f_index = 0

    while index < len(value):
        if value[index] == "\\":
            ret += "\\" + value[index + 1]
            index += 1
        elif value[index] == "%":
            # print(f_index, f_index % len(items))
            ret += str(items[f_index % len(items)])
            f_index += 1
        else:
            ret += value[index]
        index += 1
    return ret


def fractionify(item, context=None):
    import re

    if vy_type(item) == Number:
        from fractions import Fraction

        frac = Fraction(item).limit_denominator()
        return [frac.numerator, frac.denominator]
    elif type(item) is str:
        if re.match(r"-?\d+(\.\d+)?", item):
            return fractionify(eval(item))
        else:
            return item
    else:
        return vectorise(fractionify, item)


def function_call(fn, vector, context=None):
    if type(fn) is Function:
        return fn(vector, self=fn)
    else:
        import vyxal.interpreter

        return [
            {
                Number: lambda: len(prime_factors(fn)),
                str: lambda: exec(vyxal.interpreter.vy_compile(fn)) or [],
            }.get(vy_type(fn), lambda: vectorised_not(fn))()
        ]


def gcd(lhs, rhs=None, context=None):
    if rhs:
        return {
            (Number, Number): lambda: math.gcd(int(lhs), int(rhs)),
            (Number, str): lambda: max(
                set(divisors_of(str(lhs))) & set(divisors_of(rhs)), key=lambda x: len(x)
            ),
            (str, Number): lambda: max(
                set(divisors_of(lhs)) & set(divisors_of(str(rhs))), key=lambda x: len(x)
            ),
            (str, str): lambda: max(
                set(divisors_of(lhs)) & set(divisors_of(rhs)), key=lambda x: len(x)
            ),
        }.get((vy_type(lhs), vy_type(rhs)), lambda: vectorise(gcd, lhs, rhs))()

    else:
        # I can't use vy_reduce because ugh reasons
        lhs = array_builtins.deref(lhs, True)
        return int(numpy.gcd.reduce(lhs))


def get_input(predefined_level=None, context=None):
    level = CTX.input_level
    if predefined_level is not None:
        level = predefined_level

    if level in CTX.input_values:
        source, index = CTX.input_values[level]
    else:
        source, index = [], -1
    if source:
        ret = source[index % len(source)]
        CTX.input_values[level][1] += 1

        if CTX.keg_mode and type(ret) is str:
            return [ord(c) for c in ret]
        return ret
    else:
        try:
            temp = vy_eval(input())
            if CTX.keg_mode and type(temp) is str:
                return [ord(c) for c in temp]
            return temp
        except:
            return 0


def graded(item, context=None):
    return {Number: lambda: item + 2, str: lambda: item.upper(),}.get(
        vy_type(item),
        lambda: Generator(
            map(
                lambda x: x[0],
                sorted(enumerate(array_builtins.deref(item)), key=lambda x: x[-1]),
            )
        ),
    )()


def graded_down(item, context=None):
    return {Number: lambda: item - 2, str: lambda: item.lower(),}.get(
        vy_type(item),
        lambda: Generator(
            map(
                lambda x: x[0],
                sorted(
                    enumerate(array_builtins.deref(item)),
                    key=lambda x: x[-1],
                    reverse=True,
                ),
            )
        ),
    )()


def halve(item, context=None):
    return {
        Number: lambda: divide(item, 2),
        str: lambda: wrap(item, ceiling(len(item) / 2)),
    }.get(vy_type(item), lambda: vectorise(halve, item))()


def infinite_replace(haystack, needle, replacement, context=None):
    import copy

    loop = True
    prev = copy.deepcopy(haystack)
    while (
        loop
    ):  # I intentionally used a post-test loop here to avoid making more calls to replace than neccesary
        haystack = replace(haystack, needle, replacement)
        loop = haystack != prev
        prev = copy.deepcopy(haystack)
    return haystack


def inserted(vector, item, index, context):
    temp = array_builtins.deref(iterable(vector), False)
    t_vector = type(temp)
    if t_vector is list:
        temp.insert(index, item)
        return temp
    return {
        str: lambda: temp[:index] + str(item) + temp[index:],
    }.get(t_vector, lambda: inserted(temp._dereference(), item, index))()


def integer_divide(lhs, rhs, context):
    types = vy_type(lhs), vy_type(rhs)
    return {
        (Number, Number): lambda: lhs // rhs,
        (Number, str): lambda: divide(lhs, rhs)[0],
        (str, Number): lambda: divide(lhs, rhs)[0],
        (Function, types[1]): lambda: vy_reduce(lhs, reverse(rhs), context)[0],
        (types[0], Function): lambda: vy_reduce(rhs, reverse(lhs), context)[0],
    }.get(types, lambda: vectorise(integer_divide, lhs, rhs))()


def integer_list(value, context=None):
    charmap = dict(zip("etaoinshrd", "0123456789"))
    ret = []
    for c in value.split():
        temp = ""
        for m in c:
            temp += charmap[m]
        ret.append(int(temp))
    return ret


def is_divisble(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)
    return {
        (Number, Number): lambda: int(modulo(lhs, rhs) == 0 and rhs != 0),
        (str, str): lambda: (lhs,) * len(rhs),
        (str, Number): lambda: (lhs,) * rhs,
        (Number, str): lambda: (rhs,) * lhs,
    }.get(types, lambda: vectorise(is_divisble, lhs, rhs))()


def is_empty(item, context=None):
    return {Number: lambda: item % 3, str: lambda: int(item == "")}.get(
        vy_type(item), lambda: vectorise(is_empty, item)
    )()


def is_prime(n, context=None):
    if type(n) is str:
        if n.upper() == n.lower():
            return -1
        else:
            return int(n.upper() == n)
    if vy_type(n) in [list, Generator]:
        return vectorise(is_prime, n)
    return 1 if sympy.ntheory.isprime(n) else 0


def is_square(n, context=None):
    if type(n) in (float, str):
        return 0
    elif isinstance(n, int):
        return int(
            any([exponate(y, 2) == n for y in range(1, math.ceil(n / 2) + 1)])
        ) or int(n == 0)
    else:
        return vectorise(is_square, n)


def iterable_shift(vector, direction, times=1, context=None):
    vector = array_builtins.deref(iterable(vector))
    t_vector = type(vector)
    for _ in range(times):
        if direction == ShiftDirections.LEFT:
            if t_vector is list:
                # [1, 2, 3] -> [2, 3, 1]
                vector = vector[::-1]
                temp = pop(vector)
                vector = vector[::-1]
                vector.append(temp)
            else:
                # abc -> bca
                vector = join(vector[1:], vector[0])
        elif direction == ShiftDirections.RIGHT:
            if t_vector is list:
                # [1, 2, 3] -> [3, 1, 2]
                temp = pop(vector)
                vector.insert(0, temp)
            else:
                # abc -> cab
                vector = join(vector[-1], vector[:-1])

    return vector


def join(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)
    return {
        (types[0], types[1]): lambda: str(lhs) + str(rhs),
        (Number, Number): lambda: vy_eval(str(lhs) + str(rhs)),
        (types[0], list): lambda: [lhs] + rhs,
        (list, types[1]): lambda: lhs + [rhs],
        (types[0], Generator): lambda: [lhs] + rhs._dereference(),
        (Generator, types[1]): lambda: lhs._dereference() + [rhs],
        (list, list): lambda: lhs + rhs,
        (list, Generator): lambda: lhs + rhs._dereference(),
        (Generator, list): lambda: lhs._dereference() + rhs,
        (Generator, Generator): lambda: lhs._dereference() + rhs._dereference(),
    }[types]()


def join_on(vector, item, context=None):
    types = vy_type(vector), vy_type(item)
    return {
        (Number, Number): lambda: vy_eval(str(item).join(str(vector))),
        (Number, str): lambda: item.join(str(vector)),
        (str, str): lambda: item.join(vector),
        (list, types[1]): lambda: vy_str(item).join([vy_str(n) for n in vector]),
        (Generator, types[1]): lambda: vy_str(item).join(
            [vy_str(n) for n in array_builtins.deref(vector)]
        ),
    }[types]()


def levenshtein_distance(s1, s2, context=None):
    # https://stackoverflow.com/a/32558749
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(
                    1 + min((distances[i1], distances[i1 + 1], distances_[-1]))
                )
        distances = distances_
    return distances[-1]


def log(lhs, rhs, context=None):
    types = (vy_type(lhs), vy_type(rhs))
    if types == (str, str):
        ret = ""
        for i in range(min(len(lhs), len(rhs))):
            if rhs[i].isupper():
                ret += lhs[i].upper()
            elif rhs[i].islower():
                ret += lhs[i].lower()
            else:
                ret += lhs[i]

        if len(lhs) > len(rhs):
            ret += lhs[i + 1 :]

        return ret

    return {
        (Number, Number): lambda: math.log(lhs, rhs),
        (str, Number): lambda: "".join([c * rhs for c in lhs]),
        (Number, str): lambda: "".join([c * lhs for c in rhs]),
        (list, list): lambda: array_builtins.mold(lhs, rhs),
        (list, Generator): lambda: array_builtins.mold(
            lhs, list(map(array_builtins.deref, array_builtins.deref(rhs)))
        ),
        (Generator, list): lambda: array_builtins.mold(
            list(map(array_builtins.deref, array_builtins.deref(lhs))), rhs
        ),
        (Generator, Generator): lambda: array_builtins.mold(
            list(map(array_builtins.deref, array_builtins.deref(lhs))),
            list(map(array_builtins.deref, array_builtins.deref(rhs))),
        ),  # There's a chance molding raw generators won't work
    }.get(types, lambda: vectorise(log, lhs, rhs))()


def lshift(lhs, rhs, context=None):
    types = (vy_type(lhs), vy_type(rhs))
    return {
        (Number, Number): lambda: lhs << rhs,
        (Number, str): lambda: rhs.ljust(lhs),
        (str, Number): lambda: lhs.ljust(rhs),
        (str, str): lambda: lhs.ljust(len(rhs) - len(lhs)),
        (types[0], list): lambda: [lshift(lhs, item) for item in rhs],
        (list, types[1]): lambda: [lshift(item, rhs) for item in lhs],
        (list, list): lambda: list(map(lambda x: lshift(*x), vy_zip(lhs, rhs))),
        (list, Generator): lambda: two_argument(lshift, lhs, rhs),
        (Generator, list): lambda: two_argument(lshift, lhs, rhs),
        (Generator, Generator): lambda: two_argument(lshift, lhs, rhs),
    }.get(types, lambda: vectorise(lshift, lhs, rhs))()


def mirror(item, context=None):
    if vy_type(item) in (str, Number):
        return add(item, reverse(item))
    else:
        return join(item, reverse(item))


def modulo(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)

    if types[1] is Number and rhs == 0:
        return 0
    return {
        (Number, Number): lambda: lhs % rhs,
        (str, str): lambda: format_string(lhs, [rhs]),
        (str, Number): lambda: divide(lhs, rhs)[-1],
        (Number, str): lambda: divide(lhs, rhs)[-1],
        (list, types[1]): lambda: [modulo(item, rhs) for item in lhs],
        (types[0], list): lambda: [modulo(lhs, item) for item in rhs],
        (str, list): lambda: format_string(lhs, rhs),
        (list, list): lambda: list(map(lambda x: modulo(*x), vy_zip(lhs, rhs))),
        (list, Generator): lambda: two_argument(modulo, lhs, rhs),
        (Generator, list): lambda: two_argument(modulo, lhs, rhs),
        (Generator, Generator): lambda: two_argument(modulo, lhs, rhs),
    }.get(types, lambda: vectorise(modulo, lhs, rhs))()


def multiply(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)
    if types == (Function, Number):
        lhs.stored_arity = rhs
        return lhs
    elif types == (Number, Function):
        rhs.stored_arity = lhs
        return rhs
    return {
        (Number, Number): lambda: lhs * rhs,
        (str, str): lambda: [x + rhs for x in lhs],
        (str, Number): lambda: lhs * rhs,
        (Number, str): lambda: lhs * rhs,
    }.get(types, lambda: vectorise(multiply, lhs, rhs))()


def ncr(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)
    return {
        (Number, Number): lambda: unsympy(
            sympy.functions.combinatorial.numbers.nC(int(lhs), int(rhs))
        ),
        (str, Number): lambda: [random.choice(lhs) for _ in range(rhs)],
        (Number, str): lambda: [random.choice(rhs) for _ in range(lhs)],
        (str, str): lambda: int(set(lhs) == set(rhs)),
    }.get(types, lambda: vectorise(ncr, lhs, rhs))()


def negate(item, context=None):
    return {Number: lambda: -item, str: lambda: item.swapcase()}.get(
        vy_type(item), lambda: vectorise(negate, item)
    )()


def next_prime(item, context=None):
    if not isinstance(item, int):
        return item

    factor = 1
    while not is_prime(item + factor):
        factor += 1

    return item + factor


def nth_prime(item, context=None):
    t_item = vy_type(item)
    return {
        Number: lambda: sympy.ntheory.prime(int(item) + 1),
        str: lambda: Generator(substrings(item)),
    }.get(t_item, lambda: vectorise(nth_prime, item))()


def nwise_pair(lhs, rhs, context=None):
    if vy_type(rhs) != Number:
        return len(iterable(lhs)) == len(rhs)
    iters = itertools.tee(iterable(lhs), rhs)
    for i in range(len(iters)):
        for j in range(i):
            next(iters[i], None)

    return Generator(zip(*iters))


def one_argument_tail_index(vector, index, start, context=None):
    types = (vy_type(vector), vy_type(index))
    if Number not in types:
        lhs, rhs = vy_str(vector), vy_str(index)
        pobj = regex.compile(lhs)
        if start == 0:
            return pobj.findall(rhs)
        else:
            return pobj.match(rhs).groups()
    return {
        (Number, Number): lambda: iterable(vector)[start:index],
        (Number, types[1]): lambda: index[start:vector],
        (types[0], Number): lambda: vector[start:index],
    }[types]()


def order(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)
    if types == (Number, Number):
        if rhs == 0 or abs(rhs) == 1:
            return "Infinite"
        elif lhs == 0:
            return 0
        temp, remainder = lhs, 0
        count = 0
        while True:
            temp, remainder = divmod(temp, rhs)
            if remainder:
                break
            count += 1
        return count
    else:
        return infinite_replace(iterable(lhs, str), iterable(rhs, str), "")


def orderless_range(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)
    return {
        (Number, Number): lambda: Generator(
            range(int(lhs), int(rhs), (-1, 1)[lhs < rhs])
        ),
        (Number, str): lambda: stretch(rhs, lhs),
        (str, Number): lambda: stretch(lhs, rhs),
        (str, str): lambda: int(bool(regex.compile(lhs).search(rhs))),
        (types[0], Function): lambda: array_builtins.scanl_first(lhs, rhs),
        (Function, types[1]): lambda: array_builtins.scanl_first(lhs, rhs),
    }.get(types, lambda: vectorise(orderless_range, lhs, rhs))()


def osabie_newline_join(item, context=None):
    ret = []
    for n in item:
        if vy_type(n) in [list, Generator]:
            ret.append(join_on(n, " "))
        else:
            ret.append(str(n))
    return "\n".join(ret)


def overloaded_iterable_shift(lhs, rhs, direction, context=None):
    if type(rhs) is not int:
        return [lhs, iterable_shift(rhs, direction)]
    else:
        return [iterable_shift(lhs, direction, rhs)]


def palindromise(item, context=None):
    # This is different to m or bifurcate and join because it doesn't have two duplicate in the middle
    return join(item, reverse(item)[1:])


def para_apply(fn_A, fn_B, vector, context):
    temp = array_builtins.deref(vector)[::]
    args_A = pop(vector, fn_A.stored_arity, True)
    args_B = pop(temp, fn_B.stored_arity, True)
    vector.append(fn_A(args_A)[-1])
    vector.append(fn_B(args_B)[-1])
    context.stack = vector


def pluralise(lhs, rhs):
    return {
        (Number, Number): lambda: rhs,
        (str, Number): lambda: f'{rhs} {lhs}{"s" * (lhs != 1)}',
        (Number, str): lambda: f'{lhs} {rhs}{"s" * (lhs != 1)}',
    }.get((vy_type(lhs), vy_type(rhs)), lambda: vectorise(pluralise, lhs, rhs))()


def polynomial(vector):
    t_vector = vy_type(vector)
    if t_vector is Generator:
        vector = vector._dereference()
    return numpy.roots(vector).tolist()


def pop(vector, num=1, wrap=False, context=None):
    ret = []

    for _ in range(num):
        if vector:
            ret.append(vector.pop())
        else:
            x = get_input()
            ret.append(x)

    if context is not None and context.retain_items:
        vector += ret[::-1]

    if context is not None:
        context.last_popped = ret
    if num == 1 and not wrap:
        return ret[0]

    if context is not None and context.reverse_args:
        return ret[::-1]
    return ret


def prime_factors(item, context=None):
    t_item = vy_type(item)
    return {
        Number: lambda: sympy.ntheory.primefactors(int(item)),
        str: lambda: item + item[0],
    }.get(t_item, lambda: vectorise(prime_factors, item))()


def prepend(lhs, rhs, context=None):
    types = (vy_type(lhs), vy_type(rhs))
    return {
        (types[0], types[1]): lambda: join(rhs, lhs),
        (list, types[1]): lambda: [rhs] + lhs,
        (Generator, types[1]): lambda: [rhs] + lhs._dereference(),
    }[types]()


def prev_prime(item, context=None):
    if not isinstance(item, int):
        return item
    if item <= 2:
        return 0
    factor = 1
    while not is_prime(item - factor) and item - factor >= 2:
        factor += 1

    return item - factor


def product(vector, context=None):
    if type(vector) is Generator:
        return vector._reduce(multiply)
    if not vector:
        return 0
    ret = vector[0]
    for item in vector[1:]:
        ret = multiply(ret, item)
    return ret


def rand_between(lhs, rhs, context=None):
    if type(lhs) is int and type(rhs) is int:
        return random.randint(lhs, rhs)

    else:
        return random.choice([lhs, rhs])


def regex_replace(source, pattern, replacent, context=None):
    if type(replacent) is not Function:
        return regex.sub(pattern, vy_str(replacent), source)

    parts = regex.split("(" + pattern + ")", source)
    out = ""
    switch = 1
    for item in parts:

        if switch % 2:
            out += item
        else:
            out += replacent([item])[-1]
        switch += 1

    return out


def remove(vector, item, context=None):
    return {
        str: lambda: vector.replace(str(item), ""),
        Number: lambda: str(vector).replace(str(item), ""),
        list: lambda: Generator(filter(lambda x: x != item, vector)),
        Generator: lambda: remove(vector._dereference(), item),
    }[vy_type(vector)]()


def repeat(vector, times, extra=None, context=None):
    t_vector = vy_type(vector)
    if t_vector is Function and vy_type(times) is Function:

        @Generator
        def gen():
            item = extra
            while vector([item])[-1]:
                item = times([item])[-1]
                yield item

        return gen()

    elif times < 0:
        if t_vector is str:
            return vector[::-1] * times
        elif t_vector is Number:
            CTX.safe_mode = True
            temp = vy_eval(str(reverse(vector)) * times)
            CTX.safe_mode = False
            return temp
        return Generator(itertools.repeat(reversed(vector), times))
    else:
        if t_vector is str:
            return vector * times
        elif t_vector is Number:
            CTX.safe_mode = True
            temp = vy_eval(str(reverse(vector)) * times)
            CTX.safe_mode = False
            return temp
        return Generator(itertools.repeat(vector, times))


def repeat_no_collect(predicate, modifier, value, context=None):
    @Generator
    def gen():
        item = value
        while predicate([item])[-1]:
            item = modifier([item])[-1]
        yield item

    return gen()


def replace(haystack, needle, replacement, context=None):
    t_haystack = vy_type(haystack)
    if t_haystack is list:
        return [replacement if value == needle else value for value in haystack]
    elif t_haystack is Generator:
        return replace(
            haystack._dereference(), needle, replacement
        )  # Not sure how to do replacement on generators yet
    else:
        return str(haystack).replace(str(needle), str(replacement))


def request(url, context=None):
    x = urllib.request.urlopen(urlify(url)).read()
    try:
        return x.decode("utf-8")
    except:
        return x.decode("latin-1")


def reverse(vector, context=None):
    if type(vector) in [float, int]:
        s_vector = str(vector)
        if vector < 0:
            return -type(vector)(s_vector[1:][::-1])
        else:
            return type(vector)(s_vector[::-1])
    return vector[::-1]


def rshift(lhs, rhs, context=None):
    types = (vy_type(lhs), vy_type(rhs))
    return {
        (Number, Number): lambda: lhs >> rhs,
        (Number, str): lambda: rhs.rjust(lhs),
        (str, Number): lambda: lhs.rjust(rhs),
        (str, str): lambda: lhs.rjust(len(lhs) - len(rhs)),
        (types[0], list): lambda: [rshift(lhs, item) for item in rhs],
        (list, types[1]): lambda: [rshift(item, rhs) for item in lhs],
        (list, list): lambda: list(map(lambda x: rshift(*x), vy_zip(lhs, rhs))),
        (list, Generator): lambda: two_argument(rshift, lhs, rhs),
        (Generator, list): lambda: two_argument(rshift, lhs, rhs),
        (Generator, Generator): lambda: two_argument(rshift, lhs, rhs),
    }.get(types, lambda: vectorise(rshift, lhs, rhs))()


def run_length_decode(vector, context=None):
    ret = ""
    for item in vector:
        ret += item[0] * item[1]
    return ret


def sentence_case(item, context=None):
    ret = ""
    capitalise = True
    for char in item:
        ret += (lambda: char.lower(), lambda: char.upper())[capitalise]()
        if capitalise and char != " ":
            capitalise = False
        capitalise = capitalise or char in "!?."
    return ret


def set_caret(lhs, rhs, context=None):
    # Why make my own function instead of using standard ^? Because numbers and strings. that's why.
    types = vy_type(lhs), vy_type(rhs)
    new_lhs, new_rhs = {
        (Number, Number): lambda: (iterable(lhs), iterable(rhs)),
        (Number, str): lambda: (str(lhs), rhs),
        (str, Number): lambda: (lhs, str(rhs)),
    }.get(types, lambda: (iterable(lhs), iterable(rhs)))()

    return list(set(new_lhs) ^ set(new_rhs))


def set_intersection(lhs, rhs, context=None):
    # Why make my own function instead of using standard &? Because numbers and strings. that's why.
    types = vy_type(lhs), vy_type(rhs)
    new_lhs, new_rhs = {
        (Number, Number): lambda: (iterable(lhs), iterable(rhs)),
        (Number, str): lambda: (str(lhs), rhs),
        (str, Number): lambda: (lhs, str(rhs)),
    }.get(types, lambda: (iterable(lhs), iterable(rhs)))()

    return list(set(new_lhs) & set(new_rhs))


def set_union(lhs, rhs, context=None):
    # Why make my own function instead of using standard |? Because numbers and strings. that's why.
    types = vy_type(lhs), vy_type(rhs)
    new_lhs, new_rhs = {
        (Number, Number): lambda: (iterable(lhs), iterable(rhs)),
        (Number, str): lambda: (str(lhs), rhs),
        (str, Number): lambda: (lhs, str(rhs)),
    }.get(types, lambda: (iterable(lhs), iterable(rhs)))()

    return list(set(new_lhs) | set(new_rhs))


def sign_of(item, context=None):
    t = vy_type(item)
    if t == Number:
        if item < 0:
            return -1
        else:
            return [0, 1][item != 0]
    elif t is list:
        return vectorise(sign_of, item)
    else:
        return item


def split(haystack, needle, keep_needle=False, context=None):
    t_haystack = vy_type(haystack)
    if t_haystack in [Number, str]:
        haystack, needle = str(haystack), str(needle)
        if keep_needle:
            import re

            return re.split(
                f"({re.escape(needle)})", haystack
            )  # I'm so glad Vyxal now uses built-in lists
        return haystack.split(needle)
    elif t_haystack is Generator:
        return split(haystack._dereference(), needle, keep_needle)
    else:  # t_haystack is list
        ret = []
        temp = []
        for item in haystack:
            if item == needle:
                ret.append(temp)
                if keep_needle:
                    temp = [needle]
                else:
                    temp = []
            else:
                temp.append(item)
        if temp:
            ret.append(temp)
        return ret


def split_newlines_or_pow_10(item, context=None):
    return {Number: lambda: 10 ** item, str: lambda: item.split("\n")}.get(
        vy_type(item), lambda: vectorise(split_newlines_or_pow_10, item)
    )()


def split_on_words(item, context=None):
    parts = []
    word = ""

    for char in item:
        if char not in string.ascii_letters:
            if word:
                parts.append(word)
            word = ""
            parts.append(char)
        else:
            word += char

    if word:
        parts.append(word)
    return parts


def square(item, context=None):
    def grid_helper(s):
        temp = s
        while not is_square(len(temp)):
            temp += " "
        return wrap(temp, int(exponate(len(temp), 0.5)))

    return {
        Number: lambda: item * item,
        str: lambda: grid_helper(item),
    }.get(vy_type(item), lambda: multiply(item, array_builtins.deref(item)))()


def stretch(string, length, context=None):
    ret = string
    while len(ret) < length:
        ret += " " if len(ret) == 0 else ret[0]
    return ret


def string_empty(item, context=None):
    return {Number: lambda: item % 3, str: len(item) == 0}.get(
        vy_type(item), lambda: vectorise(string_empty, item)
    )()


def strip_non_alphabet(name, context=None):
    stripped = filter(lambda char: char in string.ascii_letters + "_", name)
    return "".join(stripped)


def substrings(item, context=None):
    for i in range(0, len(item) + 1):
        for j in range(1, len(item) + 1):
            yield item[i:j]


def subtract(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)

    return {
        (Number, Number): lambda: lhs - rhs,
        (str, str): lambda: lhs.replace(rhs, ""),
        (str, Number): lambda: lhs + ("-" * rhs),
        (Number, str): lambda: ("-" * lhs) + rhs,
    }.get(types, lambda: vectorise(subtract, lhs, rhs))()


def tab(x):
    return NEWLINE.join(["    " + item for item in x.split(NEWLINE)]).rstrip("    ")


def transformer_vectorise(function, vector, contex=None):
    if function.stored_arity == 1:
        return vectorise(function, pop(vector), explicit=True)
    elif function.stored_arity == 2:
        rhs, lhs = pop(vector, 2)
        return vectorise(function, lhs, rhs, explicit=True)
    elif function.stored_arity == 3:
        other, rhs, lhs = pop(vector, 3)
        return vectorise(function, lhs, rhs, other, explicit=True)
    else:
        return vectorise(
            function, pop(vector, function.stored_arity), explicit=True
        )  # idk how you'd vectorise over arity >3


def transliterate(original, new, transliterant, context=None):
    transliterant = array_builtins.deref(transliterant)
    t_string = type(transliterant)
    if t_string is list:
        transliterant = list(map(str, transliterant))
    original = array_builtins.deref(original)
    if type(original) is list:
        original = list(map(str, original))
    ret = t_string()
    for char in transliterant:
        if vy_type(char) is Number:
            char = str(char)
        if t_string is str:
            char = str(char)
        try:
            ind = original.index(char)
            ret += t_string(new[ind])
        except:
            ret += t_string(char)
    return ret


def trim(lhs, rhs, left=False, right=False, context=None):
    # I stole this from Jelly (but I overloaded it)
    # https://github.com/DennisMitchell/jellylanguage/blob/master/jelly/interpreter.py#L1131

    if type(rhs) is Function:
        lhs = iterable(lhs)

        @Generator
        def gen():
            for index, item in enumerate(lhs):
                if index % 2:
                    yield safe_apply(rhs, item)

        return gen()

    if vy_type(lhs) == Number:
        lhs = str(lhs)
    if vy_type(rhs) == Number:
        rhs = str(rhs)
    lindex = 0
    rindex = len(lhs)
    if left:
        while lindex < rindex and rhs[lindex] in lhs:
            lindex += 1
    if right:
        while lindex < rindex and rhs[rindex - 1] in lhs:
            rindex -= 1
    return lhs[lindex:rindex]


def truthy_indices(vector, context=None):
    ret = []
    for i in range(len(vector)):
        if bool(vector[i]):
            ret.append(i)
    return ret


def two_power(item, context=None):
    if vy_type(item) == Number:
        return 2 ** item
    elif vy_type(item) is str:
        out = ""
        for char in item:
            if char in string.ascii_letters:
                out += char
        return out
    else:
        return vectorise(two_power, item)


def uneval(item, context=None):
    item = [char for char in item]
    indices = [i for i, ltr in enumerate(item) if ltr in ["\\", "`"]][::-1]
    for i in indices:
        item.insert(i, "\\")
    return "`" + "".join(item) + "`"


def unsympy(item, context=None):
    if type(item) in (list, Generator):
        return vectorise(unsympy, item)
    if item.is_Integer:
        return int(item)
    elif item.is_Float:
        return float(item)
    else:
        return item


def urlify(item, context=None):
    if not (item.startswith("http://") or item.startswith("https://")):
        return "https://" + item
    return item


def vectorised_not(item, context=None):
    return {Number: lambda: int(not item), str: lambda: int(not item)}.get(
        vy_type(item), lambda: vectorise(vectorised_not, item)
    )()


def vertical_join(vector, padding=" ", context=None):
    if vy_type(padding) == vy_type(vector) == Number:
        return abs(vector - padding)

    lengths = list(map(len, array_builtins.deref(vector, True)))
    vector = [padding * (max(lengths) - len(x)) + x for x in vector]

    out = ""
    for i in range(max(lengths)):
        for item in vector:
            out += item[i]
        out += "\n"

    return out


def vertical_mirror(item, mapping=None, context=None):
    if type(item) is str:
        if mapping:
            temp = [
                s + transliterate(mapping[0], mapping[1], s[::-1])
                for s in item.split("\n")
            ]
            return "\n".join(temp)
        else:
            return "\n".join([mirror(s) for s in item.split("\n")])
    elif vy_type(item) is Number:
        return mirror(item)
    else:
        return vectorise(vertical_mirror, item, mapping)


def wrap(vector, width, context=None):
    types = vy_type(vector), vy_type(width)
    if types == (Function, types[1]):
        return array_builtins.map_every_n(width, vector, 2)
    elif types == (types[0], Function):
        return array_builtins.map_every_n(vector, width, 2)

    # Because textwrap.wrap doesn't consistently play nice with spaces
    ret = []
    temp = []
    for item in vector:
        temp.append(item)
        if len(temp) == width:
            if all([type(x) is str for x in temp]):
                ret.append("".join(temp))
            else:
                ret.append(temp[::])
            temp = []
    if len(temp) < width and temp:
        if all([type(x) is str for x in temp]):
            ret.append("".join(temp))
        else:
            ret.append(temp[::])

    return ret


def vy_abs(item, context=None):
    return {
        Number: lambda: abs(item),
        str: lambda: remove(remove(remove(item, " "), "\n"), "\t"),
    }.get(vy_type(item), lambda: vectorise(vy_abs, item))()


def vy_bin(item, context=None):
    t_item = vy_type(item)
    return {
        Number: lambda: [int(x) for x in bin(int(item))[2:]],
        str: lambda: [[int(x) for x in bin(ord(let))[2:]] for let in item],
    }.get(t_item, lambda: vectorise(vy_bin, item))()


def vy_divmod(lhs, rhs, context=None):
    types = vy_type(lhs), vy_type(rhs)

    def niceify(item, function):
        # turns a groupby object into a generator
        item = vy_sorted(item, function)
        for k, g in itertools.groupby(vy_zipmap(function, item), key=lambda x: x[0]):
            p = list(g)
            yield p[0][0]

    return {
        (types[0], Number): lambda: Generator(itertools.combinations(lhs, rhs)),
        (Number, Number): lambda: [lhs // rhs, lhs % rhs],
        (str, str): lambda: trim(lhs, rhs),
        (Function, types[1]): lambda: Generator(niceify(rhs, lhs)),
        (types[0], Function): lambda: Generator(niceify(lhs, rhs)),
    }[types]()


def vy_eval(item, context=None):
    if vy_type(item) is Number:
        return 2 ** item
    elif vy_type(item) in [list, Generator]:
        return vectorise(vy_eval, item)

    if CTX.online_version or CTX.safe_mode:
        from vyxal.interpreter import vy_compile
        from vyxal.parser import Structure, Tokenise

        try:
            return pwn.safeeval.const(item)
        except:
            f = Tokenise(item, CTX.variables_are_digraphs)
            if len(f) and f[-1][-1] in (
                Structure.STRING,
                Structure.NUMBER,
                Structure.LIST,
            ):
                try:
                    temp = vy_compile(item, vyxal_imports)
                    CTX.stack = []
                    exec(temp)
                    return CTX.stack[-1]
                except Exception as e:
                    print(e)
                    return item
            else:
                return item
    else:
        try:
            ret = eval(item)
            return ret
        except:
            return item


def vy_exec(item, context=None):
    if vy_type(item) is str:
        import vyxal.interpreter

        exec(vyxal.interpreter.vy_compile(item, vyxal_imports))
        return []
    elif vy_type(item) == Number:
        return [divide(1, item)]
    else:
        return [vectorise(vy_exec, item)]


def vy_filter(fn, vector, context=None):
    def default_case(lhs, rhs):
        # remove elements from a that are in b
        out = "" if type(lhs) is str else []
        for item in lhs:
            if item not in rhs:
                if type(out) is str:
                    out += str(item)
                else:
                    out.append(item)
        return out

    def _filter(function, vec):
        for item in vec:
            val = function([item])[-1]
            if bool(val):
                yield item

    types = (vy_type(fn), vy_type(vector))
    return {
        types: lambda: default_case(iterable(fn, str), iterable(vector, str)),
        (Function, types[1]): lambda: Generator(_filter(fn, iterable(vector, range))),
        (types[0], Function): lambda: Generator(_filter(vector, iterable(fn, range))),
    }[types]()


def vy_int(item, base=10, context=None):
    t_item = type(item)
    if t_item not in [str, float, int, complex]:
        ret = 0
        for element in item:
            ret = multiply(ret, base)
            ret = add(ret, element)
        return ret
    elif t_item is str:
        return int(item, base)
    elif t_item is complex:
        return numpy.real(item)
    elif t_item is float:
        return int(item)
    elif t_item:
        return vy_int(iterable(item), base)


def vy_map(fn, vector, context=None):
    ret = []
    t_vector = vy_type(vector)
    t_function = vy_type(fn)
    if Function not in (t_vector, t_function):

        @Generator
        def gen():
            for item in iterable(fn):
                yield [vector, item]

        return gen()

    vec, function = (fn, vector) if t_vector is Function else (vector, fn)
    if vy_type(vec) == Number:
        vec = range(CTX.MAP_START, int(vec) + CTX.MAP_OFFSET)

    if vy_type(vec) is Generator:

        @Generator
        def gen():
            for item in vec:
                yield safe_apply(function, item)

        return gen()
    for item in vec:
        result = function([item])
        ret.append(result[-1])
    return ret


def vy_max(item, other=None, context=None):
    if other is not None:
        return {
            (Number, Number): lambda: max(item, other),
            (Number, str): lambda: max(str(item), other),
            (str, Number): lambda: max(item, str(other)),
            (str, str): lambda: max(item, other),
        }.get((vy_type(item), vy_type(other)), lambda: vectorise(vy_max, item, other))()
    else:
        item = flatten(item)
        if item:
            biggest = item[0]
            for sub in item[1:]:
                res = compare(
                    array_builtins.deref(sub),
                    array_builtins.deref(biggest),
                    Comparitors.GREATER_THAN,
                )
                if vy_type(res) in [list, Generator]:
                    res = any(res)
                if res:
                    biggest = sub
            return biggest
        return item


def vy_min(item, other=None, context=None):
    if other is not None:
        ret = {
            (Number, Number): lambda: min(item, other),
            (Number, str): lambda: min(str(item), other),
            (str, Number): lambda: min(item, str(other)),
            (str, str): lambda: min(item, other),
        }.get(
            (vy_type(item), vy_type(other)),
            lambda: vectorise(
                vy_min, array_builtins.deref(item), array_builtins.deref(other)
            ),
        )()

        return ret
    else:
        item = flatten(item)
        if item:
            smallest = item[0]
            for sub in item[1:]:
                res = compare(
                    array_builtins.deref(sub),
                    array_builtins.deref(smallest),
                    Comparitors.LESS_THAN,
                )
                if vy_type(res) in [list, Generator]:
                    res = any(res)
                if res:
                    smallest = sub
            return smallest
        return item


def vy_oct(item, context=None):
    return {
        Number: lambda: oct(item)[2:],
        str: lambda: (lambda: item, lambda: oct(int(item)))[item.isnumeric()]()[2:],
    }.get(vy_type(item), lambda: vectorise(vy_oct, item))()


def vy_print(item, end="\n", raw=False, context=None):
    context.printed = True
    t_item = type(item)
    if t_item is Generator:
        item._print(end, context=context)

    elif t_item is list:
        vy_print("⟨", "", False, context)
        if item:
            for value in item[:-1]:
                vy_print(value, "|", True, context)
            vy_print(item[-1], "", True, context)
        vy_print("⟩", end, False, context)
    elif t_item is Function:
        s = function_call(item, context.stack)
        vy_print(s[0], end=end, raw=raw)
    else:
        if t_item is int and context.keg_mode:
            item = chr(item)
        if raw:
            if context.online_version:
                context.output.write(vy_repr(item) + end)
            else:
                print(vy_repr(item), end=end)
        else:
            if context.online_version:
                context.output.write(vy_str(item) + end)
            else:
                print(vy_str(item), end=end)
    """if context.online_version and len(context.output.w > 128000:
        context.output[
            2
        ] = "Program terminated after reaching the maximum character limit for output."
        sys.exit(1)
        return"""


def vy_range(item, start=0, lift_factor=0, context=None):
    t_item = vy_type(item)
    if t_item == Number:
        if item < 0:
            return range(start, int(item) + lift_factor, -1)
        return range(start, int(item) + lift_factor)
    return item


def vy_reduce(fn, vector, context):
    t_type = vy_type(vector)
    if type(fn) != Function:
        return [vector, vectorise(reverse, fn)]
    if t_type is Generator:
        return [vector._reduce(fn)]
    if t_type is Number:
        vector = list(range(context.MAP_START, int(vector) + context.MAP_OFFSET))
    vector = vector[::-1]
    working_value = pop(vector)
    vector = vector[::-1]
    for item in vector:
        working_value = fn([working_value, item], arity=2)[-1]
    return [working_value]


def vy_round(item, context=None):
    t_item = vy_type(item)
    if t_item == Number:
        return round(item)

    elif t_item is str:
        return [item[n:] for n in range(len(item) - 1, -1, -1)]
    return vectorise(vy_round, item)


def vy_sorted(vector, fn=None, context=None):
    if fn is not None and type(fn) is not Function:
        return array_builtins.inclusive_range(vector, fn)
    t_vector = type(vector)
    vector = iterable(vector, range)
    if t_vector is Generator:
        vector = vector.gen

    if fn:
        sorted_vector = sorted(vector, key=lambda x: fn([x]))
    else:
        sorted_vector = sorted(vector)

    return {
        float: lambda: float("".join(map(str, sorted_vector))),
        str: lambda: "".join(map(str, sorted_vector)),
    }.get(t_vector, lambda: Generator(sorted_vector))()


def vy_str(item, context=None):
    t_item = vy_type(item)
    return {
        Number: str,
        str: lambda x: x,
        list: lambda x: "⟨" + "|".join([vy_repr(y) for y in x]) + "⟩",
        Generator: lambda x: vy_str(x._dereference()),
        Function: lambda x: vy_str(function_call(x, CTX.stack)[0]),
    }[t_item](item)


def vy_zipmap(lhs, rhs, context=None):
    if Function not in (vy_type(lhs), vy_type(rhs)):
        return [lhs, vy_zip(rhs, rhs)]

    function = vector = None
    if type(rhs) is Function:
        function, vector = rhs, iterable(lhs, range)
    else:
        function, vector = lhs, iterable(rhs, range)

    def f():
        for item in vector:
            yield [item, safe_apply(function, item)]

    return Generator(f())
