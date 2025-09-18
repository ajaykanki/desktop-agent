from fastapi import HTTPException as e


class HTTPException(e):
    def __init__(self, status_code: int, error: str, message: str):
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.error = error
        self.status_code = status_code
