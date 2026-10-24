# The client-token question (D8), for Nathan

- **Owner:** App Manager 7. The Dev Manager read revision 1, with the costing in the [P06.2 brief](../planning/p06-2-chat-integration.md) ("The client-token question (D8)"), in DM-20 before it went to Nathan (OD-32); App Manager 7 gives this revision to Nathan as a DECISION NEEDED message.
- **Revision 2, 23 October 2026, applying DM-20 as written** ([report](../continuity/dev-manager/reviews/2026-10-23-dm-20-p06-2-b2-live-rows-and-d8.md), section 7, `ca806e3`), so it needs no further read (DM-03 G2). Revision 1 did not go to Nathan.
- **Why now:** DM-17 item 6 referred it to Nathan after B2's live rows and before Stage C's prompt; B2-C3 ran the live rows on 23 October.
- **Deletion condition:** prune when Nathan's answer is recorded in the owner-direction register and the brief.

---

**DECISION NEEDED: should the Glow app hold a Stream login token at all?**

**What it is.** Today's design gives each signed-in member's app a Stream token that lasts one hour and can only read their own match conversations. Everything they see is still drawn by Glow, and every message they send goes through Glow's server first, where block and unmatch are enforced.

**What happened.** Between 27 September and 23 October, Stream quietly added four things to our test account that such a token could use:

- scheduling a message into the match conversation without going through Glow's checks;
- two new kinds of voice and video call that the token could start or join;
- another kind of chat room.

We found them up to 26 days later and removed them, and they were still removed at the end of that evening's test run. But Stream can add more at any time without telling us. Each time, a token in someone's app could use the new feature until we notice.

**The two options.**

- **(a) Keep the token, and watch for changes.** Glow checks Stream's settings before every release and on a schedule, alerts us when something changes, and can cut off every token at once.
  - **What it costs:** the Stream chat library in the app; at launch, the token service, the checks and alerts, and the cut-off procedure.
  - **What stays open:** the gap between Stream adding something and us catching it. Checks shorten that gap; they cannot close it.
- **(b) No token in the app.** The app talks only to Glow. Glow also delivers conversation history and new messages to the app itself.
  - **What it closes:** any way for a member's app to use a Stream change, because the app never holds a Stream login. We still check Stream's settings, since Glow's server uses them, but a missed change no longer reaches members' apps.
  - **What it costs:**
    - about one more build session, with its review, before launch (history and live updates through Glow);
    - at launch, one more server process for live updates, to run and pay for. As a lighter start, notifications plus the app checking for new messages every few seconds while a conversation is open.

    It also makes the Stream library in the app and the token service unnecessary.
  - **What stays open:**
    - Glow's own checks alone decide who can see a conversation; today Stream's membership also enforces it.
    - Whether Stream is still worth its cost when only our server uses it, and how Stream counts users for billing then, are later questions, not part of this one.

**What breaks if this is not decided:** nothing already built; the server-side chat work merges either way. The next stage, the chat screens in the app, is built differently under (a) and (b), so its prompt waits for this answer.

**Recommendation: (b).** The Dev Manager recommends it too. It removes this risk instead of narrowing it, for roughly one extra build session and one more service. If you choose (a), you are accepting that the gap stays open between a Stream change and our check.

**Your answer:** "(a)" or "(b)", plus anything you want weighed.
