""" Custom exceptions for companies app """

class WebSocketException(Exception):
    """ Base class for WebSocket errors """


class ShortQueryException(WebSocketException):
    """ Raised when the search query is too short """

    def __init__(self, message="Query must be at least 3 characters long."):
        self.message = message
        super().__init__(self.message)


class InvalidPayloadException(WebSocketException):
    """ Raised when the incoming WebSocket payload is invalid """

    def __init__(self, message="Invalid input format."):
        self.message = message
        super().__init__(self.message)
