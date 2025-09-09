import contextlib
import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from fca_mcp.mcp_server.api import mcp_server


ENTERPRISE_KEY_ENV = "ENTERPRISE_LICENSE_KEY"


def create_app():
    """Create and configure FastAPI application with MCP server integration (community edition)."""

    if not os.getenv(ENTERPRISE_KEY_ENV):
        # Expose only healthcheck without MCP when no license key is set
        app = FastAPI()

        @app.get("/healthcheck")
        async def health_check():
            return JSONResponse(status_code=200, content={"status": "ok", "license": "community"})

        return app

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        async with contextlib.AsyncExitStack() as stack:
            await stack.enter_async_context(mcp_server.session_manager.run())
            yield

    app = FastAPI(lifespan=lifespan)

    @app.get("/healthcheck")
    async def health_check():
        return JSONResponse(status_code=200, content={"status": "ok", "license": "enterprise"})

    # In community mode, we still mount the MCP app but tools return 501
    app.mount("/mcp", mcp_server.streamable_http_app())

    return app


def main(reload=True):
    uvicorn.run(
        "fca_mcp.mcp_server.main:create_app",
        host="0.0.0.0",
        port=8080,
        reload=reload,
        factory=True,
        timeout_graceful_shutdown=0,
    )


if __name__ == "__main__":
    main()
