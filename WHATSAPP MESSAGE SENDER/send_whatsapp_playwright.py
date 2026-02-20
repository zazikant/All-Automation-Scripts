#!/usr/bin/env python3
"""
WhatsApp Message Sender using Playwright - OPTIMIZED VERSION 2.2
Enhanced for speed and reliability with persistent sessions and contact caching

Features:
- Persistent browser sessions (no repeated QR scans)
- Contact cache for instant lookup
- Fast URL-based navigation
- Batch operations with single browser instance
- Smart retry logic with fallback selectors
- Auto-contact name detection
- Proper image sending (as photo, not sticker)

NOTE: For MCP Playwright, use browser_file_upload tool instead of setInputFiles()!
      Python's set_input_files() works fine in the Python script context.

Author: Enhanced by Claude
Version: 2.2
"""

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time
import os
import csv
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path

# Configuration
MESSAGES_CSV = "/home/zazikant/whatsapp_messages.csv"
SESSION_DIR = "/home/zazikant/whatsapp_session"
STATE_FILE = "/home/zazikant/message_state.json"

# Contact Cache - Maps phone numbers (last 10 digits) to contact names
# Update this with your frequent contacts for instant lookups
CONTACT_CACHE: Dict[str, str] = {
    "9869101909": "Shashikant Home",
    "8999001625": "Chandrakant Shivadekar GEM",
    "8976167591": "Jaideep Singh BD GEM",
    "9820937483": "Purva",
    # Add more contacts here!
}

# Rate limiting config
BATCH_SIZE = 5
BATCH_DELAY = 120  # seconds between batches
MESSAGE_DELAY = 3  # seconds between individual messages


class WhatsAppSender:
    """Efficient WhatsApp sender with persistent sessions and caching."""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None  # Will be set in start()
        self.is_logged_in = False
        self.playwright: Optional[Any] = None
        
    def _ensure_session_dir(self):
        """Create session directory if it doesn't exist."""
        Path(SESSION_DIR).mkdir(parents=True, exist_ok=True)
    
    def start(self) -> bool:
        """Start browser with persistent session storage."""
        self._ensure_session_dir()
        
        try:
            self.playwright = sync_playwright().start()
            
            # Launch browser with persistent context
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context with storage state persistence
            if self.browser is None:
                raise RuntimeError("Browser failed to launch")
            storage_state_path = f"{SESSION_DIR}/storage_state.json"
            initial_storage = storage_state_path if os.path.exists(storage_state_path) else None
            self.context = self.browser.new_context(
                storage_state=initial_storage,
                viewport={'width': 1280, 'height': 800}
            )
            
            self.page = self.context.new_page()
            
            # Check if already logged in
            if self._check_login_status():
                print("✅ Session restored - already logged in!")
                self.is_logged_in = True
                return True
            
            # Need to login
            print("🔐 Opening WhatsApp Web...")
            self.page.goto("https://web.whatsapp.com")
            
            # Wait for login
            if self._wait_for_login():
                self._save_session()
                self.is_logged_in = True
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error starting browser: {e}")
            return False
    
    def _check_login_status(self) -> bool:
        """Quick check if already logged in."""
        page = self.page
        if page is None:
            return False
        try:
            page.goto("https://web.whatsapp.com")
            # Try to find chat list quickly
            page.wait_for_selector('[data-testid="chat-list-search"]', timeout=8000)
            return True
        except:
            return False
    
    def _wait_for_login(self, timeout: int = 120) -> bool:
        """Wait for user to scan QR code."""
        page = self.page
        if page is None:
            return False
        try:
            print("⏳ Waiting for QR scan... (timeout: {}s)".format(timeout))
            page.wait_for_selector('[data-testid="chat-list-search"]', timeout=timeout * 1000)
            print("✅ QR code scanned!")
            return True
        except:
            print("❌ Timeout waiting for QR scan")
            return False
    
    def _save_session(self):
        """Save browser session for next time."""
        ctx = self.context
        if ctx is None:
            return
        try:
            storage_path = f"{SESSION_DIR}/storage_state.json"
            ctx.storage_state(path=storage_path)
            print("💾 Session saved for next time")
        except Exception as e:
            print(f"⚠️ Could not save session: {e}")
    
    def stop(self):
        """Stop browser and save session."""
        if self.is_logged_in:
            self._save_session()
        
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to full international format."""
        # Remove spaces, dashes, and + prefix for extraction
        cleaned = re.sub(r'[\s\-+]', '', phone)
        
        # If already has country code (more than 10 digits)
        if len(cleaned) > 10:
            return f"+{cleaned}"
        
        # Default to India (+91) if no country code
        return f"+91{cleaned}"
    
    def _get_contact_name(self, phone: str, auto_detect: bool = False) -> str:
        """Get contact name from cache or auto-detect."""
        cleaned = re.sub(r'[\s\-+]', '', phone)
        last_10 = cleaned[-10:] if len(cleaned) >= 10 else cleaned
        
        # Check cache first
        if last_10 in CONTACT_CACHE:
            return CONTACT_CACHE[last_10]
        
        # Auto-detect from chat if requested
        if auto_detect and self.page is not None:
            page = self.page
            try:
                # Try to get name from chat header
                header = page.locator('header span[title], [data-testid="conversation-header-title"]').first
                if header.count() > 0:
                    name = header.inner_text()
                    if name and len(name) > 0:
                        # Cache it for next time
                        CONTACT_CACHE[last_10] = name
                        return name
            except:
                pass
        
        # Return formatted phone as fallback
        return f"+{cleaned}"
    
    def _wait_for_chat_load(self, timeout: int = 15) -> bool:
        """Wait for chat to fully load."""
        page = self.page
        if page is None:
            return False
        try:
            # Multiple selector strategies
            selectors = [
                '[data-testid="conversation-compose-box-input"]',
                'div[contenteditable="true"][data-tab="10"]',
                'footer div[contenteditable="true"]',
            ]
            
            for selector in selectors:
                try:
                    page.wait_for_selector(selector, timeout=timeout * 1000)
                    return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def _click_send(self) -> bool:
        """Click send button with multiple fallback strategies."""
        page = self.page
        if page is None:
            return False
        
        strategies = [
            lambda: page.locator('[data-testid="send"]').click(),
            lambda: page.locator('button[aria-label*="Send"]').click(),
            lambda: page.keyboard.press("Enter"),
            lambda: page.locator('span[data-icon="send"]').click(),
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                strategy()
                time.sleep(0.3)
                return True
            except Exception as e:
                if i == len(strategies) - 1:
                    print(f"❌ Could not send: {e}")
                    return False
                continue
        
        return False
    
    def send_message(self, phone: str, message: str, auto_name: bool = False) -> Tuple[bool, str]:
        """
        Send text message to phone number.
        
        Returns:
            (success: bool, contact_name: str)
        """
        page = self.page
        if page is None or not self.is_logged_in:
            print("❌ Not logged in!")
            return False, phone
        
        full_phone = self._normalize_phone(phone)
        
        try:
            # Use URL method - fastest way
            encoded_msg = message.replace(" ", "%20").replace("\n", "%0A")
            url = f"https://web.whatsapp.com/send?phone={full_phone}&text={encoded_msg}"
            
            print(f"📱 Opening chat for {full_phone}...")
            page.goto(url)
            
            # Wait for chat to load
            if not self._wait_for_chat_load(timeout=15):
                print(f"❌ Chat did not load for {full_phone}")
                return False, phone
            
            # Get contact name
            contact_name = self._get_contact_name(phone, auto_detect=auto_name)
            
            # Send message
            if self._click_send():
                print(f"✅ Sent to {contact_name}: {message[:50]}...")
                
                # Log to CSV
                log_sent_message(contact_name, message, "text")
                
                return True, contact_name
            else:
                return False, contact_name
                
        except Exception as e:
            print(f"❌ Error sending to {phone}: {e}")
            return False, phone
    
    def exit_chat(self) -> bool:
        """
        Exit current chat and go back to chat list.
        This is IMPORTANT for capturing replies properly - WhatsApp Web doesn't 
        always show new messages in real-time when inside a chat.
        
        Returns:
            success: bool
        """
        page = self.page
        if page is None:
            return False
        
        try:
            # Try clicking the back button (chevron left) in header
            back_selectors = [
                'button[aria-label*="Back"]',
                'button[title="Back"]', 
                '[data-testid="btn-back"]',
                'button[data-testid="back"]',
                'button[aria-label="Back"]',
            ]
            
            for selector in back_selectors:
                try:
                    if page.locator(selector).first.is_visible(timeout=2000):
                        page.locator(selector).first.click()
                        time.sleep(0.5)
                        print("✅ Exited chat to list")
                        return True
                except:
                    continue
            
            # Alternative: navigate directly to chat list
            page.goto("https://web.whatsapp.com/")
            time.sleep(1)
            print("✅ Navigated back to chat list")
            return True
            
        except Exception as e:
            print(f"⚠️ Could not exit chat: {e}")
            return False
    
    def send_message_and_exit(self, phone: str, message: str, auto_name: bool = False) -> Tuple[bool, str]:
        """
        Send message and exit chat to ensure replies are captured properly.
        
        Process:
        1. Send message
        2. Exit chat (go back to chat list) - CRITICAL for reply capture
        3. This allows WhatsApp to properly track new messages
        
        Returns:
            (success: bool, contact_name: str)
        """
        success, name = self.send_message(phone, message, auto_name)
        if success:
            self.exit_chat()
        return success, name
    
    def send_image(self, phone: str, image_path: str, caption: str = "") -> Tuple[bool, str]:
        """
        Send image as photo (NOT sticker) with optional caption.
        
        Returns:
            (success: bool, contact_name: str)
        """
        page = self.page
        if page is None or not self.is_logged_in:
            print("❌ Not logged in!")
            return False, phone
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return False, phone
        
        full_phone = self._normalize_phone(phone)
        
        try:
            # Open chat
            url = f"https://web.whatsapp.com/send?phone={full_phone}"
            print(f"📱 Opening chat for {full_phone}...")
            page.goto(url)
            
            if not self._wait_for_chat_load(timeout=15):
                print(f"❌ Chat did not load")
                return False, phone
            
            contact_name = self._get_contact_name(phone, auto_detect=True)
            
            # Click attach button
            print("📎 Clicking attachment button...")
            attach_clicked = False
            
            attach_selectors = [
                '[data-testid="conversation-attachment-button"]',
                'button[title*="Attach"]',
                'button[aria-label*="Attach"]',
                '[data-icon="attach-menu-plus"]',
            ]
            
            for selector in attach_selectors:
                try:
                    page.locator(selector).first.click()
                    attach_clicked = True
                    time.sleep(0.5)
                    break
                except:
                    continue
            
            if not attach_clicked:
                print("❌ Could not click attach button")
                return False, contact_name
            
            # Click "Photos & videos" menu (IMPORTANT: not "Document")
            print("🖼️ Clicking Photos & videos...")
            try:
                page.click('text=Photos & videos', timeout=5000)
                time.sleep(0.5)
            except:
                # Try alternative selectors
                try:
                    page.locator('button:has-text("Photos")').first.click()
                except:
                    print("❌ Could not find Photos & videos option")
                    return False, contact_name
            
            # Upload file
            print(f"📤 Uploading {os.path.basename(image_path)}...")
            try:
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(image_path)
                time.sleep(2)  # Wait for preview to load
            except Exception as e:
                print(f"❌ Could not upload file: {e}")
                return False, contact_name
            
            # Add caption if provided
            if caption:
                print(f"📝 Adding caption...")
                try:
                    # Try multiple caption input selectors
                    caption_selectors = [
                        '[data-testid="caption-input"]',
                        'div[contenteditable="true"][data-tab="1"]',
                        'div[contenteditable="true"]',
                    ]
                    
                    for selector in caption_selectors:
                        try:
                            caption_box = page.locator(selector).first
                            if caption_box.count() > 0:
                                caption_box.fill(caption)
                                time.sleep(0.5)
                                break
                        except:
                            continue
                except:
                    pass  # Caption not critical
            
            # Click send in preview modal
            print("📨 Sending image...")
            try:
                # Try multiple send button selectors in modal
                send_selectors = [
                    '[data-testid="send"]',  # In preview modal
                    'div[role="button"]:has(span[data-icon="send"])',
                    'button:has-text("Send")',
                ]
                
                for selector in send_selectors:
                    try:
                        page.locator(selector).first.click()
                        print(f"✅ Image sent to {contact_name}")
                        
                        # Log
                        log_sent_message(contact_name, f"{os.path.basename(image_path)} | {caption}", "image")
                        
                        time.sleep(1)
                        return True, contact_name
                    except:
                        continue
                
                print("❌ Could not click send in preview")
                return False, contact_name
                
            except Exception as e:
                print(f"❌ Error sending image: {e}")
                return False, contact_name
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, phone

    def send_image_and_exit(self, phone: str, image_path: str, caption: str = "") -> Tuple[bool, str]:
        """
        Send image and exit chat to ensure replies are captured properly.
        
        Returns:
            (success: bool, contact_name: str)
        """
        success, name = self.send_image(phone, image_path, caption)
        if success:
            self.exit_chat()
        return success, name
    
    def send_batch(self, phones: List[str], message: str) -> Dict:
        """
        Send messages to multiple contacts with rate limiting.
        Uses single browser session for efficiency.
        During batch delay, checks for replies from previous messages.
        """
        results = {"success": [], "failed": []}
        
        for i, phone in enumerate(phones):
            batch_num = (i // BATCH_SIZE) + 1
            pos_in_batch = (i % BATCH_SIZE) + 1
            
            print(f"\n[{batch_num}] {pos_in_batch}/{min(BATCH_SIZE, len(phones) - (batch_num-1)*BATCH_SIZE)}: {phone}")
            
            # FIRST: Check for any unread replies before sending new message
            # This catches replies to previous messages that weren't captured yet
            print("  🔍 Checking for pending replies...")
            self._check_and_capture_unread_replies(phone)
            
            success, name = self.send_message(phone, message, auto_name=True)
            
            if success:
                results["success"].append({"phone": phone, "name": name})
            else:
                results["failed"].append(phone)
            
            # Rate limiting
            if pos_in_batch < BATCH_SIZE and i < len(phones) - 1:
                time.sleep(MESSAGE_DELAY)
            
            if pos_in_batch == BATCH_SIZE and i < len(phones) - 1:
                print(f"⏳ Batch {batch_num} complete. Waiting {BATCH_DELAY}s... (checking for replies)")
                
                # Check for replies during the wait time
                self._check_replies_during_delay(BATCH_DELAY - 10)
                
                time.sleep(10)  # Small buffer
        
        # Final reply check after all batches
        print(f"\n🔍 Final reply check...")
        self._check_replies_during_delay(15)
        
        print(f"\n{'='*60}")
        print(f"✅ Success: {len(results['success'])}/{len(phones)}")
        if results["failed"]:
            print(f"❌ Failed: {results['failed']}")
        
        return results
    
    def _check_and_capture_unread_replies(self, phone: str) -> List[Dict]:
        """
        Check for unread replies in a specific chat BEFORE sending a new message.
        This captures any replies that came after previous messages but before
        the new message we're about to send.
        """
        page = self.page
        if page is None:
            return []
        
        new_replies = []
        
        try:
            # Try to navigate to chat via URL (faster)
            try:
                phone_clean = phone.replace("+", "").replace(" ", "")
                page.goto(f"https://web.whatsapp.com/send?phone={phone_clean}", timeout=10000)
                time.sleep(2)
            except:
                pass
            
            # Check for unread messages
            try:
                # Look for unread indicator in the chat
                unreadSelectors = [
                    'span[class*="message-unread"]',
                    'span[class*="unread-count"]',
                    'div[class*="unread"]',
                    '[data-testid="unread-count"]'
                ]
                
                has_unread = False
                for sel in unreadSelectors:
                    if page.locator(sel).count() > 0:
                        has_unread = True
                        break
                
                if not has_unread:
                    # Also check if there are any incoming messages at all
                    msgs = page.locator('[data-testid="msg-container"], div[data-id]').all()
                    if msgs:
                        # Check if any messages are incoming (not from us)
                        for msg in msgs:
                            is_outgoing = msg.locator('[data-testid="msg-outgoing"], [data-testid="msg-dblcheck"]').count() > 0
                            if not is_outgoing:
                                # Found incoming message - check if we have a sent message before it
                                break
                    return []
                
                # Get contact name
                try:
                    header = page.locator('header').first
                    contact = "Unknown"
                    if header.locator('span[title]').count() > 0:
                        contact = header.locator('span[title]').inner_text()
                except:
                    contact = phone
                
                # Get all messages
                msgs = page.locator('[data-testid="msg-container"], div[data-id]').all()
                if not msgs:
                    return []
                
                # Find the last outgoing message
                last_outgoing_idx = -1
                for idx, msg in enumerate(msgs):
                    is_outgoing = msg.locator('[data-testid="msg-outgoing"], [data-testid="msg-dblcheck"]').count() > 0
                    if is_outgoing:
                        last_outgoing_idx = idx
                
                # Collect all incoming messages after the last outgoing
                all_replies = []
                for idx in range(last_outgoing_idx + 1, len(msgs)):
                    msg = msgs[idx]
                    is_outgoing = msg.locator('[data-testid="msg-outgoing"], [data-testid="msg-dblcheck"]').count() > 0
                    if not is_outgoing:
                        msg_text_el = msg.locator('span[class*="selectable-text"], span.copyable-text').first
                        if msg_text_el.count() > 0:
                            reply_text = msg_text_el.inner_text()
                            if reply_text:
                                all_replies.append(reply_text)
                
                if all_replies:
                    combined_reply = " + ".join(all_replies)
                    if update_reply_for_message(contact, combined_reply):
                        print(f"  📩 Captured reply: {combined_reply[:50]}...")
                        new_replies.append({"contact": contact, "message": combined_reply})
            
            except Exception as e:
                pass  # Silently continue if check fails
        
        except Exception as e:
            pass
        
        return new_replies
    
    def _check_replies_during_delay(self, duration: int) -> List[Dict]:
        """
        Check for replies from contacts during the delay period.
        Splits the duration into multiple checks to be responsive.
        """
        page = self.page
        if page is None:
            return []
        
        last_ids = load_last_message_ids()
        new_replies = []
        
        # Split duration into chunks of ~10 seconds each
        chunk_size = 10
        chunks = max(1, duration // chunk_size)
        
        for _ in range(chunks):
            try:
                # Navigate to chat list
                try:
                    page.locator('[data-testid="chat-list"]').first.wait_for(timeout=2000)
                except:
                    pass
                
                chat_rows = page.locator('[data-testid="chat-list"] > div > div').all()
                
                for row in chat_rows[:15]:  # Check top 15 chats
                    try:
                        # Get contact name
                        try:
                            title_el = row.locator('span[title]').first
                            contact = title_el.inner_text() if title_el.count() > 0 else "Unknown"
                        except:
                            continue
                        
                        # Skip if we've already processed this contact recently
                        if contact in last_ids:
                            continue
                        
                        # Check if there are UNREAD messages (new responses)
                        # Unread indicator is typically a span with message count or "new" text
                        unread_indicator = row.locator('span[class*="message"], span[class*="unread"], div[class*="unread"]')
                        
                        # If no unread indicator, skip this chat (no new messages)
                        if unread_indicator.count() == 0:
                            continue
                        
                        print(f"📬 {contact} has new messages - checking...")
                        
                        # Click to open chat
                        row.click()
                        time.sleep(0.8)
                        
                        # Get all messages
                        msgs = page.locator('[data-testid="msg-container"], div[data-id]').all()
                        if not msgs:
                            continue
                        
                        # Find last outgoing message
                        last_outgoing_idx = -1
                        for idx, msg in enumerate(msgs):
                            is_outgoing = msg.locator('[data-testid="msg-outgoing"], [data-testid="msg-dblcheck"]').count() > 0
                            if is_outgoing:
                                last_outgoing_idx = idx
                        
                        if last_outgoing_idx == -1:
                            continue
                        
                        # Collect all replies after last outgoing
                        all_replies = []
                        for idx in range(last_outgoing_idx + 1, len(msgs)):
                            msg = msgs[idx]
                            is_outgoing = msg.locator('[data-testid="msg-outgoing"], [data-testid="msg-dblcheck"]').count() > 0
                            if not is_outgoing:
                                msg_text_el = msg.locator('span[class*="selectable-text"], span.copyable-text').first
                                if msg_text_el.count() > 0:
                                    reply_text = msg_text_el.inner_text()
                                    if reply_text:
                                        all_replies.append(reply_text)
                        
                        if all_replies:
                            combined_reply = " + ".join(all_replies)
                            msg_id = str(hash(combined_reply))
                            
                            if contact not in last_ids or last_ids[contact] != msg_id:
                                if update_reply_for_message(contact, combined_reply):
                                    print(f"📩 Reply from {contact}: {combined_reply[:50]}...")
                                    new_replies.append({"contact": contact, "message": combined_reply})
                                
                                last_ids[contact] = msg_id
                    
                    except:
                        continue
                
                save_last_message_ids(last_ids)
                
            except Exception as e:
                print(f"⚠️ Error during reply check: {e}")
            
            # Small delay between checks
            time.sleep(chunk_size)
        
        if new_replies:
            print(f"✅ Found {len(new_replies)} replies during batch delay")
        return new_replies
    
    def check_replies(self) -> List[Dict]:
        """Check for new replies from contacts."""
        page = self.page
        if page is None:
            return []
            
        last_ids = load_last_message_ids()
        new_replies = []
        
        try:
            # Get chat list
            chat_rows = page.locator('[data-testid="chat-list"] > div > div').all()
            print(f"🔍 Checking {len(chat_rows)} chats...")
            
            for row in chat_rows[:20]:  # Check first 20 chats
                try:
                    # Get contact name from row
                    try:
                        title_el = row.locator('span[title]').first
                        contact = title_el.inner_text() if title_el.count() > 0 else "Unknown"
                    except:
                        continue
                    
                    # Check if there are UNREAD messages (new responses from user)
                    # Unread indicator is typically a span with message count or "new" text
                    unread_indicator = row.locator('span[class*="message"], span[class*="unread"], div[class*="unread"]')
                    
                    # If no unread indicator, skip this chat (no new messages to read)
                    if unread_indicator.count() == 0:
                        continue
                    
                    print(f"📬 {contact} has new messages - checking...")
                    
                    # Click to open chat (this marks messages as read)
                    row.click()
                    time.sleep(1)
                    
                    # Get all messages in the chat
                    msgs = page.locator('[data-testid="msg-container"], div[data-id]').all()
                    if not msgs:
                        continue
                    
                    # Find the last sent message (outgoing) and collect all replies after it
                    last_outgoing_idx = -1
                    for i, msg in enumerate(msgs):
                        is_outgoing = msg.locator('[data-testid="msg-outgoing"], [data-testid="msg-dblcheck"]').count() > 0
                        if is_outgoing:
                            last_outgoing_idx = i
                    
                    # Collect all incoming messages after the last outgoing
                    all_replies = []
                    for i in range(last_outgoing_idx + 1, len(msgs)):
                        msg = msgs[i]
                        is_outgoing = msg.locator('[data-testid="msg-outgoing"], [data-testid="msg-dblcheck"]').count() > 0
                        if not is_outgoing:
                            msg_text_el = msg.locator('span[class*="selectable-text"], span.copyable-text').first
                            if msg_text_el.count() > 0:
                                reply_text = msg_text_el.inner_text()
                                if reply_text:
                                    all_replies.append(reply_text)
                    
                    if all_replies:
                        # Join all replies with +
                        combined_reply = " + ".join(all_replies)
                        msg_id = str(hash(combined_reply))
                        
                        # Check if new
                        if contact not in last_ids or last_ids[contact] != msg_id:
                            # Update CSV with combined reply
                            if update_reply_for_message(contact, combined_reply):
                                print(f"📩 {contact}: {combined_reply[:60]}...")
                                new_replies.append({"contact": contact, "message": combined_reply})
                            
                            last_ids[contact] = msg_id
                    
                except Exception as e:
                    continue
            
            save_last_message_ids(last_ids)
            print(f"✅ Found {len(new_replies)} new replies")
            return new_replies
            
        except Exception as e:
            print(f"❌ Error checking replies: {e}")
            return []


def log_sent_message(contact: str, message: str, message_type: str = "text"):
    """
    Log sent message to CSV.
    Groups messages by day and contact - multiple messages same day are concatenated with +.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_key = timestamp.split(" ")[0]  # YYYY-MM-DD
    
    if message_type == "image":
        display_msg = f"Image: {message}"
    else:
        display_msg = message
    
    file_exists = os.path.exists(MESSAGES_CSV)
    
    if file_exists:
        # Read existing rows
        rows = []
        with open(MESSAGES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Check if last row is same contact and same day - concatenate with +
        if rows:
            last_row = rows[-1]
            last_date = last_row.get("timestamp", "")[:10]
            last_contact = last_row.get("contact", "").strip()
            
            if last_contact == contact.strip() and last_date == date_key:
                # Same contact and same day - concatenate messages
                existing_sent = last_row.get("sent_message", "")
                new_sent = existing_sent + " + " + display_msg if existing_sent else display_msg
                rows[-1]["sent_message"] = new_sent
                rows[-1]["timestamp"] = timestamp  # Update timestamp to latest
                
                # Clear the reply since it's now linked to the concatenated message
                rows[-1]["reply"] = ""
                
                with open(MESSAGES_CSV, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=["timestamp", "contact", "sent_message", "reply"])
                    writer.writeheader()
                    writer.writerows(rows)
                return
    
    # New row
    with open(MESSAGES_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "contact", "sent_message", "reply"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": timestamp,
            "contact": contact,
            "sent_message": display_msg,
            "reply": ""
        })


def update_reply_for_message(contact: str, reply_text: str) -> bool:
    """
    Update reply column in CSV for the most recent message to this contact.
    Multiple replies are concatenated with + until a new message is sent.
    """
    if not os.path.exists(MESSAGES_CSV):
        return False
    
    try:
        rows = []
        with open(MESSAGES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Find last row for this contact with empty reply or concatenate to existing reply
        updated = False
        for i in range(len(rows) - 1, -1, -1):
            row = rows[i]
            if row.get("contact", "").strip() == contact.strip():
                current_reply = row.get("reply", "").strip()
                
                if not current_reply:
                    # First reply for this message
                    rows[i]["reply"] = reply_text
                    updated = True
                else:
                    # Concatenate with + (user sent multiple replies without new message)
                    rows[i]["reply"] = current_reply + " + " + reply_text
                    updated = True
                break
        
        if updated:
            with open(MESSAGES_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "contact", "sent_message", "reply"])
                writer.writeheader()
                writer.writerows(rows)
        
        return updated
    except:
        return False


def load_last_message_ids() -> Dict:
    """Load last message IDs from state file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_last_message_ids(state: Dict):
    """Save last message IDs to state file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


# CLI Interface
def main():
    import sys
    
    args = sys.argv[1:]
    
    if not args:
        print("WhatsApp Sender v2.0 - Optimized")
        print("=" * 60)
        print("Usage:")
        print("  python send_whatsapp.py PHONE 'message'")
        print("  python send_whatsapp.py PHONE 'message' --auto-name")
        print("  python send_whatsapp.py --image PHONE /path/img.jpg 'caption'")
        print("  python send_whatsapp.py --batch 'p1,p2,p3' 'message'")
        print("  python send_whatsapp.py --check-replies")
        print("  python send_whatsapp.py --keep-alive")
        print("\nExamples:")
        print('  python send_whatsapp.py "+919869101909" "Hello!"')
        print('  python send_whatsapp.py "9869101909" "Hi" --auto-name')
        print('  python send_whatsapp.py --image "+919869101909" "./photo.jpg" "Check this out"')
        return
    
    # Parse arguments
    keep_alive = '--keep-alive' in sys.argv
    auto_name = '--auto-name' in sys.argv
    
    # Remove flags from args
    args = [a for a in args if not a.startswith('--')]
    
    with WhatsAppSender(headless=False) as sender:
        if not sender.is_logged_in:
            print("❌ Failed to login")
            return
        
        if '--batch' in sys.argv:
            # Batch mode
            phones = [p.strip() for p in args[0].split(',')]
            message = args[1] if len(args) > 1 else "Hello!"
            sender.send_batch(phones, message)
            
        elif '--image' in sys.argv:
            # Image mode
            phone = args[0]
            image_path = args[1]
            caption = args[2] if len(args) > 2 else ""
            success, name = sender.send_image(phone, image_path, caption)
            
        elif '--check-replies' in sys.argv:
            # Check replies
            sender.check_replies()
            
        else:
            # Single message
            phone = args[0]
            message = args[1] if len(args) > 1 else "Hello!"
            success, name = sender.send_message(phone, message, auto_name=auto_name)
        
        # Keep session alive if requested
        if keep_alive:
            print("\n💾 Session kept alive. Press Ctrl+C to exit.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Exiting...")


if __name__ == "__main__":
    main()
