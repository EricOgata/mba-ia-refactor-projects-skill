class EnrollmentRepository {
    constructor(db) {
        this.db = db;
    }

    async create({ userId, courseId }, tx = this.db) {
        const { lastID } = await tx.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId]
        );
        return lastID;
    }

    deleteByUserId(userId, tx = this.db) {
        return tx.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    }
}

module.exports = { EnrollmentRepository };
