from wssrv.core.shared.response_object import ResponseSuccess
from wssrv.core.shared.use_case import UseCase


class AddMessageUseCase(UseCase):
    async def process(self, request_object):
        return ResponseSuccess(await self.repo.add(request_object))
