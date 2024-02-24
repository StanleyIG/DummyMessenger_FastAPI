import subprocess
import sys
import time


def run():
    python_path = sys.executable  # patho_to\myenv\Scripts\python.exe
    activate = python_path.replace('python.exe', 'activate')
    process = []
    while True:
        action = input(
            'Выберать действие: q - выход , s - запустить сервер, k - запустить клиент x - закрыть все окна: ')
        if action == 'q':
            break

        # Запуск сервера
        elif action == 's':
            process.append(subprocess.Popen(
                [python_path, 'server.py'], creationflags=subprocess.CREATE_NEW_CONSOLE))

            time.sleep(3)  # необходимо подождать пока полностью не запустится
            # серверная часть, а потом уже запустить клиентскую часть, чтобы не выходили внезапные ошибки
            process.append(subprocess.Popen(
                  [python_path, 'client.py'], creationflags=subprocess.CREATE_NEW_CONSOLE))
            
        elif action == 'x':
            while process:
                process.pop().kill()


if __name__ == '__main__':
    run()
