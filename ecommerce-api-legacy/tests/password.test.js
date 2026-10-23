const { test } = require('node:test');
const assert = require('node:assert/strict');
const { hashPassword, verifyPassword } = require('../src/utils/password');

test('hashPassword gera hash scrypt com salt e verifyPassword valida', () => {
    const first = hashPassword('senha-secreta');
    const second = hashPassword('senha-secreta');

    assert.match(first, /^scrypt\$[0-9a-f]{32}\$[0-9a-f]{128}$/);
    assert.notEqual(first, second, 'hashes devem ser diferentes por causa do salt');
    assert.equal(verifyPassword('senha-secreta', first), true);
    assert.equal(verifyPassword('senha-errada', first), false);
    assert.equal(verifyPassword('senha-secreta', 'hash-invalido'), false);
});
