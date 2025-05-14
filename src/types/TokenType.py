from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFICATION = "verification"
    ACTIVATION = "activation"
    DEACTIVATION = "deactivation"
    LOST_PASSWORD = "lost_password"
