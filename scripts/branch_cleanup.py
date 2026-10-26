"""Delete remote branches whose commits are all in main (M04). Standard library only.

Its only network use is `git` against the remote and GitHub's listing of open PRs. It
runs no repository code. Every read fails closed: if the open PRs, the remote's
branches or main's head cannot be read, nothing is deleted and the run fails.
"""

import argparse
import http.client
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request


# D5: the keep-list is held on main, so a change to it is full scope. The manager and
# Dev Manager branches are always fully merged after integration (DM-13 item 10).
MAIN = "main"
KEEP = (MAIN, "claude/magical-wozniak-yfmmx2", "claude/dev-manager")

API = "https://api.github.com"
PER_PAGE = 100
MAX_PAGES = 50
SHA = re.compile(r"[0-9a-f]{40}")
REPOSITORY = re.compile(r"[A-Za-z0-9-]+/[A-Za-z0-9._-]+")

# D3: git gets the token only from the environment. The helper's text names the
# variable, not its value, and the empty helper before it drops every helper configured
# earlier, so none of them is handed the token to store. The token never goes into an
# argument, a file, git config or any output.
CREDENTIAL_HELPER = (
    '!f() { test "$1" = get && test -n "$GITHUB_TOKEN" && '
    'printf "username=x-access-token\\npassword=%s\\n" "$GITHUB_TOKEN"; }; f'
)
NETWORK = ("-c", "credential.helper=", "-c", "credential.helper=" + CREDENTIAL_HELPER)


class Refused(Exception):
    """A read failed or a precondition did not hold: delete nothing."""


def git(args, env, network=False):
    # Names are data: every value is one list element, and no shell is involved. Only
    # the commands that reach the remote get the token's variable.
    command = ["git", *(NETWORK if network else ()), *args]
    if not network:
        env = {key: value for key, value in env.items() if key != "GITHUB_TOKEN"}
    return subprocess.run(command, env=env, capture_output=True, check=False)


def diagnostic(result, env):
    """git's last error line, for the log; the token, were it ever there, is masked."""
    lines = [line for line in result.stderr.decode("utf-8", errors="replace").splitlines() if line.strip()]
    text = lines[-1] if lines else f"git status {result.returncode}"
    token = env.get("GITHUB_TOKEN")
    return text.replace(token, "***") if token else text


def deletes(event, dry_run_input, forced_dry_run=False):
    """D8 (DM-32 1.7): a push deletes; a dispatch deletes only on an exact "false"."""
    if forced_dry_run:
        return False
    if event == "push":
        return True
    if event == "workflow_dispatch":
        return dry_run_input == "false"
    return False


def pr_entries(items):
    if not isinstance(items, list):
        raise Refused("a page of open PRs is not a list")
    entries = []
    for item in items:
        number = item.get("number") if isinstance(item, dict) else None
        head = item.get("head") if isinstance(item, dict) else None
        base = item.get("base") if isinstance(item, dict) else None
        head_ref = head.get("ref") if isinstance(head, dict) else None
        base_ref = base.get("ref") if isinstance(base, dict) else None
        if type(number) is not int or not all(isinstance(r, str) and r for r in (head_ref, base_ref)):
            raise Refused("an open PR has no number, head or base")
        entries.append((number, head_ref, base_ref))
    return entries


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def _open(request, timeout):
    return urllib.request.build_opener(_NoRedirect).open(request, timeout=timeout)


def has_next(link):
    return any(re.search(r';\s*rel="next"', part) for part in (link or "").split(","))


def read_open_prs(repository, token, urlopen=_open):
    """DM-32 1.3: every page, until GitHub links no next page; any error refuses."""
    if not token:
        raise Refused("GITHUB_TOKEN is not set, so the open PRs cannot be read")
    if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
        raise Refused("GITHUB_REPOSITORY is missing or malformed")
    entries = []
    for page in range(1, MAX_PAGES + 1):
        request = urllib.request.Request(
            f"{API}/repos/{repository}/pulls?state=open&per_page={PER_PAGE}&page={page}",
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "glow-branch-cleanup",
            },
        )
        request.add_unredirected_header("Authorization", f"Bearer {token}")
        try:
            with urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise Refused(f"open PRs, page {page}: HTTP {response.status}")
                body = response.read()
                link = response.headers.get("Link", "")
            items = json.loads(body)
        except Refused:
            raise
        except (OSError, ValueError, http.client.HTTPException) as error:  # urllib's errors are OSErrors
            raise Refused(f"open PRs, page {page}: {type(error).__name__}") from None
        entries += pr_entries(items)
        if not has_next(link):
            return entries
    raise Refused(f"open PRs: more than {MAX_PAGES} pages")


def read_prs_file(path):
    try:
        with open(path, encoding="utf-8") as source:
            return pr_entries(json.load(source))
    except (OSError, ValueError) as error:
        raise Refused(f"open PRs file: {type(error).__name__}") from None


def read_heads(remote, env):
    result = git(["ls-remote", remote], env, network=True)
    if result.returncode != 0:
        raise Refused(f"git ls-remote failed: {diagnostic(result, env)}")
    heads = {}
    try:
        lines = result.stdout.decode("utf-8", errors="strict").splitlines()
    except UnicodeError:
        raise Refused("git ls-remote printed a name that is not UTF-8") from None
    for line in lines:
        sha, tab, ref = line.partition("\t")
        if not tab or not SHA.fullmatch(sha):
            raise Refused("git ls-remote printed an unexpected line")
        if ref.startswith("refs/heads/"):
            heads[ref.removeprefix("refs/heads/")] = sha
    if MAIN not in heads:
        raise Refused("the remote has no main branch")
    return heads


def resolve_main(sha, env):
    if git(["cat-file", "-e", f"{sha}^{{commit}}"], env).returncode != 0:
        raise Refused("main's current head is not a commit in this checkout")


def merged(sha, main_sha, env):
    """True if the head is an ancestor of main, False if not, None if unresolvable."""
    status = git(["merge-base", "--is-ancestor", sha, main_sha], env).returncode
    return True if status == 0 else False if status == 1 else None


def decide(name, sha, main_sha, protected, env):
    if name in KEEP:
        return "keep", "keep-list"
    if name in protected:
        return "keep", "open PR " + ", ".join(protected[name])
    is_merged = merged(sha, main_sha, env)
    if is_merged is None:
        return "keep", "unresolvable"
    if not is_merged:
        return "keep", "unmerged"
    return "delete", "merged into main"


def delete_branch(remote, name, sha, env):
    """D6: delete only at the checked head; a refused lease keeps the branch."""
    ref = "refs/heads/" + name
    result = git(["push", "--porcelain", "--no-verify", f"--force-with-lease={ref}:{sha}", remote, ":" + ref], env, network=True)
    if result.returncode == 0:
        return "deleted", "merged into main", True
    if b"stale info" in result.stdout:
        return "kept", "lease refused: moved since it was checked", True
    return "kept", f"deletion failed: {cell(diagnostic(result, env))}", False


def cell(text):
    """Branch names are data: one code span per cell, with the table's pipe escaped."""
    text = "".join(c if c.isprintable() else f"\\u{ord(c):04x}" for c in text)
    fence = "`" * (max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    return f"{fence} {text} {fence}".replace("|", "\\|")


class Summary:
    """DM-32 1.5: each line is appended and closed at once, so it survives a failure."""

    def __init__(self, path):
        self.path = path

    def write(self, *lines):
        text = "".join(line + "\n" for line in lines)
        sys.stdout.write(text)
        sys.stdout.flush()
        if self.path:
            with open(self.path, "a", encoding="utf-8") as summary:
                summary.write(text)


def main(argv=None, environ=None, urlopen=_open):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--dry-run", action="store_true", help="decide and report, but delete nothing")
    parser.add_argument("--open-prs-json", help="read the open PRs from this file; dry run only")
    args = parser.parse_args(argv)
    environ = dict(os.environ if environ is None else environ)
    env = {**environ, "GIT_TERMINAL_PROMPT": "0"}
    summary = Summary(environ.get("GITHUB_STEP_SUMMARY"))
    event = environ.get("CLEANUP_EVENT", "")
    deleting = deletes(event, environ.get("CLEANUP_DRY_RUN"), args.dry_run)
    summary.write("## Branch cleanup", "", f"- Mode: **{'delete' if deleting else 'dry run'}** (event {cell(event) if event else 'none'})")
    try:
        if args.remote.startswith("-"):
            raise Refused("the remote's name starts with '-'")
        if args.open_prs_json and deleting:
            raise Refused("--open-prs-json is accepted only in a dry run")
        heads = read_heads(args.remote, env)
        main_sha = heads[MAIN]
        resolve_main(main_sha, env)
        if args.open_prs_json:
            prs = read_prs_file(args.open_prs_json)
        else:
            prs = read_open_prs(environ.get("GITHUB_REPOSITORY"), environ.get("GITHUB_TOKEN"), urlopen)
    except Refused as refusal:
        summary.write(f"- **Refused, nothing deleted:** {cell(str(refusal))}")
        return 2
    protected = {}
    for number, head, base in prs:
        protected.setdefault(head, []).append(f"#{number} (head)")
        protected.setdefault(base, []).append(f"#{number} (base)")
    decisions = [(name, sha, *decide(name, sha, main_sha, protected, env)) for name, sha in sorted(heads.items())]
    summary.write(
        f"- `main`: `{main_sha}`",
        "- Restore a deleted branch from its row: `git push origin <head>:refs/heads/<branch>`.",
        "",
        f"### Open pull requests read: {len(prs)}",
        "",
        "| PR | Head | Base |",
        "|---|---|---|",
        *(f"| #{number} | {cell(head)} | {cell(base)} |" for number, head, base in prs),
        "",
        "### Branches",
        "",
        "| Branch | Head | Decision | Reason |",
        "|---|---|---|---|",
    )
    failed = False
    for name, sha, action, reason in decisions:
        decision = "kept"
        if action == "delete":
            decision = "would delete"
            if deleting:
                decision, reason, ok = delete_branch(args.remote, name, sha, env)
                failed |= not ok
        summary.write(f"| {cell(name)} | `{sha}` | {decision} | {reason} |")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
