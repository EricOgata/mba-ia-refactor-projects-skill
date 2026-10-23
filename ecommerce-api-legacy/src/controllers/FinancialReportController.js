const { asyncHandler } = require('../middleware/asyncHandler');

function createFinancialReportController({ financialReportService }) {
    return {
        getReport: asyncHandler(async (req, res) => {
            const report = await financialReportService.generate();
            res.json(report);
        }),
    };
}

module.exports = { createFinancialReportController };
