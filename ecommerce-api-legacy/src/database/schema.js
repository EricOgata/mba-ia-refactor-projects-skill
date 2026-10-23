const crypto = require('crypto');
const { runMigrations } = require('./migrator');
const { hashPassword } = require('../utils/password');

async function initializeSchema(db) {
    await runMigrations(db);

    const { count } = await db.get('SELECT COUNT(*) AS count FROM users');
    if (count > 0) return;

    // Senha aleatória: o usuário de seed não possui fluxo de login neste serviço.
    const seedPassword = hashPassword(crypto.randomBytes(32).toString('hex'));

    await db.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', seedPassword]
    );
    await db.run(
        "INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)"
    );
    await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
}

module.exports = { initializeSchema };
