/**
 * send_image.js — Send an image (or any file) to a WhatsApp contact
 *
 * Usage:
 *   node send_image.js "<phone>" "<absolute_path_to_image>" "<optional_caption>"
 *
 * Examples:
 *   node send_image.js "9869101909" "C:/images/photo.jpg" "Check this out!"
 *   node send_image.js "9820937483" "D:/docs/report.pdf"
 *
 * - Auto-resolves contact name from WhatsApp (no CONTACT_CACHE needed)
 * - Logs to whatsapp_messages.csv automatically.
 *
 * ⚠️  MANDATORY WORKFLOW: Always run check_replies.js BEFORE sending!
 */

const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const path = require("path");
const fs = require("fs");
const { resolveContactName, toWaId } = require("./utils/contacts");
const { logSentMessage } = require("./utils/csv_logger");

// --- Read CLI args ---
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error("❌ Usage: node send_image.js <phone> <image_path> [caption]");
    console.error('   Example: node send_image.js "9869101909" "C:/images/photo.jpg" "Caption"');
    process.exit(1);
}

const phone = args[0];
const imagePath = path.resolve(args[1]);
const caption = args[2] || "";
const fileName = path.basename(imagePath);
const digits = phone.replace(/\D/g, "");
const last10 = digits.slice(-10);
const waId = toWaId(phone);

if (!fs.existsSync(imagePath)) {
    console.error(`❌ File not found: ${imagePath}`);
    process.exit(1);
}

console.log(`📱 Preparing to send image to ${phone}...`);
console.log(`🖼️  File: ${imagePath}`);
if (caption) console.log(`📝 Caption: ${caption}`);

// --- WhatsApp Client ---
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
    try {
        const chats = await client.getChats();

        // Auto-resolve display name from WhatsApp API
        const contactName = await resolveContactName(client, phone, chats);
        const isUnknown = contactName.startsWith("+91");

        if (isUnknown) {
            console.log(`🔍 Unknown contact — verifying ${phone} is on WhatsApp...`);
            let isRegistered = false;
            try { isRegistered = await client.isRegisteredUser(waId); } catch (e) { }
            if (!isRegistered) {
                console.error(`❌ ${phone} is NOT on WhatsApp. Image not sent.`);
                await logSentMessage(last10, contactName, "[NOT ON WHATSAPP]");
                await client.destroy();
                process.exit(0);
            }
            console.log(`   ✅ ${phone} is on WhatsApp. Proceeding...`);
        }

        console.log(`👤 Contact resolved: "${contactName}"`);

        const media = MessageMedia.fromFilePath(imagePath);
        const sendOptions = caption ? { caption } : {};

        // Strategy 1: Find chat by name or phone number
        let targetChat = chats.find(c =>
            c.name && c.name.toLowerCase().trim() === contactName.toLowerCase().trim()
        );

        if (!targetChat) {
            targetChat = chats.find(c => {
                const chatIdLast10 = (c.id.user || "").replace(/\D/g, "").slice(-10);
                return chatIdLast10 === last10 || (c.name && c.name.includes(last10));
            });
        }

        if (targetChat) {
            console.log(`✅ Found chat: "${targetChat.name || targetChat.id.user}"`);
            await targetChat.sendMessage(media, sendOptions);
            console.log(`✅ Image sent to ${contactName}: ${fileName}`);
            console.log(`⏳ Waiting 5s for server delivery confirmation...`);
            await new Promise(resolve => setTimeout(resolve, 5000));

            const logMessage = caption ? `Image: ${fileName} | ${caption}` : `Image: ${fileName}`;
            await logSentMessage(last10, contactName, logMessage);
            console.log(`📊 Logged to whatsapp_messages.csv`);
            await client.destroy();
            process.exit(0);
        }

        // Strategy 2: Direct ID send
        console.log(`⚠️  No existing chat found. Sending via direct ID: ${waId}`);
        let sent = false;
        for (const id of [waId, `${last10}@c.us`, `${digits}@c.us`]) {
            try {
                await client.sendMessage(id, media, sendOptions);
                console.log(`✅ Image sent to ${contactName} [${id}]: ${fileName}`);
                await new Promise(resolve => setTimeout(resolve, 5000));
                const logMessage = caption ? `Image: ${fileName} | ${caption}` : `Image: ${fileName}`;
                await logSentMessage(last10, contactName, logMessage);
                console.log(`📊 Logged to whatsapp_messages.csv`);
                sent = true;
                break;
            } catch (e) {
                console.log(`   ⚠️  Failed [${id}]: ${e.message}`);
            }
        }

        if (!sent) {
            console.error(`❌ Could not send to ${phone}.`);
            await logSentMessage(last10, contactName, `[SEND FAILED]`);
        }

    } catch (err) {
        console.error("❌ Error:", err.message);
    } finally {
        await client.destroy();
        process.exit(0);
    }
});

client.on("auth_failure", (msg) => {
    console.error("❌ Auth failed:", msg);
    process.exit(1);
});

client.initialize();
