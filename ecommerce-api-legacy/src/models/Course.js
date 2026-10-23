function isPurchasable(course) {
    return Boolean(course && course.active === 1);
}

module.exports = { isPurchasable };
