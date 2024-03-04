import uvicorn
import os
from fastapi import FastAPI, Request
from proxy import ProxyHandler

app = FastAPI()

if __name__ == "__main__":
    proxy = ProxyHandler()
    port = int(os.environ["PORT"])

@app.post("/chat/completions")
async def proxy_post(request: Request):
    return await proxy.do_POST(request)

uvicorn.run(app, host='0.0.0.0', port=port, log_level="info")