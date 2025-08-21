import os
from dataclasses import dataclass, field
from enum import StrEnum

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
    AUTHORIZATION_SECRET: str = field(
        default="3f698872043d4b21c1e7b5284c652b57cdd47eb8513bef6dedd5b4a4fe71a239"
    )
    PREFERREDCODEC: str = field(default="m4a")
    DOWNLOAD_PATH: str = field(default="/mnt/storage")
    DB_URL: str = field(
        default=f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    ASSEMBLY_AI_BASE_URL: str = field(default="https://api.assemblyai.com")
    ASSEMBLY_AI_KEY: str = field(default_factory=lambda: os.environ["ASSEMBLY_AI_KEY"])


settings = Settings()
