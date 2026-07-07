#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/check-release-readiness.sh [--strict-release] [vMAJOR.MINOR.PATCH]

Checks tests, package metadata, GitHub Actions workflow syntax, source/wheel
builds, twine metadata validation, and release tag/version consistency.

Examples:
  scripts/check-release-readiness.sh
  scripts/check-release-readiness.sh v0.1.0
  scripts/check-release-readiness.sh --strict-release v0.1.0
USAGE
}

STRICT_RELEASE=0
RELEASE_TAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict-release)
      STRICT_RELEASE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    v*)
      if [[ -n "${RELEASE_TAG}" ]]; then
        echo "Only one release tag may be provided." >&2
        exit 2
      fi
      RELEASE_TAG="$1"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    echo "Install local release tools with: python -m pip install -e \".[test,release]\"" >&2
    echo "For actionlint, use the Docker check or install the actionlint binary on the host." >&2
    echo "Docker check: docker compose run --build --rm check" >&2
    exit 1
  fi
}

PACKAGE_VERSION="$(python - <<'PY'
from tbot223_base import __version__

print(__version__)
PY
)"

if [[ -z "${RELEASE_TAG}" ]]; then
  RELEASE_TAG="v${PACKAGE_VERSION}"
  echo "Release tag not provided; using ${RELEASE_TAG} from package version."
fi

if [[ ! "${RELEASE_TAG}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Release tag must use vMAJOR.MINOR.PATCH format, for example v0.1.0." >&2
  exit 1
fi

TAG_VERSION="${RELEASE_TAG#v}"

if [[ "${TAG_VERSION}" != "${PACKAGE_VERSION}" ]]; then
  echo "Package version ${PACKAGE_VERSION} does not match release tag ${RELEASE_TAG}." >&2
  exit 1
fi

echo "Checking package metadata baseline..."
python - <<'PY'
import pathlib
import tomllib

from tbot223_base import __version__

pyproject = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
project = pyproject["project"]
dynamic_version = pyproject["tool"]["setuptools"]["dynamic"]["version"]["attr"]

assert project["name"] == "tbot223-base"
assert project["dynamic"] == ["version"]
assert project["requires-python"] == ">=3.10"
assert project["license"] == "Apache-2.0"
assert project["license-files"] == ["LICENSE"]
assert dynamic_version == "tbot223_base.__version__"

print(f"metadata baseline ok: {project['name']} {__version__}")
PY

echo "Checking local release tag state..."
if git rev-parse --git-dir >/dev/null 2>&1; then
  if git rev-parse -q --verify "refs/tags/${RELEASE_TAG}^{commit}" >/dev/null; then
    TAG_COMMIT="$(git rev-list -n 1 "${RELEASE_TAG}")"

    if git rev-parse -q --verify "refs/remotes/origin/main" >/dev/null; then
      git merge-base --is-ancestor "${TAG_COMMIT}" origin/main
      echo "tag ancestry ok: ${RELEASE_TAG} is contained in origin/main"
    else
      echo "origin/main is not available locally; skipping tag ancestry check."
      if [[ "${STRICT_RELEASE}" -eq 1 ]]; then
        echo "Strict release mode requires origin/main for ancestry validation." >&2
        exit 1
      fi
    fi
  else
    echo "Local tag ${RELEASE_TAG} does not exist yet."
    if [[ "${STRICT_RELEASE}" -eq 1 ]]; then
      echo "Strict release mode requires the local release tag to exist." >&2
      exit 1
    fi
  fi
fi

require_command actionlint

echo "Checking Python syntax..."
python -m py_compile \
  tbot223_base/__init__.py \
  tbot223_base/result.py \
  tbot223_base/exception_tracker.py

echo "Running tests..."
pytest -q

echo "Checking GitHub Actions workflows..."
actionlint .github/workflows/*.yml

echo "Checking whitespace in git diff..."
git diff --check

echo "Building package in a temporary copy..."
TMP_DIR="$(mktemp -d /tmp/tbot223-base-release-check.XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT

rsync -a \
  --exclude .git \
  --exclude .mypy_cache \
  --exclude .pytest_cache \
  --exclude .ruff_cache \
  --exclude .venv \
  --exclude build \
  --exclude dist \
  --exclude "*.egg-info" \
  ./ "${TMP_DIR}/src/"

python -m build --sdist --wheel --no-isolation --outdir "${TMP_DIR}/dist" "${TMP_DIR}/src"

echo "Checking built distributions..."
python -m twine check "${TMP_DIR}"/dist/*

python - <<'PY' "${TMP_DIR}/dist" "${PACKAGE_VERSION}"
import email.parser
import pathlib
import sys
import zipfile

dist_dir = pathlib.Path(sys.argv[1])
expected_version = sys.argv[2]
wheels = sorted(dist_dir.glob("*.whl"))
sdists = sorted(dist_dir.glob("*.tar.gz"))

assert len(wheels) == 1, wheels
assert len(sdists) == 1, sdists

with zipfile.ZipFile(wheels[0]) as wheel:
    metadata_name = next(name for name in wheel.namelist() if name.endswith(".dist-info/METADATA"))
    metadata = email.parser.Parser().parsestr(wheel.read(metadata_name).decode())

assert metadata["Name"] == "tbot223-base"
assert metadata["Version"] == expected_version
assert metadata["Requires-Python"] == ">=3.10"

print(wheels[0].name)
print(sdists[0].name)
print("distribution metadata ok")
PY

echo "Release readiness checks passed for ${RELEASE_TAG}."
