class MobileMoneyError(Exception):
    """Exception de base pour tous les backends."""

    def __init__(self, backend: str, message: str, code: str = ""):
        self.backend = backend
        self.message = message
        self.code = code
        super().__init__(f"[{backend}] {message}")


class InvalidSignatureError(MobileMoneyError):
    """Signature webhook invalide."""
    pass


class PaymentTimeoutError(MobileMoneyError):
    """Le provider n'a pas répondu dans les délais."""
    pass