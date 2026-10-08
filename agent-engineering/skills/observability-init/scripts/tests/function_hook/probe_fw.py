"""Stands for the web framework: not part of the application's own package."""


async def framework_entry(scope, then):
    return await then()


def library_helper(fn, *a):
    return fn(*a)


async def library_with_span(tracer, then):
    """A library that opens its own span, waits inside it, then opens a second span and calls back."""
    import asyncio

    with tracer.start_as_current_span("lib.outer"):
        await asyncio.sleep(0.01)
        with tracer.start_as_current_span("lib.inner"):
            pass
        return then(1)


async def background(tracer, started, then, times):
    """Library work started by an own function and still running after that function has returned."""
    with tracer.start_as_current_span("lib.background"):
        await started.wait()
        for i in range(times):
            then(i)
