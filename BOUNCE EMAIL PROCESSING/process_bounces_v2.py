import os
import re
import csv
import imaplib
import email
from email.header import decode_header
from email import policy
from email.parser import BytesParser
import logging
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

OUTPUT_DIR = "/home/zazikant/All-Automation-Scripts/BOUNCE EMAIL PROCESSING/output"
BATCH_COUNTER_FILE = os.path.join(OUTPUT_DIR, "batch_counter.txt")

def get_batch_number():
    if not os.path.exists(BATCH_COUNTER_FILE):
        return 1
    with open(BATCH_COUNTER_FILE, "r") as f:
        return int(f.read().strip()) + 1

def save_batch_number(batch_num):
    with open(BATCH_COUNTER_FILE, "w") as f:
        f.write(str(batch_num))

def save_batch_csv(bounces, batch_num):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = os.path.join(OUTPUT_DIR, f"batch_{batch_num}_results.csv")
    
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["email id of recipient", "bounce reason", "error code", "bounce type", "date of bounce email received"])
        for b in bounces:
            writer.writerow([
                b["recipient"],
                b["reason"],
                b["error_code"],
                b["bounce_type"],
                b["date"]
            ])
    
    logging.info(f"Saved batch {batch_num} to {filename}")
    return filename

# ---
# Configuration ---
IMAP_SERVER = "mail.gemengserv.net"
IMAP_USERNAME = "news@gemengserv.net"
IMAP_PASSWORD = "H4ck-y0u"

BATCH_SIZE = 5
STATE_FILE = "last_processed_uid.txt"

START_DATE = datetime(2026, 4, 1)
END_DATE = datetime(2026, 4, 30)
# ---
# End Configuration ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

EMAIL_SEPARATOR = "---GEMINI_EMAIL_SEPARATOR---"

@dataclass
class RFC3463Status:
    class_code: str
    subject_code: str
    detail_code: str
    full_code: str
    
    @property
    def is_permanent(self) -> bool:
        return self.class_code == '5'
    
    @property
    def is_temporary(self) -> bool:
        return self.class_code == '4'
    
    @property
    def is_success(self) -> bool:
        return self.class_code == '2'

STATUS_DESCRIPTIONS = {
    '5.1.1': 'Bad destination mailbox address',
    '5.1.2': 'Bad destination system address',
    '5.1.3': 'Bad destination mailbox address syntax',
    '5.2.1': 'Mailbox disabled, not accepting messages',
    '5.2.2': 'Mailbox full',
    '5.2.3': 'Message length exceeds administrative limit',
    '5.3.2': 'System not accepting network messages',
    '5.4.1': 'Unable to route',
    '5.5.0': 'Other or undefined protocol status',
    '5.5.1': 'Invalid command',
    '5.5.2': 'Syntax error',
    '5.6.1': 'Media not supported',
    '5.7.1': 'Delivery not authorized, message refused',
    '5.7.26': 'DMARC policy violation',
    '4.2.2': 'Mailbox full (temporary)',
    '4.3.1': 'Insufficient system resources',
    '4.3.2': 'Service not available',
    '4.4.1': 'Connection timed out',
    '4.4.7': 'Delivery time expired',
    '4.7.0': 'Delivery restricted by policy',
    '4.7.1': 'Delivery restricted due to policy',
}

BOUNCE_ACTIONS = {
    '5.1.1': ('hard_bounce', 'Bad destination mailbox - remove from list'),
    '5.1.2': ('hard_bounce', 'Bad destination domain - remove from list'),
    '5.2.1': ('hard_bounce', 'Mailbox disabled - remove from list'),
    '5.2.2': ('soft_bounce', 'Mailbox full - retry later'),
    '5.7.1': ('hard_bounce', 'Policy blocked - review authentication'),
    '5.7.26': ('hard_bounce', 'DMARC failed - fix DKIM/SPF'),
    '4.2.2': ('soft_bounce', 'Mailbox full - retry later'),
    '4.4.1': ('soft_bounce', 'Connection timeout - retry with backoff'),
    '4.4.7': ('soft_bounce', 'Delivery expired - retry fresh'),
    '4.7.0': ('soft_bounce', 'Policy throttling - retry later'),
    '4.7.1': ('soft_bounce', 'Policy throttling - retry later'),
}

fallback_hard_codes = ['550', '5.0.0', '5.1.0', '5.4.1', '5.4.14', 'user unknown', 'not found', 'invalid']
fallback_soft_codes = ['421', '450', '451', '452', '4.0.0', '4.2.2', 'downstream', 'timeout', 'try again', 'temporary']

def parse_rfc3463_status(status: str) -> Optional[RFC3463Status]:
    if not status:
        return None
    match = re.match(r'^([245])\.(\d+)\.(\d+)$', status.strip())
    if not match:
        return None
    class_code, subject_code, detail_code = match.groups()
    return RFC3463Status(
        class_code=class_code,
        subject_code=subject_code,
        detail_code=detail_code,
        full_code=status.strip()
    )

def get_status_description(status: str) -> str:
    parsed = parse_rfc3463_status(status)
    if not parsed:
        return 'Unknown status code'
    full_status = f"{parsed.class_code}.{parsed.subject_code}.{parsed.detail_code}"
    return STATUS_DESCRIPTIONS.get(full_status, f"Unknown ({full_status})")

def get_recommended_action(status_code: str) -> tuple:
    return BOUNCE_ACTIONS.get(status_code, ('unknown', 'Check manually'))

def classify_bounce(status_code: str) -> str:
    parsed = parse_rfc3463_status(status_code)
    if parsed:
        if parsed.class_code == '5':
            return 'hard_bounce'
        elif parsed.class_code == '4':
            return 'soft_bounce'
    return 'unknown'

def parse_dsn_email(raw_email: bytes):
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)
    is_dsn = False
    status = None
    action = None
    diagnostic_code = None
    recipient = None
    
    if msg.get_content_type() == 'multipart/report':
        report_type = msg.get_param('report-type')
        if report_type == 'delivery-status':
            is_dsn = True
    
    if is_dsn and msg.is_multipart():
        for part in msg.get_payload():
            if part.get_content_type() == 'message/delivery-status':
                status = part.get('Status')
                action = part.get('Action')
                diagnostic_code = part.get('Diagnostic-Code')
                final_recipient = part.get('Final-Recipient', '')
                if final_recipient and '; ' in final_recipient:
                    recipient = final_recipient.split('; ', 1)[1]
                break
    
    return is_dsn, status, action, diagnostic_code, recipient

def get_last_uid():
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE, "r") as f:
        content = f.read().strip()
        return int(content) if content.isdigit() else 0

def save_last_uid(uid):
    with open(STATE_FILE, "w") as f:
        f.write(str(uid))

def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" not in content_disposition and content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode()
                    return body
                except:
                    continue
    else:
        try:
            body = msg.get_payload(decode=True).decode()
        except:
            body = ""
    return body

def detect_bounce_from_body(body: str, subject: str) -> tuple:
    if not body:
        return False, None
    
    body_lower = body.lower()
    subject_lower = subject.lower()
    
    bounce_indicators = ['undelivered', 'mail delivery', 'returned to sender', 'delivery failed', 
                     'delivery status', 'message could not be delivered', 'recipient address']
    has_bounce_indicator = any(ind in subject_lower or ind in body_lower for ind in bounce_indicators)
    
    if not has_bounce_indicator:
        return False, None
    
    rfc_status = None
    for code in ['5.7.26', '5.7.1', '5.4.14', '5.2.2', '5.2.1', '5.1.10', '5.1.1', '5.1.0', '5.0.0']:
        if code in body_lower:
            rfc_status = code
            break
    
    if not rfc_status:
        for code in ['4.7.1', '4.7.0', '4.4.7', '4.4.1', '4.3.2', '4.2.2', '4.0.0']:
            if code in body_lower:
                rfc_status = code
                break
    
    if not rfc_status:
        has_hard = any(code in body_lower for code in fallback_hard_codes)
        has_soft = any(code in body_lower for code in fallback_soft_codes)
        
        if has_hard:
            rfc_status = '5.1.1'
        elif has_soft:
            rfc_status = '4.4.1'
    
    return rfc_status is not None, rfc_status

IGNORED_RECIPIENTS = ['news@gemengserv.net', 'admin@gemengserv.com']

def extract_recipient_from_bounce(msg, body: str) -> str:
    for part in msg.walk():
        if part.get_content_type() == 'message/delivery-status':
            final_recipient = part.get('Final-Recipient', '')
            if final_recipient and '; ' in final_recipient:
                recipient = final_recipient.split('; ', 1)[1]
                if recipient and recipient not in IGNORED_RECIPIENTS:
                    return recipient
    
    patterns = [
        r'(?:failed|invalid|unknown recipient)[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'<([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>',
        r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ]
    
    body_lower = body.lower()
    for pattern in patterns:
        match = re.search(pattern, body_lower)
        if match:
            recipient = match.group(1)
            if recipient and recipient not in IGNORED_RECIPIENTS:
                return recipient
    
    return ''

def fetch_emails():
    mail = None
    last_uid = get_last_uid()
    try:
        logging.info(f"Connecting to IMAP server: {IMAP_SERVER}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USERNAME, IMAP_PASSWORD)
        mail.select("inbox")

        date_filter = f"SINCE {START_DATE.strftime('%d-%b-%Y')} BEFORE {END_DATE.strftime('%d-%b-%Y')}"
        search_criteria = f"({date_filter})"
        if last_uid > 0:
            search_criteria = f"({date_filter} UID {last_uid + 1}:*)"
        
        logging.info(f"Searching with criteria: {search_criteria}")

        status, messages = mail.uid('search', None, search_criteria)
        if status != "OK":
            logging.error("Failed to search for emails.")
            return

        email_uids = messages[0].split()
        if not email_uids:
            logging.info("No new emails found.")
            return

        logging.info(f"Found {len(email_uids)} new emails. Processing batch of {BATCH_SIZE}.")

        processed_count = 0
        latest_uid = 0
        batch_bounces = []
        batch_num = get_batch_number()
        
        for uid in email_uids:
            if processed_count >= BATCH_SIZE:
                logging.info(f"Batch size of {BATCH_SIZE} reached.")
                break

            status, data = mail.uid('fetch', uid, "(RFC822)")
            if status != "OK":
                logging.warning(f"Failed to fetch email with UID {uid.decode()}")
                continue

            raw_msg = data[0][1]
            msg = email.message_from_bytes(raw_msg)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            if "DMARC" in subject:
                logging.info(f"Ignoring DMARC report with UID {uid.decode()}")
                latest_uid = int(uid)
                continue

            is_bounce, rfc_status = detect_bounce_from_body('', subject)
            
            if not is_bounce:
                body = get_email_body(msg)
                is_bounce, rfc_status = detect_bounce_from_body(body, subject)
                
                if is_bounce and rfc_status:
                    recipient = extract_recipient_from_bounce(msg, body)
                    bounce_type = classify_bounce(rfc_status)
                    action, reason = get_recommended_action(rfc_status)
                    
                    logging.info(f"Found bounce (RFC: {rfc_status}, Type: {bounce_type}) UID {uid.decode()}")

            if not is_bounce:
                logging.info(f"Ignoring non-bounce email with UID {uid.decode()}")
                latest_uid = int(uid)
                continue

            date_tuple = email.utils.parsedate_tz(msg['Date'])
            email_date = None
            if date_tuple:
                local_date = email.utils.mktime_tz(date_tuple)
                email_date = datetime.fromtimestamp(local_date)
                date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(local_date))
            else:
                date_str = "Date not found"

            if email_date:
                if not (START_DATE <= email_date <= END_DATE):
                    logging.info(f"Skipping email outside March 2026: {date_str} (UID: {uid.decode()})")
                    latest_uid = int(uid)
                    continue
            else:
                logging.warning(f"Could not parse date for UID {uid.decode()}. Skipping.")
                latest_uid = int(uid)
                continue

            body = get_email_body(msg)

            if body:
                recipient = extract_recipient_from_bounce(msg, body)
                
                if not recipient or recipient in IGNORED_RECIPIENTS:
                    logging.info(f"Ignoring bounce to sender/ignored address (UID: {uid.decode()})")
                    latest_uid = int(uid)
                    continue
                
                action, reason = get_recommended_action(rfc_status)
                
                batch_bounces.append({
                    "recipient": recipient,
                    "reason": reason,
                    "error_code": rfc_status,
                    "bounce_type": classify_bounce(rfc_status),
                    "date": date_str
                })
                
                print(EMAIL_SEPARATOR)
                print(f"---GEMINI_DATE_SEPARATOR---{date_str}")
                print(f"---RFC3463_STATUS---{rfc_status}")
                print(f"---BOUNCE_TYPE---{classify_bounce(rfc_status)}")
                print(f"---BOUNCE_DESCRIPTION---{get_status_description(rfc_status)}")
                print(f"---RECIPIENT---{recipient}")
                print(body)

                processed_count += 1
                latest_uid = int(uid)
                logging.info(f"Successfully fetched bounce UID {uid.decode()} - {recipient}")
            else:
                logging.warning(f"Could not extract body from UID {uid.decode()}. Skipping.")

            time.sleep(1)
        
        if latest_uid > 0:
            save_last_uid(latest_uid)
            logging.info(f"Saved last processed UID: {latest_uid}")
        
        if batch_bounces:
            filename = save_batch_csv(batch_bounces, batch_num)
            print(f"\n---BATCH_CSV_SAVED---{filename}")
            print(f"---BATCH_SUMMARY---{len(batch_bounces)} bounces processed")
            save_batch_number(batch_num)

    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if mail:
            mail.logout()
            logging.info("Logged out from IMAP server.")

if __name__ == "__main__":
    fetch_emails()