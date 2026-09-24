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
# prints no environment values. The first run takes about two minutes, mostly
# building Python.
#
# Trust rules, checked before anything in a tree is executed:
# - The prefix and link directories belong to the running account and are not
#   writable by group or others. Their parents belong to that account or root
#   and are not writable by group or others unless sticky (/tmp). The link
#   directory's path contains no symlink.
# - Every installed entry belongs to the running account and no non-link is
#   writable by group or others. Archives are extracted without their recorded
#   owners (the Node archive records uid 1000).
# - A tree's root is a real directory. Every symlink in it is relative, never
#   climbs above the root and resolves to a regular file inside the tree.
# An existing tree that breaks these rules is replaced from the verified
# archive, never repaired in place. An unsafe directory stops the script.
set -euo pipefail
umask 022
unset CDPATH  # cd must never search it; a relative --prefix is relative to the working directory
# npm would otherwise read and write V8 compile cache in $TMPDIR, outside the checked trees.
export NODE_DISABLE_COMPILE_CACHE=1

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
command -v setsid >/dev/null || die "setsid (util-linux) is required"

uid=$(id -u)
work=''
child=''

# Each long step runs in its own process group (run), so SIGINT or SIGTERM
# stops the whole step, then the temporary directory is removed.
group_running() {  # process-group-id: a member that has not exited (zombies excluded)
  ps -e -o pgid= -o stat= | awk -v group="$1" '$1 == group && $2 !~ /^Z/ { found = 1 } END { exit !found }'
}

stop_child() {
  [ -n "$child" ] || return 0
  kill -TERM -- "-$child" 2>/dev/null || true
  local waited=0
  while [ "$waited" -lt 50 ] && group_running "$child"; do
    sleep 0.1
    waited=$((waited + 1))
  done
  kill -KILL -- "-$child" 2>/dev/null || true
  wait "$child" 2>/dev/null || true
  child=''
}

cleanup() { if [ -n "$work" ]; then rm -rf -- "$work"; fi; }

interrupted() {  # signal
  trap '' INT TERM
  stop_child
  cleanup
  trap - "$1" EXIT
  printf 'glow-toolchain: stopped by SIG%s; temporary files removed\n' "$1" >&2
  kill -s "$1" "$$"
  exit $((128 + $(kill -l "$1")))
}

trap cleanup EXIT
trap 'interrupted INT' INT
trap 'interrupted TERM' TERM

# Without job control a background step is never a process-group leader, so
# setsid(1) does not fork and the step's pid is its process-group id.
set +m
run() {  # directory log command...: own process group, waited for; log "-" keeps the output
  local dir=$1 log=$2
  shift 2
  (
    cd -- "$dir" || exit 1
    if [ "$log" != - ]; then exec >"$log" 2>&1; fi
    exec setsid "$@"
  ) </dev/null &
  child=$!
  local status=0
  wait "$child" || status=$?
  child=''
  return "$status"
}

safe_dir() {  # physical-directory label
  local dir=$1 info owner mode
  [ -d "$dir" ] && [ ! -L "$dir" ] || die "$2 $1 is not a directory"
  info=$(stat -c '%u %a' -- "$dir") || die "cannot inspect $2 $1"
  owner=${info% *} mode=$((8#${info#* }))
  [ "$owner" = "$uid" ] || die "$2 $1 is not owned by the running account (uid $uid)"
  [ $((mode & 8#022)) -eq 0 ] || die "$2 $1 is writable by group or others"
  while [ "$dir" != / ]; do
    dir=${dir%/*}
    dir=${dir:-/}
    info=$(stat -c '%u %a' -- "$dir") || die "cannot inspect $dir"
    owner=${info% *} mode=$((8#${info#* }))
    { [ "$owner" = 0 ] || [ "$owner" = "$uid" ]; } \
      && { [ $((mode & 8#022)) -eq 0 ] || [ $((mode & 8#1000)) -ne 0 ]; } \
      || die "$2 $1 has an unsafe parent $dir: it must belong to root or the running account and must not be writable by group or others unless sticky"
  done
}

mkdir -p -- "$prefix"
prefix=$(cd -P -- "$prefix" && pwd -P)
safe_dir "$prefix" "prefix directory"
if [ "$link" = true ]; then
  mkdir -p -- "$HOME/.local/bin"
  link_dir=$(cd -P -- "$HOME/.local/bin" && pwd -P)
  # PATH resolves this directory again at every lookup, so its path may not
  # pass through a symlink that could later be retargeted.
  [ "$link_dir" = "$(cd -L -- "$HOME/.local/bin" && pwd -L)" ] \
    || die "link directory $HOME/.local/bin must not be or pass through a symlink"
  safe_dir "$link_dir" "link directory"
fi
node_dir="$prefix/node-v$NODE_VERSION-linux-x64"
python_dir="$prefix/python-$PYTHON_VERSION"
work=$(mktemp -d)
case "$work" in /*) ;; *) work="$PWD/$work" ;; esac  # a relative TMPDIR

download() {  # url destination
  # -q (first) ignores ~/.curlrc. A stalled transfer (under 1 KiB/s for 60 s)
  # fails and is retried; there is no total time limit.
  run "$work" - curl -q --fail --silent --show-error --location --proto '=https' --tlsv1.2 \
    --connect-timeout 30 --speed-limit 1024 --speed-time 60 \
    --retry 3 --retry-delay 2 --output "$2" "$1" || die "download failed: $1"
}

verify_sha256() {  # file expected-hex label
  echo "$2  $1" | sha256sum --check --status || die "$3 SHA-256 mismatch"
}

link_inside() {  # tree-root symlink: relative, never above the root, to a regular file inside
  local root=$1 entry=$2 text rest part depth target
  case "$entry" in "$root"/*) ;; *) return 1 ;; esac
  text=$(readlink -- "$entry" 2>/dev/null) || return 1
  case "$text" in /* | '') return 1 ;; esac
  rest=${entry#"$root"/}
  rest=${rest//[!\/]/}
  depth=${#rest}  # depth of the link's directory below the root
  rest=$text/
  while [ -n "$rest" ]; do
    part=${rest%%/*}
    rest=${rest#*/}
    case "$part" in
      '' | .) ;;
      ..) depth=$((depth - 1)); [ "$depth" -ge 0 ] || return 1 ;;
      *) depth=$((depth + 1)) ;;
    esac
  done
  target=$(realpath -e -- "$entry" 2>/dev/null) || return 1
  case "$target" in "$root"/*) ;; *) return 1 ;; esac
  [ -f "$entry" ]
}

trusted_tree() {  # directory: see the trust rules at the top
  local root=$1 foreign
  [ -d "$root" ] && [ ! -L "$root" ] || return 1
  root=$(realpath -e -- "$root") || return 1
  foreign=$(find "$root" \( ! -user "$uid" -o \( ! -type l -perm /022 \) \) -print -quit) || return 1
  [ -z "$foreign" ] || return 1
  # pipefail: a find error or any failing link rejects the tree.
  find "$root" -type l -print0 | while IFS= read -r -d '' entry; do
    link_inside "$root" "$entry" || exit 1
  done
}

node_npm() {  # the npm inside the Node tree, never another npm on PATH
  PATH="$node_dir/bin:$PATH" "$node_dir/bin/npm" "$@"
}

install_node() {
  if { [ -e "$node_dir" ] || [ -L "$node_dir" ]; } && ! trusted_tree "$node_dir"; then
    log "replacing $node_dir: it breaks the ownership, permission or symlink rules"
  elif [ -x "$node_dir/bin/node" ] && [ "$("$node_dir/bin/node" --version)" = "v$NODE_VERSION" ] &&
    [ "$(node_npm --version)" = "$NPM_VERSION" ]; then
    log "Node $NODE_VERSION with npm $NPM_VERSION already installed"
    return
  fi
  log "installing Node $NODE_VERSION"
  download "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz" "$work/node.tar.xz"
  verify_sha256 "$work/node.tar.xz" "$NODE_SHA256" "Node archive"
  rm -rf -- "$node_dir"
  run "$work" - tar --no-same-owner --no-same-permissions -xJf "$work/node.tar.xz" -C "$prefix"
  log "installing npm $NPM_VERSION"
  download "https://registry.npmjs.org/npm/-/npm-$NPM_VERSION.tgz" "$work/npm.tgz"
  local integrity
  integrity=$("$node_dir/bin/node" -e 'const c=require("crypto"),f=require("fs");process.stdout.write("sha512-"+c.createHash("sha512").update(f.readFileSync(process.argv[1])).digest("base64"))' "$work/npm.tgz")
  [ "$integrity" = "$NPM_INTEGRITY" ] || die "npm tarball SHA-512 mismatch"
  run "$work" "$work/npm-install.log" env PATH="$node_dir/bin:$PATH" "$node_dir/bin/npm" install \
    --global --prefix "$node_dir" --offline --no-audit --no-fund --loglevel=error "$work/npm.tgz" || {
    tail -n 40 "$work/npm-install.log" >&2
    die "npm install failed"
  }
}

install_python() {
  # --version succeeds even without a standard library, so an interrupted
  # install is detected by importing the required modules. -I keeps
  # PYTHONPATH, the working directory and user site-packages out of the check.
  if { [ -e "$python_dir" ] || [ -L "$python_dir" ]; } && ! trusted_tree "$python_dir"; then
    log "replacing $python_dir: it breaks the ownership, permission or symlink rules"
  elif [ -x "$python_dir/bin/python3.12" ] &&
    [ "$("$python_dir/bin/python3.12" --version)" = "Python $PYTHON_VERSION" ] &&
    "$python_dir/bin/python3.12" -I -c "$PYTHON_MODULES" 2>/dev/null; then
    log "Python $PYTHON_VERSION already installed"
    return
  fi
  log "building Python $PYTHON_VERSION (about two minutes)"
  download "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz" "$work/python.tgz"
  verify_sha256 "$work/python.tgz" "$PYTHON_SHA256" "Python source"
  run "$work" - tar --no-same-owner --no-same-permissions -xzf "$work/python.tgz" -C "$work"
  rm -rf -- "$python_dir"
  local step
  for step in configure make install; do
    case "$step" in
      configure) set -- ./configure --prefix="$python_dir" --with-ensurepip=install --disable-test-modules ;;
      make) set -- make -j"$(nproc)" ;;
      install) set -- make install ;;
    esac
    run "$work/Python-$PYTHON_VERSION" "$work/python-$step.log" "$@" || {
      tail -n 40 "$work/python-$step.log" >&2
      die "Python $step failed"
    }
  done
  "$python_dir/bin/python3.12" -I -c "$PYTHON_MODULES" \
    || die "Python is missing a required standard-library module"
}

install_node
install_python

trusted_tree "$node_dir" && trusted_tree "$python_dir" \
  || die "installed toolchain breaks the ownership, permission or symlink rules"
node_version=$("$node_dir/bin/node" --version)
npm_version=$(node_npm --version)
python_version=$("$python_dir/bin/python3.12" --version)
[ "$node_version" = "v$NODE_VERSION" ] || die "unexpected Node version"
[ "$npm_version" = "$NPM_VERSION" ] || die "unexpected npm version"
[ "$python_version" = "Python $PYTHON_VERSION" ] || die "unexpected Python version"

if [ "$link" = true ]; then
  for tool in node npm npx; do
    ln -sfn "$node_dir/bin/$tool" "$link_dir/$tool"
  done
  ln -sfn "$python_dir/bin/python3.12" "$link_dir/python3.12"
  log "linked node, npm, npx and python3.12 into $link_dir"
else
  log "add to PATH: $node_dir/bin:$python_dir/bin"
fi
log "ready: node $node_version, npm $npm_version, $python_version"
