# Contributing to python-dispatch

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Pull Requests

Pull requests are the best way to propose changes to the project. We actively welcome your pull requests.

### Basic Steps

1. Fork the [repo](https://github.com/nocarryr/python-dispatch) and **create a new
    branch** from `master`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Issue that pull request!

### Your First Code Contribution

Working on your first Pull Request? Here are a couple of resources to get you started:

- [Github Help: Creating a pull request](https://help.github.com/en/desktop/contributing-to-projects/creating-a-pull-request)
- [How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github)
- [The FirstTimersOnly Movement](http://www.firsttimersonly.com/)


## Limit Changes per Pull Request

- Avoid changes to the project's configuration or meta-data such as
  - Version Information
  - Packaging Configuration
  - Testing / Deployment Configuration
- Try to avoid making large sets of changes if they could be broken into smaller ones.
  Instead, split them into separate pull requests.

## Coding Style

While this project does not fully (probably not even partially) adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/),
the existing code-base does maintain a certain level of consistency.  Please try
to follow the style if possible. Ruff checks a focused set of correctness rules
for the core package and Sphinx plugin without enforcing a formatting rewrite.

### Basic Guidelines

- 4 spaces for indentation, not tabs.
- Avoid trailing whitespace.
- Prefer readability and clarity over complicated/complex: see the
    [Zen of Python](https://www.python.org/dev/peps/pep-0020/)


## Follow the Goals and Philosophy of the Project

- No dependencies should ever be introduced.
- Keep things simple and light-weight.
- Avoid adding public methods/attributes to the `Dispatcher` class, especially
  if the method/attribute names are common.
  - Since `Dispatcher` is meant to be subclassed by users of this project,
    it needs to stay out of a developer's way as much as possible.
- Preserve compatibility with Python 3.11 and newer and avoid platform-specific
  assumptions. CI tests Python 3.11, 3.12, 3.13, and 3.14.

## Local Development

### Environment / Installation

```bash
git clone https://github.com/<gh-user-name>/python-dispatch.git
cd python-dispatch
```

Use [uv](https://docs.astral.sh/uv/) to create a virtual environment and
install the editable workspace, including the Sphinx plugin and development
dependencies:

```bash
uv sync
```

### Running Tests

Install the workspace test dependencies and run the lint check with
[uv](https://docs.astral.sh/uv/):

```bash
uv sync --group test
uv run ruff check
```

CI runs the same Ruff check on Python 3.13.

To check the core package and Sphinx plugin with mypy, including untyped
function bodies and targeting the minimum supported Python version:

```bash
uv run mypy
```

CI runs this check on Python 3.13 and requires it to pass.

Run the core and plugin suites separately; each has its own `conftest.py`:

```bash
uv run pytest tests pydispatch doc README.md
uv run pytest sphinx-plugin/tests
```

To build the documentation with warnings treated as errors:

```bash
uv run sphinx-build -b html -W --keep-going doc/source /tmp/python-dispatch-docs
```

For other invocation methods, see the [pytest docs](https://pytest.org/en/latest/).
## License

By contributing, you agree that your contributions will be licensed under
project's (MIT) [license](LICENSE.txt).

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md)
