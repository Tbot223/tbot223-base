#!/usr/bin/env python3
"""Validate required public API docstring sections from Python ASTs."""

from __future__ import annotations

import ast
import pathlib
import sys
from collections.abc import Iterable


ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
PUBLIC_METHODS = {
    "tbot223_base/result.py": {
        "ResultStatus": {"normalize"},
        "ResultUnwrapException": {"__init__"},
        "Result": {
            "__new__",
            "ok",
            "failure",
            "cancelled",
            "status",
            "error",
            "context",
            "data",
            "success",
            "is_success",
            "is_failure",
            "is_cancelled",
            "unwrap",
            "expect",
            "unwrap_or",
        },
    },
    "tbot223_base/exception_tracker.py": {
        "ExceptionTracker": {
            "__init__",
            "get_exception_location",
            "get_exception_info",
            "get_public_exception_info",
            "get_exception_return",
            "get_public_exception_return",
            "get_error_code",
        },
        "ExceptionTrackerDecorator": {"__init__"},
    },
}
REQUIRED_SECTIONS = ("### Arguments", "### Returns")
CONTRACT_DOCS = (
    "docs/contracts/en/human/docstring-contract.md",
    "docs/contracts/ko/human/docstring-contract.md",
)


def iter_methods(class_node: ast.ClassDef) -> Iterable[ast.FunctionDef | ast.AsyncFunctionDef]:
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def validate_python_docstrings() -> list[str]:
    errors: list[str] = []
    for relative_path, classes in PUBLIC_METHODS.items():
        source_path = ROOT_DIR / relative_path
        module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        class_nodes = {
            node.name: node
            for node in module.body
            if isinstance(node, ast.ClassDef)
        }

        for class_name, method_names in classes.items():
            class_node = class_nodes.get(class_name)
            if class_node is None:
                errors.append(f"{relative_path}: missing public class {class_name}")
                continue
            methods = {method.name: method for method in iter_methods(class_node)}

            for method_name in method_names:
                method = methods.get(method_name)
                symbol = f"{relative_path}:{class_name}.{method_name}"
                if method is None:
                    errors.append(f"{symbol}: missing public method")
                    continue

                docstring = ast.get_docstring(method, clean=False)
                if docstring is None:
                    errors.append(f"{symbol}: missing docstring")
                    continue
                for section in REQUIRED_SECTIONS:
                    if section not in docstring:
                        errors.append(f"{symbol}: missing {section}")
                if any(isinstance(node, ast.Raise) for node in ast.walk(method)):
                    if "### Raises" not in docstring:
                        errors.append(f"{symbol}: raises but lacks ### Raises")
    return errors


def validate_contract_examples() -> list[str]:
    errors: list[str] = []
    for relative_path in CONTRACT_DOCS:
        document = (ROOT_DIR / relative_path).read_text(encoding="utf-8")
        if "result = tracker.get_exception_info" not in document:
            errors.append(f"{relative_path}: missing get_exception_info example")
        if "print(result.success)  # False" not in document:
            errors.append(f"{relative_path}: get_exception_info example must show failure")
    return errors


def main() -> int:
    errors = validate_python_docstrings() + validate_contract_examples()
    if errors:
        print("Docstring contract check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Docstring contract check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
