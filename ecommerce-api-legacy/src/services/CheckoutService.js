const { NotFoundError, PaymentDeniedError, ValidationError } = require('../errors');
const { createEnrollment } = require('../models/Enrollment');
const { createPayment, PAYMENT_STATUS } = require('../models/Payment');
const { createUser } = require('../models/User');
const { isPurchasable } = require('../models/Course');
const { hashPassword } = require('../utils/password');

class CheckoutService {
    constructor({
        userRepository,
        courseRepository,
        enrollmentRepository,
        paymentRepository,
        auditLogRepository,
        paymentGateway,
        unitOfWork,
        logger,
    }) {
        this.userRepository = userRepository;
        this.courseRepository = courseRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.paymentRepository = paymentRepository;
        this.auditLogRepository = auditLogRepository;
        this.paymentGateway = paymentGateway;
        this.unitOfWork = unitOfWork;
        this.logger = logger;
    }

    async checkout({ name, email, password, courseId, card }) {
        const course = await this.courseRepository.findActiveById(courseId);
        if (!isPurchasable(course)) throw new NotFoundError('Curso não encontrado');

        let user = await this.userRepository.findByEmail(email);
        if (!user) {
            if (!password) throw new ValidationError('pwd é obrigatório para novo usuário');

            const userId = await this.userRepository.create(createUser({
                name,
                email,
                pass: hashPassword(password),
            }));
            user = { id: userId };
        }

        const status = this.paymentGateway.charge({ card });
        this.logger.info({
            event: 'payment.processed',
            userId: user.id,
            courseId: course.id,
            cardLast4: String(card).slice(-4),
            status,
        }, 'Payment processed');

        if (status !== PAYMENT_STATUS.PAID) throw new PaymentDeniedError('Pagamento recusado');

        return this.unitOfWork.transaction(async (tx) => {
            const enrollmentId = await this.enrollmentRepository.create(
                createEnrollment({ userId: user.id, courseId: course.id }),
                tx
            );
            await this.paymentRepository.create(
                createPayment({ enrollmentId, amount: course.price, status }),
                tx
            );
            await this.auditLogRepository.create(`Checkout curso ${course.id} por ${user.id}`, tx);

            return { enrollmentId };
        });
    }
}

module.exports = { CheckoutService };
