from fastapi import FastAPI
from src.Controllers import authController, userController

app = FastAPI()

app.include_router(authController.router)
app.include_router(userController.router)