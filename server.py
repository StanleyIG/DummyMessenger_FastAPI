from fastapi import FastAPI
from fastapi import Depends
from pydantic import BaseModel

# инициализация объекта приложения сервера FastAPI
app = FastAPI()

# создание схемы сериализации и валидации данных с помощью встроенной бтблиотеки 
# pydantic

class UserBodyRequest(BaseModel):
       name: str
       text: str

@app.post('/add-message')
async def add_message():
       pass