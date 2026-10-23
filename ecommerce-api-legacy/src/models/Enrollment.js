function createEnrollment({ userId, courseId }) {
    if (!Number.isInteger(userId) || userId <= 0) throw new TypeError('userId is invalid');
    if (!Number.isInteger(courseId) || courseId <= 0) throw new TypeError('courseId is invalid');

    return { userId, courseId };
}

module.exports = { createEnrollment };
