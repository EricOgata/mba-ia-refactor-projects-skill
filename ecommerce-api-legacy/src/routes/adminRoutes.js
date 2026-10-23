const { Router } = require('express');

function createAdminRoutes({ financialReportController, requireAdmin }) {
    const router = Router();
    router.get('/admin/financial-report', requireAdmin, financialReportController.getReport);
    return router;
}

module.exports = { createAdminRoutes };
