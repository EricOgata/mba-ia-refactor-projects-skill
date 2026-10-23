class AuditLogRepository {
    constructor(db) {
        this.db = db;
    }

    async create(action, tx = this.db) {
        const { lastID } = await tx.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
        return lastID;
    }
}

module.exports = { AuditLogRepository };
