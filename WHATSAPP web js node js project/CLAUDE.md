# CLAUDE.md — WhatsApp Web.js Workflow

## Overview

This project uses **whatsapp-web.js** (Node.js) to automate sending text messages and images via WhatsApp, and logs all activity to **`whatsapp_messages.csv`**. The AI agent runs terminal commands — it never manually controls the browser DOM.

---

## Architecture

```
Whatsapp Message Sender/
├── keep_alive.js         → First-time QR login + persistent session
├── send_text.js          → Send a text message to a contact
├── send_image.js         → Send an image (with optional caption)
├── send_batch.js         → Send messages in batches from CSV (with delays)
├── check_replies.js      → Check unread replies from known contacts
├── repair_csv.js         → One-time script to fix CSV schema/alignment
├── debug_chats.js        → Debug: list all chats + verify phone IDs
├── utils/
│   ├── contacts.js       → Name resolution + CONTACT_CACHE
│   └── csv_logger.js     → CSV read/write (whatsapp_messages.csv)
├── whatsapp_messages.csv → Log of all sent messages & replies
├── input_contacts.csv    → Input file for batch sending
└── .wwebjs_auth/         → Persistent session (auto-created)
```

---

## Setup

### Install Dependencies
```bash
npm install
```

### First-Time Login (QR Scan)
```bash
node keep_alive.js
```
- Session saved to `.wwebjs_auth/`.
- Open `qr_code.png` for a clear scan if the terminal version is too small.

---

## Intelligent Contact Resolution

The system intelligently resolves names using the following priority:
1.  **`CONTACT_CACHE`** override (highest priority).
2.  **WhatsApp Chat Name** (if already chatted).
3.  **WhatsApp Profile Name** (Pushname).
4.  **Formatted Phone Number** (Fallback).

### Contact Cache (`utils/contacts.js`)
Use this ONLY if you want to override the name stored in the CSV:
```js
const CONTACT_CACHE = {
  "9869101909": "Shashikant Home",
};
```

---

## Commands

### ⚠️ MANDATORY: Check Replies First
```bash
node check_replies.js
```
Always run this BEFORE sending. Uses phone-number matching for 100% reliability.

### Send a Text Message
```bash
node send_text.js "9082167025" "Hello!"
```

### Batch Sending
```bash
node send_batch.js
```
- Delayed batches with automatic reply checking during wait times.
- Final reply check runs automatically after the last send.
- **Phone number convention in `input_contacts.csv`**:
  - `9869101909` — no `+` → default India (+91)
  - `+919869101909` — with `+` → full E.164 international number (India)
  - `+9719869101909` → UAE
  - `+12025551234` → USA
  - **Rule**: `+` means trust the full number. No `+` means assume +91 India.

---

## CSV Format (`whatsapp_messages.csv`)

Tracks Phone + Name for perfect reply capture.
```
timestamp,phone,contact,sent_message,reply
2026-02-25 11:30:00,9869101909,Shashikant Home,"Image: safety management.jpg | caption",
2026-02-25 11:30:05,9869101909,Shashikant Home,Hello,Thanks for messaging
```
- **phone**: Last 10 digits.
- **contact**: Auto-resolved display name.
- **Each sent message is its own row** (changed 2026-02-25 — no more same-day concatenation).
- **Reply linking**: `updateReply` always attaches the reply to the LAST row for a contact (by phone). So the reply for a batch of sends goes on the last message row.
- Old 4-column rows are gracefully handled and migrated.

---

## ⚠️ Critical Technical Learnings (2026-02-24)

### 1. Match by Phone ID, NOT Name
WhatsApp `@lid` IDs are internal. Match chats by `c.id.user` (phone digits) or exact `c.name` containing the 10 digits.

### 2. ID Fallback
If `getChats()` doesn't find a new contact, use the direct ID format: `91XXXXXXXXXX@c.us`. Always verify registration via `isRegisteredUser` first.

### 3. False-Positive Prevention
Avoid partial name matches like `last10.includes(name)` because names with no digits will match everything. Use strict `chatId === last10` or `chatName.includes(last10)`.

### 4. CSV Schema Stability
The logger now automatically verifies and fixes CSV headers on every run.

---

## ⚠️ Critical Technical Learnings (2026-02-25)

### 5. One Row Per Message (csv_logger.js)
`logSentMessage` now **always appends a new row** for every send. The old behavior concatenated same-day same-contact messages with `" + "`. This was changed so each send is independently trackable.

### 6. Reply Linking Behavior
`updateReply` scans from the **bottom of the CSV** and attaches the reply to the **last row** for that contact. If you send an image and then a text in one batch, the reply will appear on the text row. This is correct — it reflects the most recent outgoing message.

### 7. Session Lock Error on Restart
If `send_batch.js` throws `The browser is already running for...`, a previous `node` or `chrome` process is still holding the `.wwebjs_auth/session/lockfile`. Fix:
```bash
taskkill /F /IM node.exe /T
taskkill /F /IM chrome.exe /T
```
Then re-run the script.

### 8. Scientific Notation in Contact Names
If a phone number (e.g. `9082167025`) is ever stored as the contact name and then opened/saved by Excel or a spreadsheet tool, it may be corrupted to scientific notation (`9.19082E+11`). This breaks chat matching. Fix: manually correct the `contact` column in `whatsapp_messages.csv`, or add the contact to `CONTACT_CACHE` in `utils/contacts.js` to override it.

### 9. International Phone Number Support (2026-02-25)
`toWaId()` in `utils/contacts.js` now uses the `+` prefix as a reliable signal:
- **With `+`** → the full number is used as-is (E.164 international format)
- **Without `+`** → assumes Indian 10-digit number, prepends `91`

All sending scripts (`send_text.js`, `send_image.js`, `send_batch.js`) now call `toWaId(phone)` instead of hardcoding `91${last10}`.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Sent to wrong person | Fixed: No longer uses partial string subsets for chat lookup. |
| Missing replies | Fixed: Schema updated to match by phone number. |
| Duplicate contacts | Fixed: `getKnownContacts` merges old/new CSV rows by phone/name. |
| Data misaligned | Run `node repair_csv.js` to fix old CSV rows. |
| Session lock on start | Kill lingering `node.exe` / `chrome.exe` processes, then retry. |
| Contact shown as `9.19082E+11` | Scientific notation corruption from Excel. Fix in CSV or add override to `CONTACT_CACHE`. |
| CSV locked (`EBUSY`) during batch | Close `whatsapp_messages.csv` in your editor before running `send_batch.js`. |
