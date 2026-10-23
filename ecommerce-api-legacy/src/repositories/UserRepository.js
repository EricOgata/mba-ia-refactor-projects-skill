class UserRepository {
    constructor(db) {
        this.db = db;
    }

    findByEmail(email, tx = this.db) {
        return tx.get('SELECT id, name, email, pass FROM users WHERE email = ?', [email]);
    }

    findById(id, tx = this.db) {
        return tx.get('SELECT id, name, email FROM users WHERE id = ?', [id]);
    }

    async create({ name, email, pass }, tx = this.db) {
        const { lastID } = await tx.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, pass]
        );
        return lastID;
    }

    deleteById(id, tx = this.db) {
        return tx.run('DELETE FROM users WHERE id = ?', [id]);
    }
}

module.exports = { UserRepository };
