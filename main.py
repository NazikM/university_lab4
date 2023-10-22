import uvicorn
from fastapi import FastAPI

from app.database import Base, engine
from app.middlewares import FailedRequestLimitMiddleware
from app.routers import auth, main

app = FastAPI()

app.add_middleware(FailedRequestLimitMiddleware)

# Including routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(main.router, tags=["Main Page"])

# Create all tables defined in your models
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)
