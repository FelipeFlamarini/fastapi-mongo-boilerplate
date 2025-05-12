from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFICATION = "verification"
    ACTIVATION = "activation"
    DEACTIVATION = "deactivation"
    PASSWORD_RESET = "password_reset"
