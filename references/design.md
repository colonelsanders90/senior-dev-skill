# Design Principles

Load at the **Design** step (02) of the core workflow, or whenever you're shaping modules, types, or boundaries.

---

## Separation of Concerns

One module, one reason to change. If a function fetches from the database, formats HTML, and sends an email, it's three functions wearing a trench coat.

### Layering discipline

- **Domain** — business rules, pure, no I/O.
- **Application** — orchestrates domain + infrastructure. Still no direct I/O.
- **Infrastructure** — databases, APIs, file systems, clocks, randomness.
- **Interface** — HTTP handlers, CLI entry points, UI.

Rule of thumb: push side effects to the edges. The core of the system should be pure functions operating on data. This is what makes code testable, portable, and reasonable.

### Function size

If a function doesn't fit on a screen, it's probably doing too much. If it has more than 3-4 parameters, the parameters probably want to be an object.

---

## Domain-Driven Design

**Ubiquitous language** — Code uses the same words the business uses. If the user says "objective", don't call it `Goal` in code. If a product manager wouldn't recognise a class name, it's probably wrong.

**Aggregates** — Identify the consistency boundaries. Within an aggregate, all rules hold; across aggregates, you reach for eventual consistency. Don't let a single transaction touch three aggregates.

**Value objects vs entities** — If two instances with the same fields are interchangeable (e.g. `Money`, `EmailAddress`), it's a value object. Make it immutable. If identity matters over time (e.g. `User`, `Order`), it's an entity.

**Bounded contexts** — Don't let `User` from the billing context leak into the auth context. They're different concepts that happen to share a name.

---

## Readability — Non-Negotiable

**Names matter more than comments.** A well-named function needs fewer comments. `calculate_monthly_recurring_revenue` beats `calc_mrr` beats a comment explaining what `calc` means.

**Write code for the reader.** You will read it 10x more often than you write it. Optimise for that ratio.

**Prefer boring.** Clever code is code with a higher bug rate. The senior move is to write the obvious solution and move on.

**Comments explain *why*, not *what*.** The code shows what. If *why* is obvious from the code, no comment is needed. If *why* is non-obvious (a workaround, a business rule, a historical decision), that's exactly where a comment earns its place.

**Consistency over personal preference.** Match the style of the surrounding code. A codebase with five styles is harder to read than one with a style you mildly dislike.
