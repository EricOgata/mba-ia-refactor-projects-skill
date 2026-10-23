const { AuditLogRepository } = require('./repositories/AuditLogRepository');
const { CourseRepository } = require('./repositories/CourseRepository');
const { EnrollmentRepository } = require('./repositories/EnrollmentRepository');
const { PaymentRepository } = require('./repositories/PaymentRepository');
const { ReportRepository } = require('./repositories/ReportRepository');
const { UserRepository } = require('./repositories/UserRepository');
const { CheckoutService } = require('./services/CheckoutService');
const { FinancialReportService } = require('./services/FinancialReportService');
const { PaymentGateway } = require('./services/PaymentGateway');
const { UserService } = require('./services/UserService');
const { createCheckoutController } = require('./controllers/CheckoutController');
const { createFinancialReportController } = require('./controllers/FinancialReportController');
const { createUserController } = require('./controllers/UserController');

function buildContainer({ db, config, logger }) {
    const userRepository = new UserRepository(db);
    const courseRepository = new CourseRepository(db);
    const enrollmentRepository = new EnrollmentRepository(db);
    const paymentRepository = new PaymentRepository(db);
    const auditLogRepository = new AuditLogRepository(db);
    const reportRepository = new ReportRepository(db);

    const paymentGateway = new PaymentGateway({ apiKey: config.paymentGatewayKey });

    const checkoutService = new CheckoutService({
        userRepository,
        courseRepository,
        enrollmentRepository,
        paymentRepository,
        auditLogRepository,
        paymentGateway,
        unitOfWork: db,
        logger,
    });

    const financialReportService = new FinancialReportService({ reportRepository });

    const userService = new UserService({
        userRepository,
        enrollmentRepository,
        paymentRepository,
        unitOfWork: db,
    });

    return {
        checkoutController: createCheckoutController({ checkoutService }),
        financialReportController: createFinancialReportController({ financialReportService }),
        userController: createUserController({ userService }),
    };
}

module.exports = { buildContainer };
