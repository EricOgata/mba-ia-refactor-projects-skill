const { Router } = require('express');

function createUserRoutes({ userController, requireAdmin }) {
    const router = Router();
    router.delete('/users/:id', requireAdmin, userController.remove);
    return router;
}

module.exports = { createUserRoutes };
