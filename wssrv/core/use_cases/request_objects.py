from wssrv.core.shared import request_object as req


class AddMessageRequestObject(req.ValidRequestObject):
    TYPE = 'AddMessage'

    def __init__(self, data_):
        super(AddMessageRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data: dict = None):
        invalid_req = req.InvalidRequestObject()

        if invalid_req.has_errors():
            return invalid_req

        return AddMessageRequestObject(data)
