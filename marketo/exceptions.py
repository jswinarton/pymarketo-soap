class DoesNotExist(Exception):
    pass


class AuthenticationError(Exception):
    pass


class RequestExpired(Exception):
    pass


class MarketoFault(object):
    ERROR_MAP = {
        '20103': DoesNotExist,
        '20014': AuthenticationError,
        '20016': RequestExpired,
    }

    def __init__(self, fault):
        self.fault = fault

    @property
    def error_code(self):
        return self.fault.fault.detail.serviceException.code

    def raise_error(self, message):
        if self.error_code in self.ERROR_MAP:
            raise self.ERROR_MAP[self.error_code](message)
