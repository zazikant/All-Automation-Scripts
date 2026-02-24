# WhatsApp Message Sender & Reply Tracker

An intelligent WhatsApp automation tool built with `whatsapp-web.js` that auto-resolves contact names and tracks all messages/replies in a structured CSV format.

## 🚀 Features

- **Intelligent Name Resolution**: Auto-detects names from WhatsApp profiles—no manual address book needed.
- **Reply Capture**: Automatically identifies and logs unread replies from your contacts.
- **Batch Sending**: Send text or images to hundreds of contacts with built-in delays to prevent spam detection.
- **Persistent Sessions**: Log in once via QR code and stay logged in.
- **Phone-Based Logging**: Reliable tracking in `whatsapp_messages.csv` indexed by phone number.

## 🛠 Setup

1. **Install Node.js** (v16 or higher).
2. **Clone the repo** and install dependencies:
   ```bash
   npm install
   ```
3. **Prepare your contacts**:
   - Copy `input_contacts.csv.example` to `input_contacts.csv`.
   - Add your target phone numbers and messages.
4. **Login**:
   ```bash
   node keep_alive.js
   ```
   Scan the QR code with your phone (Linked Devices).

## 📖 Usage

### Every time you start:
```bash
node check_replies.js
```
*MANDATORY: Always check replies first to capture incoming data into your CSV.*

### Sending Messages:
```bash
node send_batch.js
```
Runs the batch process from your CSV.

---

For detailed technical instructions, session handling, and architecture, see [CLAUDE.md](./CLAUDE.md).

## 🚫 Security Note
This project creates a `.wwebjs_auth` folder. **Never share or upload this folder**, as it contains your private WhatsApp session data. The included `.gitignore` protects this by default.
