from typing import TYPE_CHECKING

from litestar.exceptions import HTTPException

from yt_dlp_api.utils import get_http_status_message

if TYPE_CHECKING:
    from litestar import Litestar


def create_app() -> "Litestar":
    from litestar import Litestar, Request, Response, get
    from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
    from litestar.middleware import DefineMiddleware
    from litestar.openapi.config import OpenAPIConfig
    from litestar.openapi.plugins import SwaggerRenderPlugin
    from litestar.openapi.spec import Components, SecurityScheme
    from litestar.plugins.prometheus import PrometheusConfig, PrometheusController
    from litestar.plugins.structlog import StructlogPlugin
    from litestar_granian import GranianPlugin

    from yt_dlp_api.auth import AuthenticationMiddleware
    from yt_dlp_api.config import settings
    from yt_dlp_api.controllers.jobs import JobsController
    from yt_dlp_api.controllers.transcription import TranscriptionController
    from yt_dlp_api.controllers.yt_dlp import YtDlpController

    def app_exception_handler(request: Request, exc: HTTPException) -> Response[dict[str, str]]:  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
        return Response(
            content={
                "error": get_http_status_message(exc.status_code),
                "detail": exc.detail,
            },
            status_code=exc.status_code,
        )

    @get("/")
    async def index() -> dict[str, str]:
        return {"msg": "ok"}

    auth_middleware = DefineMiddleware(AuthenticationMiddleware, exclude="schema")
    app = Litestar(
        debug=settings.ENVIRONMENT.is_qa,
        openapi_config=OpenAPIConfig(
            title="yt-dlp-api",
            version="0.0.1",
            render_plugins=[SwaggerRenderPlugin()],
            components=Components(
                security_schemes={
                    "HeaderAuth": SecurityScheme(
                        type="apiKey", security_scheme_in="header", name="authorization"
                    )
                }
            ),
            security=[{"HeaderAuth": []}],
        ),
        exception_handlers={HTTPException: app_exception_handler},
        plugins=[
            GranianPlugin(),
            StructlogPlugin(),
            OpenTelemetryPlugin(OpenTelemetryConfig()),
        ],
        route_handlers=[
            index,
            PrometheusController,
            JobsController,
            YtDlpController,
            TranscriptionController,
        ],
        middleware=[
            auth_middleware,
            PrometheusConfig(app_name="yt_dlp_api", prefix="yt_dlp_api").middleware,
        ],
        on_startup=[],
    )

    return app
