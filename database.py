from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_async_engine('sqlite+aiosqlite:///./data/menu.db', connect_args={'check_same_thread': False})

Sessionlocal = async_sessionmaker(
                                bind=engine, #Коли створюєш працівників, давай їм доступ саме до ЦЬОГО двигуна (нашої бази)
                                autoflush=False,#True (за замовчуванням): Як тільки ти щось змінив у коді (наприклад user.name = "Ivan"), SQLAlchemy одразу біжить і синхронізує це з базою (навіть без commit)(в нас False записуй тоді коли я скажу)
                                expire_on_commit=False,#Якщо тут True, то після команди commit() сесія "забуває" всі дані об'єкта, вважаючи їх застарілими. Якщо ти спробуєш прочитати order.id після коміту, база спробує оновити дані, але в асинхронному коді це викличе помилку
                                class_=AsyncSession #Кажемо заводу: "Випускай саме асинхронних працівників".
                                ) # -Factory

Base = declarative_base() #Base має "магічний список" (metadata). Всі, хто успадковується від Base, автоматично потрапляють у цей список.

async def get_db():
    async with Sessionlocal() as db:
        yield db
