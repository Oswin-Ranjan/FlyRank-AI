from fastapi import FastAPI

from app.api.routes.usage import router as usage_router


app = FastAPI(
    title="FlyRank Usage Metering & Billing Engine",
    version="1.0.0",
)


app.include_router(usage_router)


@app.get("/")
def root():
    return {
        "message": "Usage Metering & Billing Engine is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }