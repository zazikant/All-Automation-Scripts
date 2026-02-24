/**
 * contacts.js — Shared contact cache (optional override)
 *
 * CONTACT_CACHE is now OPTIONAL. The system auto-resolves names from WhatsApp API.
 * Add entries here only if you want to override the WhatsApp display name.
 */

const CONTACT_CACHE = {
  "9869101909": "Shashikant Home",
  "8976167591": "Jaideep Singh BD GEM",
  "9820937483": "Purva",
  "8999001625": "Chandrakant Shivadekar GEM",
  // Add overrides here if you want a custom name instead of WhatsApp profile name:
  // "XXXXXXXXXX": "Your Custom Name",
};

/**
 * Get contact name from phone number (cache only, no WhatsApp API).
 * Falls back to formatted phone if not in cache.
 * @param {string} phone
 * @returns {string}
 */
function getContactName(phone) {
  const digits = phone.replace(/\D/g, "");
  const last10 = digits.slice(-10);
  return CONTACT_CACHE[last10] || `+91${last10}`;
}

/**
 * Resolve contact display name intelligently:
 * 1. Check CONTACT_CACHE (manual override)
 * 2. Look up chat name from existing chats (handles @lid, saved contacts)
 * 3. Try WhatsApp contact API for pushname (what the person set as their profile name)
 * 4. Fall back to formatted phone number
 *
 * @param {import('whatsapp-web.js').Client} client - Connected WhatsApp client
 * @param {string} phone - Phone number (any format)
 * @param {Array} [chats] - Optional pre-fetched chats array (avoids duplicate getChats call)
 * @returns {Promise<string>} Resolved display name
 */
async function resolveContactName(client, phone, chats = null) {
  const digits = phone.replace(/\D/g, "");
  const last10 = digits.slice(-10);
  const waId = `91${last10}@c.us`;

  // Step 1: Check manual cache override first
  if (CONTACT_CACHE[last10]) {
    return CONTACT_CACHE[last10];
  }

  // Step 2: Look for existing chat and use its display name
  try {
    const chatList = chats || await client.getChats();
    const matchedChat = chatList.find((c) => {
      const chatIdLast10 = (c.id.user || "").replace(/\D/g, "").slice(-10);
      return (
        chatIdLast10 === last10 ||
        (c.name || "").includes(last10)
      );
    });

    if (matchedChat && matchedChat.name && !matchedChat.name.match(/^\+?\d+$/)) {
      // Chat has a real name (not just a phone number), use it
      return matchedChat.name;
    }
  } catch (e) {
    // ignore, fall through
  }

  // Step 3: Try WhatsApp contact API for profile pushname
  try {
    const contact = await client.getContactById(waId);
    const name = contact.pushname || contact.name;
    if (name && name.trim() && !name.match(/^\+?\d+$/)) {
      return name.trim();
    }
  } catch (e) {
    // Contact API failed (might be @lid contact) — fall through
  }

  // Step 4: Fall back to formatted phone number
  return `+91${last10}`;
}

/**
 * Convert phone number to WhatsApp chat ID format.
 * Defaults to India (+91) if no country code.
 * @param {string} phone
 * @returns {string} e.g. "919869101909@c.us"
 */
function toWaId(phone) {
  const digits = phone.replace(/\D/g, "");
  if (digits.length > 10) {
    return `${digits}@c.us`;
  }
  return `91${digits}@c.us`;
}

module.exports = { CONTACT_CACHE, getContactName, resolveContactName, toWaId };
