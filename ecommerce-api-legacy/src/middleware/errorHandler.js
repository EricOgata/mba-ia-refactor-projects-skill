function createErrorHandler({ logger }) {
    return function errorHandler(err, req, res, next) {
        if (res.headersSent) return next(err);

        const statusCode = Number.isInteger(err.statusCode) ? err.statusCode : 500;

        if (statusCode >= 500) {
            logger.error({
                err: { name: err.name, message: err.message, stack: err.stack },
                method: req.method,
                path: req.path,
            }, 'Unhandled error');
        } else {
            logger.warn({
                code: err.code,
                message: err.message,
                method: req.method,
                path: req.path,
            }, 'Request failed');
        }

        const message = statusCode >= 500 ? 'Internal Server Error' : err.message;
        return res.status(statusCode).send(message);
    };
}

module.exports = { createErrorHandler };
