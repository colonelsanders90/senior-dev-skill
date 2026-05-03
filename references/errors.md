# Exception Handling

Load whenever you're writing code that can fail, or reviewing code that touches `try/except`, `try/catch`, or error returns.

Exceptions are for exceptional situations, not control flow.

---

## Rules

**Catch specific exceptions.** `except Exception:` or `catch (Throwable)` is almost always a bug in disguise. You catch what you can handle; everything else propagates.

**Never swallow silently.** `except: pass` is an atrocity. At minimum, log it. Preferably, re-raise with context.

**Fail fast at the boundary.** Validate inputs the moment they enter your system. An invalid input that travels three layers deep before failing produces a stack trace that tells you nothing.

**Don't leak internals.** A user sees "Something went wrong, reference ID abc123". The logs see the full stack trace. Never expose database errors, file paths, or library internals to end users.

**Clean up resources.** Use `with` / `using` / `try-finally` / RAII. Network connections, file handles, locks — they all need deterministic cleanup.

**Wrap, don't swallow.** When catching a low-level exception to translate it, include the original as a cause (`raise NewError(...) from e`). Don't discard the stack trace.

---

## Anti-pattern to avoid

```python
# Don't do this
try:
    result = complex_operation()
except Exception as e:
    return None  # error vanished, debugging ruined
```

## What to do instead

```python
try:
    result = complex_operation()
except SpecificError as e:
    logger.exception("complex_operation failed for user %s", user_id)
    raise OperationFailedError("Could not complete operation") from e
```
