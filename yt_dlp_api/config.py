from dataclasses import dataclass, field, fields
from enum import StrEnum
from typing import Self

import structlog

log: structlog.stdlib.BoundLogger = structlog.get_logger()


class Environment(StrEnum):
    TEST = "TEST"
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_testing(self) -> bool:
        return self == Environment.TEST

    @property
    def is_development(self) -> bool:
        return self == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        return self == Environment.STAGING

    @property
    def is_qa(self) -> bool:
        return self in {
            Environment.TEST,
            Environment.DEVELOPMENT,
            Environment.STAGING,
        }

    @property
    def is_production(self) -> bool:
        return self == Environment.PRODUCTION


@dataclass
class Settings:
    ENVIRONMENT: Environment = field(default=Environment.DEVELOPMENT)
