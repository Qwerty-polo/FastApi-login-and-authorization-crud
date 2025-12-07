from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_async_engine('sqlite+aiosqlite:///./menu.db', connect_args={'check_same_thread': False})

Sessionlocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False,class_=AsyncSession )

Base = declarative_base()

async def get_db():
    async with Sessionlocal() as db:
        yield db
