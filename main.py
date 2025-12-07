import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware

from Routers import menu, login
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #список сайтів, яким можна до нас стукати.
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

if __name__ == '__main__':
    uvicorn.run("main:app",reload=False)
