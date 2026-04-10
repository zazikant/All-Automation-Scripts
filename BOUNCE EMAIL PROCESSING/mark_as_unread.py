import imaplib
import logging

# --- Configuration ---
# Using the same credentials as process_bounces.py
IMAP_SERVER = "mail.gemengserv.net"
IMAP_USERNAME = "news@gemengserv.net"
IMAP_PASSWORD = "H4ck-y0u"
# --- End Configuration ---

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def mark_all_as_unread():
    """
    Connects to IMAP and marks all emails in the inbox as unread.
    """
    mail = None
    try:
        logging.info(f"Connecting to IMAP server: {IMAP_SERVER}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USERNAME, IMAP_PASSWORD)
        mail.select("inbox")

        logging.info("Searching for all emails.")
        status, messages = mail.uid('search', None, "ALL")
        if status != "OK":
            logging.error("Failed to search for emails.")
            return

        email_uids = messages[0].split()
        if not email_uids:
            logging.info("No emails found in the inbox.")
            return

        logging.info(f"Found {len(email_uids)} emails. Marking them as unread.")

        for uid in email_uids:
            mail.uid('store', uid, '-FLAGS', '(\Seen)')

        logging.info("All emails have been marked as unread.")

    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if mail:
            mail.logout()
            logging.info("Logged out from IMAP server.")

if __name__ == "__main__":
    mark_all_as_unread()
