const { asyncHandler } = require('../middleware/asyncHandler');
const { validateCheckout } = require('../validators/checkoutValidator');

function createCheckoutController({ checkoutService }) {
    return {
        checkout: asyncHandler(async (req, res) => {
            const data = validateCheckout(req.body);
            const { enrollmentId } = await checkoutService.checkout(data);

            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        }),
    };
}

module.exports = { createCheckoutController };
