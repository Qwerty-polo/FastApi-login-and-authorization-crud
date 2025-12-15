import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware

from Routers import menu, login, orders, simple_ws

from contextlib import asynccontextmanager
from database import engine, Base
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"], #список сайтів, яким можна до нас стукати.
    allow_credentials=True, #True. Це важливо, бо ми використовуємо Куки (Cookies) для входу. Без цього фронтенд не зможе передати токен
    allow_methods=["*"], #Список дозволених методів (GET, POST...)
    allow_headers=["*"], #Список дозволених заголовків
)

###########
app.mount('/static', StaticFiles(directory='static'), name='static')
#ось цю папку static зроби публічною, нехай люди дивляться картинки
###########


app.include_router(menu.router, tags=['Menu'])
app.include_router(login.router, tags=['login'])
app.include_router(orders.router,tags=['Orders'])
app.include_router(simple_ws.router,tags=['WebSocket'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("server is running")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        print("server is stopped")

app = FastAPI(lifespan=lifespan)

if __name__ == '__main__':
    uvicorn.run("main:app",reload=False)
