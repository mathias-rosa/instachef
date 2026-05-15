import asyncio
import json
from math import ceil

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from connectors import CookachuConnector
from core.ports import RecipeRepository
from core.process_reel import ProcessReelService
from domain.recipe_record import RecipeRecord


class RecipePage(BaseModel):
    items: list[RecipeRecord]
    page: int
    page_size: int
    total: int
    total_pages: int


class ApiConnector(CookachuConnector):
    def __init__(
        self,
        service: ProcessReelService,
        repository: RecipeRepository,
        frontend_url: str,
        host: str,
        port: int,
    ) -> None:
        self.service = service
        self.repository = repository
        self.frontend_url = frontend_url
        self.host = host
        self.port = port
        self.app = self._build_app()

    def _build_app(self) -> FastAPI:
        app = FastAPI(title="Cookachu API", version="0.1.0")

        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                self.frontend_url,
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        router = APIRouter(prefix="/api/v1")

        @router.get("/health")
        async def health() -> dict[str, str]:
            return {"status": "ok"}

        @router.get("/recipes", response_model=RecipePage)
        async def list_recipes(
            page: int = Query(1, ge=1, description="Page number, starting at 1."),
            page_size: int = Query(
                10,
                ge=1,
                le=50,
                description="Number of recipes per page.",
            ),
        ) -> RecipePage:
            return await asyncio.to_thread(
                self._paginate_recipes,
                page,
                page_size,
            )

        @router.get("/recipes/{recipe_id}", response_model=RecipeRecord)
        async def get_recipe(recipe_id: str) -> RecipeRecord:
            record = await asyncio.to_thread(
                self.repository.find_by_id,
                recipe_id,
            )
            if not record:
                raise HTTPException(status_code=404, detail="Recipe not found")
            return record

        app.include_router(router)
        # save open API spec to file
        openapi = get_openapi(title=app.title, version=app.version, routes=app.routes)
        with open("openapi.json", "w") as f:
            f.write(json.dumps(openapi, indent=2))
        return app

    def _paginate_recipes(self, page: int, page_size: int) -> RecipePage:
        ids = self.repository.list_ids()
        total = len(ids)
        start_index = (page - 1) * page_size
        page_ids = ids[start_index : start_index + page_size]
        items: list[RecipeRecord] = []
        for record_id in page_ids:
            record = self.repository.find_by_id(record_id)
            if record:
                items.append(record)

        total_pages = ceil(total / page_size) if total else 0

        return RecipePage(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )

    async def run(self) -> None:
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()
