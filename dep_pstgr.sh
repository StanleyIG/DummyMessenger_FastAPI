#!/bin/bash

if grep -q "NAME=\"Ubuntu\"" /etc/os-release; then
    echo "Используется Ubuntu"
    # Создание файла .env с переменными окружения по умолчанию
    echo "USER=user" > .env
    echo "PASSWORD=123321" >> .env
    echo "DB=server" >> .env
    docker compose up -d
    python3 launcher_for_ubuntu.py
elif [ "$OS" == "Windows_NT" ]; then
    echo "Используется Windows"
    echo "Выполните способ №1"
    exit 1
fi