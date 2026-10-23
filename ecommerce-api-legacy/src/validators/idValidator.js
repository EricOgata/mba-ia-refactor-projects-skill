const { ValidationError } = require('../errors');

function validateId(rawId) {
    const id = Number(rawId);
    if (!Number.isInteger(id) || id <= 0) throw new ValidationError('Bad Request');
    return id;
}

module.exports = { validateId };
