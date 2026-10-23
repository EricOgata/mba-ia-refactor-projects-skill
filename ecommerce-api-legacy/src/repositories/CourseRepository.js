class CourseRepository {
    constructor(db) {
        this.db = db;
    }

    findActiveById(id, tx = this.db) {
        return tx.get(
            'SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1',
            [id]
        );
    }
}

module.exports = { CourseRepository };
