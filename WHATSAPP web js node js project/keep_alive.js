/**
 * keep_alive.js — First-time QR login & persistent session
 *
 * Usage: node keep_alive.js
 *
 * - Shows a QR code in the terminal on first run.
 * - ALSO saves QR as qr_code.png in the project folder — open it for full view!
 * - Scan the QR code with your WhatsApp phone.
 * - Session is saved to .wwebjs_auth/ — no QR needed on subsequent runs.
 * - This script stays alive until you press Ctrl+C.
 */

const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const QRCode = require("qrcode");
const path = require("path");

const QR_IMAGE_PATH = path.join(__dirname, "qr_code.png");

console.log("🚀 Starting WhatsApp Web client...");
console.log("📁 Session will be saved to .wwebjs_auth/");

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: ".wwebjs_auth",
    }),
    puppeteer: {
        headless: true,
        args: [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ],
    },
});

client.on("qr", (qr) => {
    console.log("\n📱 Scan this QR code with your WhatsApp phone:\n");
    qrcode.generate(qr, { small: true });

    // Save as PNG image for full-size viewing
    QRCode.toFile(QR_IMAGE_PATH, qr, { width: 400, margin: 2 }, (err) => {
        if (!err) {
            console.log(`\n🖼️  Full-size QR saved as: qr_code.png`);
            console.log(`   → Open it in File Explorer to scan clearly!`);
        }
    });

    console.log("\n⏳ Waiting for QR scan...");
});

client.on("authenticated", () => {
    console.log("\n✅ Authenticated! Session saved to .wwebjs_auth/");
});

client.on("ready", () => {
    console.log("✅ WhatsApp Web is ready!");
    console.log("✅ You can now run send_text.js, send_image.js, and check_replies.js");
    console.log("ℹ️  Keep this terminal open, or press Ctrl+C to exit.");
    console.log("ℹ️  Future scripts will restore this session automatically.");
});

client.on("auth_failure", (msg) => {
    console.error("❌ Authentication failed:", msg);
    console.error("   Delete .wwebjs_auth/ folder and try again.");
    process.exit(1);
});

client.on("disconnected", (reason) => {
    console.warn("⚠️  Client disconnected:", reason);
    console.warn("   Re-run this script if you need to reconnect.");
});

client.initialize();
