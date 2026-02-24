/**
 * csv_logger.js — CSV read/write helper
 * Format: timestamp,phone,contact,sent_message,reply
 *
 * `phone`   - raw last-10 digits (e.g. "9869101909")
 * `contact` - display name (from WhatsApp API or CONTACT_CACHE)
 *
 * Backward compatible: old 4-column rows (no phone) are read and upgraded gracefully.
 */

const fs = require("fs");
const path = require("path");
const readline = require("readline");

const CSV_FILE = path.join(__dirname, "..", "whatsapp_messages.csv");
const CSV_HEADER = "timestamp,phone,contact,sent_message,reply";

/**
 * Ensure CSV file exists with correct header.
 * If file exists but has the old header, it will be updated.
 */
function ensureCsvExists() {
    if (!fs.existsSync(CSV_FILE)) {
        fs.writeFileSync(CSV_FILE, CSV_HEADER + "\n", "utf8");
        console.log("📄 Created whatsapp_messages.csv");
        return;
    }

    // Check if header is correct
    const firstLine = fs.readFileSync(CSV_FILE, 'utf8').split('\n')[0].trim();
    if (firstLine !== CSV_HEADER) {
        console.log("⚠️  Legacy CSV header detected. Updating header...");
        const content = fs.readFileSync(CSV_FILE, 'utf8').split('\n');
        content[0] = CSV_HEADER;
        fs.writeFileSync(CSV_FILE, content.join('\n'), 'utf8');
        console.log("✅ CSV header updated to 5-column format.");
    }
}

/**
 * Get current timestamp in format: YYYY-MM-DD HH:MM:SS
 */
function getTimestamp() {
    const now = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}

/**
 * Escape a CSV field (wrap in quotes if it contains commas, quotes, or newlines).
 */
function escapeField(value) {
    if (value === null || value === undefined) return "";
    const str = String(value);
    if (str.includes(",") || str.includes('"') || str.includes("\n")) {
        return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
}

/**
 * Log a sent message to CSV.
 * If the last row is for the same phone on the same day, concatenate with " + ".
 * @param {string} phone - Last-10 digit phone number
 * @param {string} contact - Display name (WhatsApp resolved)
 * @param {string} message - Message text or image description
 */
async function logSentMessage(phone, contact, message) {
    ensureCsvExists();
    const rows = await readAllRows();
    const now = getTimestamp();
    const today = now.split(" ")[0];
    const last10 = (phone || "").replace(/\D/g, "").slice(-10);

    // Check if last row is for same phone on same day
    let updated = false;
    if (rows.length > 0) {
        const lastRow = rows[rows.length - 1];
        const lastDay = lastRow.timestamp ? lastRow.timestamp.split(" ")[0] : "";
        const lastPhone = (lastRow.phone || "").replace(/\D/g, "").slice(-10);

        if (
            lastPhone &&
            last10 &&
            lastPhone === last10 &&
            lastDay === today
        ) {
            // Update last row: concatenate message and update timestamp + contact name
            const existing = lastRow.sent_message || "";
            lastRow.sent_message = existing ? `${existing} + ${message}` : message;
            lastRow.timestamp = now;
            lastRow.contact = contact || lastRow.contact; // refresh display name
            updated = true;
        }
    }

    if (updated) {
        // Rewrite the entire CSV
        const lines = [CSV_HEADER.trim()];
        for (const row of rows) {
            lines.push(
                [
                    escapeField(row.timestamp),
                    escapeField(row.phone),
                    escapeField(row.contact),
                    escapeField(row.sent_message),
                    escapeField(row.reply),
                ].join(",")
            );
        }
        fs.writeFileSync(CSV_FILE, lines.join("\n") + "\n", "utf8");
        console.log(`📝 Updated CSV entry for ${contact} (concatenated)`);
    } else {
        // Append a new row
        const row = [
            escapeField(now),
            escapeField(last10),
            escapeField(contact),
            escapeField(message),
            "", // reply
        ].join(",");
        fs.appendFileSync(CSV_FILE, row + "\n", "utf8");
        console.log(`📝 Logged NEW sent message for ${contact}`);
    }
}

/**
 * Read all rows from the CSV and return as array of objects.
 * Handles both old 4-column format (no phone) and new 5-column format.
 * @returns {Promise<Array>}
 */
async function readAllRows() {
    ensureCsvExists();
    return new Promise((resolve) => {
        const rows = [];
        const rl = readline.createInterface({
            input: fs.createReadStream(CSV_FILE),
            crlfDelay: Infinity,
        });

        let isHeader = true;
        let headers = [];

        rl.on("line", (line) => {
            if (!line.trim()) return;

            if (isHeader) {
                headers = line.split(",").map((h) => h.trim());
                isHeader = false;
                return;
            }

            const values = parseCSVLine(line);

            // Resilient column matching:
            const obj = {
                timestamp: values[0] || "",
                phone: "",
                contact: "",
                sent_message: "",
                reply: ""
            };

            if (values.length === 5) {
                // New format: timestamp,phone,contact,sent_message,reply
                obj.phone = values[1] || "";
                obj.contact = values[2] || "";
                obj.sent_message = values[3] || "";
                obj.reply = values[4] || "";
            } else if (values.length === 4) {
                // Old format: timestamp,contact,sent_message,reply
                obj.contact = values[1] || "";
                obj.sent_message = values[2] || "";
                obj.reply = values[3] || "";
            } else {
                // Unknown format, try best effort based on current headers
                headers.forEach((h, i) => { if (h in obj) obj[h] = values[i] || ""; });
            }

            rows.push(obj);
        });

        rl.on("close", () => resolve(rows));
    });
}

/**
 * Parse a single CSV line respecting quoted fields.
 */
function parseCSVLine(line) {
    const result = [];
    let current = "";
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
            if (inQuotes && line[i + 1] === '"') {
                current += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (char === "," && !inQuotes) {
            result.push(current);
            current = "";
        } else {
            current += char;
        }
    }
    result.push(current);
    return result;
}

/**
 * Update the reply for the most recent row matching a contact by PHONE NUMBER.
 * Falls back to contact name match for old rows without phone.
 * If a reply already exists, append with " + " separator.
 * @param {string} phone - Last-10 digit phone number
 * @param {string} contact - Display name (for name-based fallback)
 * @param {string} replyText
 * @returns {boolean} true if updated, false if no matching row found
 */
async function updateReply(phone, contact, replyText) {
    ensureCsvExists();
    const rows = await readAllRows();
    const last10 = (phone || "").replace(/\D/g, "").slice(-10);

    // Find the LAST row for this contact — match by phone first, then name
    let targetIndex = -1;
    for (let i = rows.length - 1; i >= 0; i--) {
        const rowPhone = (rows[i].phone || "").replace(/\D/g, "").slice(-10);
        const rowContact = (rows[i].contact || "").toLowerCase().trim();

        if (last10 && rowPhone && rowPhone === last10) {
            targetIndex = i;
            break;
        }
        // Name-based fallback for old rows without phone
        if (!rowPhone && contact && rowContact === contact.toLowerCase().trim()) {
            targetIndex = i;
            break;
        }
    }

    if (targetIndex === -1) {
        console.log(`⚠️  No CSV entry found for: ${contact} (${phone})`);
        return false;
    }

    // Append reply to existing
    const existing = rows[targetIndex].reply || "";
    rows[targetIndex].reply = existing
        ? `${existing} + ${replyText}`
        : replyText;

    // Rewrite the entire CSV
    const lines = [CSV_HEADER.trim()];
    for (const row of rows) {
        lines.push(
            [
                escapeField(row.timestamp),
                escapeField(row.phone),
                escapeField(row.contact),
                escapeField(row.sent_message),
                escapeField(row.reply),
            ].join(",")
        );
    }

    fs.writeFileSync(CSV_FILE, lines.join("\n") + "\n", "utf8");
    console.log(`📝 Updated reply for ${contact}: ${replyText.slice(0, 60)}...`);
    return true;
}

/**
 * Get all contacts we have previously sent messages to.
 * Returns array of {phone, contact} objects.
 * @returns {Promise<Array<{phone: string, contact: string}>>}
 */
async function getKnownContacts() {
    const rows = await readAllRows();

    // Use two maps for dedup: one by phone, one by contact name
    // This merges old rows (no phone) with new rows (with phone) for the same contact
    const byPhone = new Map();   // last10 → {phone, contact}
    const byName = new Map();   // contact.toLowerCase() → {phone, contact}

    for (const r of rows) {
        let phone = (r.phone || "").replace(/\D/g, "").slice(-10);
        const contact = (r.contact || "").trim();
        if (!contact) continue;

        // Extract phone from contact name if it looks like a phone number
        if (!phone && contact.match(/^\+?\d{10,13}$/)) {
            phone = contact.replace(/\D/g, "").slice(-10);
        }

        const nameKey = contact.toLowerCase();

        if (phone) {
            if (!byPhone.has(phone)) {
                byPhone.set(phone, { phone, contact });
            } else if (!byPhone.get(phone).contact || byPhone.get(phone).contact.startsWith("+91")) {
                // Prefer a real name over a phone-formatted name
                if (!contact.match(/^\+?\d{10,13}$/)) {
                    byPhone.get(phone).contact = contact;
                }
            }
        } else {
            // Old row: no phone — index by name, phone stays empty for now
            if (!byName.has(nameKey)) {
                byName.set(nameKey, { phone: "", contact });
            }
        }
    }

    // Merge name-only entries: if byPhone already has an entry whose resolved
    // contact name matches a byName entry, the byPhone entry wins (has phone).
    // Only keep byName entries that have NO matching phone entry.
    const result = [...byPhone.values()];
    for (const entry of byName.values()) {
        const nameKey = entry.contact.toLowerCase();
        const alreadyCovered = result.some(r => r.contact.toLowerCase() === nameKey);
        if (!alreadyCovered) {
            result.push(entry);
        }
    }

    return result;
}

module.exports = {
    logSentMessage,
    updateReply,
    readAllRows,
    getKnownContacts,
    ensureCsvExists,
};
