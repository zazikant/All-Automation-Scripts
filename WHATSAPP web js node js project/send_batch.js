/**
 * send_batch.js — Send messages to multiple contacts from a CSV file
 *
 * Workflow:
 * 1. Reads input_contacts.csv (phone,message,image_path,caption)
 * 2. Auto-resolves contact names from WhatsApp (no CONTACT_CACHE needed)
 * 3. Sends messages or images in batches of 10
 * 4. Waits 120s (2 minutes) between batches, checking replies every 30s
 * 5. Final reply check after all batches complete
 *
 * Usage:
 *   node send_batch.js
 */

const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");
const { resolveContactName, toWaId } = require("./utils/contacts");
const { logSentMessage } = require("./utils/csv_logger");
const { runCheckReplies } = require("./check_replies");

const INPUT_FILE = "input_contacts.csv";
const BATCH_SIZE = 10;
const BATCH_DELAY_MS = 120000; // 2 minutes
const REPLY_CHECK_INTERVAL_MS = 30000; // Check replies every 30s during delay

/**
 * Reads contacts from the input CSV file.
 */
async function readInputContacts() {
    const contacts = [];
    return new Promise((resolve, reject) => {
        if (!fs.existsSync(INPUT_FILE)) {
            return reject(new Error(`Input file not found: ${INPUT_FILE}`));
        }

        fs.createReadStream(INPUT_FILE)
            .pipe(csv())
            .on("data", (row) => {
                if (row.phone && (row.message || row.image_path)) {
                    contacts.push(row);
                }
            })
            .on("end", () => resolve(contacts))
            .on("error", reject);
    });
}

/**
 * Main Batch Process
 */
async function startBatchProcess() {
    console.log("🚀 Starting Batch Processing...");

    const allContacts = await readInputContacts();
    console.log(`📋 Loaded ${allContacts.length} contacts from ${INPUT_FILE}`);

    if (allContacts.length === 0) {
        console.log("ℹ️  No contacts to process. Exiting.");
        return;
    }

    const client = new Client({
        authStrategy: new LocalAuth({ dataPath: ".wwebjs_auth" }),
        puppeteer: {
            headless: true,
            args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        },
    });

    client.on("qr", (qr) => {
        console.log("\n⚠️  Session not found! Scan QR first:\n");
        qrcode.generate(qr, { small: true });
    });

    client.on("ready", async () => {
        console.log("✅ WhatsApp Web is ready!");

        // Run initial reply check before starting
        await runCheckReplies(client);

        const batches = [];
        for (let i = 0; i < allContacts.length; i += BATCH_SIZE) {
            batches.push(allContacts.slice(i, i + BATCH_SIZE));
        }

        console.log(`📦 Split into ${batches.length} batches.`);

        for (let i = 0; i < batches.length; i++) {
            console.log(`\n--- Processing Batch ${i + 1} of ${batches.length} ---`);

            const currentBatch = batches[i];
            // Fetch chats once per batch for efficiency
            const chats = await client.getChats();

            for (const entry of currentBatch) {
                const { phone, message, image_path, caption } = entry;
                const digits = phone.replace(/\D/g, "");
                const last10 = digits.slice(-10);
                const waId = toWaId(phone);

                const isImage = image_path && image_path.trim() !== "" && fs.existsSync(image_path);

                if (isImage) {
                    console.log(`📱 Sending IMAGE to ${phone}...`);
                    console.log(`🖼️  File: ${image_path}`);
                } else {
                    console.log(`📱 Sending TEXT to ${phone}...`);
                }

                try {
                    // Auto-resolve display name from WhatsApp
                    const contactName = await resolveContactName(client, phone, chats);
                    const isUnknown = contactName.startsWith("+91");

                    // Verify unknown contacts are on WhatsApp before sending
                    if (isUnknown) {
                        console.log(`   🔍 Unknown contact — verifying ${phone} is on WhatsApp...`);
                        let isRegistered = false;
                        try { isRegistered = await client.isRegisteredUser(waId); } catch (e) { }
                        if (!isRegistered) {
                            console.log(`   ❌ ${phone} is NOT on WhatsApp. Logging and skipping.`);
                            await logSentMessage(last10, contactName, "[NOT ON WHATSAPP]");
                            await new Promise(r => setTimeout(r, 1000));
                            continue;
                        }
                        console.log(`   ✅ ${phone} is on WhatsApp. Proceeding...`);
                    }

                    console.log(`   👤 Contact: "${contactName}"`);

                    // Find chat by phone ID first (most reliable), then by name
                    let targetChat = chats.find(c => {
                        const chatIdLast10 = (c.id.user || "").replace(/\D/g, "").slice(-10);
                        return chatIdLast10 === last10;
                    });

                    if (!targetChat) {
                        targetChat = chats.find(c =>
                            c.name && c.name.toLowerCase().trim() === contactName.toLowerCase().trim()
                        );
                    }

                    if (!targetChat) {
                        targetChat = chats.find(c =>
                            c.name && c.name.includes(last10)
                        );
                    }

                    if (targetChat) {
                        if (isImage) {
                            const media = MessageMedia.fromFilePath(image_path);
                            await targetChat.sendMessage(media, { caption: caption || "" });
                            console.log(`   ✅ Image Sent!`);
                            await new Promise(r => setTimeout(r, 5000));
                        } else {
                            await targetChat.sendMessage(message);
                            console.log(`   ✅ Sent!`);
                        }
                    } else {
                        // Direct ID fallback (new contact, no existing chat)
                        console.log(`   ⚠️  No existing chat. Sending via direct ID: ${waId}`);
                        if (isImage) {
                            const media = MessageMedia.fromFilePath(image_path);
                            await client.sendMessage(waId, media, { caption: caption || "" });
                            console.log(`   ✅ Image Sent (Direct ID)`);
                            await new Promise(r => setTimeout(r, 5000));
                        } else {
                            await client.sendMessage(waId, message);
                            console.log(`   ✅ Sent (Direct ID)`);
                        }
                    }

                    // Log to CSV with phone + resolved name
                    const logMsg = isImage
                        ? `Image: ${path.basename(image_path)}${caption ? " | " + caption : ""}`
                        : message;
                    await logSentMessage(last10, contactName, logMsg);

                    await new Promise(r => setTimeout(r, 3000));

                } catch (err) {
                    console.error(`   ❌ Failed to send to ${phone}:`, err.message);
                    try {
                        const contactName = await resolveContactName(client, phone, chats);
                        await logSentMessage(last10, contactName, `[SEND FAILED: ${err.message}]`);
                    } catch (_) { }
                }
            }

            // Between-batch delay with reply checks
            if (i < batches.length - 1) {
                console.log(`\n⏳ Batch complete. Waiting ${BATCH_DELAY_MS / 1000}s before next batch...`);
                let remainingDelay = BATCH_DELAY_MS;
                while (remainingDelay > 0) {
                    console.log(`   ⏱️  ${remainingDelay / 1000}s remaining...`);
                    await runCheckReplies(client);
                    const step = Math.min(REPLY_CHECK_INTERVAL_MS, remainingDelay);
                    await new Promise(r => setTimeout(r, step));
                    remainingDelay -= step;
                }
            }
        }

        console.log("\n✅ All batches processed successfully.");

        // Final reply check after last batch (catches replies to the last sends)
        console.log("\n⏳ Waiting 10s for last replies before final check...");
        await new Promise(r => setTimeout(r, 10000));
        await runCheckReplies(client);

        await client.destroy();
        process.exit(0);
    });

    client.on("auth_failure", (msg) => {
        console.error("❌ Auth failed:", msg);
        process.exit(1);
    });

    client.initialize();
}

startBatchProcess().catch(err => {
    console.error("❌ Fatal Error:", err.message);
    process.exit(1);
});
