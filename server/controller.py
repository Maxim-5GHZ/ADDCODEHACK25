import uvicorn
import bdrequest
from fastapi import FastAPI
from fastapi.responses import FileResponse

class controller():
    def __init__(self):
        self.app = FastAPI()


    def _controllers(self):
        @self.app.get("/")
        def read_root():
            return FileResponse("html/index.html")

        @self.app.get("/favicon.ico")
        def ico():
            return FileResponse("ico/favicon.ico")


    def run(self):
        self._controllers()
        uvicorn.run(self.app, host="0.0.0.0", port=8000)