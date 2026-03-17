from fastapi import FastAPI
from dotenv import load_dotenv
from routers import crawler, naverworks
from services.scheduler import start_scheduler

load_dotenv()

app = FastAPI(title="BTW API", version="1.0.0")

app.include_router(crawler.router, prefix="/crawler", tags=["crawler"])
app.include_router(naverworks.router, prefix="/naverworks", tags=["naverworks"])


@app.on_event("startup")
async def startup_event():
    start_scheduler()


@app.get("/health")
def health():
    return {"status": "ok"}
