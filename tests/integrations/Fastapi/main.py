from fastapi import FastAPI

from loki_middleware import FastapiLokiMiddleware

app = FastAPI()
app.add_middleware(
    FastapiLokiMiddleware,
    exclude_paths=[]
)

@app.get("/test-endpoint")
def read_root():
    return {"status": "ok"}
