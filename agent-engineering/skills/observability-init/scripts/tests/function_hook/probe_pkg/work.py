"""Stands for an application's own code: every function here is recorded by the hook under test."""

import asyncio
import random


def leaf(i):
    return i


def recurse(n):
    return 0 if n == 0 else 1 + recurse(n - 1)


def fails(i):
    raise ValueError(f"boom {i}")


def catches(i):
    try:
        fails(i)
    except ValueError:
        return leaf(i)


def numbers(n):
    for k in range(n):
        yield k


def uses_generator(n):
    total = 0
    for k in numbers(n):
        total += leaf(k)
    return total


def abandons_generator():
    g = numbers(5)
    next(g)
    del g
    return leaf(1)


async def a_leaf(i):
    await asyncio.sleep(random.random() / 200)
    return leaf(i)


async def a_inner(i):
    await asyncio.sleep(random.random() / 200)
    first = await a_leaf(i)
    await asyncio.sleep(0)
    return first + await asyncio.to_thread(leaf, 0)


async def a_outer(i):
    await asyncio.sleep(random.random() / 200)
    return await a_inner(i)


async def a_numbers(n):
    for k in range(n):
        await asyncio.sleep(0)
        yield k


async def a_uses_generator(n):
    total = 0
    async for k in a_numbers(n):
        total += leaf(k)
    return total


async def a_slow(i):
    await asyncio.sleep(30)
    return i


async def a_cancelled(i):
    return await a_slow(i)


def takes_text(value):
    return value


def takes_object(config, items, blob, big, text):
    return {"a": 1}


async def a_calls_library(framework, tracer):
    return await framework.library_with_span(tracer, leaf)


def numbers_inside_library_span(tracer):
    with tracer.start_as_current_span("lib.in_generator"):
        yield 1
        leaf(2)


def uses_generator_with_span(tracer):
    for k in numbers_inside_library_span(tracer):
        leaf(k)


def named_secret(api_key, headers, plain):
    return plain


def read_token(plain):
    return plain


def calls_back(fn):
    fn()
    return 1


def raises(exc):
    raise exc


def step(i, fail):
    leaf(i)
    if fail:
        raise ValueError("no")


def loops(n, failing=()):
    done = 0
    for i in range(n):
        try:
            step(i, i in failing)
            done += 1
        except ValueError:
            pass
    return done


def opens_library_span(tracer):
    with tracer.start_as_current_span("lib.in_step"):
        pass


def loops_with_library(n, tracer):
    for _ in range(n):
        opens_library_span(tracer)


def closes_generators(n):
    for _ in range(n):
        generator = numbers(5)
        next(generator)
        generator.close()


async def a_step(i):
    await asyncio.sleep(0)
    return leaf(i)


async def a_fans_out(n):
    return await asyncio.gather(*[a_step(i) for i in range(n)])


def loops_generators_with_span(n, tracer):
    for _ in range(n):
        for _k in numbers_inside_library_span(tracer):
            with tracer.start_as_current_span("consumer.mark"):
                pass


def starts_a_trace_of_its_own(n, tracer):
    from opentelemetry.context import Context

    with tracer.start_as_current_span("new.root", context=Context()):
        for i in range(n):
            leaf(i)


async def a_starts_background(coroutine):
    return asyncio.ensure_future(coroutine)


async def a_worker(started, n):
    await started.wait()
    return [leaf(i) for i in range(n)]
