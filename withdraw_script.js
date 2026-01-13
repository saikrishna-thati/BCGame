/**
 * WooFi/Orderly Full USDC Withdrawal Script - V2 (Parallel Processing)
 *
 * Purpose: Scan all wallets and withdraw USDC with parallel processing for speed
 *
 * Features:
 * - Parallel processing of wallets (configurable concurrency)
 * - Batch processing per seed phrase
 * - Real-time progress updates
 * - Comprehensive summary
 */

const { ethers } = require('ethers');
const axios = require('axios');
const nacl = require('tweetnacl');
const bs58 = require('bs58');
const fs = require('fs');
require('dotenv').config();

// --- Configuration ---
const RPC_URL = 'https://sepolia-rollup.arbitrum.io/rpc';
const PROVIDER = new ethers.JsonRpcProvider(RPC_URL);

// API Endpoints
const ORDERLY_API_URL = 'https://testnet-api.orderly.org';

// Contracts
const ORDERLY_OFF_CHAIN_DOMAIN_CONTRACT = '0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC';
const ORDERLY_VAULT_CONTRACT_ARB_SEPOLIA = '0x0EaC556c0C2321BA25b9DC01e4e3c95aD5CDCd2f';
// Orderly L2 Ledger (Verifying contract for Withdrawals)
const ORDERLY_LEDGER_CONTRACT_L2 = '0x1826B75e2ef249173FC735149AE4B8e9ea10abff';

// Chain IDs
const ARB_SEPOLIA_CHAIN_ID = 421614;
const ORDERLY_L2_CHAIN_ID = 291;

// Broker
const BROKER_ID = 'woofi_pro';

// Wallet indices to scan
const MIN_INDEX = 0;
const MAX_INDEX = 300;

// PARALLEL PROCESSING CONFIG
const CONCURRENCY = 20; // Number of wallets to process simultaneously (increased for speed)

// Target address
const TARGET_ADDRESS = process.env.FUNDER_PRIVATE_KEY
    ? new ethers.Wallet(process.env.FUNDER_PRIVATE_KEY).address
    : '0xF22B976EA899662017EC98d3E1B1299aDfD89df2';

// Helper
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

const log = (msg, level = 'INFO') => {
    const time = new Date().toISOString().split('T')[1].split('.')[0];
    const prefix = level === 'INFO' ? '' : `[${level}] `;
    console.log(`[${time}] ${prefix}${msg}`);
};

// Statistics (thread-safe with atomic operations)
const stats = {
    totalWalletsChecked: 0,
    walletsWithBalance: 0,
    successfulWithdrawals: 0,
    failedWithdrawals: 0,
    totalUSDCWithdrawn: 0,
    errors: []
};

/**
 * Create an axios instance with retry logic
 */
function createApiClient() {
    const client = axios.create({
        baseURL: ORDERLY_API_URL,
        timeout: 30000,
        headers: { 'Content-Type': 'application/json' }
    });
    return client;
}

/**
 * Get account from API
 */
async function getAccountFromAPI(api, userAddress) {
    try {
        const res = await api.get(`/v1/get_account?address=${userAddress}&broker_id=${BROKER_ID}`);
        if (res.data.success && res.data.data) {
            return res.data.data;
        }
        return null;
    } catch (err) {
        return null;
    }
}

/**
 * Register account if needed
 */
async function registerAccount(api, wallet) {
    try {
        const nonceRes = await api.get('/v1/registration_nonce');
        const registrationNonce = nonceRes.data.data.registration_nonce;

        const domain = {
            name: 'Orderly',
            version: '1',
            chainId: ARB_SEPOLIA_CHAIN_ID,
            verifyingContract: ORDERLY_OFF_CHAIN_DOMAIN_CONTRACT
        };

        const types = {
            Registration: [
                { name: 'brokerId', type: 'string' },
                { name: 'chainId', type: 'uint256' },
                { name: 'timestamp', type: 'uint64' },
                { name: 'registrationNonce', type: 'uint256' }
            ]
        };

        const timestamp = Date.now();
        const message = {
            brokerId: BROKER_ID,
            chainId: ARB_SEPOLIA_CHAIN_ID,
            timestamp: timestamp,
            registrationNonce: registrationNonce
        };

        const signature = await wallet.signTypedData(domain, types, message);

        await api.post('/v1/register_account', {
            message,
            signature,
            userAddress: wallet.address
        });

        return true;
    } catch (err) {
        if (err.response?.data?.message?.includes('already')) {
            return true;
        }
        return false;
    }
}

/**
 * Add Orderly Key
 */
async function addOrderlyKey(api, wallet) {
    const keyPair = nacl.sign.keyPair();
    const orderlyKey = 'ed25519:' + bs58.encode(Buffer.from(keyPair.publicKey));
    const orderlySecret = Buffer.from(keyPair.secretKey);
    const timestamp = Date.now();

    const domain = {
        name: 'Orderly',
        version: '1',
        chainId: ARB_SEPOLIA_CHAIN_ID,
        verifyingContract: ORDERLY_OFF_CHAIN_DOMAIN_CONTRACT
    };

    const types = {
        AddOrderlyKey: [
            { name: 'brokerId', type: 'string' },
            { name: 'chainId', type: 'uint256' },
            { name: 'orderlyKey', type: 'string' },
            { name: 'scope', type: 'string' },
            { name: 'timestamp', type: 'uint64' },
            { name: 'expiration', type: 'uint64' }
        ]
    };

    const message = {
        brokerId: BROKER_ID,
        chainId: ARB_SEPOLIA_CHAIN_ID,
        orderlyKey: orderlyKey,
        scope: 'read,trading',
        timestamp: timestamp,
        expiration: timestamp + 1000 * 60 * 60 * 24 * 30
    };

    const signature = await wallet.signTypedData(domain, types, message);

    try {
        await api.post('/v1/orderly_key', {
            message,
            signature,
            userAddress: wallet.address
        });
        return { orderlyKey, orderlySecret };
    } catch (err) {
        return null;
    }
}

/**
 * Create signed request headers
 */
function createAuthHeaders(orderlyKey, orderlySecret, accountId, method, path, body = null) {
    const timestamp = Date.now().toString();
    let message = `${timestamp}${method}${path}`;
    if (body) {
        message += JSON.stringify(body);
    }

    const signatureBytes = nacl.sign.detached(Buffer.from(message), orderlySecret);
    const signature = Buffer.from(signatureBytes).toString('base64url');

    return {
        'orderly-account-id': accountId,
        'orderly-key': orderlyKey,
        'orderly-timestamp': timestamp,
        'orderly-signature': signature,
        'Content-Type': 'application/json'
    };
}

/**
 * Get USDC balance with retry
 */
async function getUSDCBalance(api, orderlyKey, orderlySecret, accountId) {
    const path = '/v1/client/holding';

    for (let attempt = 1; attempt <= 3; attempt++) {
        const headers = createAuthHeaders(orderlyKey, orderlySecret, accountId, 'GET', path);

        try {
            const res = await api.get(path, { headers });
            if (res.data.success && res.data.data?.holding) {
                const usdc = res.data.data.holding.find(h => h.token === 'USDC');
                return usdc ? parseFloat(usdc.holding) : 0;
            }
            return 0;
        } catch (err) {
            const errMsg = err.response?.data?.message || err.message;
            if (errMsg.includes('orderly key error') && attempt < 3) {
                await delay(1500);
                continue;
            }
            return 0;
        }
    }
    return 0;
}

/**
 * Get withdrawal nonce
 */
async function getWithdrawNonce(api, orderlyKey, orderlySecret, accountId) {
    const path = '/v1/withdraw_nonce';
    const headers = createAuthHeaders(orderlyKey, orderlySecret, accountId, 'GET', path);

    try {
        const res = await api.get(path, { headers });
        return res.data.data.withdraw_nonce;
    } catch (err) {
        return null;
    }
}

/**
 * Withdraw USDC
 */
async function withdrawUSDC(api, wallet, amount, accountId, orderlyKey, orderlySecret, receiverAddress) {
    const withdrawNonce = await getWithdrawNonce(api, orderlyKey, orderlySecret, accountId);
    if (!withdrawNonce) {
        return false;
    }

    const timestamp = Date.now();
    const amountWei = ethers.parseUnits(amount.toString(), 6).toString();

    // IMPORTANT: Withdrawals use Orderly L2 Ledger contract as verifying contract
    const domain = {
        name: 'Orderly',
        version: '1',
        chainId: ORDERLY_L2_CHAIN_ID, // 291
        verifyingContract: ORDERLY_LEDGER_CONTRACT_L2
    };

    const types = {
        Withdraw: [
            { name: 'brokerId', type: 'string' },
            { name: 'chainId', type: 'uint256' },
            { name: 'receiver', type: 'address' },
            { name: 'token', type: 'string' },
            { name: 'amount', type: 'uint256' },
            { name: 'withdrawNonce', type: 'uint64' },
            { name: 'timestamp', type: 'uint64' }
        ]
    };

    const withdrawMessage = {
        brokerId: BROKER_ID,
        chainId: ARB_SEPOLIA_CHAIN_ID, // Destination Chain ID
        receiver: receiverAddress,
        token: 'USDC',
        amount: amountWei,
        withdrawNonce: withdrawNonce,
        timestamp: timestamp
    };

    const signature = await wallet.signTypedData(domain, types, withdrawMessage);

    const path = '/v1/withdraw_request';
    const body = {
        message: withdrawMessage,
        signature: signature,
        userAddress: wallet.address,
        verifyingContract: ORDERLY_LEDGER_CONTRACT_L2 // Send the contract address used for verification
    };

    const headers = createAuthHeaders(orderlyKey, orderlySecret, accountId, 'POST', path, body);

    try {
        await api.post(path, body, { headers });
        return true;
    } catch (err) {
        // Log detailed error if possible
        if (err.response) {
            console.error(`Withdrawal Error details:`, err.response.data);
        }
        return false;
    }
}

/**
 * Process a single wallet (FAST - skip unregistered wallets)
 */
async function processWallet(wallet, seedIdx, walletIdx) {
    const api = createApiClient();
    const address = wallet.address;
    const prefix = `[S${seedIdx + 1}:I${walletIdx}]`;

    stats.totalWalletsChecked++;

    try {
        // Step 1: Quick check if account exists (NO registration - just skip if not found)
        const accountData = await getAccountFromAPI(api, address);

        if (!accountData || !accountData.account_id) {
            // No account = no USDC, skip immediately
            return null;
        }

        const accountId = accountData.account_id;

        // Step 2: Add Orderly key (required to check balance)
        const keyData = await addOrderlyKey(api, wallet);
        if (!keyData) {
            return null;
        }

        const { orderlyKey, orderlySecret } = keyData;

        // Step 3: Reduced delay for key propagation (was 2000, now 500)
        await delay(500);

        // Step 4: Check balance
        const balance = await getUSDCBalance(api, orderlyKey, orderlySecret, accountId);

        if (balance <= 0) {
            return null;
        }

        // Found USDC!
        stats.walletsWithBalance++;
        log(`${prefix} 💰 Found ${balance} USDC at ${address.slice(0, 8)}...`);

        // Step 5: Withdraw
        const result = await withdrawUSDC(
            api,
            wallet,
            balance,
            accountId,
            orderlyKey,
            orderlySecret,
            TARGET_ADDRESS
        );

        if (result) {
            stats.successfulWithdrawals++;
            stats.totalUSDCWithdrawn += balance;
            log(`${prefix} ✅ Withdrawn ${balance} USDC -> ${TARGET_ADDRESS.slice(0, 8)}...`);
            return { address, balance, success: true };
        } else {
            stats.failedWithdrawals++;
            log(`${prefix} ❌ Withdrawal failed for ${balance} USDC`, 'ERROR');
            return { address, balance, success: false };
        }

    } catch (err) {
        stats.errors.push({ seedIdx, walletIdx, address, error: err.message });
        return null;
    }
}

/**
 * Process wallets in parallel batches
 */
async function processInParallel(wallets, seedIdx) {
    const results = [];

    // Process in batches of CONCURRENCY
    for (let i = 0; i < wallets.length; i += CONCURRENCY) {
        const batch = wallets.slice(i, i + CONCURRENCY);

        const batchPromises = batch.map(({ wallet, walletIdx }) =>
            processWallet(wallet, seedIdx, walletIdx)
        );

        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults.filter(r => r !== null));

        // Small delay between batches to prevent rate limiting
        if (i + CONCURRENCY < wallets.length) {
            await delay(100);
        }
    }

    return results;
}

/**
 * Main function
 */
async function main() {
    console.log('');
    log('═'.repeat(60));
    log('   WooFi/Orderly USDC Withdrawal Script V2 (PARALLEL)');
    log('═'.repeat(60));
    console.log('');

    // Read seed phrases
    if (!fs.existsSync('seedphrases_2000wallets.txt')) {
        log('ERROR: seedphrases_2000wallets.txt not found!', 'ERROR');
        process.exit(1);
    }

    const seedPhrases = fs.readFileSync('seedphrases_2000wallets.txt', 'utf8')
        .split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);

    const totalWallets = seedPhrases.length * (MAX_INDEX - MIN_INDEX + 1);

    log(`Found ${seedPhrases.length} seed phrases`);
    log(`Scanning indices ${MIN_INDEX} to ${MAX_INDEX} (${MAX_INDEX - MIN_INDEX + 1} wallets per seed)`);
    log(`Total wallets to check: ${totalWallets}`);
    log(`Concurrency: ${CONCURRENCY} parallel workers`);
    log(`Target address: ${TARGET_ADDRESS}`);
    console.log('');

    const startTime = Date.now();

    // Process each seed phrase
    for (let seedIdx = 0; seedIdx < seedPhrases.length; seedIdx++) {
        const seedPhrase = seedPhrases[seedIdx];
        log(`─── Seed Phrase ${seedIdx + 1}/${seedPhrases.length} ───`);

        let mnemonic;
        try {
            mnemonic = ethers.Mnemonic.fromPhrase(seedPhrase);
        } catch (err) {
            log(`Invalid seed phrase at index ${seedIdx}, skipping`, 'ERROR');
            continue;
        }

        // Create all wallet objects for this seed phrase
        const wallets = [];
        for (let walletIdx = MIN_INDEX; walletIdx <= MAX_INDEX; walletIdx++) {
            const wallet = ethers.HDNodeWallet.fromMnemonic(
                mnemonic,
                `m/44'/60'/0'/0/${walletIdx}`
            ).connect(PROVIDER);
            wallets.push({ wallet, walletIdx });
        }

        // Process all wallets in parallel
        await processInParallel(wallets, seedIdx);

        console.log('');
    }

    // Print summary
    const duration = ((Date.now() - startTime) / 1000).toFixed(1);
    const durationMin = (duration / 60).toFixed(1);

    console.log('');
    log('═'.repeat(60));
    log('   SUMMARY');
    log('═'.repeat(60));
    log(`Total wallets checked:     ${stats.totalWalletsChecked}`);
    log(`Wallets with USDC:         ${stats.walletsWithBalance}`);
    log(`Successful withdrawals:    ${stats.successfulWithdrawals}`);
    log(`Failed withdrawals:        ${stats.failedWithdrawals}`);
    log(`Total USDC withdrawn:      ${stats.totalUSDCWithdrawn.toFixed(2)} USDC`);
    log(`Duration:                  ${duration}s (${durationMin} min)`);
    log(`Speed:                     ${(stats.totalWalletsChecked / duration * 60).toFixed(1)} wallets/min`);
    log(`Target address:            ${TARGET_ADDRESS}`);

    if (stats.errors.length > 0) {
        console.log('');
        log(`Errors encountered: ${stats.errors.length}`, 'WARN');
        stats.errors.slice(0, 5).forEach(e => {
            log(`  - S${e.seedIdx + 1}:I${e.walletIdx}: ${e.error}`, 'WARN');
        });
    }

    console.log('');
    log('═'.repeat(60));
    log('   DONE!');
    log('═'.repeat(60));
    console.log('');

    if (stats.successfulWithdrawals > 0) {
        log('Note: Withdrawals are processed via LayerZero bridge.');
        log('Funds typically arrive in 10-30 minutes.');
    }
}

main().catch(err => {
    log(`FATAL ERROR: ${err.message}`, 'ERROR');
    console.error(err);
    process.exit(1);
});