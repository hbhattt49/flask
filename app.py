from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()
JUPYTER_INTERNAL_URL = "http://jupyterlab.default.svc.cluster.local:8888"

@app.api_route("/jupyterlab/{full_path:path}", methods=["GET", "POST"])
async def proxy_to_jupyter(full_path: str, request: Request):
    async with httpx.AsyncClient() as client:
        proxied_url = f"{JUPYTER_INTERNAL_URL}/{full_path}"
        response = await client.request(
            method=request.method,
            url=proxied_url,
            headers=request.headers.raw,
            content=await request.body()
        )
        return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))
