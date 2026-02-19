# WhatsApp Message Sender - Instructions

## Summary

**Script** (`send_whatsapp_playwright.py`): Uses Playwright - ✅ **WORKS**
- Direct browser automation via Chromium
- More reliable and stable
- Works for both existing and new contacts

---

## How to Use

### Quick Start (via Playwright MCP)

Just ask me to:
1. Open WhatsApp Web
2. Log in via QR code (you scan once)
3. Send message to [phone number]

### Python Script

Run manually:
```bash
cd /home/zazikant
python send_whatsapp_playwright.py
```

Or with arguments:
```bash
# Single message
python send_whatsapp_playwright.py "+919869101909" "Hello!"

# Send image
python send_whatsapp_playwright.py --image "+919869101909" "/path/to/image.jpg" "optional caption"

# Batch send
python send_whatsapp_playwright.py --batch "+919999999999,+918888888888" "Hello everyone!"

# Check replies
python send_whatsapp_playwright.py --check-replies
```

---

## What Works (Tested ✅)

### Seamless Message Sending
The **URL method** is the most reliable:
```
https://web.whatsapp.com/send?phone=+91XXXXXXXXXX&text=YourMessage
```

This works because:
1. Navigating to this URL opens the chat with the message pre-filled in compose box
2. Just click the send button or press Enter
3. Works for **both existing AND new contacts**

### Flow:
1. Open `https://web.whatsapp.com/send?phone={phone}&text={message}`
2. Wait for chat to load (compose box appears)
3. Click send button `[data-testid="send"]` OR press Enter
4. Done!

### Sending Images (IMPORTANT - Not Stickers!)

The key is to use the **"Photos & videos"** menu option, NOT the generic file input:

**Manual/MCP Method:**
1. Navigate to chat via URL or click on contact
2. Click attachment button (the paperclip icon)
3. **Click "Photos & videos"** from the dropdown menu (NOT "Document")
4. Select/Upload the image file
5. Wait for preview modal to appear
6. Click **Send** button
7. Verify it shows "Photo" in chat list (NOT "Sticker")

**Common Mistake:**
- ❌ Using `input[type="file"]` directly sends as sticker
- ✅ Using "Photos & videos" menu sends as image

### Batch Sending
- Rate limited: 5 messages per batch
- 2 minute delay between batches
- Individual delay: 3 seconds between messages

---

## Key Selectors

| Element | Selector |
|---------|----------|
| Chat search | `[data-testid="chat-list-search"]` |
| Compose box | `[data-testid="conversation-compose-box-input"]` |
| Send button | `[data-testid="send"]` |
| Attach button | `[data-testid="conversation-attachment-button"]` |
| File input | `input[type="file"]` |
| Photos & videos menu | `text=Photos & videos` |

**IMPORTANT: When sending images via Playwright MCP:**
1. Click Attach button
2. Wait for menu to appear
3. Click "Photos & videos" option (not "Document" or direct file input!)
4. Upload file via file chooser
5. Click Send in preview modal

---

## Files

| File | Purpose |
|------|---------|
| `/home/zazikant/send_whatsapp_playwright.py` | Main script with all functions |
| `/home/zazikant/whatsapp_messages.csv` | Log of sent messages + replies (single row per message) |
| `/home/zazikant/message_state.json` | State tracking for seen messages |

### CSV Format (whatsapp_messages.csv)

```
timestamp,contact,sent_message,reply
2026-02-19 11:28,Shashikant Home,Image: safety management.jpg,Amazing
2026-02-19 11:29,Chandrakant Shivadekar GEM,Image: safety management.jpg,Great 👍👍.. amazing
2026-02-19 11:30,Jaideep Singh BD GEM,Image: safety management.jpg + caption,Cool
```

- **sent_message**: Shows "Image: filename.jpg" for images, or the text message
- **reply**: Filled in when check_for_replies runs (matches reply to most recent sent message)

## Checking Replies

### Method 1: Python Script
```bash
python send_whatsapp_playwright.py --check-replies
```
This opens WhatsApp Web, checks all chats for new messages (replies from contacts), and updates the `reply` column in `whatsapp_messages.csv`.

### Method 2: Manual (Playwright MCP)
Just ask me to check for replies - I can view the chat list and recent messages to see responses.

### Reply Tracking
- The script tracks message IDs in `message_state.json` to avoid duplicate entries
- Only incoming messages (from contacts, not your own) are matched
- Finds the most recent sent message to that contact and fills in the reply column

### Current Replies Logged
Run `--check-replies` or check the CSV file to see responses.
