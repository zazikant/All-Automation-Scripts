/**
 * debug_chats.js — List all chats and their WhatsApp IDs
 * Run this to see what contacts/chats are available and their exact IDs.
 */
const { Client, LocalAuth } = require("whatsapp-web.js");

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: ".wwebjs_auth" }),
    puppeteer: {
        headless: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
    },
});

client.on("ready", async () => {
    console.log("✅ Connected. Fetching chats...\n");

    try {
        const chats = await client.getChats();
        console.log(`Found ${chats.length} chats:\n`);

        for (const chat of chats.slice(0, 20)) {
            console.log(`  Name: ${chat.name}`);
            console.log(`  ID:   ${chat.id._serialized}`);
            console.log(`  Msgs: ${chat.lastMessage ? chat.lastMessage.body?.slice(0, 40) : "none"}`);
            console.log("  ---");
        }

        // Also check contacts registered on WhatsApp
        console.log("\n🔍 Checking if 919869101909 is registered on WhatsApp...");
        try {
            const isRegistered = await client.isRegisteredUser("919869101909@c.us");
            console.log(`  919869101909@c.us registered: ${isRegistered}`);
        } catch (e) {
            console.log(`  Error checking: ${e.message}`);
        }

        try {
            const isRegistered2 = await client.isRegisteredUser("9869101909@c.us");
            console.log(`  9869101909@c.us registered: ${isRegistered2}`);
        } catch (e) {
            console.log(`  Error checking: ${e.message}`);
        }

    } catch (err) {
        console.error("Error:", err.message);
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
