from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

# data formatting for request
class NavData(BaseModel):
    id: str
    text: str | None = None

app = FastAPI()

# api server class with callback function
class PosiApiServer():

    def __init__(self):
        self.kivyCallback = None

    def set_kivy_caller(self, callback=None):
        if callback:
            self.kivyCallback = callback

    def start_fastapi(self):
        app.state.server = self   # 👈 attach instance
        uvicorn.run(app, host="0.0.0.0", port=8089, reload=False)

# handle post requests
@app.post("/nav/")
async def process_nav_notification(item: NavData, request: Request):
    server: PosiApiServer = request.app.state.server

    print(f"{item.id}: {item.text}")

    if server.kivyCallback:
        server.kivyCallback(item.id, item.text)

    return item

# test locally
if __name__ == "__main__":
    def kivy_func(id, text):
        print("CALLBACK FROM API:", id, text)

    apiServ = PosiApiServer()
    apiServ.set_kivy_caller(kivy_func)
    apiServ.start_fastapi()
