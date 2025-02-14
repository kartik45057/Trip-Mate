from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer
from app.database.db_main import create_db_and_tables, close_db_connections
from app.routes import expense_route, trip_route, user_route, root_route
from fastapi import FastAPI
from app.models import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic here
    create_db_and_tables()

    yield  # This is where the app runs

    # Shutdown logic here
    close_db_connections()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(lifespan=lifespan)

app.include_router(root_route.router)
app.include_router(user_route.router)
app.include_router(trip_route.router)
app.include_router(expense_route.router)


    


    
