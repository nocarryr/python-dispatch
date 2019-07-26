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
to follow the style if possible.  Don't worry about it too much though, there's no
[flakes](https://pypi.org/project/pyflakes/) or [lint](https://www.pylint.org/) here.

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
- Ensure compatibility across all conceivable platforms and Python versions. (currently 2.7, 3.4, 3.5, 3.6, 3.7)

## Local Development

### Environment / Installation

```bash
git clone https://github.com/<gh-user-name>/python-dispatch.git
cd python-dispatch
```

It's recommended to use a virtual environment for development and testing.
See https://virtualenv.pypa.io/en/latest/ or https://docs.python.org/3.7/library/venv.html for details.

Create a new environment at the root of your working tree and activate it:
```bash
python -m venv venv
source venv/bin/activate
```

Install the project in 'editable' mode:
```bash
pip install -e .
```

Currently, the only dependency for testing is [pytest](https://pypi.org/project/pytest/),
but to make tests run faster, it's a good idea to install [pytest-xdist](https://pypi.org/project/pytest-xdist/):
```bash
pip install pytest pytest-xdist
```

### Running Tests

To run the entire test suite:
```bash
py.test -n auto
# -n auto will use all available CPU cores
```

For other invocation methods, see the [pytest docs](https://pytest.org/en/latest/)

There is a test in the suite that will take an *extremely* long time: `tests/test_subclass_init.py`. To avoid having to wait for it every time, you can make
a change to it, make sure to **revert it** before committing.

`tests/test_subclass_init.py` line 83:
```python
for i in range(40000):          # <--- change this to something like 4000
    before_init = time.time()
```

## License

By contributing, you agree that your contributions will be licensed under
project's (MIT) [license](LICENSE.txt).

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md)
