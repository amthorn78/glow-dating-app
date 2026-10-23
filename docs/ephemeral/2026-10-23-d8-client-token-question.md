# The client-token question (D8), for Nathan

- **Owner:** App Manager 7. The Dev Manager reads this message, with the costing in the [P06.2 brief](../planning/p06-2-chat-integration.md) ("The client-token question (D8)"), in DM-20 before it goes to Nathan (OD-32). Then App Manager 7 gives it to Nathan as a DECISION NEEDED message.
- **Revision 1, 23 October 2026.**
- **Why now:** DM-17 item 6 referred it to Nathan after B2's live rows and before Stage C's prompt; B2-C3 ran the live rows on 23 October.
- **Deletion condition:** prune when Nathan's answer is recorded in the owner-direction register and the brief.

---

**DECISION NEEDED: should the Glow app hold a Stream login token at all?**

**What it is.** Today's design gives each signed-in member's app a short-lived Stream token that can only read their own match conversations. Everything they see is still drawn by Glow, and every message they send goes through Glow's server first, where block and unmatch are enforced.

**What happened.** Between 27 September and 23 October, Stream quietly added four things to our test account that such a token could use: scheduling a message into the match conversation without going through Glow's checks, starting or joining voice and video calls, and a second kind of chat room. We found them up to 26 days later, removed them, and the removals held. But Stream can add more at any time without telling us, and each time a token in someone's app could use the new feature until we notice.

**The two options.**

- **(a) Keep the token, and watch for changes.** Glow checks Stream's settings before every release and on a schedule, alerts us when something changes, and can cut off every token at once. **What stays open:** the gap between Stream adding something and us catching it. Checks shorten that gap; they cannot close it.
- **(b) No token in the app.** The app talks only to Glow. Glow also delivers conversation history and new messages to the app itself. **What it closes:** every way a Stream change could reach a member, permanently. **What it costs:** about one more build session before launch (history and live updates through Glow), and at launch one more small server process for live updates (or, as a lighter start, notifications plus the app checking for new messages every few seconds while a conversation is open). It also makes the planned Stream mobile library unnecessary.

**What breaks if this is not decided:** nothing already built; the server-side chat work merges either way. The next stage, the chat screens in the app, is built differently under (a) and (b), so its prompt waits for this answer.

**Recommendation: (b).** The Dev Manager recommends it too. It removes the risk instead of narrowing it, for roughly one extra session and one small service. If you choose (a), you are accepting that the gap stays open between a Stream change and our check.

**Your answer:** "(a)" or "(b)", plus anything you want weighed.
