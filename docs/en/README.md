[한국어 (Korean)](../ko/README.md)

> Runtime baseline: package version `1.0.0a1` (`tbot223_base.__version__ == "1.0.0a1"`).

# tbot223-base Docs

English documentation for using `Result`, `ResultStatus`, and `ExceptionTracker`.

`1.0.0a1` is a rebuilding alpha and is not recommended for production use. Start with [Rebuilding](rebuilding.md).

## Start Here

- [Root README](../../README.md): project orientation, design intent, audience fit, trade-offs, and quickstart.
- [Rebuilding](rebuilding.md): withdrawn-release rationale, current guarantees, and required gates.
- [Getting Started](guides/getting-started.md): import the package from a checkout or editable install and use the core APIs.
- [Executable Examples](guides/examples.md): run standalone scripts under `examples/` for `Result` and `ExceptionTracker` flows.
- [Package and CI Guide](guides/package-and-ci.md): use `pyproject.toml`, editable installs, compatibility CI, and release publishing.

## Reference

- [Result Reference](reference/result.md): required payloads, typed factories, status model, and unwrap helpers.
- [ExceptionTracker Reference](reference/exception-tracker.md): debug payloads, public payloads, masking, and safe context capture.

## Release Notes

- [Release Notes](release-notes.md)

## Contracts

- [Writing contracts](../contracts/README.md)
- [API contract](../contracts/en/human/api-contract.md)
