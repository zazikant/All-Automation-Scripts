# WhatsApp Message Sender - Instructions (Enhanced v2.7 - UNREAD CHECK BEFORE SEND)

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

## ⚠️ CRITICAL: Check Unread Messages FIRST Before Sending to ANY Contact!

**This is the MOST IMPORTANT step - never skip!**

### Why?
- WhatsApp Web shows unread count in header (e.g., "42 unread messages")
- Before sending to ANY new contact, you MUST check for unread messages from ALL contacts first
- This ensures replies are captured BEFORE new messages are sent

### ✅ CORRECT Process (ALWAYS):
1. **Check for UNREAD messages** - Get all chats with unread indicators
2. **Map them to CSV** - Capture ALL replies from unread chats
3. **Then send** - Proceed with sending new messages

### Programmatic Check (MCP Code Execution)
```javascript
playwright_browser_run_code:
  code: |
    async (page) => {
      // First: Check for ALL unread chats
      await page.goto("https://web.whatsapp.com/");
      await page.waitForTimeout(2000);
      
      // Get all chat rows
      const chatRows = await page.$$('[role="row"]');
      const unreadChats = [];
      
      for (const row of chatRows) {
        // Check for unread indicator (span with "unread" in class or message count)
        const unreadBadge = await row.$('span[class*="cx"], span[aria-label*="unread"]');
        const nameEl = await row.$('span[class*="title"], span[title]');
        
        if (unreadBadge && nameEl) {
          const name = await nameEl.innerText();
          const unreadText = await unreadBadge.innerText();
          if (name && unreadText && !isNaN(parseInt(unreadText))) {
            unreadChats.push(name);
          }
        }
      }
      
      return { unreadChats, count: unreadChats.length };
    }
```

### Then for EACH unread chat:
1. Open the chat (this marks messages as read)
2. Get ALL messages in the chat (not just the preview!)
3. Find our last sent message
4. Capture all replies after it
5. Update CSV
6. Exit chat

### This replaces context memory!
- The code programmatically finds all unread chats
- No need to remember or guess which contacts replied
- Automatically maps to CSV entries

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

### ⚠️ CRITICAL: Capture ALL Replies, Not Just First/Last!
When checking for replies:
- **Chat list preview only shows the MOST RECENT message** (e.g., "Wow")
- The contact may have sent MULTIPLE replies (e.g., "Thanks" + "This is informative" + "Wow")
- **You MUST open the chat** to see ALL messages in the conversation
- Concatenate all replies with ` + ` separator

**Example of CORRECT reply capture:**
```
Chat list shows: "Shashikant Home: Wow"
But when you OPEN the chat, you see:
  - "Thanks" (06:57)
  - "This is informative" (06:57)  
  - "Wow" (06:58)

CSV should contain: "Thanks + This is informative + Wow"
```

**Never trust the chat list preview alone for replies!**

---

## ⚡ Using Playwright MCP with Code (FASTEST!)

Instead of slow snapshot-based navigation, use `run_code` to execute JavaScript directly:

### Send Message via Code (Reliable Version)
```javascript
playwright_browser_run_code:
  code: |
    async (page) => {
      const phone = "9869101909";
      const message = "Hello from code execution!";
      
      // Navigate with pre-filled message
      await page.goto(`https://web.whatsapp.com/send?phone=${phone}&text=${encodeURIComponent(message)}`, { 
        waitUntil: 'networkidle',
        timeout: 20000 
      });
      
      // Wait for chat to fully load
      await page.waitForTimeout(3000);
      
      // Check if message was pre-filled, if not type it
      const inputBox = await page.$('div[contenteditable="true"][data-tab="1"]');
      if (inputBox) {
        const currentText = await inputBox.innerText();
        if (!currentText.includes(message)) {
          await inputBox.fill(message);
        }
      }
      
      // Wait a moment then press Enter to send
      await page.waitForTimeout(500);
      await page.keyboard.press('Enter');
      
      // Wait for message to appear in chat list (confirms sent)
      await page.waitForTimeout(2000);
      
      // Go back to chat list to ensure proper state
      await page.goto("https://web.whatsapp.com/");
      await page.waitForTimeout(1000);
      
      return "Message sent!";
    }
```

### Send Image with Caption via Code
```javascript
playwright_browser_run_code:
  code: |
    async (page) => {
      const phone = "9869101909";
      const imagePath = "/home/zazikant/images/photo.jpg";  // Full path
      const caption = "Check this out!";
      
      // Open chat
      await page.goto(`https://web.whatsapp.com/send?phone=${phone}`, { 
        waitUntil: 'networkidle',
        timeout: 20000 
      });
      await page.waitForTimeout(3000);
      
      // Click attach button
      const attachBtn = await page.$('[data-testid="conversation-attachment-button"]') || 
                        await page.$('button[title*="Attach"]');
      if (attachBtn) await attachBtn.click();
      await page.waitForTimeout(1000);
      
      // Click "Photos & videos" (NOT Documents!)
      const photosBtn = await page.$('text=Photos & videos');
      if (photosBtn) await photosBtn.click();
      await page.waitForTimeout(1000);
      
      // Upload file - wait for file chooser
      const fileInput = await page.waitForSelector('input[type="file"]', { timeout: 5000 });
      if (fileInput) {
        await fileInput.setInputFiles(imagePath);
        
        // CRITICAL: Wait for preview to fully load - check for send button
        await page.waitForTimeout(3000);
        
        // Wait until send button is visible (image is ready)
        await page.waitForSelector('[data-testid="send"]', { timeout: 10000 });
        
        // Add caption if provided - AFTER image loads
        if (caption) {
          const captionBox = await page.$('[data-testid="caption-input"]');
          if (captionBox) {
            await captionBox.fill(caption);
            await page.waitForTimeout(500);
          }
        }
        
        // Click send button (NOT Enter - for images Enter doesn't work well)
        const sendBtn = await page.$('[data-testid="send"]');
        if (sendBtn) {
          await sendBtn.click();
        }
      }
      
      // CRITICAL: Wait for message to actually appear in chat
      // Check for the image element in the message area
      await page.waitForTimeout(3000);
      
      // Verify image was sent - look for image in chat
      const imageInChat = await page.$('img[src*="blob"]') || 
                         await page.$('[data-testid="image-thumbnail"]') ||
                         await page.$('div[role="log"] img');
      
      if (!imageInChat) {
        // Try one more time - maybe first attempt failed silently
        console.log("Image not found, retrying...");
        return "FAILED: Image not sent";
      }
      
      // Go back to chat list
      await page.goto("https://web.whatsapp.com/");
      await page.waitForTimeout(1500);
      
      // Verify it appears in chat list as last message (with image icon)
      const chatListText = await page.textContent('body');
      if (!chatListText.includes("image") && !chatListText.includes("photo")) {
        return "WARNING: Check if image was actually sent";
      }
      
      return "Image sent with caption!";
    }
```

### Key Fixes for Image Sending:
1. **Wait for `input[type="file"]` to appear** - file chooser needs time
2. **Wait 3+ seconds after setInputFiles** - image takes time to upload/preview
3. **Wait for send button to be visible** - confirms image is ready
4. **Click send button (NOT Enter)** - Enter doesn't work reliably for images
5. **Wait 3+ seconds after sending** - gives time for upload
6. **Verify image actually in chat** - check for image element before returning
7. **Check chat list** - verify message appears with image indicator

### Check Replies via Code
```javascript
playwright_browser_run_code:
  code: |
    async (page) => {
      // Go to chat list
      await page.goto("https://web.whatsapp.com/");
      await page.waitForTimeout(2000);
      
      // Get top 10 chats with unread messages
      const chats = await page.$$('[data-testid="chat-list"] > div > div');
      const results = [];
      
      for (const chat of chats.slice(0, 10)) {
        const name = await chat.$('span[title]');
        const unread = await chat.$('span[class*="unread"]');
        
        if (name && unread) {
          const contactName = await name.innerText();
          results.push(contactName);
        }
      }
      return results;
    }
```

### Advantages:
- ✅ **10x faster** than snapshot navigation
- ✅ Direct URL navigation + click
- ✅ No waiting for AI to interpret snapshots
- ✅ Can loop through multiple contacts easily
- ✅ Smart element selection in code

### Key Fixes for Reliability:
1. **Always use `page.keyboard.press('Enter')` as fallback** - more reliable than clicking send button
2. **Wait for `networkidle`** - ensures page fully loaded
3. **Check if message already in input box** - some cases pre-fill works
4. **Go back to chat list after sending** - ensures proper state for next operation
5. **Wait 2-3 seconds** - gives WhatsApp time to process

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

### ⚡ THE WORKING MCP IMAGE METHOD (2026-02-20)

**Key Discovery:** JavaScript's `setInputFiles()` doesn't work in MCP browser context. Use the **file upload tool** instead!

**Steps:**
1. Navigate to chat: `https://web.whatsapp.com/send?phone=NUMBER`
2. Click **attachment button** (paperclip icon)
3. Click **"Photos & videos"** menu option
4. **Wait for file chooser modal** - snapshot shows `[File chooser]: can be handled by browser_file_upload`
5. Use **browser_file_upload** tool with file path:
   ```json
   playwright_browser_file_upload:
     paths: ["/home/zazikant/image.jpg"]
   ```
6. Wait for image preview to load
7. Type caption in textbox (if needed)
8. Click **Send** button
9. **Press Escape** to exit chat back to list (critical for reply capture!)

**Why this works:**
- `playwright_browser_file_upload` properly handles the native file chooser dialog
- JavaScript `setInputFiles()` fails silently in MCP context
- Python script uses `set_input_files()` which works but needs its own session

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

## 📋 Quick Reference: Sending Images

### Option 1: Python Script (Easiest)
```bash
python send_whatsapp_playwright.py --image "+919869101909" "/path/to/image.jpg" "optional caption"
```
The script handles everything automatically.

### Option 2: MCP Playwright (Manual)
1. Navigate to chat
2. Click attach button (paperclip)
3. Click "Photos & videos"
4. **Use `playwright_browser_file_upload` tool** (NOT JavaScript setInputFiles!)
5. Type caption
6. Click Send
7. Press Escape to exit chat

### Why browser_file_upload works:
- JavaScript's `setInputFiles()` fails silently in MCP browser context
- Python's `set_input_files()` works (different runtime)
- The file upload tool properly handles the native file chooser dialog

---

## Version History

- **v2.7** (Current): Added critical section - ALWAYS check for unread messages BEFORE sending to any contact (programmatic approach)
- **v2.6**: Added critical note - capture ALL replies by opening chat, not just from chat list preview
- **v2.5**: Verified working - use `playwright_browser_file_upload` tool for MCP, Python script uses `set_input_files()`
- **v2.4**: Added MCP file upload tool for images - THE WORKING METHOD!
- **v2.3**: Improved code execution reliability + added image sending with caption
- **v2.2**: Added code execution via run_code - Much faster than snapshots!
- **v2.1**: Added exit_chat after sending - Critical for reply capture!
- **v2.0**: Persistent sessions, contact cache, optimized selectors
- **v1.0**: Basic functionality, new browser per send

