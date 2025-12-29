# Contributing to pandas_lint

Thank you for your interest in contributing to `pandas_lint`! We welcome contributions of all forms, including bug reports, feature requests, documentation improvements, and code changes.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/Jean-EstevezT/pandas_lint.git
   cd pandas_lint
   ```
3. **Set up a virtual environment** and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .[dev]
   ```

## Development Workflow

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Write your code and tests.
3. Run the test suite to ensure everything is working:
   ```bash
   pytest
   ```
4. Run linters/formatters:
   ```bash
   black .
   isort .
   flake8
   ```

## Submitting a Pull Request

1. Push your changes to your fork.
2. Open a Pull Request on the main repository.
3. Provide a clear description of your changes and why they are necessary.

## Code of Conduct

Please be respectful and professional in all interactions.
