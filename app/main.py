# app/main.py

from fastapi import FastAPI
from app.routes import router
# Initialize FastAPI app
app = FastAPI()

# Include the routes from routes.py
app.include_router(router)

@app.get("/")
def root():
    return {"message": "YouTube Info Service is running"}
