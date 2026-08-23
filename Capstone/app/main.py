from fastapi import FastAPI

app = FastAPI(
    title="FlyRank Usage Metering & Billing Engine",
    version="1.0.0",
)


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