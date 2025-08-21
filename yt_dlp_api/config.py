import os
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
    PREFERREDCODEC: str = field(default="m4a")
    DOWNLOAD_PATH: str = field(default="/tmp")
    DB_URL: str = field(
        default=f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )


settings = Settings()
