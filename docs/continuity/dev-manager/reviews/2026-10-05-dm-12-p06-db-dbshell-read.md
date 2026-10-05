# DM-12 — `dbshell` and condition 2.2

- **Consultation:** DM-12, revision 1, from App Manager 5, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `16c94500eb6a008d7466f84a3dffa7f150dbdc9c`, the head of `claude/magical-wozniak-yfmmx2` (PR28, a draft) when I fetched it. **This read covers that commit** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway, and ran nothing from the proof.

## 1. What I read

**At `16c9450`:**

- the README's "The run's marker" and "Limits";
- the brief's diff since `dd67696`: revision 6's status line, the F1 note under DM-10's 2.2 in D1, "Sessions", and "Carried to P06.2" item 6;
- `glow_ordering_proof/marker.py`'s module docstring, `install`, `RefusedDatabase` and `_refuse`;
- the CI policy's diff since `ee25d1d`, the only governing change in that range, which I confirmed;
- the register's OD-17 row.

**From the consultation:** F1's mechanism, as C2's exact-head review gives it and the manager verified it. I did not read Django's source for this read; section 7 says so.

**Notion, read-only, about 11:34 UTC on 5 October:**

- *Implementation Control*, matched to `16c9450`;
- *Dev Manager — reviews and approvals*;
- the register copy, matched to `16c9450`;
- the Work Register's P06.DB row;
- the uses-table rows for C2 (revisions 1 and 2) and C2's exact-head review.

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 F1's classification | **Approved:** outside the correction classes. No C3 before the merge |
| 2 The README's rule, the brief's note and item 6 | **Approved with conditions:** the README's rule and the brief's note as written. Item 6 changes from "optional" to "before P06.2's first run of the suite on any database", alongside the R2 guard, in the words below |
| 3 The CI policy's sentence | **Confirmed:** my DM-10 item 4, word for word |
| 4 Notion | **Matches `16c9450`** |

Nothing blocks PR28 going ready for Codex. The words in item 2 are records changes and need no further read. No item is Nathan's.

## 3. Findings

### Item 1 — F1 is outside the correction classes: approved

**What 2.2 was for.** CX3's harm was that the proof's own documented first command, `migrate`, changed a misdirected database by itself. Condition 2.2 makes every connection the proof's settings open through Django check the marker first, so that no proof command reaches an unmarked database. C2's exact-head review confirmed that this holds, and the code shows it:

- `marker.install` registers the check on `connection_created` from the settings;
- `RefusedDatabase` is deliberately not a `DatabaseError`, so no command can swallow it.

**What `dbshell` is.** It is not one of the proof's commands, and no job step or documented step runs it. It starts the interactive client `psql` as a separate program and does nothing to any database by itself. A change happens only if a person both points the proof's variables at the wrong server and then types a statement into `psql`. That is the same as opening `psql` on that server directly, which no guard in the proof can prevent.

So the nearest class, "let the job or the proof connect to anything but its own disposable database", is not met: neither the job nor any proof command connects anywhere unchecked. Correcting before the merge would cost a pass, a review and a Codex round for a path no proof command uses.

**My part.** My heading for 2.2 said "wired so no command can skip it". What I meant, and what the condition's body specifies, is the connection path through Django. I did not name `dbshell`, the one Django command that bypasses that path. The review was right to test the heading literally. The README's new rule now says exactly what is checked and what is not.

### Item 2 — The README's rule, the brief's note and item 6: approved with conditions

**The README's rule** ("The run's marker" and "Limits"): approved as written. It is accurate in both places:

- every connection the proof's settings open through Django is checked;
- `dbshell` starts `psql` outside Django, is not checked, and is never run with the proof's settings.

**The brief's note under DM-10's 2.2:** approved, apart from the word "optional", which follows item 6 below.

**Item 6: required for P06.2, not optional.** P06.2's sessions will use the proof's settings for local iteration before CI (D4), as R2's guard anticipates. In those sessions, `dbshell` is the one Django command that reaches a database unchecked. A refusing `dbshell` makes "no command under the proof's settings reaches a database unchecked" true in code rather than by a README rule, which is the standard CX3 set.

It costs P06.2 one small change in the pass that already lands the R2 guard. One design note: a proof-local management command needs the proof package to be an installed app, which today it is not (`INSTALLED_APPS` lists `contenttypes`, `auth` and `glow_persistence`). P06.2's brief should choose the mechanism; nothing here requires it now.

**Words.**

- **The brief's "Carried to P06.2", item 6.** Replace it with:

  > 6. **`dbshell` refused** (F1; DM-12). Before P06.2's first run of the suite on any database, local or CI, with the reused-database guard (item 1): `dbshell` under the proof's settings refuses with the marker's refusal, with an offline test, so that no command under the proof's settings reaches a database unchecked.

- **In the brief's F1 note under 2.2, in "Sessions" and in the README's "Limits" line,** replace "carried to P06.2 as optional" with "carried to P06.2, before its first run of the suite on any database (item 6; DM-12)".

These are records in non-governing files. Applied as written, they need no further read.

### Item 3 — The CI policy's sentence: confirmed

At `16c9450`, the sentence that begins "The one database is P06.DB's" contains, after "keeps in files readable only by the job's user;", exactly the words of my DM-10 item 4: "every proof command refuses, before any other statement, a database whose comment is not the run's marker, a value the job generates and masks, and a step shows a wrong marker refused, with the database left without a table, before the migrations run;". It is the only change to a governing file between `ee25d1d` and `16c9450`, so it needs no further read (G2).

It stays accurate after F1, because `dbshell` is not a proof command.

### Item 4 — Notion: matches `16c9450`

- ***Implementation Control*** is matched to `16c9450`, which records C2's exact-head review, its record fixes and DM-12. It names brief revision 6.
- ***Dev Manager — reviews and approvals*** has DM-10's and DM-11's dispositions, matching the review log (DM-11's notes the 2.3 query as my error, and AM5-19), and DM-12 pending. My session row runs through DM-11, merged at `a9eae28`.
- **The register copy** is matched to `16c9450`. OD-17's state matches the repository through "before PR28 goes ready for Codex".
- **The Work Register** has one P06.DB row, "In progress". Its text matches through C2's review, F1 "carries an optional guard to P06.2", and "Next: DM-12". When item 2 above is applied, the word "optional" there changes too.
- **The uses table** matches the prompt headers:
  - C2 revision 1: 1.92, not run, superseded;
  - C2 revision 2: 2.03, pick "not recorded", as its header says;
  - C2's exact-head review: 2.83, picked Opus 5.5 at extra high.

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 | Approved: F1 is outside the correction classes; no C3 |
| 2 | Approved with conditions: item 6 required before P06.2's first run, in the words above |
| 3 | Confirmed |
| 4 | Notion matches `16c9450` |

## 5. Questions for Nathan

None.

## 6. Documentation to update

- **The brief:** item 6, the F1 note and "Sessions", in item 2's words.
- **The README:** the "Limits" line, in item 2's words.
- **Notion:** the P06.DB row's "optional".
- **The review log:** DM-12's disposition. Record there that 2.2's heading was mine and overstated.

## 7. Limits

- **Django's `dbshell` behavior** is taken from C2's exact-head review and the manager's verification (`client.py`, `base/client.py:23` to `28`). I did not read Django's source in this read.
- **Notion:** the pages in section 1 only.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 5's session

> **From Dev Manager 2 to App Manager 5 (relayed by Nathan, 5 October 2026)**
>
> DM-12 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-10-05-dm-12-p06-db-dbshell-read.md`. My read covers `16c9450`. Nothing blocks PR28 going ready for Codex, and no item is Nathan's.
>
> **1. F1: outside the correction classes; no C3.** 2.2 covers every connection the proof's settings open through Django, and the review confirmed that holds. `dbshell` is no proof command and changes nothing by itself. 2.2's heading, "no command can skip it", was mine and overstated what the condition's body requires.
>
> **2. The README's rule and the brief's note: approved. Item 6: required, not optional.** Replace "Carried to P06.2" item 6 with:
>
> "6. **`dbshell` refused** (F1; DM-12). Before P06.2's first run of the suite on any database, local or CI, with the reused-database guard (item 1): `dbshell` under the proof's settings refuses with the marker's refusal, with an offline test, so that no command under the proof's settings reaches a database unchecked."
>
> In the F1 note under 2.2, in "Sessions" and in the README's "Limits" line, replace "carried to P06.2 as optional" with "carried to P06.2, before its first run of the suite on any database (item 6; DM-12)". Note for P06.2's brief: a proof-local command needs the package as an installed app, which it is not today.
>
> These are records changes and need no further read.
>
> **3. The CI policy's sentence:** confirmed, my DM-10 item 4 word for word.
>
> **4. Notion** matches `16c9450`. The P06.DB row's "optional" changes with item 2.

Status: complete
