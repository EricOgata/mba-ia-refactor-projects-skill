const { PAYMENT_STATUS } = require('../models/Payment');

class PaymentGateway {
    constructor({ apiKey } = {}) {
        // Reservada para a integração real; a simulação nunca a expõe em log.
        this.apiKey = apiKey;
    }

    charge({ card }) {
        // Simulação do gateway legado: cartões iniciados em 4 são aprovados.
        return String(card).startsWith('4') ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    }
}

module.exports = { PaymentGateway };
