const { Router } = require('express');

function createCheckoutRoutes({ checkoutController }) {
    const router = Router();
    router.post('/checkout', checkoutController.checkout);
    return router;
}

module.exports = { createCheckoutRoutes };
