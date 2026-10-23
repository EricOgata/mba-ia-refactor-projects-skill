const PAYMENT_STATUS = Object.freeze({
    PAID: 'PAID',
    DENIED: 'DENIED',
});

function createPayment({ enrollmentId, amount, status }) {
    if (!Number.isInteger(enrollmentId) || enrollmentId <= 0) throw new TypeError('enrollmentId is invalid');
    if (typeof amount !== 'number' || Number.isNaN(amount)) throw new TypeError('amount is invalid');
    if (!Object.values(PAYMENT_STATUS).includes(status)) throw new TypeError('status is invalid');

    return { enrollmentId, amount, status };
}

module.exports = { PAYMENT_STATUS, createPayment };
