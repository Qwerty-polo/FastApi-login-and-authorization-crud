from urllib import response

from fastapi import Depends, HTTPException
from authx import AuthX, config, AuthXConfig
from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.responses import Response
from typing import Annotated
from Routers.auth import verify_password, get_password_hash
from database import get_db

from fastapi.security import HTTPBearer
from models import UserModel
from schemas import UserLogin, UserResponse

router = APIRouter()


security_headers = HTTPBearer(auto_error=False) #Це означає: "Якщо токена в заголовку немає — не кричи 'Помилка!', а промовчи"
#Бо токен може бути в куках. Якби тут було True, система б ламалася при вході через куки, вимагаючи заголовок

config = AuthXConfig() #Що це: Створення порожнього списку налаштувань
config.JWT_SECRET_KEY = 'secret' #Цим словом сервер "підписує" кожен токен
config.JWT_ACCESS_COOKIE_NAME = "my_access_token" #Назва "кишені" в браузері
config.JWT_TOKEN_LOCATION = ["cookies", "headers"] #Інструкція охоронцю, де шукати перепустку


################
config.JWT_COOKIE_CSRF_PROTECT = False #За замовчуванням система вимагає два документи: перепустку (токен) + довідку (CSRF).
# Оскільки у Swagger складно передавати цю "довідку", ми сказали: "Поки що пропускай тільки по перепустці, не ускладнюй
################
security = AuthX(config) #ініціалізація (запуск) системи безпеки з твоїми налаштуваннями.


SessionDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[dict, Depends(security.access_token_required)]



@router.post('/token')
async def login_for_access_token(
        creds: UserLogin,
        db: SessionDep):
    query = select(UserModel).where(UserModel.username == creds.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not await verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = security.create_access_token(uid=str(user.id))

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post('/register', response_model=UserResponse)
async def register(user: UserLogin, db: SessionDep):
    query = (select(UserModel).where(UserModel.username == user.username))
    result = await db.execute(query)
    user_one = result.scalar_one_or_none()

    if user_one is not None:
        raise HTTPException(status_code=409,detail="user already exist")

    hash_pass = await get_password_hash(user.password)

    new_user = UserModel(
        username=user.username,
        hashed_password=hash_pass
    )
    print(f"Що ми хешуємо: '{user.password}'")
    print(f"Довжина: {len(user.password)}")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(creds: UserLogin,response: Response,db: SessionDep):
    query = select(UserModel).where(UserModel.username == creds.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user or not await verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access_token": token}
#dependencies=[Depends(security.access_token_required),Depends(security_headers)]
@router.get("/protected")
async def protected(db: SessionDep):
    return {"hello": "world"}

