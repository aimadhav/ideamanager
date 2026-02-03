import { makeWASocket, useMultiFileAuthState, DisconnectReason } from '@whiskeysockets/baileys';
import qrcode from 'qrcode-terminal';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

// Fix for __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to store authentication credentials
// We store this in the main data directory, not inside src
const AUTH_DIR = path.resolve(__dirname, '../../data/whatsapp_auth');

async function connectToWhatsApp() {
    // Ensure auth directory exists
    if (!fs.existsSync(AUTH_DIR)) {
        fs.mkdirSync(AUTH_DIR, { recursive: true });
    }

    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

    const sock = makeWASocket({
        // printQRInTerminal: true, // DEPRECATED: Caused issues with v6.7.9
        auth: state,
        // Silent logging to keep terminal clean
        logger: (await import('pino')).default({ level: 'silent' }) 
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\nScan this QR code with your WhatsApp app:');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Connection closed due to ', lastDisconnect.error, ', reconnecting ', shouldReconnect);
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('\n✅ Connected to WhatsApp!');
            listGroups(sock);
        }
    });

    sock.ev.on('creds.update', saveCreds);
}

async function listGroups(sock) {
    console.log('Fetching groups... (this may take a few seconds)');
    
    // Fetch all chats
    const groups = await sock.groupFetchAllParticipating();
    const groupList = Object.values(groups);

    console.log('\n=== YOUR GROUPS ===');
    if (groupList.length === 0) {
        console.log('No groups found.');
    } else {
        groupList.forEach(g => {
            console.log(`Name: ${g.subject}`);
            console.log(`ID:   ${g.id}`);
            console.log('-------------------');
        });
    }
    console.log('\nCopy the ID of the group you want to use into your .env file as WHATSAPP_GROUP_ID');
    console.log('Press Ctrl+C to exit.');
}

connectToWhatsApp();
