import subprocess
import sys
import os
import time


def run():
    python_path = sys.executable
    process = []
    while True:
        action = input(
            'Выбрать действие: q - выход, s - запуск программы, x - закрыть все окна: ')
        if action == 'q':
            break
        
        # Запуск сервера
        if action == 's':
            process.append(subprocess.Popen(["gnome-terminal", "--", python_path, "server.py"]))
            time.sleep(3)
            client_args = [python_path, 'client.py']
            process.append(subprocess.Popen(["gnome-terminal", "--", *client_args]))
        
        elif action == 'x':
            for p in process:
                p.kill()

if __name__ == '__main__':
    run()
