# WhatsApp Message Sender - Instructions (Enhanced v2.1)

## Summary

**Script** (`send_whatsapp_playwright.py`): Uses Playwright - ✅ **WORKS & OPTIMIZED**
- Direct browser automation via Chromium
- **Persistent sessions** - No repeated QR scans
- **Fast contact lookup** - Cached contact mappings
- **Reliable selectors** - Multiple fallback strategies
- **Batch operations** - Single browser instance for multiple sends
- **Smart retry logic** - Auto-retry on failures
- **Exit chat after send** - Critical for capturing replies!

---

## Quick Start

### Option 1: MCP Playwright (Fastest - Recommended)

Just tell me: _"Send to [phone number]"_ and I'll handle it instantly using the active browser session.

### Option 2: Python Script

```bash
# Send single message
python send_whatsapp_playwright.py "+919869101909" "Hello!"

# Send with auto-detect contact name
python send_whatsapp_playwright.py "9820937483" "Hello!" --auto-name

# Send image
python send_whatsapp_playwright.py --image "+919869101909" "/path/to/image.jpg" "optional caption"

# Batch send (most efficient - single browser session)
python send_whatsapp_playwright.py --batch "+919999999999,+918888888888" "Hello everyone!"

# Check replies for all contacts
python send_whatsapp_playwright.py --check-replies

# Keep session alive for faster subsequent sends
python send_whatsapp_playwright.py --keep-alive
```

---

## ⚠️ CRITICAL: Exit Chat After Sending

**This is the MOST IMPORTANT step for capturing replies!**

### Why?
- WhatsApp Web doesn't always show new messages in real-time when you're already inside a chat
- If you stay in the chat after sending, you might miss replies
- **2 back-to-back replies will be missed** if you don't exit and re-enter

### ✅ CORRECT Process:
1. **Send message** → Log to CSV
2. **EXIT chat** (go back to chat list) ← **CRITICAL**
3. Wait for reply
4. **Re-enter chat** to see new messages properly
5. Capture reply → Update CSV

### The Script Does This Automatically!
Use these methods instead:
```python
# These methods automatically exit chat after sending:
sender.send_message_and_exit(phone, message)      # For text
sender.send_image_and_exit(phone, image_path)     # For images

# The script will:
# 1. Send the message
# 2. Exit the chat (go back to chat list)
# 3. This ensures replies are captured properly
```

### Via MCP (Manual Steps):
If using manual Playwright MCP:
1. Send message
2. **Click "Back" button** to exit chat to list ← CRITICAL STEP!
3. Wait a moment
4. Re-enter chat to check for replies

---

## Efficient Contact Finding (NEW!)

### Method 1: Direct Phone Number Mapping (Fastest)
The script now includes a **contact cache** that maps phone numbers to saved contact names:

```python
CONTACT_CACHE = {
    "9869101909": "Shashikant Home",
    "8976167591": "Jaideep Singh BD GEM",
    "9820937483": "Purva",
    # Add your contacts here!
}
```

**Benefits:**
- ✅ No searching needed
- ✅ Instant chat open
- ✅ Works even if contact renamed

### Method 2: URL Direct Navigation (Universal)
```
https://web.whatsapp.com/send?phone=+91XXXXXXXXXX&text=YourMessage
```

**Pros:**
- Works for ANY number (saved or unsaved)
- Opens chat instantly
- Pre-fills message text

**Cons:**
- Number must include country code

### Method 3: Search by Name (Fallback)
If contact is saved but not in cache:
1. Click "New chat" button
2. Type name/number in search
3. Click result
4. Wait 1-2 seconds

---

## Sending Images Efficiently

### ✅ CORRECT Method (Sends as Photo)

**Via Python Script:**
```python
send_whatsapp_image("+919869101909", "/path/to/image.jpg", "Caption here")
```

**Via MCP (Manual Steps):**
1. Navigate to chat via URL: `https://web.whatsapp.com/send?phone=NUMBER`
2. Click **attachment button** (paperclip icon)
3. Click **"Photos & videos"** menu option
4. Upload file
5. Click **Send**
6. ✅ Verify chat shows "Photo" (not "Sticker")

### ❌ AVOID (Sends as Sticker)
- Direct file input without using "Photos & videos" menu
- Results in low-quality sticker instead of image

---

## Performance Tips

### 1. Use Persistent Sessions
```bash
# First time - scan QR
python send_whatsapp_playwright.py --keep-alive

# Subsequent sends - instant, no QR scan
python send_whatsapp_playwright.py "+919869101909" "Hello!"
```

### 2. Batch Operations
```bash
# Send to 10 contacts in one session
python send_whatsapp_playwright.py --batch "p1,p2,p3,p4,p5,p6,p7,p8,p9,p10" "Hello!"
```

**What happens during batch send:**
- Sends messages in batches (default 10 per batch)
- **During batch delay**: Automatically checks for replies from contacts
- **After all batches**: Final reply check
- All sent messages and replies are logged to CSV in real-time

### 3. Pre-populate Contact Cache
Edit the `CONTACT_CACHE` dictionary in the script with your frequent contacts.

### 4. Use Full Phone Numbers
Always include country code: `+91` for India, `+1` for US, etc.

---

## Key Selectors (Updated)

| Element | Primary Selector | Fallback |
|---------|-----------------|----------|
| Chat search | `[data-testid="chat-list-search"]` | `input[placeholder*="Search"]` |
| Compose box | `[data-testid="conversation-compose-box-input"]` | `div[contenteditable="true"]` |
| Send button | `[data-testid="send"]` | `button[aria-label*="Send"]` |
| Attach button | `[data-testid="conversation-attachment-button"]` | `button[title*="Attach"]` |
| Photos menu | `text=Photos & videos` | `button:has-text("Photos")` |
| Caption input | `[data-testid="caption-input"]` | `div[contenteditable="true"]` |
| Chat loaded | `[data-testid="conversation-compose-box-input"]` | Text input visible |

---

## Files

| File | Purpose |
|------|---------|
| `/home/zazikant/send_whatsapp_playwright.py` | Main optimized script |
| `/home/zazikant/whatsapp_messages.csv` | Log of sent messages + replies |
| `/home/zazikant/message_state.json` | Message ID tracking for replies |
| `/home/zazikant/whatsapp_session/` | Persistent browser storage (created automatically) |

### CSV Format (whatsapp_messages.csv)

The CSV captures all sent messages and responses with the following format:

```
timestamp,contact,sent_message,reply
2026-02-19 12:24,Purva (+919820937483),Hello! This is a test message from Playwright automation.,Not interested
```

**Format Rules:**
- **sent_message**: Multiple messages sent on the same day to the same contact are concatenated with ` + ` separator
  - Text messages: "Hello" + "How are you?"  
  - Images/Videos: "safety management.jpg" + "document.pdf"
  - Mixed: "Hello!" + "Image: photo.jpg" + "document.pdf"
- **reply**: All user responses received after a sent message (until the next message is sent) are concatenated with ` + ` separator
  - Example: "Thanks" + "But I need more info" + "Please call me"

**Grouping Logic:**
- Messages are grouped by: Date + Contact
- Within each group, all sent messages are concatenated with ` + `
- Within each message-response pair, all replies are concatenated with ` + `
- **Only NEW/UNREAD messages** are captured as replies (chat must show unread indicator)

**How Reply Tracking Works:**
1. **Before each new message**: Checks for any unread replies in that chat first
2. Opens the chat (marks messages as read)
3. Collects all messages after our last sent message
4. Updates CSV with reply
5. Then sends the new message
6. **During batch delay**: Checks for replies from other contacts

**This captures:**
- ✅ Replies to messages sent in previous batches
- ✅ Replies that came after we sent a message but before we sent the next one
- ✅ New/unread messages in any chat

**Example Output:**
```
timestamp,contact,sent_message,reply
2026-02-19 11:28,Shashikant Home,safety management.jpg + presentation.pdf,Thanks + Looks good + Call me tomorrow
2026-02-19 12:24,Purva (+919820937483),Hello! How are you?,Not interested
2026-02-19 14:30,Jaideep Singh BD GEM,Hello! + Image: brochure.jpg + document.pdf,Got it + Thanks
```

---

## Troubleshooting

### Issue: "Chat not loading"
**Solution:** 
- Ensure phone number includes country code (`+91` not just `9869...`)
- Try searching by saved contact name instead
- Check if contact blocked you

### Issue: "Image sent as sticker"
**Solution:**
- Must click "Photos & videos" menu, not direct file upload
- Verify in chat list - should say "Photo" not "Sticker"

### Issue: "QR code keeps appearing"
**Solution:**
- Use `--keep-alive` flag
- Check `whatsapp_session/` folder exists
- Don't close browser between sends

### Issue: "Contact name not found"
**Solution:**
- Add to `CONTACT_CACHE` dictionary
- Use `--auto-name` flag to auto-detect from chat
- Manually specify: `"+919869101909"` instead of just the number

---

## Advanced Usage

### Custom Contact Mapping
```python
# In send_whatsapp_playwright.py, update CONTACT_CACHE:
CONTACT_CACHE = {
    "9869101909": "Shashikant Home",
    "9820937483": "Purva",
    "YOUR_NUMBER": "Contact Name",
}
```

### Retry Logic
```python
# Script automatically retries failed sends up to 3 times
send_with_retry(phone, message, max_retries=3)
```

### Rate Limiting (Built-in)
- 10 messages per batch
- 3 second delay between messages
- 120 second delay between batches
- **During batch delay**: Checks for replies from previous messages
- Prevents WhatsApp from flagging as spam

---

## MCP Playwright Workflow (Fastest)

For instant sending via this interface:

1. **I maintain persistent browser session** - No QR scans needed
2. **Use URL navigation** - Direct chat open: `https://web.whatsapp.com/send?phone=NUMBER`
3. **Cached selectors** - Fast element detection
4. **Immediate send** - No unnecessary waits

**Example conversation:**
```
You: Send "Hello" to 9869101909
Me: ✅ Sent to Shashikant Home: Hello
```

**Total time: 5-10 seconds** vs 30-60 seconds with old method

---

## Version History

- **v2.1** (Current): Added exit_chat after sending - Critical for reply capture!
- **v2.0**: Persistent sessions, contact cache, optimized selectors
- **v1.0**: Basic functionality, new browser per send

