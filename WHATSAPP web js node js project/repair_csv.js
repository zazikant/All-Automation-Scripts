const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CSV_FILE = path.join(__dirname, 'whatsapp_messages.csv');
const BACKUP_FILE = path.join(__dirname, 'whatsapp_messages_backup.csv');
const NEW_HEADER = 'timestamp,phone,contact,sent_message,reply';

async function repairCsv() {
    console.log('🛠 Starting CSV Repair...');

    if (!fs.existsSync(CSV_FILE)) {
        console.error('❌ CSV file not found!');
        return;
    }

    // 1. Create backup
    fs.copyFileSync(CSV_FILE, BACKUP_FILE);
    console.log(`📂 Backup created at ${BACKUP_FILE}`);

    const fileStream = fs.createReadStream(CSV_FILE);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    const lines = [];
    let isHeader = true;
    let rowCount = 0;
    let fixedCount = 0;

    for await (const line of rl) {
        if (!line.trim()) continue;

        if (isHeader) {
            lines.push(NEW_HEADER);
            isHeader = false;
            continue;
        }

        const values = parseCSVLine(line);
        rowCount++;

        // Intelligent detection:
        // If it has 5 columns, it's the NEW format but might have been mis-written
        // because the header was only 4 columns.
        if (values.length === 5) {
            // New format: timestamp,phone,contact,sent_message,reply
            // If the 4th column contains 'hellloooo' or similar, it's likely aligned.
            // If the 5th column contains 'hellloooo' (the message), it was shifted!

            // Check if column 5 contains message-like content while column 4 is empty
            if (values[3] === "" && values[4] !== "" && !values[4].includes(' + ')) {
                // Potential shift: timestamp, phone, contact, empty, message
                // Actually, if it was logged under the OLD header:
                // timestamp, contact, sent_message, reply
                // but 5 values were passed:
                // timestamp, last10, contact, message, ""
                // The old parser would think: col1=ts, col2=last10, col3=contact, col4=message
                // But the file actually contains 5 values.

                // Let's look at the actual data from the view_file:
                // 45: 2026-02-24 16:02:13,9082167025,Cynthia Nadar,hellloooo,
                // These are already 5 columns and look correct for the NEW format:
                // ts, phone, contact, message, reply (empty)

                lines.push(line);
            } else {
                lines.push(line);
            }
        } else if (values.length === 4) {
            // Old format: timestamp,contact,sent_message,reply
            // Convert to: timestamp,phone,contact,sent_message,reply
            const [ts, contact, msg, reply] = values;

            // Try to extract phone from contact if it's a number
            let phone = "";
            if (contact && contact.match(/^\+?\d{10,13}$/)) {
                phone = contact.replace(/\D/g, "").slice(-10);
            }

            const newLine = [ts, phone, contact, msg, reply].map(escapeField).join(',');
            lines.push(newLine);
            fixedCount++;
        } else {
            // Unexpected column count, keep as is but log warning
            console.warn(`⚠️ Line ${rowCount + 1} has ${values.length} columns: ${line}`);
            lines.push(line);
        }
    }

    fs.writeFileSync(CSV_FILE, lines.join('\n') + '\n', 'utf8');
    console.log(`✅ Repair complete! Fixed ${fixedCount} old rows.`);
    console.log(`📈 Processed ${rowCount} data rows.`);
}

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

function escapeField(value) {
    if (value === null || value === undefined) return "";
    const str = String(value);
    if (str.includes(",") || str.includes('"') || str.includes("\n")) {
        return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
}

repairCsv().catch(console.error);
