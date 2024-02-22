import asyncio
import uvicorn
from fastapi.requests import Request
from typing import Optional, Annotated
from fastapi import FastAPI, APIRouter
from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import desc
from sqlalchemy.future import select
import datetime
from uvicorn import Server, Config
from aioredis import client


message_route = APIRouter()

# создание схемы сериализации и валидации данных с помощью встроенной бтблиотеки
# pydantic


class UserBodyRequestToDB(BaseModel):
    name: str
    text: str


class UserBodyAll(UserBodyRequestToDB):
    id: int
    date: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# создание движка для асинхронного взаимодействия с базой, а так-же создание создание асинхронной сессии
async_db_engine = create_async_engine("sqlite+aiosqlite:///server.db")
async_session = async_sessionmaker(async_db_engine, expire_on_commit=False)


# async def get_async_session():
#     """функция, которая вернет объект генератора сессии"""
#     async with async_session() as session:
#         return session


# # создание модели сообщений
class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Messages(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String(1000), nullable=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)


async def create_db():
    """создание базы"""
    async with async_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Запросы к базе через класс MessageRepository(паттерн репозиторий)
class MessageRepository:
    @classmethod
    async def add_message_get_lst_ten(cls, user_post: UserBodyRequestToDB):
        async with async_session() as session:
            # !метод model_dump используется в последнем обновлении pydantic 2.6.1, в более ранних версиях может не работать!
            user_dict: dict = user_post.model_dump()
            new_message = Messages(**user_dict)
            # cls.new_message = new_message
            session.add(new_message)
            await session.commit()
            query = select(Messages).filter(
                Messages.name == new_message.name).order_by(Messages.id).limit(10)
            result = await session.execute(query)
            last_ten_messages = result.scalars().all()
            messages = [UserBodyAll.model_validate(
                message) for message in last_ten_messages]
            return {'messages': messages, 'count_messages': len(messages)}


# роут для добавления сообщения в базу данных
@message_route.post('/add-message')
async def add_message(user_post: Annotated[UserBodyRequestToDB, Depends()]):
    # new_message = Messages(name=user_post.name, text=user_post.text)
    last_ten_mess = await MessageRepository.add_message_get_lst_ten(user_post)
    return last_ten_mess


# @message_route.post('/add-message')
# async def add_message(user_post: Annotated[UserBodyRequestToDB, Depends()],
#                       db: AsyncSession = Depends(get_async_session)):
#     # Тут взаимодействие с базой данных:
#     user_dict: dict = user_post.model_dump()
#     new_message = Messages(**user_dict)
#     db.add(new_message)
#     await db.commit()
#     query = select(Messages).filter(Messages.name == new_message.name).order_by(desc(Messages.id)).limit(10)
#     result = await db.execute(query)
#     last_ten_messages = result.scalars().all()
#     return last_ten_messages


# функция выполняет процесс создания приложения и запуск зависимостей, в частности создание базы
app_ports = [5001, 5002, 5003]  # Порты, на которых будут запущены сервера


def create_app():
    """создание приложения, подключение роута(ов) и запуск зависимостей"""
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """При запуске сервера создаётся база, если базы ещё не существует"""
        try:
            await create_db()
        except:
            pass
        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(message_route)

    return app


app = create_app()


# сылка на источник https://gist.github.com/tenuki/ff67f87cba5c4c04fd08d9c800437477

class MyServer(Server):
    async def run(self, sockets=None):
        self.config.setup_event_loop()
        return await self.serve(sockets=sockets)


async def run():
    apps = []
    for cfg in app_ports:
        config = Config("server:app", host="127.0.0.1",
                        port=cfg)
        server = MyServer(config=config)
        apps.append(server.run())
    return await asyncio.gather(*apps)

# сылка на источник https://gist.github.com/tenuki/ff67f87cba5c4c04fd08d9c800437477

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
