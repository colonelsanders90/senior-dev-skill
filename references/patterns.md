# Patterns — Use Deliberately

Load when reaching for Singleton, or when the problem has optimal substructure (potential dynamic programming).

---

## Singleton — Use Sparingly

Singleton is a tool. It's also the most abused pattern in the catalogue. Before reaching for it, ask: "Am I doing this because I genuinely have exactly one of this thing, or because I can't be bothered to pass it as a parameter?"

### Legitimate uses

- Logging facade.
- Configuration loader (immutable after startup).
- Connection pool, thread pool, cache — things that are expensive to create and genuinely shared.

### Illegitimate uses

- Business logic. A singleton `OrderService` is a god object waiting to happen.
- Anything with mutable state shared across threads without synchronisation.
- "Because I need to access it from everywhere" — that's what dependency injection is for.

### If you must

- Make it thread-safe. Double-checked locking, language idioms (Python modules are already singletons; `Lazy<T>` in .NET; `sync.Once` in Go).
- Make the state immutable where possible.
- Make it mockable for tests. A singleton that can't be substituted in tests is a testing black hole.

**Preferred alternative:** Dependency injection. Pass the collaborator in. Let the composition root (the top of your application) decide whether it's one instance or many. Your code stops caring.

---

## Dynamic Programming — Recurrence First, Then Memoise

Before reaching for a DP table, state the recurrence in plain maths or pseudocode. `f(n) = f(n-1) + f(n-2)` before any Python.

Order of operations:
1. Identify optimal substructure.
2. Write the recurrence.
3. Implement top-down with recursion + memoisation.
4. If it matters, convert to bottom-up tabulation.
5. If it *still* matters, reduce state dimensions.

Skipping straight to a 2D array is how bugs get written.
