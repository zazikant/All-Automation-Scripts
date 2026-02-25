/**
 * send_text.js — Send a text message to a WhatsApp contact
 *
 * Usage:
 *   node send_text.js "<phone>" "<message>"
 *
 * Examples:
 *   node send_text.js "9869101909" "Hello! How are you?"
 *   node send_text.js "+919820937483" "Good morning!"
 *
 * - Auto-resolves contact name from WhatsApp (no CONTACT_CACHE needed)
 * - Logs the sent message to whatsapp_messages.csv automatically.
 *
 * ⚠️  MANDATORY WORKFLOW: Always run check_replies.js BEFORE sending!
 */

const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const { resolveContactName, toWaId } = require("./utils/contacts");
const { logSentMessage } = require("./utils/csv_logger");

// --- Read CLI args ---
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error("❌ Usage: node send_text.js <phone> <message>");
    console.error('   Example: node send_text.js "9869101909" "Hello!"');
    process.exit(1);
}

const phone = args[0];
const message = args[1];
const digits = phone.replace(/\D/g, "");
const last10 = digits.slice(-10);
const waId = toWaId(phone);

console.log(`📱 Preparing to send to ${phone}...`);
console.log(`💬 Message: ${message}`);

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

        // For unknown contacts, verify they're on WhatsApp first
        const contactName = await resolveContactName(client, phone, chats);
        const isUnknown = contactName.startsWith("+91");

        if (isUnknown) {
            console.log(`🔍 Unknown contact — verifying ${phone} is on WhatsApp...`);
            let isRegistered = false;
            try { isRegistered = await client.isRegisteredUser(waId); } catch (e) { }
            if (!isRegistered) {
                console.error(`❌ ${phone} is NOT on WhatsApp. Message not sent.`);
                await logSentMessage(last10, contactName, "[NOT ON WHATSAPP]");
                await client.destroy();
                process.exit(0);
            }
            console.log(`   ✅ ${phone} is on WhatsApp. Proceeding...`);
        }

        console.log(`👤 Contact resolved: "${contactName}"`);

        // Strategy 1: Find chat by matching contact name or phone number
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
            await targetChat.sendMessage(message);
            console.log(`✅ Message sent to ${contactName}: "${message}"`);
            console.log(`⏳ Waiting 5s for server delivery confirmation...`);
            await new Promise(resolve => setTimeout(resolve, 5000));
            await logSentMessage(last10, contactName, message);
            console.log(`📊 Logged to whatsapp_messages.csv`);
            await client.destroy();
            process.exit(0);
        }

        // Strategy 2: Direct ID send (new contact, no existing chat)
        console.log(`⚠️  No existing chat found. Sending via direct ID: ${waId}`);
        let sent = false;
        for (const id of [waId, `${last10}@c.us`, `${digits}@c.us`]) {
            try {
                await client.sendMessage(id, message);
                console.log(`✅ Message sent to ${contactName} [${id}]`);
                await new Promise(resolve => setTimeout(resolve, 5000));
                await logSentMessage(last10, contactName, message);
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
