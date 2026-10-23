const { asyncHandler } = require('../middleware/asyncHandler');
const { validateId } = require('../validators/idValidator');

function createUserController({ userService }) {
    return {
        remove: asyncHandler(async (req, res) => {
            const id = validateId(req.params.id);
            await userService.deleteUser(id);

            res.status(200).send('Usuário deletado com sucesso.');
        }),
    };
}

module.exports = { createUserController };
