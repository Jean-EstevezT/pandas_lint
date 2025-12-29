# pandas_lint

![PyPI - Version](https://img.shields.io/pypi/v/pandas-linter)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pandas-linter)
![License](https://img.shields.io/github/license/Jean-EstevezT/pandas_lint)

**pandas_lint** is a static code analysis tool designed to help you write more efficient and readable Pandas and NumPy code. It detects common anti-patterns and performance bottlenecks, offering suggestions to improve your data processing pipelines.

## Features

- **Performance Optimization**: Identifies slow operations like `apply()`, usage of `iterrows()`, and inefficient string manipulations.
- **Best Practices**: Enforces standard Pandas coding styles and conventions.
- **Safety**: Warns about potential issues like `SettingWithCopyWarning` risks and modification of views.
- **Easy Integration**: Zero-config needed to get started, but fully configurable via `pyproject.toml`.

## Installation

You can install `pandas_lint` directly from PyPI:

```bash
pip install pandas-linter
```

## Usage

### Command Line Interface

To lint a file or directory:

```bash
pandas-lint path/to/your/script.py
pandas-lint path/to/your/project/
```

To automatically fix issues where possible (experimental):

```bash
pandas-lint path/to/script.py --autofix
```

### Configuration

You can configure `pandas_lint` in your `pyproject.toml` file:

```toml
[tool.pandas-linter]
ignore = ["STY001", "PERF002"]
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

