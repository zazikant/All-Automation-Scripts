#!/usr/bin/env python3
"""
WhatsApp Message Sender using Playwright
More reliable than PyWhatKit - uses browser automation directly

Features:
- Send single messages (works for new and existing contacts)
- Send images
- Batch sending with rate limiting (5 per batch, 2 min delay)
- Check for replies and log to CSV (sent message + reply in same row)
"""

from playwright.sync_api import sync_playwright
import time
import os
import csv
import json
from datetime import datetime

MESSAGES_CSV = "/home/zazikant/whatsapp_messages.csv"

def log_sent_message(contact, message, message_type="text"):
    """
    Log a sent message to CSV. Creates new row with empty reply column.
    Reply will be filled when check_for_replies runs.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format the message for display
    if message_type == "image":
        display_msg = f"Image: {message}" if message else "Image sent"
    else:
        display_msg = message[:200] if message else "(empty)"
    
    file_exists = os.path.exists(MESSAGES_CSV)
    
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
    
    print(f"📝 Logged sent message to {contact}: {display_msg[:50]}...")


def get_contact_name_from_phone(phone):
    """Simple mapping for known contacts - can be expanded."""
    # Known contacts mapping
    contacts_map = {
        "+919869101909": "Shashikant Home",
        "+918999001625": "Chandrakant Shivadekar GEM",
        "+918976167591": "Jaideep Singh BD GEM",
    }
    return contacts_map.get(phone, phone)


def update_reply_for_message(contact, reply_text):
    """
    Find the most recent sent message to this contact without a reply
    and update the reply column.
    """
    if not os.path.exists(MESSAGES_CSV):
        return False
    
    # Read all rows
    rows = []
    with open(MESSAGES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find the last row for this contact with empty reply
    updated = False
    for i in range(len(rows) - 1, -1, -1):
        row = rows[i]
        if row.get("contact", "").strip() == contact.strip() and not row.get("reply", "").strip():
            rows[i]["reply"] = reply_text[:500]  # Limit reply length
            updated = True
            print(f"✅ Updated reply for {contact}: {reply_text[:50]}...")
            break
    
    if updated:
        # Write back
        with open(MESSAGES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "contact", "sent_message", "reply"])
            writer.writeheader()
            writer.writerows(rows)
    
    return updated


def send_whatsapp_message(phone_number, message, headless=False):
    """
    Send a WhatsApp message using Playwright.
    
    Uses URL method: https://web.whatsapp.com/send?phone=...&text=...
    This works seamlessly for both existing and new contacts.
    
    Args:
        phone_number: Full phone number with country code (e.g., +919876543210)
        message: The message text to send
        headless: Whether to run browser in headless mode (default: False)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        print("Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com")
        
        # Wait for login
        try:
            page.wait_for_selector('[data-testid="chat-list-search"]', timeout=60000)
            print("Logged in!")
        except:
            print("Please scan QR code to login. Waiting...")
            try:
                page.wait_for_selector('[data-testid="chat-list-search"]', timeout=120000)
                print("QR code scanned!")
            except:
                print("Timeout waiting for QR scan")
                browser.close()
                return False
        
        # Use URL method - opens chat with message pre-filled
        encoded_message = message.replace(" ", "%20").replace("\n", "%0A")
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
        
        print(f"Opening chat for {phone_number}...")
        page.goto(url)
        
        # Wait for compose box
        try:
            page.wait_for_selector('[data-testid="conversation-compose-box-input"]', timeout=30000)
            print("Chat loaded!")
        except:
            print(f"Could not load chat for {phone_number}")
            browser.close()
            return False
        
        time.sleep(0.5)
        
        # Send via button or Enter key
        try:
            page.locator('[data-testid="send"]').click()
        except:
            page.keyboard.press("Enter")
        
        time.sleep(1)
        print(f"✅ Message sent to {phone_number}")
        
        # Log the sent message
        contact_name = get_contact_name_from_phone(phone_number)
        log_sent_message(contact_name, message, message_type="text")
        
        browser.close()
        return True


def send_whatsapp_image(phone_number, image_path, caption=""):
    """
    Send an image via WhatsApp using Playwright.
    
    IMPORTANT: Must use "Photos & videos" menu option, NOT direct file input.
    Direct file input sends as sticker instead of image!
    
    Args:
        phone_number: Full phone number with country code
        image_path: Path to the image file
        caption: Optional caption for the image
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com")
        
        try:
            page.wait_for_selector('[data-testid="chat-list-search"]', timeout=60000)
            print("Logged in!")
        except:
            print("Please scan QR code...")
            try:
                page.wait_for_selector('[data-testid="chat-list-search"]', timeout=120000)
            except:
                print("Timeout")
                browser.close()
                return False
        
        # Navigate to chat
        url = f"https://web.whatsapp.com/send?phone={phone_number}"
        print(f"Opening chat for {phone_number}...")
        page.goto(url)
        
        try:
            page.wait_for_selector('[data-testid="conversation-compose-box-input"]', timeout=30000)
            print("Chat opened!")
        except:
            print(f"Could not find chat")
            browser.close()
            return False
        
        # Click attach button - CRITICAL: Must click "Photos & videos" menu option
        try:
            page.click('[data-testid="conversation-attachment-button"]')
            time.sleep(0.5)
        except:
            print("Attach button not found")
            browser.close()
            return False
        
        # IMPORTANT: Click "Photos & videos" option to avoid sending as sticker
        try:
            page.click('text=Photos & videos')
            time.sleep(0.5)
        except:
            print("Could not find Photos & videos option")
            browser.close()
            return False
        
        # Now upload file via file chooser
        try:
            # Set files directly on the page's file chooser
            page.locator('input[type="file"]').set_input_files(image_path)
            time.sleep(2)
        except:
            print("Could not upload file")
            browser.close()
            return False
        
        # Add caption if provided
        if caption:
            try:
                page.wait_for_selector('[data-testid="caption-input"]', timeout=5000)
                page.locator('[data-testid="caption-input"]').fill(caption)
                time.sleep(0.5)
            except:
                pass  # Caption might not be supported
        
        # Click Send button in preview modal
        try:
            page.wait_for_selector('[data-testid="send"]', timeout=10000)
            page.click('[data-testid="send"]')
            print(f"✅ Image sent to {phone_number}")
            
            # Log the sent message
            image_name = os.path.basename(image_path)
            contact_name = get_contact_name_from_phone(phone_number)
            log_sent_message(contact_name, image_name, message_type="image")
            
            time.sleep(2)
            browser.close()
            return True
        except:
            print("Could not send")
            browser.close()
            return False


def send_whatsapp_batch(contacts, message, batch_size=5, batch_delay=120, individual_delay=3):
    """
    Send messages to multiple contacts with rate limiting.
    
    Args:
        contacts: List of phone numbers (with country code)
        message: Message to send to all contacts
        batch_size: Number of messages per batch (default: 5)
        batch_delay: Delay between batches in seconds (default: 120 = 2 minutes)
        individual_delay: Delay between each message in seconds (default: 3)
    
    Returns:
        Dictionary with success/failure counts
    """
    results = {"success": [], "failed": [], "total": len(contacts)}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com")
        
        try:
            page.wait_for_selector('[data-testid="chat-list-search"]', timeout=60000)
            print("Logged in!")
        except:
            print("Please scan QR code...")
            try:
                page.wait_for_selector('[data-testid="chat-list-search"]', timeout=120000)
                print("QR scanned!")
            except:
                print("Timeout")
                browser.close()
                return results
        
        total_sent = 0
        
        for i, phone in enumerate(contacts):
            batch_num = i // batch_size + 1
            batch_position = i % batch_size + 1
            
            print(f"\n[{batch_num}] {batch_position}/{batch_size}: {phone}")
            
            encoded_message = message.replace(" ", "%20").replace("\n", "%0A")
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            
            try:
                page.goto(url)
                page.wait_for_selector('[data-testid="conversation-compose-box-input"]', timeout=15000)
                
                # Send
                try:
                    page.locator('[data-testid="send"]').click()
                except:
                    page.keyboard.press("Enter")
                
                print(f"✅ Sent")
                
                # Log the sent message
                contact_name = get_contact_name_from_phone(phone)
                log_sent_message(contact_name, message, message_type="text")
                
                results["success"].append(phone)
                total_sent += 1
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                results["failed"].append(phone)
            
            # Delays
            if batch_position < batch_size and i < len(contacts) - 1:
                time.sleep(individual_delay)
            
            if batch_position == batch_size and i < len(contacts) - 1:
                print(f"⏳ Batch complete. Waiting {batch_delay}s...")
                time.sleep(batch_delay)
        
        browser.close()
    
    print(f"\n{'='*50}")
    print(f"Results: {len(results['success'])}/{results['total']} sent")
    if results["failed"]:
        print(f"Failed: {results['failed']}")
    
    return results


def load_last_message_ids(state_file="message_state.json"):
    """Load last known message IDs from file"""
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            return json.load(f)
    return {}


def save_last_message_ids(state, state_file="message_state.json"):
    """Save last known message IDs to file"""
    with open(state_file, 'w') as f:
        json.dump(state, f)


def check_for_replies(state_file="message_state.json"):
    """
    Check all chats for new messages (replies) and update CSV.
    Finds the most recent sent message to each contact and updates the reply column.
    """
    last_ids = load_last_message_ids(state_file)
    new_replies = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com")
        
        try:
            page.wait_for_selector('[data-testid="chat-list-search"]', timeout=60000)
            print("Logged in!")
        except:
            print("Scan QR...")
            try:
                page.wait_for_selector('[data-testid="chat-list-search"]', timeout=120000)
            except:
                print("Timeout")
                browser.close()
                return []
        
        # Get chats
        try:
            chat_list = page.locator('[data-testid="chat-list"]')
            chat_rows = chat_list.locator('div > div[tabindex]').all()
        except:
            print("No chats found")
            browser.close()
            return []
        
        print(f"Checking {len(chat_rows)} chats...")
        
        for row in chat_rows:
            try:
                # Get contact name
                try:
                    title = row.locator('span[class*="title"], span[title]').first
                    contact = title.inner_text() if title.count() > 0 else "Unknown"
                except:
                    contact = "Unknown"
                
                # Click to load messages
                row.click()
                time.sleep(1.5)
                
                # Get last message
                messages = page.locator('[data-testid="message"]').all()
                if not messages:
                    continue
                
                last_msg = messages[-1]
                msg_id = last_msg.get_attribute('data-id') or str(hash(last_msg.inner_text()))
                
                # Check if from them (not us)
                is_outgoing = last_msg.locator('[data-testid="msg-outgoing"]').count() > 0
                
                if not is_outgoing:
                    msg_text = last_msg.locator('span[class*="copyable-text"]').first.inner_text()
                    
                    if contact not in last_ids or last_ids[contact] != msg_id:
                        # Update the CSV with this reply
                        updated = update_reply_for_message(contact, msg_text)
                        if updated:
                            print(f"📩 {contact}: {msg_text[:50]}...")
                        new_replies.append({
                            "contact": contact,
                            "message": msg_text
                        })
                        last_ids[contact] = msg_id
                
            except:
                continue
        
        browser.close()
    
    save_last_message_ids(last_ids, state_file)
    
    print(f"\n✅ Checked for replies - found {len(new_replies)} new replies")
    
    return new_replies


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch":
            # Batch: python send_whatsapp.py --batch "phone1,phone2,phone3" "message"
            contacts = [p.strip() for p in sys.argv[2].split(",")]
            msg = sys.argv[3] if len(sys.argv) > 3 else "Hello!"
            send_whatsapp_batch(contacts, msg)
        elif sys.argv[1] == "--check-replies":
            check_for_replies()
        elif sys.argv[1] == "--image":
            # Image: python send_whatsapp.py --image +91XXXXXXXXXX /path/img.jpg "caption"
            target = sys.argv[2]
            image_path = sys.argv[3]
            caption = sys.argv[4] if len(sys.argv) > 4 else ""
            send_whatsapp_image(target, image_path, caption)
        else:
            # Single: python send_whatsapp.py +91XXXXXXXXXX "message"
            target = sys.argv[1]
            msg = sys.argv[2]
            send_whatsapp_message(target, msg)
    else:
        print("WhatsApp Sender")
        print("Usage:")
        print("  python send_whatsapp.py +91XXXXXXXXXX \"message\"")
        print("  python send_whatsapp.py --image +91XXXXXXXXXX /path/img.jpg")
        print("  python send_whatsapp.py --batch \"p1,p2,p3\" \"message\"")
        print("  python send_whatsapp.py --check-replies")
