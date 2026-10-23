const { PAYMENT_STATUS } = require('../models/Payment');

class FinancialReportService {
    constructor({ reportRepository }) {
        this.reportRepository = reportRepository;
    }

    async generate() {
        const rows = await this.reportRepository.getFinancialRows();
        const courses = new Map();

        for (const row of rows) {
            if (!courses.has(row.course_id)) {
                courses.set(row.course_id, { course: row.course, revenue: 0, students: [] });
            }

            const courseData = courses.get(row.course_id);
            if (row.enrollment_id === null || row.enrollment_id === undefined) continue;

            const paid = row.paid === null || row.paid === undefined ? 0 : row.paid;
            if (row.payment_status === PAYMENT_STATUS.PAID) courseData.revenue += paid;

            courseData.students.push({
                student: row.student || 'Unknown',
                paid,
            });
        }

        return Array.from(courses.values());
    }
}

module.exports = { FinancialReportService };
