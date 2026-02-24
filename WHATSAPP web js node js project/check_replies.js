/**
 * check_replies.js — Check and log replies from known contacts
 *
 * Now uses PHONE-NUMBER based matching against chat IDs.
 * No reliance on CONTACT_CACHE — works for saved and unsaved contacts.
 */

const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const { updateReply, getKnownContacts, readAllRows } = require("./utils/csv_logger");

/**
 * Main logic to check and log replies.
 * @param {Client} activeClient - Optional. If provided, uses this client instead of creating a new one.
 */
async function runCheckReplies(activeClient = null) {
    let client = activeClient;
    let ownClient = false;

    if (!client) {
        client = new Client({
            authStrategy: new LocalAuth({ dataPath: ".wwebjs_auth" }),
            puppeteer: {
                headless: true,
                args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            },
        });

        client.on("qr", (qr) => {
            console.log("\n⚠️  Session not found! Scan QR to log in first:\n");
            qrcode.generate(qr, { small: true });
            console.log("\n→ After scanning, re-run this command.");
        });

        ownClient = true;
    }

    const performCheck = async () => {
        try {
            console.log("\n🔍 Checking for replies from known contacts...");

            // Step 1: Get all contacts from CSV as {phone, contact} objects
            const knownContacts = await getKnownContacts();
            if (knownContacts.length === 0) {
                console.log("ℹ️  No contacts in CSV yet. Send a message first.");
                return;
            }

            const displayList = knownContacts.map(k => k.contact || k.phone).join(", ");
            console.log(`📋 Known contacts from CSV: ${displayList}\n`);

            // Step 2: Get ALL chats
            const chats = await client.getChats();

            // Step 3: Read current CSV to know what's already captured
            const csvRows = await readAllRows();

            let repliesCaptured = 0;

            // Step 4: For each known contact, find their chat by PHONE NUMBER
            for (const { phone, contact } of knownContacts) {
                const last10 = (phone || "").replace(/\D/g, "").slice(-10);

                // Find chat: prefer phone-based match (c.id.user), fall back to name match
                let chat = null;

                if (last10) {
                    // Primary: match by phone number in chat ID (works for @c.us chats)
                    chat = chats.find((c) => {
                        const chatIdLast10 = (c.id.user || "").replace(/\D/g, "").slice(-10);
                        return chatIdLast10 === last10;
                    });

                    // Secondary: match by phone digits in chat NAME (handles @lid chats
                    // where c.id.user is an internal WhatsApp ID, not the phone number)
                    if (!chat) {
                        chat = chats.find((c) => {
                            const chatName = (c.name || "");
                            const chatNameDigits = chatName.replace(/\D/g, "").slice(-10);
                            return chatName.includes(last10) || chatNameDigits === last10;
                        });
                    }
                }

                // Fallback: match by contact name (for old rows or saved contacts)
                if (!chat && contact) {
                    chat = chats.find((c) => {
                        const chatName = (c.name || "").toLowerCase();
                        const known = contact.toLowerCase();
                        return chatName.includes(known) || known.includes(chatName);
                    });
                }

                if (!chat) {
                    console.log(`   ⚠️  No chat found for "${contact}" (${phone || "no phone"}), skipping.`);
                    continue;
                }

                console.log(`\n📥 Checking chat: "${chat.name || chat.id.user}" (matches "${contact}")`);

                // Step 5: Fetch recent messages
                const messages = await chat.fetchMessages({ limit: 50 });

                // Step 6: Find the last message WE sent
                let lastOutgoingIndex = -1;
                for (let i = messages.length - 1; i >= 0; i--) {
                    if (messages[i].fromMe) {
                        lastOutgoingIndex = i;
                        break;
                    }
                }

                if (lastOutgoingIndex === -1) {
                    console.log(`   ℹ️  No outgoing messages found in this chat, skipping.`);
                    continue;
                }

                // Step 7: Collect ALL incoming messages after our last sent message
                const replies = [];
                for (let i = lastOutgoingIndex + 1; i < messages.length; i++) {
                    const msg = messages[i];
                    if (!msg.fromMe) {
                        let body = msg.body;
                        if (!body && msg.hasMedia) {
                            body = `[${msg.type}]`;
                        }
                        if (body) replies.push(body.trim());
                    }
                }

                if (replies.length === 0) {
                    console.log(`   ℹ️  No replies after last sent message.`);
                    continue;
                }

                const combinedReply = replies.join(" + ");

                // Step 8: Compare against what's already in the CSV (avoid duplicates)
                let lastCsvReply = "";
                for (let i = csvRows.length - 1; i >= 0; i--) {
                    const rowPhone = (csvRows[i].phone || "").replace(/\D/g, "").slice(-10);
                    const rowContact = (csvRows[i].contact || "").toLowerCase().trim();
                    const matches = (last10 && rowPhone === last10) ||
                        (!last10 && contact && rowContact === contact.toLowerCase().trim());
                    if (matches) {
                        lastCsvReply = csvRows[i].reply || "";
                        break;
                    }
                }

                // Only log truly new replies
                if (lastCsvReply && combinedReply === lastCsvReply) {
                    console.log(`   ✅ Replies already captured, no changes.`);
                    continue;
                }

                let replyToLog = combinedReply;
                if (lastCsvReply && combinedReply.startsWith(lastCsvReply + " + ")) {
                    replyToLog = combinedReply.slice((lastCsvReply + " + ").length).trim();
                    if (!replyToLog) {
                        console.log(`   ✅ No new messages since last capture.`);
                        continue;
                    }
                    console.log(`   💬 NEW replies: ${replyToLog.slice(0, 80)}${replyToLog.length > 80 ? "..." : ""}`);
                } else {
                    console.log(`   💬 Replies captured (${replies.length}): ${combinedReply.slice(0, 80)}${combinedReply.length > 80 ? "..." : ""}`);
                }

                // Step 9: Update CSV (phone-based match)
                const updated = await updateReply(phone, contact, replyToLog);
                if (updated) {
                    repliesCaptured++;
                    console.log(`   ✅ CSV updated for "${contact}"`);
                }

                await chat.sendSeen();
            }

            // Summary
            console.log(`\n${"=".repeat(50)}`);
            if (repliesCaptured > 0) {
                console.log(`✅ Done! Captured replies from ${repliesCaptured} contact(s).`);
                console.log(`📊 whatsapp_messages.csv has been updated.`);
            } else {
                console.log("ℹ️  No new replies found from known contacts.");
            }
            console.log(`${"=".repeat(50)}\n`);

        } catch (err) {
            console.error("❌ Error checking replies:", err.message);
        }
    };

    if (ownClient) {
        return new Promise((resolve) => {
            client.on("ready", async () => {
                console.log("✅ Connected to WhatsApp");
                await performCheck();
                try { await client.destroy(); } catch (_) { }
                resolve();
            });

            client.on("auth_failure", (msg) => {
                console.error("❌ Auth failed:", msg);
                try { client.destroy(); } catch (_) { }
                resolve();
            });

            client.initialize();
        });
    } else {
        await performCheck();
    }
}

module.exports = { runCheckReplies };

if (require.main === module) {
    runCheckReplies();
}
