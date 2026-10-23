class AppError extends Error {
    constructor(message, statusCode, code) {
        super(message);
        this.name = this.constructor.name;
        this.statusCode = statusCode;
        this.code = code;
        if (Error.captureStackTrace) Error.captureStackTrace(this, this.constructor);
    }
}

class ValidationError extends AppError {
    constructor(message = 'Bad Request') {
        super(message, 400, 'VALIDATION_ERROR');
    }
}

class NotFoundError extends AppError {
    constructor(message = 'Not found') {
        super(message, 404, 'NOT_FOUND');
    }
}

class PaymentDeniedError extends AppError {
    constructor(message = 'Pagamento recusado') {
        super(message, 400, 'PAYMENT_DENIED');
    }
}

module.exports = { AppError, ValidationError, NotFoundError, PaymentDeniedError };
