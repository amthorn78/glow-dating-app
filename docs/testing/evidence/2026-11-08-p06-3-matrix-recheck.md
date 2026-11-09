# P06.3 — Recheck of matrix rows AP-50, AP-51 and GP-51

- **What:** the recheck that P06.3's brief owes before it is written. The rows are those [the matrix](../../planning/store-legal-safety-requirements.md) owns to P06.3 (DM-37 3.1 and 5.1; the matrix, section 10: "before P06.3's brief"; the carried-items file, "Carried to P06.3").
- **Who and when:** App Manager 10, on 8 November 2026, between 21:20 and 21:28 UTC, while writing [P06.3's brief](../../planning/p06-3-notifications.md). This is a records reading of three public pages. It is not an implementation or review session.
- **Method:** the section 10 rule. Each row's source is re-read, the row's date is updated, the IDs stay as they are, and the reading is recorded here.
  - **First pass:** the web-fetch tool read the three URLs. It could not read two parts:
    - it read section 4.5.4 of Apple's guidelines only through a model-extracted summary, because the page text it kept stopped at section 2.5.8;
    - Apple's "Asking permission to use notifications" page came back as a 77-character page shell, because the body is rendered by JavaScript.
  - **Second pass:** `curl` fetched each page's raw HTML, or Apple's DocC JSON for the documentation page (the route P09.3a's session used; its record, section 4). A Python script with `-I` stripped the tags and extracted the sentences below. Each file was written to the manager's scratchpad and hashed. It was not committed.
- **Research, not legal advice** (the matrix's opening note applies).

## The sources

| Source | URL fetched | Final URL | HTTP, bytes | SHA-256 of the fetched file | Page date |
|---|---|---|---|---|---|
| Apple App Review Guidelines | `https://developer.apple.com/app-store/review/guidelines/` | the same | 200, 240,818 | `6adfc4d98ef3160f98b86d3ab3365a6a5439349db2eeab7c84cc003ca7787ffc` | "Last Updated: October 16, 2026", the same revision P09.3a read |
| Apple, "Asking permission to use notifications" (DocC JSON) | `https://developer.apple.com/tutorials/data/documentation/usernotifications/asking-permission-to-use-notifications.json` | the same | 200, 27,654 | `2cd2a04b07f4bd8a554e387c5f7fdbc547d23e4911d9f18fbe6dd71a8c2abd83` | none given |
| Android, "Notification permission" | `https://developer.android.com/develop/ui/views/notifications/notification-permission` | `https://developer.android.com/develop/ui/compose/notifications/notification-permission` (a `301` from the `views` path) | 200, 367,087 | `a210b17272c1f36b85a05ad7eaa37a077ed9584185b5bce043f02a9d0dad9645` | "Last updated 2026-10-28 UTC" |

## The readings

**AP-50: confirmed.**
- **Section 5.1.2 ("Data Use and Sharing"), item (i):** *"Your app may not require users to enable system functionalities (such as push notifications, location services, tracking) in order to access functionality, content, use the app, or receive monetary or other compensation, including but not limited to gift cards and codes."*
  - The row quotes this sentence's opening, ending in an ellipsis.
  - The sentence is in the same revision of 16 October 2026 that P09.3a read, so it is not new since that reading.
- **Section 5.1.1 ("Data Collection and Storage"), item (iv):** *"Access: Apps must respect the user's permission settings and not attempt to manipulate, trick, or force people to consent to unnecessary data access."* The item also says: *"Where possible, provide alternative solutions for users who don't grant consent."*
  - These words support the row's "must respect permission choices".

**AP-51: confirmed.**
- **Section 4.5.4:** *"Push Notifications must not be required for the app to function, and should not be used to send sensitive personal or confidential information."*
  - The section's next sentence: *"Push Notifications should not be used for promotions or direct marketing purposes unless customers have explicitly opted in to receive them via consent language displayed in your app's UI, and you provide a method in your app for a user to opt out from receiving such messages."*
  - Glow's P06.3 sends no promotional push. The brief's notification kinds are match and message only (its D4).
- **"Asking permission to use notifications":**
  - the abstract: *"Request permission to display alerts, play sounds, or badge the app's icon in response to a notification."*
  - on timing: *"Make the request in a context that helps people understand why your app needs authorization."*
  - on context: *"Sending the request in context provides a better experience than automatically requesting…"*
  - The page also describes provisional authorization, quiet notifications on a trial basis. The brief does not use it (its D5).

**GP-51: confirmed.**
- *"Your app must wait to send notifications until after you request the new permission and the user grants that permission to your app."*
- *"Android 13 (API level 33) and higher supports a runtime permission for sending non-exempt (including Foreground Services (FGS)) notifications from an app: POST_NOTIFICATIONS."*
- The section "Request the permission in context" begins: *"When you request notification permissions within your app, do so in the correct context, so that it's explicitly clear what the notifications are used for and why the user should opt in."*
- **The row's URL now redirects** from the `views` path to the `compose` path. The matrix row now cites the final URL.

## What changed in the matrix

- **The rows:** AP-50, AP-51 and GP-51 each add "rechecked 2026-11-08 (P06.3)" after their read date, and GP-51's link is the final URL.
  - No requirement, quotation, owner or state changed.
  - None of the three is UNCONFIRMED: every part of each was read in the source's own words on 8 November.
- **The header's "Research date" bullet** names this recheck and its record.

## Limits

- **One reading of each page,** at the time above. Store policies change (the matrix, section 10, "Rows most likely to change"), so the next recheck point is the one section 10 names: before release artifacts in P09.2 and P12.
- **Only these three rows were rechecked.** The other P06-adjacent rows (AP-46, AP-47, GP-46 and GP-52, on purpose strings, refusals and rationale) are not owned by P06.3. They are not rechecked here.
- **The tag stripping is a script, not a browser render.** Each quoted sentence was found as one continuous string in the stripped text. The script's source is not kept; the files' hashes are recorded above.
- The hashes identify the files fetched then, which were not kept. The Android page differs on every fetch (a script nonce), and the guidelines page fetched by the Dev Manager at 21:43 UTC had the same length and a different hash, so a hash does not re-identify a page; the quoted sentences do (DM-44).
- **The Dev Manager's independent check** (DM-44 item 10): its own fetch found all eleven quoted sentences, each as one continuous string, with the same page dates. The DocC JSON matched this record byte for byte.
