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

---

## CSV Format (`whatsapp_messages.csv`)

Tracks Phone + Name for perfect reply capture.
```
timestamp,phone,contact,sent_message,reply
2026-02-24 16:00:00,9869101909,Shashikant Home,Hi,Hello!
```
- ** phone**: Last 10 digits.
- ** contact**: Auto-resolved display name.
- Old 4-column rows are gracefully handled and merged.

---

## ⚠️ Critical Technical Learnings (2026-02-24)

### 1. Match by Phone ID, NOT Name
WhatsApp `@lid` IDs are internal. Match chats by `c.id.user` (phone digits) or exact `c.name` containing the 10 digits.

### 2. ID Fallback
If `getChats()` doesn't find a new contact, use the direct ID format: `91XXXXXXXXXX@c.us`. Always verify registration via `isRegisteredUser` first.

### 3. False-Positive Prevention
Avoid partial name matches like `last10.includes(name)` because names with no digits will match everything. Use strict `chatId === last10` or `chatName.includes(last10)`.

### 4. CSV Schema Stability
The logger now automatically verifies and fixes CSV headers on ہر run.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Sent to wrong person | Fixed: No longer uses partial string subsets for chat lookup. |
| Missing replies | Fixed: Schema updated to match by phone number. |
| Duplicate contacts | Fixed: `getKnownContacts` merges old/new CSV rows by phone/name. |
| Data misaligned | Run `node repair_csv.js` to fix old CSV rows. |
