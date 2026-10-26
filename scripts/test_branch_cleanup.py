"""Exercise the cleanup's selection on real Git histories with a bare remote (M04)."""

import contextlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest import mock
import urllib.error
import urllib.parse

import branch_cleanup
from branch_cleanup import cell, deletes, main

TOKEN = "test-token-0123456789abcdef"
# D5, by name: the test checks these, not the script's own list.
KEEP = ("main", "claude/magical-wozniak-yfmmx2", "claude/dev-manager")
ROW = re.compile(r"^\| ` (\S+) ` \| `([0-9a-f]{40})` \| ([a-z ]+) \| (.*) \|$")


def pr(number, head, base="main"):
    return {"number": number, "head": {"ref": head}, "base": {"ref": base}}


class Page:
    def __init__(self, body, link, status=200):
        self.body, self.headers, self.status = body, {"Link": link}, status

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class BranchCleanupTests(unittest.TestCase):
    def setUp(self):
        self.old = os.getcwd()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = {
            "PATH": os.environ.get("PATH", os.defpath),
            "HOME": self.temp.name,
            "LANG": "C.UTF-8",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        self.remote = self.root / "remote.git"
        self.git("init", "-q", "--bare", "--initial-branch=main", str(self.remote), cwd=self.root)
        self.work = self.repo("work")
        os.chdir(self.work)
        self.summary = self.root / "summary.md"
        self.requests = []
        # main has two commits; "merged" branches sit at the first, behind main.
        self.base = self.new_commit(None, "base")
        self.main = self.new_commit(self.base, "main advances")
        self.push(self.main, "main")

    def tearDown(self):
        os.chdir(self.old)
        self.temp.cleanup()

    def git(self, *args, cwd=None, check=True, input=None):
        result = subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True, input=input)
        if check and result.returncode:
            raise AssertionError(f"git {args} failed: {result.stderr}")
        return result.stdout.strip()

    def repo(self, name):
        path = self.root / name
        self.git("init", "-q", "--initial-branch=main", str(path), cwd=self.root)
        self.git("config", "user.email", "test@example.invalid", cwd=path)
        self.git("config", "user.name", "Test", cwd=path)
        self.git("remote", "add", "origin", str(self.remote), cwd=path)
        return path

    def new_commit(self, parent, message, cwd=None):
        tree = self.git("hash-object", "-t", "tree", "-w", "--stdin", cwd=cwd, input="") if parent is None else self.git("rev-parse", f"{parent}^{{tree}}", cwd=cwd)
        return self.git("commit-tree", tree, *(["-p", parent] if parent else []), "-m", message, cwd=cwd)

    def push(self, sha, name, cwd=None):
        self.git("push", "-q", "--force", "origin", f"{sha}:refs/heads/{name}", cwd=cwd)

    def remote_heads(self):
        lines = self.git("ls-remote", str(self.remote)).splitlines()
        return {ref.removeprefix("refs/heads/"): sha for sha, ref in (line.split("\t") for line in lines) if ref.startswith("refs/heads/")}

    def listing(self, pages, fail=None):
        def urlopen(request, timeout):
            self.requests.append(request)
            page = int(urllib.parse.parse_qs(urllib.parse.urlsplit(request.full_url).query)["page"][0])
            if fail and page in fail:
                return fail[page](request)
            link = f'<https://api.github.com/repositories/1/pulls?page={page + 1}>; rel="next"' if page < len(pages) else ""
            return Page(json.dumps(pages[page - 1]).encode(), link)

        return urlopen

    def cleanup(self, *argv, event="push", dry_run="", pages=([],), opener=None, **environ):
        env = {
            **self.env,
            "GITHUB_STEP_SUMMARY": str(self.summary),
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_TOKEN": TOKEN,
            "CLEANUP_EVENT": event,
            "CLEANUP_DRY_RUN": dry_run,
        }
        for key, value in environ.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(list(argv), environ=env, urlopen=opener or self.listing(pages))
        return code, output.getvalue()

    def rows(self):
        return {m[1]: (m[2], m[3], m[4]) for m in map(ROW.match, self.summary.read_text().splitlines()) if m}

    # Acceptance check 2: a merged branch is selected.
    def test_merged_branch_is_selected(self):
        self.push(self.base, "merged")
        self.push(self.main, "fresh")  # DM-32 1.4: a branch at a commit of main counts as merged
        code, _ = self.cleanup()
        self.assertEqual(code, 0)
        self.assertNotIn("merged", self.remote_heads())
        self.assertNotIn("fresh", self.remote_heads())
        self.assertEqual(self.rows()["merged"], (self.base, "deleted", "merged into main"))

    # Acceptance check 2: an unmerged branch is kept.
    def test_unmerged_branch_is_kept(self):
        unmerged = self.new_commit(self.base, "work not in main")
        self.push(unmerged, "unmerged")
        code, _ = self.cleanup()
        self.assertEqual(code, 0)
        self.assertIn("unmerged", self.remote_heads())
        self.assertEqual(self.remote_heads()["unmerged"], unmerged)
        self.assertEqual(self.rows()["unmerged"], (unmerged, "kept", "unmerged"))

    # Acceptance check 2: each keep-list name is kept while merged.
    def test_keep_list_names_are_kept_while_merged(self):
        for name in KEEP[1:]:
            self.push(self.base, name)
        code, _ = self.cleanup()
        self.assertEqual(code, 0)
        for name in KEEP:
            with self.subTest(name=name):
                self.assertIn(name, self.remote_heads())
                self.assertEqual(self.rows()[name][1:], ("kept", "keep-list"))

    # Acceptance check 2: the head and the base of an open PR are kept, including a
    # fork's same-named head.
    def test_open_pr_head_and_base_are_kept(self):
        for name in ["pr-head", "pr-base", "fork-head", "merged"]:
            self.push(self.base, name)
        fork = pr(8, "fork-head")
        fork["head"]["repo"] = {"full_name": "someone/fork"}
        code, _ = self.cleanup(pages=([pr(7, "pr-head", "pr-base"), fork],))
        self.assertEqual(code, 0)
        heads = self.remote_heads()
        for name, reason in [("pr-head", "open PR #7 (head)"), ("pr-base", "open PR #7 (base)"), ("fork-head", "open PR #8 (head)")]:
            with self.subTest(name=name):
                self.assertIn(name, heads)
                self.assertEqual(self.rows()[name][1:], ("kept", reason))
        self.assertNotIn("merged", heads)
        self.assertIn("| #7 | ` pr-head ` | ` pr-base ` |", self.summary.read_text())

    # Acceptance check 2: a branch moved after selection is kept, because the lease is
    # refused.
    def test_branch_moved_after_selection_is_kept_by_the_lease(self):
        self.push(self.base, "moved")
        self.push(self.base, "merged")
        moved_to = self.new_commit(self.base, "pushed after the selection")
        real = branch_cleanup.delete_branch

        def push_first(remote, name, sha, env):
            if name == "moved":
                self.push(moved_to, "moved")
            return real(remote, name, sha, env)

        with mock.patch.object(branch_cleanup, "delete_branch", push_first):
            code, _ = self.cleanup()
        self.assertEqual(code, 0)
        self.assertIn("moved", self.remote_heads())
        self.assertEqual(self.remote_heads()["moved"], moved_to)
        self.assertEqual(self.rows()["moved"], (self.base, "kept", "lease refused: moved since it was checked"))
        self.assertNotIn("merged", self.remote_heads())

    # Acceptance check 2: an unresolvable head is kept. Its commit was pushed from
    # another clone, so this checkout cannot test its ancestry.
    def test_unresolvable_head_is_kept(self):
        other = self.repo("other")
        foreign = self.new_commit(None, "never fetched here", cwd=other)
        self.push(foreign, "foreign", cwd=other)
        code, _ = self.cleanup()
        self.assertEqual(code, 0)
        self.assertIn("foreign", self.remote_heads())
        self.assertEqual(self.remote_heads()["foreign"], foreign)
        self.assertEqual(self.rows()["foreign"], (foreign, "kept", "unresolvable"))

    # Acceptance check 2 (DM-32 1.3): a failed PR listing deletes nothing.
    def test_failed_listing_deletes_nothing(self):
        full_page = [pr(n, f"other-{n}") for n in range(1, 101)]

        def http_error(request):
            raise urllib.error.HTTPError(request.full_url, 502, "Bad Gateway", {}, None)

        def url_error(request):
            raise urllib.error.URLError("connection refused")

        cases = {
            "HTTP error on page 2": dict(pages=(full_page, []), opener=self.listing((full_page, []), fail={2: http_error})),
            "network error on page 1": dict(opener=self.listing(([],), fail={1: url_error})),
            "not JSON": dict(opener=self.listing(([],), fail={1: lambda r: Page(b"<html>", "")})),
            "not a list": dict(opener=self.listing(([],), fail={1: lambda r: Page(b'{"message": "x"}', "")})),
            "an entry without a head": dict(pages=([{"number": 1, "base": {"ref": "main"}}],)),
            "an entry whose number is not an integer": dict(pages=([{**pr(1, "x"), "number": "1"}],)),
            "a status other than 200": dict(opener=self.listing(([],), fail={1: lambda r: Page(b"[]", "", status=204)})),
            "no token": dict(GITHUB_TOKEN=None),
            "no repository": dict(GITHUB_REPOSITORY=None),
            "endless pages": dict(pages=[[]] * (branch_cleanup.MAX_PAGES + 1)),
        }
        for label, kwargs in cases.items():
            with self.subTest(label):
                self.push(self.base, "merged")
                self.summary.write_text("")
                code, _ = self.cleanup(**kwargs)
                self.assertEqual(code, 2)
                self.assertIn("merged", self.remote_heads())
                text = self.summary.read_text()
                self.assertIn("Refused, nothing deleted", text)
                self.assertNotIn("| deleted |", text)

    # Acceptance check 2 (DM-32 1.3): a two-page listing is read whole.
    def test_two_page_listing_is_read_whole(self):
        self.push(self.base, "second-page")
        self.push(self.base, "merged")
        pages = ([pr(n, f"other-{n}") for n in range(1, 101)], [pr(101, "second-page")])
        code, _ = self.cleanup(pages=pages)
        self.assertEqual(code, 0)
        self.assertEqual([urllib.parse.parse_qs(urllib.parse.urlsplit(r.full_url).query)["page"] for r in self.requests], [["1"], ["2"]])
        for request in self.requests:
            self.assertTrue(request.full_url.startswith("https://api.github.com/repos/owner/repo/pulls?state=open&per_page=100&"))
            self.assertEqual(request.unredirected_hdrs["Authorization"], f"Bearer {TOKEN}")
        self.assertEqual(self.rows()["second-page"][1:], ("kept", "open PR #101 (head)"))
        self.assertNotIn("merged", self.remote_heads())
        self.assertIn("### Open pull requests read: 101", self.summary.read_text())

    # Acceptance check 2 (DM-32 1.5): a run that fails midway has already written each
    # deletion's row, with its head, so the summary restores what it deleted.
    def test_failure_midway_has_written_each_deletion(self):
        for name in ["a-merged", "b-merged", "c-merged"]:
            self.push(self.base, name)
        real = branch_cleanup.delete_branch
        calls = []

        def lost_runner(remote, name, sha, env):
            calls.append(name)
            if len(calls) == 2:
                raise RuntimeError("runner lost")
            return real(remote, name, sha, env)

        with mock.patch.object(branch_cleanup, "delete_branch", lost_runner), self.assertRaises(RuntimeError):
            self.cleanup()
        heads = self.remote_heads()
        self.assertNotIn("a-merged", heads)
        self.assertIn("b-merged", heads)
        self.assertIn("c-merged", heads)
        self.assertIn("a-merged", self.rows())
        self.assertEqual(self.rows()["a-merged"], (self.base, "deleted", "merged into main"))

    # Acceptance check 2 (DM-32 1.7): on a dispatch, any dry_run value but an exact
    # "false" is a dry run; a push deletes.
    def test_dispatch_deletes_only_on_exact_false(self):
        for value in [None, "", "true", "True", "False", "FALSE", " false", "false ", "false\n", "0", "no", "off"]:
            with self.subTest(value=value):
                self.assertFalse(deletes("workflow_dispatch", value))
        self.assertTrue(deletes("workflow_dispatch", "false"))
        for value in [None, "", "true"]:
            self.assertTrue(deletes("push", value))
        for event in [None, "", "pull_request", "pull_request_target", "schedule", "workflow_run"]:
            self.assertFalse(deletes(event, "false"))
        self.assertFalse(deletes("push", "", forced_dry_run=True))
        self.push(self.base, "merged")
        code, _ = self.cleanup(event="workflow_dispatch", dry_run="False")
        self.assertEqual(code, 0)
        self.assertEqual(self.rows()["merged"][1], "would delete")
        self.assertIn("merged", self.remote_heads())
        code, _ = self.cleanup(event="workflow_dispatch", dry_run="false")
        self.assertEqual(code, 0)
        self.assertNotIn("merged", self.remote_heads())

    # Acceptance check 2: a dry run deletes nothing and selects the same set.
    def test_dry_run_deletes_nothing_and_selects_the_same_set(self):
        for name in ["merged-1", "merged-2", "pr-head", KEEP[1]]:
            self.push(self.base, name)
        self.push(self.new_commit(self.base, "unmerged"), "unmerged")
        pages = ([pr(3, "pr-head")],)
        before = self.remote_heads()
        selected = []
        for argv, event, dry_run in [((), "workflow_dispatch", "true"), (("--dry-run",), "push", "")]:
            self.summary.write_text("")
            code, _ = self.cleanup(*argv, event=event, dry_run=dry_run, pages=pages)
            self.assertEqual(code, 0)
            self.assertEqual(self.remote_heads(), before)
            self.assertIn("Mode: **dry run**", self.summary.read_text())
            selected.append({name for name, row in self.rows().items() if row[1] == "would delete"})
        self.summary.write_text("")
        code, _ = self.cleanup(pages=pages)
        self.assertEqual(code, 0)
        deleted = {name for name, row in self.rows().items() if row[1] == "deleted"}
        self.assertEqual(selected, [{"merged-1", "merged-2"}] * 2)
        self.assertEqual(deleted, {"merged-1", "merged-2"})
        self.assertEqual(set(before) - set(self.remote_heads()), deleted)

    # Acceptance check 2: a name with shell metacharacters is handled as data, in git's
    # arguments and in the summary's table.
    def test_names_with_shell_metacharacters_are_data(self):
        names = ["meta/$(touch${IFS}pwned)", "meta/a;touch${IFS}pwned2", "meta/x|y`z`", "meta/<b>&amp;'q\"", "-lead"]
        for name in names:
            self.push(self.base, name)
        code, _ = self.cleanup()
        for directory in [self.work, self.root]:
            self.assertEqual(list(directory.glob("pwned*")), [])
        self.assertEqual(code, 0)
        self.assertFalse(set(names) & set(self.remote_heads()))
        rows = [line for line in self.summary.read_text().splitlines() if line.startswith("| `") and self.base in line]
        self.assertEqual(len(rows), len(names))
        for name, line in zip(sorted(names), rows):
            with self.subTest(name=name):
                self.assertEqual(len(re.findall(r"(?<!\\)\|", line)), 5)
                self.assertTrue(line.startswith(f"| {cell(name)} |"))
        self.assertIn("| `` meta/x\\|y`z` `` |", self.summary.read_text())

    # D7: a failed remote read, or main's head missing or unresolvable, deletes nothing.
    def test_fails_closed_on_remote_and_main(self):
        self.push(self.base, "merged")
        other = self.repo("other")

        def no_remote():
            return self.cleanup("--remote", "nowhere")

        def option_remote():
            return self.cleanup("--remote", "--upload-pack=touch pwned")

        def no_main():
            self.git("update-ref", "-d", "refs/heads/main", cwd=self.remote)
            return self.cleanup()

        def foreign_main():
            self.push(self.new_commit(None, "main from elsewhere", cwd=other), "main", cwd=other)
            return self.cleanup()

        for case in [no_remote, option_remote, no_main, foreign_main]:
            with self.subTest(case.__name__):
                self.summary.write_text("")
                code, _ = case()
                self.assertEqual(code, 2)
                self.assertEqual(self.remote_heads()["merged"], self.base)
                self.assertIn("Refused, nothing deleted", self.summary.read_text())
                self.assertFalse(list(self.work.glob("pwned*")))

    # The open PRs file is for the pre-merge dry run only.
    def test_open_prs_file_is_for_dry_runs_only(self):
        self.push(self.base, "pr-head")
        self.push(self.base, "merged")
        listing = self.root / "open-prs.json"
        listing.write_text(json.dumps([pr(9, "pr-head")]))

        def no_api(request, timeout):
            raise AssertionError("the API was called")

        code, _ = self.cleanup("--open-prs-json", str(listing), opener=no_api)
        self.assertEqual(code, 2)
        self.assertIn("merged", self.remote_heads())
        self.summary.write_text("")
        code, _ = self.cleanup("--dry-run", "--open-prs-json", str(listing), opener=no_api)
        self.assertEqual(code, 0)
        self.assertEqual(self.rows()["pr-head"][1:], ("kept", "open PR #9 (head)"))
        self.assertEqual(self.rows()["merged"][1], "would delete")

    # A deletion the remote refuses is reported, the others go on, and the run fails.
    def test_refused_deletion_is_reported_and_fails_the_run(self):
        self.push(self.base, "guarded")
        self.push(self.base, "merged")
        hook = self.remote / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nif grep -q ' refs/heads/guarded$'; then echo 'deletion refused' >&2; exit 1; fi\n")
        hook.chmod(0o755)
        code, _ = self.cleanup()
        self.assertEqual(code, 1)
        self.assertIn("guarded", self.remote_heads())
        self.assertNotIn("merged", self.remote_heads())
        self.assertEqual(self.rows()["guarded"][1], "kept")
        self.assertTrue(self.rows()["guarded"][2].startswith("deletion failed: "))

    # D3 (DM-32 1.1): git gets the token from the environment only, and only for the
    # commands that reach the remote; it is in no argument, output, config or file.
    def test_token_reaches_git_only_through_the_environment(self):
        self.push(self.base, "merged")
        with mock.patch.object(branch_cleanup.subprocess, "run", wraps=subprocess.run) as run:
            code, output = self.cleanup()
        self.assertEqual(code, 0)
        self.assertNotIn("merged", self.remote_heads())
        commands = [(call.args[0], call.kwargs["env"]) for call in run.call_args_list]
        self.assertTrue(any("push" in command for command, _ in commands))
        for command, env in commands:
            self.assertFalse(any(TOKEN in arg for arg in command))
            reaches_remote = "ls-remote" in command or "push" in command
            self.assertEqual(env.get("GITHUB_TOKEN"), TOKEN if reaches_remote else None)
        self.assertNotIn(TOKEN, output)
        self.assertNotIn(TOKEN, self.summary.read_text())
        for path in self.root.rglob("*"):
            if path.is_file():
                self.assertNotIn(TOKEN.encode(), path.read_bytes(), path)
        # The helper hands the token to git when git asks, and nothing without it.
        fill = ["git", *branch_cleanup.NETWORK, "credential", "fill"]
        query = "protocol=https\nhost=example.invalid\n\n"
        given = subprocess.run(fill, input=query, capture_output=True, text=True, env={**self.env, "GITHUB_TOKEN": TOKEN, "GIT_TERMINAL_PROMPT": "0"})
        self.assertIn(f"username=x-access-token\npassword={TOKEN}\n", given.stdout)
        absent = subprocess.run(fill, input=query, capture_output=True, text=True, env={**self.env, "GIT_TERMINAL_PROMPT": "0"})
        self.assertNotEqual(absent.returncode, 0)
        self.assertNotIn("password=", absent.stdout)


if __name__ == "__main__":
    unittest.main()
