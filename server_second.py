import uvicorn
from fastapi.requests import Request
from typing import Optional, Annotated
from fastapi import FastAPI, APIRouter
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import desc
from sqlalchemy.future import select
import datetime


message_route = APIRouter()

# создание движка для асинхронного взаимодействия с базой, а так-же создание создание асинхронной сессии
async_db_engine = create_async_engine("sqlite+aiosqlite:///server.db")
async_session = async_sessionmaker(async_db_engine, expire_on_commit=False)


async def get_async_session():
    """функция, которая вернет async_session"""
    async with async_session() as session:
        yield session


class Model(DeclarativeBase):
    pass

class Messages(Model):
    __tablename__ = "server"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)



async def create_db():
    """создание базы"""
    async with async_db_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

# создание схемы сериализации и валидации данных с помощью встроенной бтблиотеки
# pydantic


class UserBodyRequestToDB(BaseModel):
    name: str
    text: str


class UserBodyID(UserBodyRequestToDB):
    idx: int


# роут для добавления сообщения в базу данных

@message_route.post('/add-message')
async def add_message(user_post: Annotated[UserBodyRequestToDB, Depends()],
                      db: AsyncSession = Depends(get_async_session)):
    # Используется новый pydantic 2.6.1, на более старых возможно нет этого метода !
    user_dict: dict = user_post.model_dump() 
    new_message = Messages(**user_dict)
    # либо new_message = Messages(user_post.name, user_post.text)
    db.add(new_message)
    await db.commit()
    async with db as session:
        query = select(Messages).order_by(desc(Messages.id)).limit(11)
        result = await session.execute(query)
        last_ten_messages = result.scalars().all()
    return last_ten_messages[1: len(last_ten_messages) + 1]

# или так
# @message_route.post('/add-message')
# async def add_message(user_post: Annotated[UserBodyRequestToDB, Depends()],
#                       db: AsyncSession = Depends(get_async_session)):
#     new_message = Messages(name=user_post.name, text=user_post.text)
#     db.add(new_message)
#     await db.commit()

#     async with db as session:
#         # Получаем ID только что добавленного сообщения
#         new_message_id = new_message.id

#         # Выполняем запрос для получения последних 10 сообщений исключая только что добавленное
#         query = select(Messages).filter(Messages.id != new_message_id).order_by(desc(Messages.id)).limit(10)
#         result = await session.execute(query)
#         last_ten_messages = result.scalars().all()

#         # Выводит тип последних 10 сообщений, чтобы убедиться, что все в порядке

#     return last_ten_messages


# функция выполняет процесс создания приложения и запуск зависимостей, в частности создание базы
def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """При запуске сервера создаётся база, если база уже создана, то соответсвенно этот код 
        выполняться повторно уже не будет, согласно документации FastAPI"""
        await create_db()
        yield
    app = FastAPI(lifespan=lifespan)
    app.include_router(message_route)

    return app


# Запуск сервера FastAPI
app = create_app()
if __name__ == '__main__':
    uvicorn.run('server_second:app', host='127.0.0.1', port=5000, reload=True)
