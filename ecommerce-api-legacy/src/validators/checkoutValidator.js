const { ValidationError } = require('../errors');
const { isValidEmail } = require('../models/User');

function validateCheckout(body) {
    const data = body && typeof body === 'object' ? body : {};
    const { usr, eml, pwd, c_id, card } = data;

    if (!usr || !eml || c_id === undefined || c_id === null || !card) {
        throw new ValidationError('Bad Request');
    }
    if (typeof usr !== 'string' || !usr.trim()) throw new ValidationError('Bad Request');
    if (typeof eml !== 'string' || !isValidEmail(eml)) throw new ValidationError('Bad Request');

    const courseId = Number(c_id);
    if (!Number.isInteger(courseId) || courseId <= 0) throw new ValidationError('Bad Request');
    if (typeof card !== 'string' || !/^\d{13,19}$/.test(card)) throw new ValidationError('Bad Request');
    if (pwd !== undefined && typeof pwd !== 'string') throw new ValidationError('Bad Request');

    return { name: usr, email: eml, password: pwd, courseId, card };
}

module.exports = { validateCheckout };
