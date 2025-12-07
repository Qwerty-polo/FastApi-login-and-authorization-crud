from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import models, schemas
from models import CategoryModel, DishModel
from schemas import CategoryResponse, CategoryCreate, DishCreate, DishUpdate
from Routers.login import security

import shutil # Допомагає зберігати файли
import uuid   # Допомагає генерувати унікальні імена (щоб файл "logo.png" не перезаписав інший "logo.png")
from fastapi import UploadFile, File # Спеціальні типи для файлів
router = APIRouter()


@router.post('/categories', response_model=CategoryResponse,dependencies=[Depends(security.access_token_required)])
async def create_categories(category: CategoryCreate,db: AsyncSession = Depends(get_db)):
    db_category = CategoryModel(name=category.name)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.post('/categories/{category_id}/dishes/', dependencies=[Depends(security.access_token_required)])
async def create_dish(category_id: int,dish_data: DishCreate, db: AsyncSession = Depends(get_db)):
    db_dish = DishModel(
                        category_id=category_id,
                        name=dish_data.name,
                        price = dish_data.price,
                        description=dish_data.description
                        )

    db.add(db_dish)
    await db.commit()
    await db.refresh(db_dish)
    return db_dish

@router.get('/categories/{category_id}', response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):

    query = (select(CategoryModel).options(selectinload(CategoryModel.dishes))
             .where(CategoryModel.id == category_id))

    result = await db.execute(query)
    list_of_dishes = result.scalar_one_or_none()

    if list_of_dishes is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return list_of_dishes

@router.delete('/dishes/{dish_id}',dependencies=[Depends(security.access_token_required)])
async def delete_dishes(dish_id: int, db: AsyncSession = Depends(get_db)):
    query = (select(DishModel).where (DishModel.id == dish_id))
    result = await db.execute(query)
    dish_delete = result.scalar_one_or_none()
    if dish_delete is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    await db.delete(dish_delete)
    await db.commit()
    return {"status": "success"}


@router.post("/dishes/{dish_id}/image", response_model=schemas.DishResponse, dependencies=[Depends(security.access_token_required)])
async def upload_dish_image(
        dish_id: int,
        file: UploadFile = File(...),  # Ми очікуємо файл
        db: AsyncSession = Depends(get_db),
        # Можна додати security, щоб тільки адмін міг вантажити фотки:
        # user_data = Depends(security.access_token_required)
):
    # 1. Шукаємо страву
    query = select(DishModel).where(DishModel.id == dish_id)
    result = await db.execute(query)
    dish = result.scalar_one_or_none()

    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    # 2. Генеруємо унікальне ім'я файлу
    # file.filename.split(".")[-1] - це ми дістаємо розширення (наприклад, "jpg" або "png")
    # uuid.uuid4() - генерує випадковий набір букв і цифр
    extension = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{extension}"

    # 3. Шлях, куди зберегти
    file_path = f"static/images/{new_filename}"

    # Ми відкриваємо файл у режимі "wb" (write binary) і копіюємо туди байти з завантаженого файлу
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ми записуємо не весь файл, а тільки посилання на нього
    dish.image_url = file_path

    await db.commit()
    await db.refresh(dish)

    return dish

@router.delete("/delete/{category}")
async def delete_category(category: int, db: AsyncSession = Depends(get_db)):
    query = (select(CategoryModel).where (CategoryModel.id == category))
    result = await db.execute(query)
    category_delete = result.scalar_one_or_none()
    if category_delete is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category_delete)
    await db.commit()
    return {"status": "success"}
@router.patch('/dishes/{dish_id}', response_model=schemas.DishUpdate,dependencies=[Depends(security.access_token_required)])
async def Dish_update(dish_id: int,dish_update: DishUpdate, db: AsyncSession = Depends(get_db)):
    query = (select(DishModel).where(DishModel.id == dish_id))
    result = await db.execute(query)
    dish_patch = result.scalar_one_or_none()
    if dish_patch is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    if dish_update.name is not None:
        dish_patch.name = dish_update.name
    if dish_update.description is not None:
        dish_patch.description = dish_update.description
    if dish_update.price is not None:
        dish_patch.price = dish_update.price
    if dish_update.is_active is not None:
        dish_patch.is_active = dish_update.is_active


        # or if you want you can do it like this
# ## 2. Проходимо циклом і оновлюємо поля
# for key, value in update_data.items():
#     # setattr(об'єкт, "назва_поля", значення) - це вбудована функція Python
#     setattr(dish_patch, key, value)

    await db.commit()
    await db.refresh(dish_patch)
    return dish_patch

@router.get("/dishes", response_model=List[schemas.DishResponse])
async def get_dishes(min_price: float  | None = None,
               max_price: float | None=None,
               is_active:bool | None=None,
               db: AsyncSession = Depends(get_db)):

    query = select(DishModel)
    if min_price is not None:
        query = query.where(DishModel.price >= min_price)

    if max_price is not None:
        query = query.where(DishModel.price <= max_price)

    if is_active is not None:
        query = query.where(DishModel.is_active == is_active)

    result = await db.execute(query)
    data = result.scalars().all()
    return data

