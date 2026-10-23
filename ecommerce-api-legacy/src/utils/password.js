const crypto = require('crypto');

const ALGORITHM = 'scrypt';
const SALT_BYTES = 16;
const KEY_BYTES = 64;

function hashPassword(password) {
    if (typeof password !== 'string' || password.length === 0) {
        throw new TypeError('password is required');
    }

    const salt = crypto.randomBytes(SALT_BYTES);
    const derived = crypto.scryptSync(password, salt, KEY_BYTES);
    return `${ALGORITHM}$${salt.toString('hex')}$${derived.toString('hex')}`;
}

function verifyPassword(password, storedHash) {
    if (typeof password !== 'string' || typeof storedHash !== 'string') return false;

    const [algorithm, saltHex, hashHex] = storedHash.split('$');
    if (algorithm !== ALGORITHM || !saltHex || !hashHex) return false;

    const salt = Buffer.from(saltHex, 'hex');
    const expected = Buffer.from(hashHex, 'hex');
    if (salt.length === 0 || expected.length === 0) return false;

    const derived = crypto.scryptSync(password, salt, expected.length);
    return derived.length === expected.length && crypto.timingSafeEqual(derived, expected);
}

module.exports = { hashPassword, verifyPassword };
