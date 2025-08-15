import subprocess
import os
import hashlib
import socket
import sys
import time
import zipfile
import requests
import re
import shutil
from tqdm import tqdm

# Конфигурация
CLIENT_DIR = r"C:\Quantuum\client\*"
EXPECTED_CODE = "2556503"
JAVA_PATH = r"C:\Quantuum\java\bin\java"
QUANTUUM_DIR = r"C:\Quantuum"
REQUIRED_FOLDERS = ['assets', 'client', 'java']

# Параметры
delay = 0.01
time_multipliers = {'s':1, 'm':60, 'h':3600, 'd':86400, 'w':604800, 'mo':2592000, 'y':31536000}
CLIENT_VERSION = "1.4"

def check_folders():
    """Проверяет наличие обязательных папок"""
    for folder in REQUIRED_FOLDERS:
        path = os.path.join(QUANTUUM_DIR, folder)
        if not os.path.exists(path) or not os.path.isdir(path):
            return False
    return True

def delete_folders():
    """Удаляет обязательные папки если они существуют"""
    for folder in REQUIRED_FOLDERS:
        path = os.path.join(QUANTUUM_DIR, folder)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
            animated_print(f"Удалена папка: {folder}")

def get_hwid():
    try:
        cmd = 'powershell "Get-WmiObject -Class Win32_BIOS | Select-Object -ExpandProperty SerialNumber"'
        sn = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
        return hashlib.sha256(sn.encode()).hexdigest()
    except Exception:
        return None

def download_and_extract_zip(url, extract_to):
    try:
        os.makedirs(extract_to, exist_ok=True)
        zip_path = os.path.join(extract_to, "client_temp.zip")
        
        # Скачивание с прогресс-баром
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as f, tqdm(
            desc="Скачивание клиента",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))
        
        # Распаковка архива
        animated_print("\nРаспаковка архива...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_to)
        
        # Удаление архива
        os.remove(zip_path)
        animated_print("Архив успешно удален")
        return True
    except Exception as e:
        animated_print(f"Ошибка загрузки: {e}")
        return False

def run_jar(ram):
    try:
        env = os.environ.copy()
        env['CLIENT_LAUNCHED'] = EXPECTED_CODE
        os.chdir(QUANTUUM_DIR)

        command = [
            JAVA_PATH,
            f"-Xmx{ram}G",
            "-noverify",
            "-cp",
            CLIENT_DIR,
            "Start"
        ]
        command.extend(sys.argv[1:])

        creationflags = subprocess.CREATE_NO_WINDOW
        process = subprocess.Popen(
            command,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags
        )
        return process.pid
    except Exception as e:
        animated_print(f"Ошибка при запуске клиента: {e}")
        return None

def animated_print(text, end='\n', flush=True):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    if flush:
        sys.stdout.flush()

def get_input(prompt, digits_only=False):
    animated_print(prompt, end='', flush=False)
    value = input().strip()
    if digits_only and not value.isdigit():
        return ""
    return value

def parse_duration(ds):
    if ds.lower() == "lifetime":
        return None
    secs = 0
    matches = re.findall(r'(\d+)(y|mo|w|d|h|m|s)', ds.lower())
    for val, unit in matches:
        secs += int(val) * time_multipliers[unit]
    return secs

def format_russian_time(seconds):
    if seconds is None:
        return "∞"
    intervals = (
        ('дн.', 86400),
        ('ч.', 3600),
        ('мин.', 60),
    )
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{value} {name}")
    return ' '.join(result) or "<1 мин."

def main():
    banner = [
        "░██████╗░██╗░░░██╗░█████╗░███╗░░██╗████████╗██╗░░░██╗██╗░░░██╗███╗░░░███╗",
        "██╔═══██╗██║░░░██║██╔══██╗████╗░██║╚══██╔══╝██║░░░██║██║░░░██║████╗░████║",
        "██║██╗██║██║░░░██║███████║██╔██╗██║░░░██║░░░██║░░░██║██║░░░██║██╔████╔██║",
        "╚██████╔╝██║░░░██║██╔══██║██║╚████║░░░██║░░░██║░░░██║██║░░░██║██║╚██╔╝██║",
        "░╚═██╔═╝░╚██████╔╝██║░░██║██║░╚███║░░░██║░░░╚██████╔╝╚██████╔╝██║░╚═╝░██║",
        "░░░╚═╝░░░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚══╝░░░╚═╝░░░░╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝"
    ]
    
    for line in banner:
        print(line)
        time.sleep(delay/2)

    username = get_input("Логин: ")
    password = get_input("Пароль: ")

    animated_print("\nПроверка лицензии...")
    hwid = get_hwid()
    if not hwid:
        animated_print("Ошибка: Не удалось получить HWID")
        time.sleep(3)
        return

    try:
        with socket.socket() as sock:
            sock.settimeout(10)
            sock.connect(("e1.aurorix.net", 20717))
            data = f"{username}:{password}:{hwid}:{CLIENT_VERSION}"
            sock.sendall(data.encode())
            response = sock.recv(8192).decode().strip()
    except Exception as e:
        animated_print(f"Ошибка сети: {e}")
        time.sleep(3)
        return

    if response == "Invalid username or password":
        animated_print("Неверный логин или пароль")
        time.sleep(3)
        return
    elif response == "Subscription expired":
        animated_print("Подписка истекла")
        time.sleep(3)
        return
    elif response.startswith("Update required"):
        animated_print(response)
        time.sleep(5)
        return

    match = re.search(r"Time:\s*(\S+)\s*\r?\nDownload:\s*(\S+)", response)
    if not match:
        animated_print("Неверный ответ сервера")
        time.sleep(3)
        return

    time_part, download_url = match.groups()
    seconds_left = parse_duration(time_part)
    
    animated_print(f"\nСтатус подписки: Активен")
    animated_print(f"Срок окончания подписки: {format_russian_time(seconds_left)}")
    
    # Проверка папок ПОСЛЕ успешной авторизации
    if not check_folders():
        animated_print("\nОбнаружены отсутствующие папки, начинаю переустановку...")
        delete_folders()
        
        # Скачивание и установка клиента
        animated_print("\nЗагрузка клиента...")
        download_and_extract_zip(download_url, QUANTUUM_DIR)
        animated_print("Клиент успешно установлен!")
        return  # Завершаем работу

    # Если папки в порядке - запускаем клиент
    ram = get_input("\nRAM (ГБ): ", digits_only=True)
    if not ram:
        animated_print("Неверный объем RAM")
        time.sleep(3)
        return
        
    animated_print("\nЗапуск клиента...")
    pid = run_jar(ram)
    
    if pid:
        animated_print(f"Клиент успешно запущен.")
        animated_print("Лоадер закроется автоматически через 5 секунд...")
        time.sleep(5)
        sys.exit(0)
    else:
        animated_print("Не удалось запустить клиент.")
        animated_print("Лоадер закроется через 5 секунд...")
        time.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    main()