import os

import fastapi
import fastapi.middleware.cors

from . import auth
from .routers import feeds, items

app = fastapi.FastAPI()

app.include_router(auth.router)
app.include_router(feeds.router)
app.include_router(items.router)

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello world."}
