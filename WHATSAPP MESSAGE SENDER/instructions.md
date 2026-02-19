# WhatsApp Message Sender - Instructions

## Summary

**New script** (`send_whatsapp_playwright.py`): Uses Playwright - ✅ **WORKS**
- Direct browser automation via Chromium
- More reliable and stable

---

## How to Use

### Option 1: Playwright MCP (Recommended for quick tasks)

Just ask me to:
1. Open WhatsApp Web
2. Log in via QR code (you scan once)
3. Send message to [phone number]

**No extra setup needed** - I have Playwright MCP tools available.

### Option 2: Python Script (`send_whatsapp_playwright.py`)

Run manually:
```bash
cd /home/zazikant
python send_whatsapp_playwright.py
```

Or with arguments:
```bash
python send_whatsapp_playwright.py "+919869101909" "Hello!"
```

---

## What Worked Today

1. ✅ Used Playwright MCP tools (browser automation)
2. ✅ You scanned QR code to log in to WhatsApp Web
3. ✅ Sent message to your own number (+917777016824)
4. ✅ Sent "hi message" to +919869101909 (Shashikant Home)

---

## For Next Time

### Just tell me:
> "Send a WhatsApp message to [phone number]: [message]"

I'll:
1. Open WhatsApp Web
2. Use existing session (no need to re-scan if browser still open)
3. Find the contact and send the message

### If session expired:
> "Open WhatsApp Web and I'll scan the QR code"

I'll:
1. Save QR code as screenshot
2. You scan it with your phone
3. Then send the message

---

## Notes

- WhatsApp Web session persists - no need to login every time
- Browser must stay open for session to work
- For sending images, provide the file path

---

## Files Created

| File | Purpose |
|------|---------|
| `/home/zazikant/send_whatsapp.py` | Original PyWhatKit script (doesn't work) |
| `/home/zazikant/send_whatsapp_playwright.py` | New Playwright script (works) |
| `/home/zazikant/instructions.md` | This file |
