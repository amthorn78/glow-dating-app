#!/bin/bash
# Glow app pinned toolchain for Claude Code cloud environments (work item M02).
#
# Installs Node 24.19.0 with npm 11.9.0 and CPython 3.12.14 from hash-verified
# downloads into $HOME/.local/share/glow-app-toolchain, then links node, npm,
# npx and python3.12 into $HOME/.local/bin (first on PATH in Claude Code cloud
# sessions). It never replaces python3 or python.
#
#   Cloud environment Setup script: paste this whole file unchanged.
#   Manual run inside a session:    bash scripts/bootstrap-toolchain.sh
#   Options: --prefix DIR  install location instead of the default above
#            --no-link     install only and print PATH guidance
#
# Linux x86_64 only; other machines follow docs/operations/local-development.md.
# The pins below must equal services/api/.python-version, the engines in both
# package.json files, .github/workflows/foundation.yml and the Dockerfile tag.
# Change them only in a reviewed PR, then paste the new file into the
# environment's Setup script. Hash provenance:
# docs/testing/evidence/2026-09-24-m02-claude-setup.md.
# The script reads no application, provider or database configuration and
# prints no environment values. The first run takes about 3-4 minutes.
#
# Every installed file belongs to the account running the script and is not
# writable by group or others. Archives are extracted without their recorded
# owners (the Node archive records uid 1000). An existing tree that breaks this
# rule is replaced from the verified archive, never repaired in place, and is
# checked before anything in it is executed.
set -euo pipefail
umask 022

readonly NODE_VERSION=24.19.0
readonly NODE_SHA256=14b342e71204f811bde6153be8e04b62aef63c236fef92b55f9c83154b409647
readonly NPM_VERSION=11.9.0
readonly NPM_INTEGRITY=sha512-BBZoU926FCypj4b7V7ElinxsWcy4Kss88UG3ejFYmKyq7Uc5XnT34Me2nEhgCOaL5qY4HvGu5aI92C4OYd7NaA==
readonly PYTHON_VERSION=3.12.14
readonly PYTHON_SHA256=6c6df908d2c3fd24e6d76869e92542abd0f33aec9dfc18df8875f89660286d43
readonly PYTHON_MODULES='import bz2, ctypes, lzma, sqlite3, ssl, zlib'

log() { printf 'glow-toolchain: %s\n' "$*"; }
die() { printf 'glow-toolchain: ERROR: %s\n' "$*" >&2; exit 1; }

prefix="$HOME/.local/share/glow-app-toolchain"
link=true
while [ "$#" -gt 0 ]; do
  case "$1" in
    --prefix) [ "$#" -ge 2 ] || die "--prefix needs a directory"; prefix="$2"; shift 2 ;;
    --no-link) link=false; shift ;;
    *) die "usage: bootstrap-toolchain.sh [--prefix DIR] [--no-link]" ;;
  esac
done

[ "$(uname -s)" = Linux ] && [ "$(uname -m)" = x86_64 ] \
  || die "Linux x86_64 only; see docs/operations/local-development.md"

mkdir -p "$prefix"
prefix=$(cd "$prefix" && pwd)
node_dir="$prefix/node-v$NODE_VERSION-linux-x64"
python_dir="$prefix/python-$PYTHON_VERSION"
uid=$(id -u)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

download() {  # url destination
  curl --fail --silent --show-error --location --proto '=https' --tlsv1.2 \
    --retry 3 --retry-delay 2 --output "$2" "$1" || die "download failed: $1"
}

verify_sha256() {  # file expected-hex label
  echo "$2  $1" | sha256sum --check --status || die "$3 SHA-256 mismatch"
}

trusted_tree() {  # directory: every entry is ours and no non-link is group/other-writable
  local foreign
  foreign=$(find "$1" \( ! -user "$uid" -o \( ! -type l -perm /022 \) \) -print -quit) || return 1
  [ -z "$foreign" ]
}

node_npm() {  # the npm inside the Node tree, never another npm on PATH
  PATH="$node_dir/bin:$PATH" "$node_dir/bin/npm" "$@"
}

install_node() {
  if [ -e "$node_dir" ] && ! trusted_tree "$node_dir"; then
    log "replacing $node_dir: it has entries owned by another account or writable by group or others"
  elif [ -x "$node_dir/bin/node" ] && [ "$("$node_dir/bin/node" --version)" = "v$NODE_VERSION" ] &&
    [ "$(node_npm --version)" = "$NPM_VERSION" ]; then
    log "Node $NODE_VERSION with npm $NPM_VERSION already installed"
    return
  fi
  log "installing Node $NODE_VERSION"
  download "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz" "$work/node.tar.xz"
  verify_sha256 "$work/node.tar.xz" "$NODE_SHA256" "Node archive"
  rm -rf "$node_dir"
  tar --no-same-owner --no-same-permissions -xJf "$work/node.tar.xz" -C "$prefix"
  log "installing npm $NPM_VERSION"
  download "https://registry.npmjs.org/npm/-/npm-$NPM_VERSION.tgz" "$work/npm.tgz"
  local integrity
  integrity=$("$node_dir/bin/node" -e 'const c=require("crypto"),f=require("fs");process.stdout.write("sha512-"+c.createHash("sha512").update(f.readFileSync(process.argv[1])).digest("base64"))' "$work/npm.tgz")
  [ "$integrity" = "$NPM_INTEGRITY" ] || die "npm tarball SHA-512 mismatch"
  PATH="$node_dir/bin:$PATH" npm install --global --prefix "$node_dir" --offline \
    --no-audit --no-fund --loglevel=error "$work/npm.tgz" >/dev/null
}

install_python() {
  # --version succeeds even without a standard library, so an interrupted
  # install is detected by importing the required modules.
  if [ -e "$python_dir" ] && ! trusted_tree "$python_dir"; then
    log "replacing $python_dir: it has entries owned by another account or writable by group or others"
  elif [ -x "$python_dir/bin/python3.12" ] &&
    [ "$("$python_dir/bin/python3.12" --version)" = "Python $PYTHON_VERSION" ] &&
    "$python_dir/bin/python3.12" -c "$PYTHON_MODULES" 2>/dev/null; then
    log "Python $PYTHON_VERSION already installed"
    return
  fi
  log "building Python $PYTHON_VERSION (about 3 minutes)"
  download "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz" "$work/python.tgz"
  verify_sha256 "$work/python.tgz" "$PYTHON_SHA256" "Python source"
  tar --no-same-owner --no-same-permissions -xzf "$work/python.tgz" -C "$work"
  rm -rf "$python_dir"
  local step
  for step in configure make install; do
    case "$step" in
      configure) set -- ./configure --prefix="$python_dir" --with-ensurepip=install --disable-test-modules ;;
      make) set -- make -j"$(nproc)" ;;
      install) set -- make install ;;
    esac
    (cd "$work/Python-$PYTHON_VERSION" && "$@") >"$work/python-$step.log" 2>&1 || {
      tail -n 40 "$work/python-$step.log" >&2
      die "Python $step failed"
    }
  done
  "$python_dir/bin/python3.12" -c "$PYTHON_MODULES" \
    || die "Python is missing a required standard-library module"
}

install_node
install_python

trusted_tree "$node_dir" && trusted_tree "$python_dir" \
  || die "installed toolchain has entries owned by another account or writable by group or others"
node_version=$("$node_dir/bin/node" --version)
npm_version=$(node_npm --version)
python_version=$("$python_dir/bin/python3.12" --version)
[ "$node_version" = "v$NODE_VERSION" ] || die "unexpected Node version"
[ "$npm_version" = "$NPM_VERSION" ] || die "unexpected npm version"
[ "$python_version" = "Python $PYTHON_VERSION" ] || die "unexpected Python version"

if [ "$link" = true ]; then
  mkdir -p "$HOME/.local/bin"
  for tool in node npm npx; do
    ln -sfn "$node_dir/bin/$tool" "$HOME/.local/bin/$tool"
  done
  ln -sfn "$python_dir/bin/python3.12" "$HOME/.local/bin/python3.12"
  log "linked node, npm, npx and python3.12 into $HOME/.local/bin"
else
  log "add to PATH: $node_dir/bin:$python_dir/bin"
fi
log "ready: node $node_version, npm $npm_version, $python_version"
