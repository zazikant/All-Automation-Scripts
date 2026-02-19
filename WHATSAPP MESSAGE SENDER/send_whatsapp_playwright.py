#!/usr/bin/env python3
"""
WhatsApp Message Sender using Playwright
More reliable than PyWhatKit - uses browser automation directly
"""

from playwright.sync_api import sync_playwright
import time
import os


def send_whatsapp_message(phone_number, message, headless=False):
    """
    Send a WhatsApp message using Playwright.
    
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
        
        print(f"Please scan QR code to login. Waiting...")
        page.wait_for_url("**/web.whatsapp.com**", wait_until="networkidle")
        
        # Wait for user to scan QR code - check for the chat search box
        try:
            page.wait_for_selector('[data-testid="chat-list-search"]', timeout=60000)
            print("QR code scanned successfully!")
        except Exception as e:
            print(f"Timeout waiting for QR scan. Please scan within 60 seconds.")
            browser.close()
            return False
        
        # Construct WhatsApp Web URL for the phone number
        # Format: https://web.whatsapp.com/send?phone=+91XXXXXXXXXX&text=encoded_message
        encoded_message = message.replace(" ", "%20").replace("\n", "%0A")
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
        
        print(f"Opening chat for {phone_number}...")
        page.goto(url)
        
        # Wait for the chat to load
        try:
            page.wait_for_selector('[data-testid="conversation-compose-box-input"]', timeout=30000)
            print("Chat opened!")
        except Exception as e:
            print(f"Could not find chat input. The number might not exist or is invalid.")
            browser.close()
            return False
        
        # If message wasn't pre-filled in URL, type it
        compose_box = page.locator('[data-testid="conversation-compose-box-input"]')
        if not message or message.strip() == "":
            compose_box.fill(message)
        
        # Wait a moment for any dynamic content
        time.sleep(1)
        
        # Find and click the send button
        try:
            send_button = page.locator('[data-testid="send"]')
            send_button.click()
            print(f"✅ Message sent successfully to {phone_number}")
            
            # Wait a moment to ensure message is sent
            time.sleep(2)
            
            browser.close()
            return True
        except Exception as e:
            print(f"Could not find send button: {e}")
            # Try pressing Enter as fallback
            try:
                page.keyboard.press("Enter")
                print(f"✅ Message sent (Enter key) to {phone_number}")
                time.sleep(2)
                browser.close()
                return True
            except:
                print("❌ Failed to send message")
                browser.close()
                return False


def send_whatsapp_message_with_session(phone_number, message, session_path="whatsapp_session"):
    """
    Send message using a persistent session to avoid QR scan every time.
    
    Args:
        phone_number: Phone number with country code
        message: Message to send
        session_path: Path to store browser session data
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        # Try to load existing session
        try:
            context = browser.new_context(storage_state=session_path)
            print("Loaded existing session")
        except:
            context = browser.new_context()
            print("New session - QR scan required")
        
        page = context.new_page()
        
        print("Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com")
        
        # Check if already logged in
        try:
            page.wait_for_selector('[data-testid="chat-list-search"]', timeout=10000)
            print("Already logged in!")
        except:
            print("Please scan QR code to login...")
            try:
                page.wait_for_selector('[data-testid="chat-list-search"]', timeout=60000)
                print("QR code scanned!")
                
                # Save session for future use
                context.storage_state(path=session_path)
                print(f"Session saved to {session_path}")
            except:
                print("Timeout waiting for QR scan")
                browser.close()
                return False
        
        # Send message
        encoded_message = message.replace(" ", "%20").replace("\n", "%0A")
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
        
        print(f"Opening chat for {phone_number}...")
        page.goto(url)
        
        try:
            page.wait_for_selector('[data-testid="conversation-compose-box-input"]', timeout=15000)
            
            # Send via button or Enter
            try:
                page.locator('[data-testid="send"]').click()
            except:
                page.keyboard.press("Enter")
            
            print(f"✅ Message sent to {phone_number}")
            time.sleep(2)
            browser.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            browser.close()
            return False


if __name__ == "__main__":
    import sys
    
    MY_NUMBER = "+917777016824"
    
    if len(sys.argv) > 2:
        # Command line usage: python send_whatsapp_playwright.py +91XXXXXXXXXX "message"
        target = sys.argv[1]
        msg = sys.argv[2]
        send_whatsapp_message(target, msg, headless=False)
    else:
        # Default usage
        print("WhatsApp Message Sender (Playwright)")
        print("=" * 40)
        
        # Example: Send to self
        send_whatsapp_message(MY_NUMBER, "Hello from Playwright! This is a test message.")
