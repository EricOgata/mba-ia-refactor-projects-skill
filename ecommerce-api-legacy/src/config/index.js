require('dotenv').config({ quiet: true });

const isProduction = process.env.NODE_ENV === 'production';

function optionalSecret(name) {
    const value = process.env[name];
    if (value) return value;
    if (isProduction) throw new Error(`Missing required environment variable: ${name}`);
    return undefined;
}

function readPort() {
    if (process.env.PORT === undefined) return 3000;
    const port = Number(process.env.PORT);
    if (!Number.isInteger(port) || port < 0 || port > 65535) {
        throw new Error('PORT must be an integer between 0 and 65535');
    }
    return port;
}

module.exports = {
    port: readPort(),
    databasePath: process.env.DATABASE_PATH || ':memory:',
    adminToken: optionalSecret('ADMIN_TOKEN'),
    paymentGatewayKey: optionalSecret('PAYMENT_GATEWAY_KEY'),
};
