import uvicorn
from blaxel import env

port = env["PORT"] or 80
host = env["HOST"] or "0.0.0.0"

if __name__ == "__main__":
    uvicorn.run("src.main:app", host=host, port=int(port), reload=False)
