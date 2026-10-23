const sqlite3 = require('sqlite3').verbose();

function createDatabase(filename) {
    const db = new sqlite3.Database(filename);

    const run = (sql, params = []) => new Promise((resolve, reject) => {
        db.run(sql, params, function onRun(err) {
            if (err) return reject(err);
            return resolve({ lastID: this.lastID, changes: this.changes });
        });
    });

    const get = (sql, params = []) => new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });

    const all = (sql, params = []) => new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });

    const exec = (sql) => new Promise((resolve, reject) => {
        db.exec(sql, (err) => (err ? reject(err) : resolve()));
    });

    const close = () => new Promise((resolve, reject) => {
        db.close((err) => (err ? reject(err) : resolve()));
    });

    const database = {
        run,
        get,
        all,
        exec,
        close,
        async transaction(work) {
            await run('BEGIN IMMEDIATE');
            try {
                const result = await work(database);
                await run('COMMIT');
                return result;
            } catch (err) {
                try {
                    await run('ROLLBACK');
                } catch (rollbackErr) {
                    err.rollbackError = rollbackErr;
                }
                throw err;
            }
        },
    };

    db.run('PRAGMA foreign_keys = ON');
    db.configure('busyTimeout', 5000);

    return database;
}

module.exports = { createDatabase };
