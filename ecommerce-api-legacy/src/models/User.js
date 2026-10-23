const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function isValidEmail(email) {
    return typeof email === 'string' && EMAIL_PATTERN.test(email);
}

function createUser({ name, email, pass }) {
    if (typeof name !== 'string' || !name.trim()) throw new TypeError('name is required');
    if (!isValidEmail(email)) throw new TypeError('email is invalid');
    if (typeof pass !== 'string' || !pass) throw new TypeError('pass is required');

    return { name, email, pass };
}

module.exports = { isValidEmail, createUser };
