from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from kivy.clock import Clock
from threading import Thread
import asyncio
from functools import partial

# data formatting for request
class NavData(BaseModel):
    title: str
    text: str | None = None
    sub_text: str | None = None
    text_lines: str | None = None
    ticker_text: str | None = None
    big_text: str | None = None

class ControlData(BaseModel):
    api: str

# FastAPI app
app = FastAPI()

# api server class with callback function
class PosiApiServer:

    def __init__(self, host="0.0.0.0", port=8089):
        self.host = host
        self.port = port
        self.kivyCallback = None
        self.server: uvicorn.Server | None = None
        self.thread: Thread | None = None

    # ----------------------------
    # Control callback
    # ----------------------------
    def set_control_caller(self, callback=None):
        self.controlCallback = callback

    # ----------------------------
    # Kivy callback
    # ----------------------------
    def set_kivy_caller(self, callback=None):
        self.kivyCallback = callback

    # ----------------------------
    # Internal server runner
    # ----------------------------
    def _run(self):
        config = uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level="info",
            loop="asyncio"
        )
        self.server = uvicorn.Server(config)
        app.state.server = self  # attach instance
        asyncio.run(self.server.serve())

    # ----------------------------
    # Public start
    # ----------------------------
    def start(self):
        if self.thread and self.thread.is_alive():
            print("Server already running")
            return
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()
        print("FastAPI started")

    # ----------------------------
    # Public stop
    # ----------------------------
    def stop(self):
        if self.server:
            print("Stopping FastAPI...")
            self.server.should_exit = True
        if self.thread:
            self.thread.join(timeout=5)
        self.server = None
        self.thread = None
        print("FastAPI stopped")

# handle post requests
@app.post("/nav/")
async def process_nav_notification(item: NavData, request: Request):
    server: PosiApiServer = request.app.state.server

    if server.kivyCallback:
        Thread(
            target=server.kivyCallback,
            kwargs={
                "item": item
            },
            daemon=True
        ).start()

    return item

@app.post("/control/")
async def internal_control(item: ControlData, request: Request):
    server: PosiApiServer = request.app.state.server

    if server.controlCallback:
        Clock.schedule_once(partial(server.controlCallback, item))

    return item

# test locally
if __name__ == "__main__":
    #def kivy_func(item):
    #    full_text = ""
    #    for i in item:
    #        txt = item[i]
    #        full_text = full_text + f"{txt}, "
    #    print(full_text)

    apiServ = PosiApiServer()
    #apiServ.set_kivy_caller(kivy_func)
    apiServ.start()
