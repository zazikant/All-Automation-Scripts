# Email Bounce Processor Workflow

## 1. Overview

This document outlines the workflow for using a Python script in conjunction with the Gemini CLI agent to process email bounce notifications from an IMAP account. 

The system is designed to be an interactive, batch-by-batch process that identifies bounced emails, uses the Gemini agent's intelligence to interpret the reason for the bounce, and saves the results into individual CSV files.

This method was specifically designed to work around potential API rate limits by using the agent for analysis, ensuring that the process is both robust and does not depend on a personal API key.

## 2. Components

- **`process_bounces.py`**: The core "Fetcher" script. This Python script is responsible for connecting to the email server, fetching a small batch of **new** emails, and printing their raw text content to the console for the agent to read. It now ignores emails with "DMARC" in the subject.

- **`last_processed_uid.txt`**: A state file that stores the Unique Identifier (UID) of the last email processed. This ensures that the script only fetches new emails and doesn't re-process old ones.

- **`/output/` (directory)**: This folder is automatically created by the script and stores the resulting CSV files from each batch.

- **`GEMINI.md`**: This documentation file.

## 3. The Workflow

This is an interactive workflow that relies on a partnership between you and the Gemini CLI agent.

### Step 1: Configuration

Before running the process, you must configure the `process_bounces.py` script:

1.  Open `process_bounces.py`.
2.  Locate the **Configuration** section at the top of the file.
3.  Set the following values:
    - `IMAP_SERVER`: Your email server's address (e.g., `imap.yourprovider.com`).
    - `IMAP_USERNAME`: Your full email address.
    - `IMAP_PASSWORD`: Your email password. **It is highly recommended to use an App-Specific Password** if your email provider supports it, as this is more secure.
    - `BATCH_SIZE`: The number of emails to process per batch (we found that `5` is a good number for this interactive workflow).

### Step 2: Execution

Once the script is configured, you can start the process.

1.  Tell the Gemini agent to run the script. For example: "run the script" or "process the next batch".
2.  The agent will execute the following command:
    ```bash
    python3 runner.py
    ```
3.  The `runner.py` script will then execute `process_bounces.py` to fetch a single batch of **new** emails, ignoring DMARC reports, and print their content to the agent's console.

### Step 3: Analysis and CSV Export

This part is performed by the Gemini agent after the script runs.

1.  The agent will read the email text that the script provided.
2.  It will analyze each email to determine the bounce reason, error code, recipient, and the date the bounce email was received. The output format will be: "email id of receipient","bounce reason","error code","date of bounce email receievd"
3.  The agent will show you the analyzed results directly in the chat.
4.  Finally, the agent will save those results to a new, unique CSV file inside the `/home/zazikant/output/` directory.

### Step 4: Iteration

The process is designed to be run repeatedly in an interactive manner. After each batch is successfully processed and saved, the agent will ask for your permission to proceed with the next one. You can continue this loop for as many batches as you need. To process the next batch, simply instruct the agent to "run the script again" or "process the next batch".

## 4. Source Code

For reference, here is the final version of the `process_bounces.py` script:

```python
import os
import imaplib
import email
from email.header import decode_header
import logging
import time

# ---
# Configuration ---
# TODO: EDIT THESE VALUES
IMAP_SERVER = "mail.gemengserv.net"  # e.g., "imap.gmail.com"
IMAP_USERNAME = "news@gemengserv.net"
IMAP_PASSWORD = "H4ck-y0u"  # Use an App Password

BATCH_SIZE = 5
STATE_FILE = "last_processed_uid.txt"
# ---
# End Configuration ---

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---
# Separator for easy parsing by the agent ---
EMAIL_SEPARATOR = "---GEMINI_EMAIL_SEPARATOR---"

def get_last_uid():
    """Reads the last processed UID from the state file."""
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE, "r") as f:
        content = f.read().strip()
        return int(content) if content.isdigit() else 0

def save_last_uid(uid):
    """Saves the last processed UID to the state file."""
    with open(STATE_FILE, "w") as f:
        f.write(str(uid))

def get_email_body(msg):
    """Extracts the body of an email, preferring plain text."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" not in content_disposition and content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode()
                    return body # Return the first plain text part found
                except:
                    continue
    else:
        try:
            # Not a multipart message, just get the payload
            body = msg.get_payload(decode=True).decode()
        except:
            body = ""
    return body

def fetch_emails():
    """
    Connects to IMAP, fetches a batch of new emails based on the last processed UID,
    and prints their body to stdout.
    """
    mail = None
    last_uid = get_last_uid()
    try:
        logging.info(f"Connecting to IMAP server: {IMAP_SERVER}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USERNAME, IMAP_PASSWORD)
        mail.select("inbox")

        search_criteria = f"UID {last_uid + 1}:*"
        if last_uid == 0:
            search_criteria = "ALL"
            logging.info("No last UID found, searching for ALL emails.")
        else:
            logging.info(f"Searching for emails with UID greater than {last_uid}")

        status, messages = mail.uid('search', None, search_criteria)
        if status != "OK":
            logging.error("Failed to search for emails.")
            return

        email_uids = messages[0].split()
        if not email_uids:
            logging.info("No new emails found.")
            return

        logging.info(f"Found {len(email_uids)} new emails. Processing a batch of up to {BATCH_SIZE}.")

        processed_count = 0
        latest_uid = 0
        for uid in email_uids:
            if processed_count >= BATCH_SIZE:
                logging.info(f"Batch size of {BATCH_SIZE} reached.")
                break

            status, data = mail.uid('fetch', uid, "(RFC822)")
            if status != "OK":
                logging.warning(f"Failed to fetch email with UID {uid.decode()}")
                continue

            msg = email.message_from_bytes(data[0][1])

            # Decode the subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            # Ignore DMARC reports
            if "DMARC" in subject:
                logging.info(f"Ignoring DMARC report with UID {uid.decode()}")
                latest_uid = int(uid)
                continue

            # Get date
            date_tuple = email.utils.parsedate_tz(msg['Date'])
            if date_tuple:
                local_date = email.utils.mktime_tz(date_tuple)
                date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(local_date))
            else:
                date_str = "Date not found"

            body = get_email_body(msg)

            if body:
                # Print the separator and body for the agent to process
                print(EMAIL_SEPARATOR)
                print(f"---GEMINI_DATE_SEPARATOR---{date_str}")
                print(body)

                processed_count += 1
                latest_uid = int(uid)
                logging.info(f"Successfully fetched email with UID {uid.decode()}.")
            else:
                logging.warning(f"Could not extract plain text body from email with UID {uid.decode()}. Skipping.")

            time.sleep(1) # Be respectful to the IMAP server
        
        if latest_uid > 0:
            save_last_uid(latest_uid)
            logging.info(f"Saved last processed UID: {latest_uid}")


    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP Error: {e}. Please check your IMAP credentials and server settings.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if mail:
            mail.logout()
            logging.info("Logged out from IMAP server.")

if __name__ == "__main__":
    fetch_emails()