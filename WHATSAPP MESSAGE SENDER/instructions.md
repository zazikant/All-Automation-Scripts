# WhatsApp Message Sender - Instructions (Enhanced v2.14)

══════════════════════════════════════════════════════════════════════════════
║  ⚠️  VERY IMPORTANT: BEFORE SENDING ANY MESSAGE - ALWAYS CHECK REPLIES FIRST!  ⚠️  ║
║                                                                              ║
║  1. Read CSV to see contacts we've sent to                                  ║
║  2. Check chat list for UNREAD messages from those contacts                 ║
║  3. Open each chat → capture ALL replies → update CSV                      ║
║  4. THEN send new message                                                   ║
║                                                                              ║
║  FAILURE TO DO THIS = MISSED REPLIES = LOST DATA                           ║
║  (This actually happened on 2026-02-20 - replies were lost!)               ║
══════════════════════════════════════════════════════════════════════════════

### What happens if you skip:
- User sent "Hi" to 9869101909 and 8976167591
- Both contacts replied ("Hello" and "Kris ka gana sunega")
- Replies were NOT captured because I didn't check first
- Had to manually update CSV after the fact

### Don't let this happen again!

## ⚠️ ⚠️ ⚠️ MANDATORY WORKFLOW - NEVER SKIP!

### BEFORE SENDING ANY MESSAGE, YOU MUST:

1. **Read CSV** → Get list of contacts we've sent messages to
2. **Check chat list** → Look for unread messages from CSV contacts
3. **Open each chat with unread** → Capture ALL replies
4. **Concatenate replies** → Join multiple replies with " + "
5. **Update CSV** → Map replies to correct contact entries
6. **Exit chat** → Press Escape to go back to chat list
7. **THEN send** → Proceed with sending new messages

### ⚠️ THIS IS NOT OPTIONAL!

- ❌ NEVER send a message without checking for replies first
- ❌ NEVER skip the unread check even if "it's just a quick message"
- ❌ NEVER forget to concatenate multiple replies with " + "

- ✅ ALWAYS check unread from CSV contacts before sending
- ✅ ALWAYS open chat to capture ALL replies (not just preview)
- ✅ ALWAYS update CSV with replies before sending new messages

**If you don't follow this workflow, you will miss replies and lose data!**

---

## ⚠️ CRITICAL: Capturing ALL Replies Accurately (2026-02-20)

### The Problem:
- Chat list preview only shows the MOST RECENT message
- There may be MULTIPLE replies after our sent message
- Missing any reply = data loss

### The Solution - ALWAYS Do This:

1. **Click on the chat** to open it fully (don't just read from preview)
2. **Scroll through message history** to find ALL messages after our sent message
3. **Capture EVERY reply** - list them all out
4. **Concatenate with " + "** - join multiple replies chronologically
5. **Verify** - make sure you didn't miss any

### Example:
```
Chat list preview shows: "I will look into it"
BUT when you OPEN the chat, you see:
  - "Thanks"
  - "I will look into it"

Correct CSV entry: Thanks + I will look into it
Wrong CSV entry:   I will look into it  ← MISSED "Thanks"!
```

### NEVER:
- ❌ Trust the chat list preview alone
- ❌ Only capture the most recent reply
- ❌ Skip opening the chat to verify all replies

### ALWAYS:
- ✅ Open the chat to see full conversation
- ✅ Scroll and read ALL messages after our sent message
- ✅ List every reply in chronological order with " + " separator
- ✅ Double-check before updating CSV

---

## ⚠️ CRITICAL: Phone Number Format for Searching Contacts

### The Rule:
When user gives a number like `9869101909` or `8976167591` → Just search with that exact number:
- `9869101909` → search for `9869101909` (WhatsApp matches +91, 0, etc.)
- `8976167591` → search for `8976167591`

WhatsApp's search is smart - it matches partial numbers against stored contacts regardless of format (+91, 0, spaces, etc.). No need to add prefixes!

---

## ⚠️ CRITICAL: Initial Setup & Login Verification

### Step 1: Show Full-Size QR Code for Login

When you need to log in or reconnect:
1. Navigate to `https://web.whatsapp.com`
2. Wait for QR code to fully load
3. **Take a FULL PAGE screenshot** - use `fullPage: true` option to capture the entire QR code
4. Share the screenshot with user to scan

**Never crop or resize the QR code** - it must be fully visible for scanning.

### Step 2: Verify Login Before Any Operation

**ALWAYS verify you are logged in before sending messages or checking replies:**

1. Take a snapshot after navigation
2. Look for these indicators of logged-in state:
   - Chat list is visible
   - "Chats" button is present
   - Contact names are visible in chat list
   
3. If you see QR code instead of chat list:
   - **STOP** - Do not proceed with any operations
   - Take full-page screenshot of QR code
   - Ask user to scan it
   - Re-verify login before continuing

### ⚠️ NEVER Proceed Without Verification

- ❌ Don't send messages if QR code is shown
- ❌ Don't check replies if not logged in
- ❌ Don't assume session is still valid

- ✅ DO verify login status first
- ✅ DO wait for chat list to appear
- ✅ DO proceed only when logged in

---

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

### Simple Programmatic Approach:

1. **Get all unread chat names** from chat list (look for "X unread messages" text)
2. **Filter by CSV** - Only check contacts we've sent messages to
3. **Open each matching chat** - Capture the reply
4. **Update CSV** - Map reply to correct entry
5. **Exit chat** - Go back to chat list
6. **Then send** - Proceed with sending new messages

### Step-by-Step:

**Step 1: Read CSV to get contacts we've sent to**
```
Contacts in CSV: Shashikant Home, Jaideep Singh BD GEM, Purva (+919820937483), Chandrakant Shivadekar GEM
```

**Step 2: Get all unread chats from chat list**
- Look at chat list - find rows with "X unread message(s)" text
- Extract contact names from those rows

**Step 3: Filter and process**
- Compare unread names with CSV contacts
- For matching contacts: open chat → get reply → update CSV → exit

**Step 4: Send new message**

### Quick Manual Check (When I have browser session):
1. Take snapshot of chat list
2. Look for "unread" text in each row
3. Extract contact name
4. If name in CSV → open chat → capture reply → update CSV → exit
5. Repeat for all unread contacts
6. Then proceed with sending
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

## ⚡ CORRECT Method to Send Messages (WORKING!)

### ❌ DON'T USE - URL Method Doesn't Work Reliably
```javascript
// THIS DOES NOT WORK RELIABLY - AVOID
await page.goto(`https://web.whatsapp.com/send?phone=${phone}&text=${encodeURIComponent(message)}`);
```

### ✅ CORRECT Method - Click Chat + Type in Input

**Step 1:** Navigate to WhatsApp Web
```javascript
await page.goto("https://web.whatsapp.com/");
await page.waitForTimeout(3000);
```

**Step 2:** Click on the contact from chat list (find by name in the rows)
```javascript
// Click on chat row - contact name appears in the chat list
await page.click('text=ContactName');  // e.g., 'text=Shashikant Home'
await page.waitForTimeout(2000);
```

**Step 3:** Find and fill the message input box (footer contenteditable)
```javascript
const inputBox = await page.$('footer div[contenteditable="true"]');
if (inputBox) {
  await inputBox.fill('Hi');
  await page.waitForTimeout(500);
  await page.keyboard.press('Enter');
}
```

**Step 4:** Verify message sent - appears in chat list with timestamp
```javascript
await page.waitForTimeout(2000);
// Message should appear in chat list as "ContactName: Hi 11:56"
```

### Complete Working Example
```javascript
async (page) => {
  const contactName = "Shashikant Home";  // Name as it appears in chat list
  const message = "Hi";
  
  // Go to WhatsApp
  await page.goto("https://web.whatsapp.com/");
  await page.waitForTimeout(3000);
  
  // Click on the contact's chat
  await page.click(`text=${contactName}`);
  await page.waitForTimeout(2000);
  
  // Type message in input box
  const inputBox = await page.$('footer div[contenteditable="true"]');
  if (inputBox) {
    await inputBox.fill(message);
    await page.waitForTimeout(500);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(2000);
  }
  
  // Go back to chat list
  await page.goto("https://web.whatsapp.com/");
  await page.waitForTimeout(1000);
  
  return "Message sent to " + contactName;
}
```

### Key Points:
- ✅ Always click on chat from list first
- ✅ Use `footer div[contenteditable="true"]` selector for input
- ✅ Press Enter to send (not click send button)
- ✅ Verify message appears in chat list after sending

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

## Efficient Contact Finding

### Method 1: Click on Chat from List (CORRECT & RELIABLE)
1. Navigate to WhatsApp Web: `https://web.whatsapp.com/`
2. Wait for chat list to load
3. Click on the contact name directly from the chat list rows
4. Type message in input box and press Enter

### Method 2: Contact Cache (Fastest)
The script includes a **contact cache** that maps phone numbers to saved contact names:

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

### ❌ AVOID: URL Direct Navigation
```
https://web.whatsapp.com/send?phone=+91XXXXXXXXXX&text=YourMessage
```
**Doesn't work reliably** - message appears typed but doesn't send properly.

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

### Issue: "Message appears typed but doesn't send"
**Problem:** Using URL pre-fill like `https://web.whatsapp.com/send?phone=...&text=hello` shows the message in the input box but doesn't actually send it.

**Root Cause:** URL pre-fill only puts text in input box - it does NOT automatically send. The Enter key press is needed but sometimes fails in MCP context.

**Solution - ALWAYS use this method:**
```javascript
// 1. Navigate to WhatsApp first
await page.goto("https://web.whatsapp.com/");
await page.waitForTimeout(3000);

// 2. Click on the chat from the list
await page.click('text=ContactName');  // Use exact name as it appears
await page.waitForTimeout(2000);

// 3. Use the correct selector (footer contenteditable)
const inputBox = await page.$('footer div[contenteditable="true"]');
if (inputBox) {
  await inputBox.fill('hello');
  await page.waitForTimeout(500);
  await page.keyboard.press('Enter');
}

// 4. Verify message appears in chat list with timestamp
```

**Key points:**
- ✅ Navigate to WhatsApp first (not directly to send URL)
- ✅ Click chat from list to open it fully
- ✅ Use `footer div[contenteditable="true"]` selector (works in MCP)
- ✅ Always press Enter after filling
- ✅ Verify message appears in chat list

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

## 📋 Quick Reference: Sending Images (UPDATED 2026-02-20)

### MCP Playwright Method (Manual Steps)

1. **Navigate to chat** - Open the contact's chat
2. **Click attach button** (paperclip icon) - ref is usually `e2034` with `button "Attach"`
3. **Click "Photos & videos"** menu option - wait for menu to appear
4. **Wait for file chooser** - snapshot shows `[File chooser]: can be handled by browser_file_upload`
5. **Use `playwright_browser_file_upload` tool** - pass array of file paths:
   ```json
   playwright_browser_file_upload:
     paths: ["/home/shashikantzarekar/safety management.jpg"]
   ```
6. **Wait for image preview** - image appears in a preview modal
7. **Click Send button** - usually ref `e2206` with `button "Send"`
8. **Wait for send** - message appears in chat with "Pending" then "Delivered"
9. **Press Escape** to exit chat back to list

### Why browser_file_upload works:
- JavaScript's `setInputFiles()` fails silently in MCP browser context
- The file upload tool properly handles the native file chooser dialog
- MUST click "Photos & videos" NOT "Document" (otherwise sends as sticker)

### Image Sending Flow (Visual Reference)
```
Chat Open → Click Attach (paperclip) → Menu appears → Click "Photos & videos" → 
[File chooser modal] → playwright_browser_file_upload → Image preview loads → 
Click Send → Image sent to chat → Escape to exit
```

---

## 📋 Quick Reference: CSV Updates

### CSV Format
```
timestamp,contact,sent_message,reply
2026-02-20 10:05,Shashikant Home (+919869101909),[Image: safety management.jpg],
```

### Key Points:
- No line numbers at start - data starts directly
- Each row: timestamp,contact,sent_message,reply
- Images format: `[Image: filename.jpg]`
- Empty reply = no response yet
- Multiple replies separated by: ` + `

### To Add New Entry:
```bash
# Edit the CSV file directly
# Append new row at the end (before empty line if any)
2026-02-20 10:05,Shashikant Home (+919869101909),[Image: safety management.jpg],
```

### Common Issue - Edit Fails:
If `edit` tool fails with "oldString not found":
- Check exact whitespace with `cat -A filename.csv`
- Copy/paste exact content from bash output
- Make sure no extra spaces/tabs

---

## Version History

- **v2.14** (Current): FIXED - Removed unreliable URL method. Now specify correct method: click chat from list → type in input box → press Enter
- **v2.13**: Added phone number format tip - always add +91 prefix when searching contacts
- **v2.12** (Current): Added critical section on capturing ALL replies - must open chat, not just read preview, concatenate all replies with " + "
- **v2.11** (Current): Added clearer image sending workflow with visual flow + CSV update guide
- **v2.10**: Made unread check workflow MANDATORY - added prominent warning at top, clarified this is never optional
- **v2.9**: Added critical login verification steps - ensure full-size QR shown and verify logged-in status before any operation
- **v2.8**: Simplified unread check workflow - check chat list for unread → filter by CSV → open & capture → update CSV
- **v2.7**: Added critical section - ALWAYS check for unread messages BEFORE sending to any contact (programmatic approach)
- **v2.6**: Added critical note - capture ALL replies by opening chat, not just from chat list preview
- **v2.5**: Verified working - use `playwright_browser_file_upload` tool for MCP, Python script uses `set_input_files()`
- **v2.4**: Added MCP file upload tool for images - THE WORKING METHOD!
- **v2.3**: Improved code execution reliability + added image sending with caption
- **v2.2**: Added code execution via run_code - Much faster than snapshots!
- **v2.1**: Added exit_chat after sending - Critical for reply capture!
- **v2.0**: Persistent sessions, contact cache, optimized selectors
- **v1.0**: Basic functionality, new browser per send

