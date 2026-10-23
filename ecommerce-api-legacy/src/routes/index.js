const { Router } = require('express');
const { createCheckoutRoutes } = require('./checkoutRoutes');
const { createAdminRoutes } = require('./adminRoutes');
const { createUserRoutes } = require('./userRoutes');

function createRoutes({
    checkoutController,
    financialReportController,
    userController,
    requireAdmin,
}) {
    const router = Router();

    router.use(createCheckoutRoutes({ checkoutController }));
    router.use(createAdminRoutes({ financialReportController, requireAdmin }));
    router.use(createUserRoutes({ userController, requireAdmin }));

    return router;
}

module.exports = { createRoutes };
