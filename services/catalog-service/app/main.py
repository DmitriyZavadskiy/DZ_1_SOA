from fastapi import FastAPI

app = FastAPI(title="Catalog Service", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "catalog-service"}
