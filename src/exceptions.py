class ServerException(Exception):
    pass

class WrapperException(Exception):
    pass

class LimitExceeded(ServerException):
    pass

class UnknownServerException(ServerException):
    pass