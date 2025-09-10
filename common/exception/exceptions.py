class ChatNotFoundError(Exception):
    def __init__(self, message: str = "Chat not found") -> None:
        self.message = message
        self.status_code = 404
        super().__init__(self.message)


class UnauthorizedAccessError(Exception):
    def __init__(self, message: str = "Unauthorized access") -> None:
        self.message = message
        self.status_code = 401
        super().__init__(self.message)


class ForbiddenAccessError(Exception):
    def __init__(self, message: str = "Forbidden access") -> None:
        self.message = message
        self.status_code = 403
        super().__init__(self.message)
