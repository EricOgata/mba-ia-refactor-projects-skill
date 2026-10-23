const { NotFoundError } = require('../errors');

class UserService {
    constructor({ userRepository, enrollmentRepository, paymentRepository, unitOfWork }) {
        this.userRepository = userRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.paymentRepository = paymentRepository;
        this.unitOfWork = unitOfWork;
    }

    async deleteUser(id) {
        return this.unitOfWork.transaction(async (tx) => {
            const user = await this.userRepository.findById(id, tx);
            if (!user) throw new NotFoundError('Usuário não encontrado');

            await this.paymentRepository.deleteByUserId(id, tx);
            await this.enrollmentRepository.deleteByUserId(id, tx);
            await this.userRepository.deleteById(id, tx);
        });
    }
}

module.exports = { UserService };
