# Modernization Plan for `python-dispatch`

This plan expands the original modernization outline into implementation-ready
work. The workspace migration, documentation upgrade, and phase 4 typing and
lint baseline are merged. Generic event and property work is deferred; the next
active phase is support metadata and documentation alignment.

## Goals and compatibility constraints

- Keep the core `python-dispatch` package lightweight and preserve its runtime
  behavior and public API. Static types must not add runtime type enforcement.
- Retain the Sphinx plugin as a workspace member while keeping the core and
  plugin independently buildable and publishable.
- Upgrade the documentation toolchain and plugin to a deliberately supported
  modern Sphinx range; verify both the declared minimum and the locked current
  release.
- Consider useful opt-in static typing for events and properties as future
  work. Do not claim that dynamic `Dispatcher.bind` keyword arguments or
  `Dispatcher.emit("name", ...)` calls are checked against per-event signatures
  unless the API is separately redesigned.
- Make the declared Python floor, classifiers, CI matrix, and contributor/user
  documentation consistent. The project currently declares Python `>=3.11`.

## Baseline before the Markdown-parser change

- The root `pyproject.toml` and `uv.lock` define a workspace containing
  `sphinx-plugin`; the separate `sphinx-plugin/uv.lock` was removed in #138.
  The root maps both workspace projects with `{ workspace = true }`, and its
  default `dev` group includes the plugin.
- CI and Read the Docs still run `uv pip install -e sphinx-plugin` after
  `uv sync`; remove these redundant installs as workspace cleanup after
  confirming each synced environment includes the plugin.
- The core is version `0.2.3`, the plugin is `0.2.2`, and both declare
  `requires-python = ">=3.11"`. The plugin depends on `sphinx<5.0.0` and pins
  several `sphinxcontrib-*` packages to old upper bounds. The root lock
  currently resolves Sphinx 4.5.0.
- The core's documentation dependencies include `m2r2>=0.3.2`; `doc/source/conf.py`
  loads `m2r2` and declares `.md` as a supported source suffix. The current
  locked `m2r2` emits a `pkg_resources` deprecation warning. The Read the Docs
  report identifies this dependency as a Python 3.13 build blocker.
- The plugin's `directives.py` and `documenters.py` extend Sphinx autodoc/domain
  behavior. Plugin tests compare generated reStructuredText to four checked-in
  snapshots and also exercise HTML, intersphinx, and linkcheck builders.
  `sphinx-rst-builder` is the current RST builder dependency.
- CI tests core on Python 3.11–3.14 but skips plugin tests on 3.14. The plugin
  metadata classifiers stop at 3.13. The distribution workflow also builds and
  exports dependency locks from the two projects separately.
- Core modules have sparse/inconsistent annotations and no configured
  type-checker or linter. `Event`, `Property`, and their descriptor/container
  methods are not generic. `documenters.py` currently detects annotated events
  using the identity test `annotation is Event`, which will need to account for
  generic annotations.
- `README.md`, `CONTRIBUTING.md`, `pydispatch/__init__.py`, and some docstrings
  still claim Python 3.6-or-earlier compatibility despite the declared 3.11
  floor. The plugin installation page says the two package versions must match,
  although their current versions differ and the plugin's dependency is a
  compatible-version range.
- The plugin now imports from the workspace environment (`uv run --frozen
  python -c "import pydispatch_sphinx"` succeeds). The duplicate CI and Read
  the Docs editable installs remain, despite the plugin being available in the
  workspace.
- With the current Python 3.14.2 / Sphinx 4.5.0 environment, the complete HTML
  docs build succeeds, but still emits the `m2r2` / `pkg_resources`
  deprecation warning. Plugin tests pass on Python 3.13 according to the
  maintainer's local verification. Earlier failures on Python 3.14.2
  (5 failures, 3 passes under Sphinx 4.5.0) were caused by the local Python
  version pin and should not be treated as the plugin's general baseline.
  Preserve the 3.13 passing result as the post-workspace, pre-Sphinx-upgrade
  baseline; 3.14 support remains a separate goal because CI currently skips
  plugin tests on that version.

## Work sequence

Phases 5 and 6 are deferred future work, not prerequisites for phase 7.
Continue with phase 7 without merging the generic-event prototype.

### 0. Establish a reproducible baseline

1. Retain the successful current full HTML docs build as the docs baseline;
   note the outstanding `m2r2` deprecation warning.
2. Record the passing plugin test result on Python 3.13 and preserve the four
   expected snapshot files as the pre-upgrade baseline. Do not treat the
   earlier Python 3.14 failures as version-independent test failures.
3. Before changing Sphinx or autodoc code, capture and review the current
   generated outputs for both `rst` and `rst` + intersphinx builders. Existing
   expected files are in
   `sphinx-plugin/tests/docroots/{test-events,test-properties}/`.
4. If testing Python 3.14 before the Sphinx-upgrade phase, investigate failures
   there separately from the passing Python 3.13 baseline.

**Exit criteria:** baseline core tests, plugin tests, and HTML documentation
build results are recorded with their Python versions; interpreter-specific
failures are not silently folded into later snapshot updates.

### 1. Remove the `m2r2` / `pkg_resources` documentation blocker

This is the priority change and should be a small standalone PR targeted at
`master`.

**Status:** Merged in #139. The README include uses MyST's parser, and the
documentation build has been verified on Python 3.13 without `pkg_resources`.
The plugin tests pass on Python 3.13, and the core tests and doctests pass on
Python 3.13 and 3.14.

1. Replace `m2r2` with `myst-parser` in the root documentation dependency group
   and replace the `m2r2` entry in `doc/source/conf.py` with `myst_parser`.
   Keep Markdown enabled (`.md` remains in `source_suffix`) so this change does
   not silently remove a documented capability.
2. Remove the direct `setuptools` dependency only if repository usage confirms
   it is no longer needed; do not use a setuptools pin as a workaround for
   importing `pkg_resources`.
3. Regenerate the root lock and verify a clean documentation environment can
   import all extensions and build the project on Python 3.13, matching the
   Read the Docs interpreter.
4. Preserve the existing Sphinx/plugin constraints for this isolated change;
   do not combine it with the Sphinx upgrade or workspace migration.

**Exit criteria:** the Read the Docs install/build sequence no longer imports
`m2r2` or relies on `pkg_resources`; the full HTML docs build succeeds; the
root lock is current. Do not proceed to the Sphinx upgrade until this change is
landed.

### 2. Verify workspace integration and remove migration leftovers

The workspace migration itself is complete in #138. Root workspace
configuration, source mappings, and the single lockfile are in place. The
remaining work is to verify the synced environments and then remove the
duplicate editable-install commands from CI and Read the Docs.

**Status:** Merged in #142. Clean
Python 3.13 syncs install the plugin without the extra command; the docs build,
core and plugin tests, and installed wheel and sdist tests pass.

1. Verify `uv sync --frozen --group doc` installs the plugin in a clean
   Read the Docs-like environment and that the full docs build can import the
   extension.
2. Verify `uv sync --frozen --group test --group doc` installs the plugin and
   runs its tests in CI without an extra `uv pip install`.
3. After confirming steps 1 and 2, remove the redundant
   `uv pip install -e sphinx-plugin` commands from `.readthedocs.yaml` and
   `.github/workflows/ci.yml`. Keep those workflow edits small and separate
   from unrelated dependency changes.
4. Keep the independent distribution builds and tests in
   `.github/workflows/dist-test.yml`. Check that each exported requirements
   file comes from the root workspace lock and that the sdist/wheel tests still
   exercise the built artifacts rather than accidentally importing workspace
   source.
5. Correct `doc/source/sphinx-plugin/install.rst`: document the actual
   compatible-version relationship or enforce synchronized releases
   deliberately. Do not leave a lockstep-version claim that contradicts package
   metadata.

**Exit criteria:** clean synced environments can import the plugin; docs and
plugin tests pass without per-directory editable installs; both distributions
remain independently buildable and testable.

### 3. Upgrade Sphinx and restore plugin support on Python 3.14

Do this after the workspace migration, in a separate reviewable change from the
typing/generics work.

**Status:** Merged in #143. Sphinx 8.2 is the
selected baseline and support is bounded to `<9` pending a separate Sphinx 9
compatibility assessment. `sphinx-design` replaces the Sphinx-4-only panels
extension. `sphinxcontrib-restbuilder` replaces the old RST builder; it
formats external links as bare URLs, so HTML tests also check rendered labels,
signatures, and links. Its generated RST can also contain internal links without
matching targets; it is used for snapshot tests, not the published HTML build.
Python 3.14 plugin tests are enabled again.

1. Raise the plugin's Sphinx lower bound to a selected modern baseline (start
   with Sphinx 7.4 or newer, subject to API compatibility testing) and remove
   the `<5.0.0` ceiling. Keep the project-wide Sphinx policy explicit: test the
   declared minimum and the latest version resolved by the root lock.
2. Remove old `sphinxcontrib-*` upper pins only after confirming the supported
   Sphinx versions bring compatible extensions. Retain any package still
   required by the supported range, with a reason and a test.
3. Check whether `standard-imghdr` remains needed with the selected Sphinx
   range and supported Python versions; remove it only if the replacement
   Sphinx/dependency set no longer needs it.
4. Resolve the `sphinx-rst-builder` issue by first testing it with the selected
   Sphinx versions. If it is incompatible, migrate the test builder to
   `sphinxcontrib.restbuilder` (or another maintained builder), updating test
   configuration without weakening the snapshot assertions.
5. Update `sphinx-plugin/pydispatch_sphinx/directives.py` and
   `sphinx-plugin/pydispatch_sphinx/documenters.py` to use supported Sphinx
   APIs. Keep event/property recognition, inheritance, directive roles,
   cross-references, and behavior for non-`Dispatcher` classes intact.
6. Regenerate each expected RST snapshot from the updated builder, then review
   the diff. Accept only explainable output-format changes; retain assertions
   for semantic content, links, event/property signatures, and ordering.
7. Run plugin tests for both Napoleon configurations and all current builder
   variants: RST, RST with intersphinx, HTML, and linkcheck. Run the full
   project HTML documentation build as well.
8. Once plugin tests pass on Python 3.14, remove the 3.14 skip in
   `.github/workflows/ci.yml` and `.github/workflows/dist-test.yml`; align the
   plugin's Python classifiers with the tested matrix.

**Exit criteria:** supported minimum and latest Sphinx builds pass, plugin
snapshots have intentional reviewed diffs, full docs and distribution tests
pass, and the plugin is no longer excluded from Python 3.14.

### 4. Correct existing annotations and add a focused type/lint gate

Make annotation corrections before introducing generic public types, so
ordinary type issues are distinguishable from generic inference issues.

**Staging:** Start with a separate Ruff PR covering the core and plugin using
focused correctness rules. Follow it with one or more annotation and mypy PRs;
do not treat the lint gate as completion of the typing work. An initial mypy
run with untyped function bodies checked reported 38 errors across the two
packages, including dynamic descriptors, weak-reference internals, and
incompatible overrides. Investigate these without blanket suppressions or
unreviewed runtime changes.

The cached-receiver bug in `_post_register_hook` was fixed separately in #144.

**Progress:** Ruff is enforced in CI for both packages (#145). Mypy is in the
test dependency group and runs on the core package as a non-blocking CI step
(#146), checking untyped bodies against Python 3.11. The core baseline initially
reported 32 errors; the initial fixes and dispatcher and property typing
reduced it to 9 (#147), including narrow ignores for existing accesses to private
name-mangled storage rather than exposing mangled names to type checkers. Async
waiter annotations (#148) and a narrow ignore for an unstubbed private helper
bring the current baseline to 8. Emission-lock state annotations also clarify
the values observed by Pylance without suppressing the remaining mypy errors;
they exposed an async-release lock-state check that was fixed and regression-tested
in #149. The async weak-method container now shares the base callback parameter
and accepts extra keyword arguments, reducing the baseline to 7. Its loop remains
required at runtime, so the signature alone does not guarantee substitutability.
The callback keyword renames, ``isfunction`` keyword rename, and async positional
argument order change are documented for 0.3.0. Continue addressing the remaining
diagnostics incrementally before making the check blocking or expanding it to the
plugin. Property initialization now stores per-instance observable defaults via
a shared helper, and property-owned observables hold their owners weakly to
allow collection. These changes fix both `_add_instance` override diagnostics;
the core mypy baseline was 5 (#151). The observable list in-place addition
signature now reflects its iterable input and identity-preserving return; a
narrow ignore accounts for mypy's comparison against overloaded `list.__add__`.
The observable copy contract and dictionary update signature now match their
concrete implementations; dictionary updates accept standard inputs and notify
about partial changes on failure (#152). Explicit checks now preserve the
existing errors for missing weak-dictionary callbacks and ownerless observable
properties. The mypy check passes for both the core package and Sphinx plugin
with the documented narrow ignores and is blocking in CI. The plugin uses
development-only Docutils stubs, and missing required `propcls` options now
produce a clear directive error. This passing baseline checks untyped function
bodies but does not mean every public API is fully annotated.
`Dispatcher` now has explicit return and straightforward argument annotations;
its dynamic callback keyword arguments remain for the generic event work.
Mypy and Ruff scopes and the minimum Python target are configured in
`pyproject.toml`, so their checks can be run without path or option arguments.

1. Select and configure a static type checker and linter in the root
   development tooling. Recommended: mypy for type checking and Ruff for
   linting. Scope the first pass to `pydispatch/` and
   `sphinx-plugin/pydispatch_sphinx/`; avoid turning this into an unrelated
   repository-wide formatting rewrite.
2. Add annotations to the core runtime surfaces, including dispatch,
   properties, async helpers, callback decorators, and public exports. Use
   `TYPE_CHECKING`, protocols, and precise unions where needed; avoid broad
   `Any` or blanket ignores to silence meaningful diagnostics.
3. Preserve existing behavior when clarifying edge cases in weak-reference
   storage, async callbacks, event return values, descriptor initialization,
   and observable list/dict mutations. If a checker reveals an actual behavior
   bug, isolate and test that fix rather than hiding it in an annotation.
4. Add the configured checks to CI and document the local command in
   `CONTRIBUTING.md`.

**Exit criteria:** the selected checks pass for both packages, existing runtime
tests pass unchanged, and no new runtime dependency is introduced.

### 5. Add opt-in generic callback signatures to `Event` — future work

**Status: Deferred.** `Dispatcher` is the primary public API, and its
string-named events and keyword-based bindings are dynamic. A generic `Event`
can check calls made directly on a typed event, but does not connect a name
passed to `Dispatcher.emit` or `Dispatcher.bind` to that signature. Annotating
an event on a dispatcher subclass does not by itself create a typed event
handle or establish that mapping. A useful typed dispatcher-facing API needs
separate design and compatibility review before resuming this phase.

**Reference prototype:** The `modernize/generic-event` branch contains an
unmerged experiment using a defaulted `ParamSpec`, a shared callback alias,
Sphinx generic-annotation detection, and a `py.typed` marker. Its conditional
`typing-extensions` dependency applies below Python 3.13. It checks direct
event calls, not the dynamic dispatcher interface; it is a reference for future
design, not an implementation assumed to exist on `master`.

When revisiting, consider whether an opt-in typed event handle connected to the
existing registry is appropriate, without changing the existing string-based
API. Keep that design separate from the baseline annotation pass.

1. Parameterize `Event` with `ParamSpec` and type its synchronous callback
   storage, registration, and invocation so an explicitly typed `Event` can
   describe its positional and keyword callback arguments.
2. Cover the async callback path and waiter path without weakening the
   synchronous signature or changing scheduling/return behavior.
3. Keep unparameterized `Event` usage valid for existing callers. Treat the
   generic as static-only: do not inspect or reject runtime callback signatures.
4. Be explicit in API docs and examples that events registered by string name
   are still dynamically dispatched; this generic does not create a statically
   checked mapping from each `Dispatcher` event name to its callback signature.
5. Update the plugin's annotated-event detection to recognize both `Event` and
   generic forms (for example by normalizing the annotation's origin), while
   continuing not to classify `Event` annotations on ordinary non-dispatcher
   classes as dispatcher events.
6. Add static typing examples/checks for valid callback signatures and
   deliberately invalid callback/emit calls, alongside runtime regression
   tests for sync, async, false-return short-circuiting, and weak references.

**Exit criteria:** examples demonstrate useful opt-in callback argument types;
existing untyped code remains accepted; static checks detect the intended
mismatches; runtime event behavior is unchanged.

### 6. Add generic property value types — future work

**Status: Deferred.** Generic descriptors could improve direct property
read/write types, but property change subscriptions also flow through the
dynamic `Dispatcher` interface. Descriptor types alone would not give
`bind` a static mapping from a property name to its callback signature.
Revisit property generics alongside the event/dispatcher API design so the
scope and value of static guarantees are clear, while retaining the existing
runtime behavior.

1. Parameterize `Property` by its value type and give its descriptor methods
   overloads for class access and instance access so a declared property value
   has the right type when read and written.
2. Parameterize `ListProperty` by element type and `DictProperty` by key/value
   types, preserving their observable container behavior. Ensure internal
   observable list/dict wrappers retain compatible container typing.
3. Model the default-`None` behavior honestly. A property that can read as
   `None` must be annotated with a nullable value type; do not make a
   non-nullable descriptor appear sound merely to make inference convenient.
4. Cover assignment, reads, list/dict element operations, defaults, and
   subclassed properties in static typing examples. Include invalid assignment
   cases in a type-check fixture, and retain runtime tests for independent
   defaults, nested observables, and change notifications.
5. Update property docs and Sphinx examples to show generic annotations and
   verify that autodoc still reports the intended value type and default.

**Exit criteria:** generic properties provide useful static read/write types,
including container element types and nullable defaults, with no change to
runtime value validation or notifications.

### 7. Align support metadata and documentation; final integration

**Progress:** Both packages require Python 3.11+ and classify 3.11–3.14,
matching the core and plugin CI and distribution test matrices. The support
documentation and obsolete pre-3.6 warning have been updated. On Python 3.13,
the core and plugin suites, mypy, Ruff, and strict HTML build pass. Both
packages' wheels and source distributions pass their core and plugin test
suites in isolated environments on Python 3.11, 3.12, 3.13, and 3.14.
The existing pytest-asyncio configuration warning and the Python 3.14
Sphinx RST builder `codecs.open` deprecation warning remain.

1. Update `README.md`, `CONTRIBUTING.md`, `pydispatch/__init__.py`, and stale
   Python-version docstrings to say Python 3.11+ and reflect the tested
   versions. Remove obsolete compatibility warnings only when the project
   metadata and CI make them unreachable.
2. Confirm both package classifiers match the versions actually tested. Keep
   `requires-python`, CI, build metadata, and installation docs consistent.
3. Run core tests, plugin tests, typing/lint checks, full HTML docs build, and
   wheel/sdist distribution tests on the supported Python matrix.
4. Check the final diff for unrelated formatting, accidental runtime
   dependencies, changed package metadata, or snapshots that mask semantic
   regressions.

## Agent handoff boundaries

Use the sequence above as dependency order, except that deferred phases 5 and 6
do not block phase 7. A task agent should own one phase at a time and report
changed files, commands run, failures, and any decisions that need maintainer
input. Do not have separate agents edit the lockfile or the same Sphinx
snapshots concurrently.
