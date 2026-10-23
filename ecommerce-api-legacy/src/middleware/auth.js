const crypto = require('crypto');

function safeEqual(left, right) {
    const leftBuffer = Buffer.from(String(left));
    const rightBuffer = Buffer.from(String(right));
    if (leftBuffer.length !== rightBuffer.length) return false;
    return crypto.timingSafeEqual(leftBuffer, rightBuffer);
}

function createRequireAdmin({ adminToken }) {
    return function requireAdmin(req, res, next) {
        if (!adminToken) {
            return res.status(503).json({ error: 'Admin authentication is not configured' });
        }

        const [scheme, token] = (req.get('authorization') || '').split(' ');
        if (scheme !== 'Bearer' || !token || !safeEqual(token, adminToken)) {
            return res.status(401).json({ error: 'Unauthorized' });
        }

        return next();
    };
}

module.exports = { createRequireAdmin };
