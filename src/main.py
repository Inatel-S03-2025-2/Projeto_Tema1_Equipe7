from fastapi import FastAPI
from src.Controllers import authController, userController
from src.Database.database import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(authController.router)
app.include_router(userController.router)