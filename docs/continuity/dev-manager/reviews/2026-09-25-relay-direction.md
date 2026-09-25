# Nathan's direction: reports in the repository, messages relayed by hand

- **Source:** Nathan Amthor, in the Dev Manager session on 25 September 2026.
- **Consultation ID:** none. This is owner input.

## The direction, word for word

> "create a message for relay, that is how we should do things, reports in repo and messages to relay manually. Make note"

## What it means for the Dev Manager relay

- **Reports stay in the repository.** The Dev Manager writes every report, and every record of owner input it receives, as a file in `docs/continuity/dev-manager/reviews/` on `claude/dev-manager`, ending with `Status: complete`. That is unchanged.
- **Nathan carries the messages.** When the Dev Manager has something for the primary manager, it gives Nathan a short, paste-ready relay message that names the report files and the branch commit. Nathan pastes it into the primary manager's session. The primary manager does not have to discover reports by watching the branch.
- **The other direction is unchanged:**
  - the primary manager's consultations to the Dev Manager still carry an ID, a basis commit and the questions;
  - when Nathan relays them by hand, they follow the same form.
- **Relay messages are pointers, not records.** Everything a message refers to is already in a pushed file, so nothing exists only in a chat.

## Documents the primary manager should update

- **The owner-direction register:** a new row for this direction, quoting it.
- **`docs/planning/dev-manager.md`, "The relay":** Nathan relays messages by hand in both directions; reports stay in `reviews/`. The Dev Manager ends each answer with a paste-ready relay message for Nathan. The branch-watching line in "Continuity" becomes a fallback, not the channel.
- **`docs/planning/manager-workflow.md`:** the Dev Manager paragraph, to match.
- **`docs/planning/start-prompts/dev-manager.md`:** say that the answer includes a relay message for Nathan.
- **Scheduled cross-session messages:** DM-03 arrived as one. Whether the primary manager may still use them, or whether all relay is now by hand, is Nathan's to confirm. On this direction's wording, I read it as by hand.

## The first relay message under this direction

It is given to Nathan in the session, and reproduced here:

> **From the Dev Manager to App Manager 3 (relayed by Nathan, 25 September 2026)**
>
> Four files are on `claude/dev-manager` at `2beb86d` and later. Please integrate them with your next records batch and record the dispositions:
>
> 1. `docs/continuity/dev-manager/reviews/2026-09-25-dm-03-governing-read-and-i1-review-prompt.md` (`23951c4`): the DM-03 answer.
>    - Before PR26 merges: G1 and G2.
>    - Before Nathan runs the I1 review prompt: R1 and R2 (re-check the configuration after the runs; report the Stream system user, and don't delete it).
>    - Before the I2b prompt is written: E1 (the brief's `.github/` contradiction).
> 2. `docs/continuity/dev-manager/reviews/2026-09-25-owner-answers-to-dm-01-dm-02.md` (`574ee0e`): Nathan's word-for-word answers to all ten DM-01 and DM-02 questions, with what each changes. **Do not ask him those questions again.** The main changes:
>    - the S15 exceptions are confirmed;
>    - a CI-only PostgreSQL proof is approved before P06.2, as a plan amendment;
>    - the app gets a separate logical database on HDE's PostgreSQL service;
>    - WordPress hosts the sales page and the staff tools, through scoped Django APIs;
>    - the flake is investigated now;
>    - there is no paid GitHub plan.
> 3. `docs/continuity/dev-manager/reviews/2026-09-25-owner-answers-addendum.md` (`2beb86d`):
>    - the Stream secret is yours to explore; bring Nathan a plain-language recommendation before I2a;
>    - Nathan holds every human role, including the HDE owner. Write the HDE contract-requirements document for him to take into HDE's own process.
> 4. `docs/continuity/dev-manager/reviews/2026-09-25-relay-direction.md` (this commit): Nathan's direction that reports stay in the repository and messages are relayed by hand. Record it in the register and the charter.

Status: complete
