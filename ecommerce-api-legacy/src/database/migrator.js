const fs = require('fs');
const path = require('path');

const MIGRATIONS_DIR = path.join(__dirname, 'migrations');

async function runMigrations(db) {
    await db.run(`
        CREATE TABLE IF NOT EXISTS schema_migrations (
            name TEXT PRIMARY KEY,
            applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    `);

    const appliedRows = await db.all('SELECT name FROM schema_migrations');
    const applied = new Set(appliedRows.map((row) => row.name));

    const files = fs.readdirSync(MIGRATIONS_DIR)
        .filter((file) => file.endsWith('.sql'))
        .sort();

    for (const file of files) {
        if (applied.has(file)) continue;

        const sql = fs.readFileSync(path.join(MIGRATIONS_DIR, file), 'utf8');
        await db.transaction(async (tx) => {
            await tx.exec(sql);
            await tx.run('INSERT INTO schema_migrations (name) VALUES (?)', [file]);
        });
    }
}

module.exports = { runMigrations };
