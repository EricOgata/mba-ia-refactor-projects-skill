const express = require('express');
const config = require('./config');
const { buildContainer } = require('./container');
const { createDatabase } = require('./database/connection');
const { initializeSchema } = require('./database/schema');
const { createRequireAdmin } = require('./middleware/auth');
const { createErrorHandler } = require('./middleware/errorHandler');
const { notFound } = require('./middleware/notFound');
const { createRoutes } = require('./routes');
const logger = require('./utils/logger');

async function bootstrap() {
    const db = createDatabase(config.databasePath);
    await initializeSchema(db);

    const app = express();
    app.use(express.json());

    const container = buildContainer({ db, config, logger });
    const requireAdmin = createRequireAdmin({ adminToken: config.adminToken });

    app.use('/api', createRoutes({ ...container, requireAdmin }));
    app.use(notFound);
    app.use(createErrorHandler({ logger }));

    const server = app.listen(config.port, () => {
        logger.info({ port: config.port }, `Frankenstein LMS rodando na porta ${config.port}...`);
    });

    const shutdown = (signal) => {
        logger.info({ signal }, 'Encerrando aplicação');
        server.close(async () => {
            try {
                await db.close();
                process.exit(0);
            } catch (err) {
                logger.error({ err }, 'Erro ao fechar banco de dados');
                process.exit(1);
            }
        });
    };

    process.once('SIGINT', () => shutdown('SIGINT'));
    process.once('SIGTERM', () => shutdown('SIGTERM'));

    return { app, server, db };
}

if (require.main === module) {
    bootstrap().catch((err) => {
        logger.error({
            err: { name: err.name, message: err.message, stack: err.stack },
        }, 'Falha ao iniciar aplicação');
        process.exit(1);
    });
}

module.exports = { bootstrap };
