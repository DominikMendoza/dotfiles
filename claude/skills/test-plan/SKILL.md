---
name: test-plan
description: Plan and write test cases for a feature that already works. Use when asked to organize, plan or add test cases after an implementation has been verified.
---

# Test case plan

The feature is already verified as working. Produce a pseudo-plan for its test
cases, present it, and implement it once it is approved.

## Never compile and never verify on your own

Do not run any build, compile, test or verification command. This holds for the
backend and for the frontend, with no exception, and for the whole session,
including after the tests are written. Writing a test is not a reason to run it.

Compilation and verification happen only in the final stage, when I ask for them
explicitly in those words. If something looks like it needs verifying, say so
and wait.

## Scope

- Backend only. No frontend tests.
- Resources and controllers are excluded.
- Unit tests for straightforward methods. If the size of the change calls for
  something closer to end to end, propose it and we discuss it first.
- Aim for the highest coverage of the code that was added or modified.

## Where each test goes

Decide per method, in this order:

1. The class under test already has a test class, and the method already has a
   test. Complement that test, as long as the change is small.
2. The class has a test class, but the method has no test. Add it there.
3. The class has no test class. Create one, following the patterns of the
   neighbouring test classes and the conventions used across the suite.

## How many

Two per method, three when the method is important enough to need it. Private
methods, and anything whose coverage already comes from testing another method,
are not tested on their own.

For a utility class write a single parameterized test instead of many near
identical ones. It stays far cleaner.

## Style

No comments. To explain why a given comparison is made, use the third argument
of the assertion, the message, rather than a comment above it.
