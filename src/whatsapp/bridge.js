import { makeWASocket, useMultiFileAuthState, DisconnectReason, downloadMediaMessage } from '@whiskeysockets/baileys';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import pino from 'pino';

// Setup paths
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '../../');
const DATA_DIR = path.resolve(PROJECT_ROOT, 'data');
const AUTH_DIR = path.resolve(DATA_DIR, 'whatsapp_auth');
const INBOX_BUFFER = path.resolve(DATA_DIR, 'inbox_buffer');
const ATTACHMENTS_BUFFER = path.resolve(DATA_DIR, 'attachments_buffer');
const STATE_FILE = path.resolve(DATA_DIR, 'whatsapp_state.json');

// Ensure directories exist
[INBOX_BUFFER, ATTACHMENTS_BUFFER].forEach(dir => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// Load Env
dotenv.config({ path: path.resolve(PROJECT_ROOT, '.env') });
const TARGET_GROUP_ID = process.env.WHATSAPP_GROUP_ID;

if (!TARGET_GROUP_ID) {
    console.error("❌ ERROR: WHATSAPP_GROUP_ID is missing in .env file.");
    process.exit(1);
}

// State Management
function getLastTimestamp() {
    try {
        if (fs.existsSync(STATE_FILE)) {
            const data = JSON.parse(fs.readFileSync(STATE_FILE));
            return data.last_timestamp || Math.floor(Date.now() / 1000);
        }
    } catch (e) { console.error("Error reading state:", e); }
    return Math.floor(Date.now() / 1000) - 86400; // Default: Last 24 hours if no state
}

function updateLastTimestamp(ts) {
    try {
        fs.writeFileSync(STATE_FILE, JSON.stringify({ last_timestamp: ts }));
    } catch (e) { console.error("Error saving state:", e); }
}

let lastProcessedTime = getLastTimestamp();

async function startBridge() {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

    const sock = makeWASocket({
        auth: state,
        // printQRInTerminal: true, // DEPRECATED
        logger: pino({ level: 'silent' }),
        // Ensure we fetch history
        markOnlineOnConnect: true 
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update; // Capture QR from update

        if (qr) {
            console.log('\nScan this QR code with your WhatsApp app:');
            // We need to import qrcode-terminal here or at top
            // Since this file didn't import it, I'll assume the user scans via get_groups first
            // But to be safe, let's just log that QR is available
            console.log("QR Code received. Please run 'node src/whatsapp/get_groups.js' first to authenticate interactively.");
            // Or better: Use the same session as get_groups so we don't need to scan again here.
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('connection closed due to ', lastDisconnect.error, ', reconnecting ', shouldReconnect);
            if (shouldReconnect) startBridge();
        } else if (connection === 'open') {
            console.log('✅ Bridge Connected! Listening for messages...');
            console.log(`Target Group: ${TARGET_GROUP_ID}`);
        }
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        for (const msg of messages) {
            if (!msg.message) continue; // Ignore system messages
            
            const jid = msg.key.remoteJid;
            const ts = msg.messageTimestamp;
            
            // FILTER: Only Target Group
            if (jid !== TARGET_GROUP_ID) continue;

            // FILTER: Deduplication (Time based)
            // We use >= to allow processing multiple messages in the same second,
            // but we rely on filename uniqueness for true deduplication.
            // Strict > might skip messages if they arrive in same batch.
            // Better to rely on file uniqueness or just process everything from the "upsert" batch if it looks new.
            // For safety, we skip anything OLDER than our last checkpoint.
            if (ts < lastProcessedTime) continue;

            console.log(`📥 Received message from ${msg.pushName || 'User'} (${ts})`);

            try {
                // 1. Extract Text
                let text = msg.message.conversation || 
                           msg.message.extendedTextMessage?.text || 
                           msg.message.imageMessage?.caption || 
                           msg.message.videoMessage?.caption ||
                           msg.message.documentMessage?.caption || "";

                // 2. Handle Attachments
                let attachmentPath = null;
                const isMedia = msg.message.imageMessage || msg.message.videoMessage || msg.message.documentMessage;

                if (isMedia) {
                    console.log("   📎 Downloading attachment...");
                    const buffer = await downloadMediaMessage(
                        msg,
                        'buffer',
                        { logger: pino({ level: 'silent' }) }
                    );
                    
                    // Generate filename
                    let ext = '.bin';
                    if (msg.message.imageMessage) ext = '.jpg';
                    if (msg.message.videoMessage) ext = '.mp4';
                    if (msg.message.documentMessage) ext = path.extname(msg.message.documentMessage.fileName || "") || '.pdf';

                    const filename = `att_${ts}_${msg.key.id}${ext}`;
                    attachmentPath = path.resolve(ATTACHMENTS_BUFFER, filename);
                    
                    fs.writeFileSync(attachmentPath, buffer);
                    console.log(`   ✅ Saved to: ${filename}`);
                }

                // 3. Create JSON Packet
                const packet = {
                    source: "whatsapp",
                    id: msg.key.id,
                    timestamp: ts,
                    sender: msg.pushName || "Unknown",
                    text: text,
                    media_path: attachmentPath, // Absolute path
                    raw_msg: msg // Debugging
                };

                const jsonFilename = `wa_${ts}_${msg.key.id}.json`;
                fs.writeFileSync(path.resolve(INBOX_BUFFER, jsonFilename), JSON.stringify(packet, null, 2));
                
                // Update State
                if (ts > lastProcessedTime) {
                    lastProcessedTime = ts;
                    updateLastTimestamp(ts);
                }

            } catch (err) {
                console.error("   ❌ Error processing message:", err);
            }
        }
    });
}

startBridge();
