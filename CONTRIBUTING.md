# Contributing

Thank you for your interest in improving the DFA Engine. This project focuses on algorithmic efficiency and strict architectural standards. Please review the guidelines below to ensure your contribution aligns with the project's goals.

## Engineering Standards

To maintain $O(1)$ runtime performance and memory efficiency, all contributions must adhere to the following:

* **Algorithmic Complexity:** Critical paths (state transitions, validation) must avoid linear searches ($O(n)$). Use hashmaps (dictionaries) or sets.
* **Memory Optimization:** New classes must utilize `__slots__` to prevent dynamic dictionary creation (`__dict__`).
* **Type Safety:** All function signatures and class attributes must use static type hints (`typing` module).
* **Code Style:** Strict adherence to **PEP 8**.

## Development Workflow

1.  **Fork and Clone** the repository.
2.  **Branching Strategy:**
    * `feat/`: New capabilities.
    * `fix/`: Bug resolution.
    * `refactor/`: Performance or memory optimizations.
    * `docs/`: Documentation updates.
3.  **Validation:** Ensure the engine runs error-free against the provided examples in `examples/` before submitting.

## Commit Guidelines

We use **Conventional Commits** to maintain a clean, semantic history:

* `feat: add support for NFA conversion`
* `fix: resolve edge case in email validator`
* `refactor: optimize transition hashmap lookup`
* `docs: update mathematical definitions`

## Pull Request Process

* Provide a clear description of the changes and their impact on performance.
* Squash intermediate commits to keep the history linear.