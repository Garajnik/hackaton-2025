import time
from vosk import Model, KaldiRecognizer
import pyaudio
import numpy as np
import pyrnnoise
import sys
import json
import logging
import csv
import wave
from datetime import datetime
from openpyxl import Workbook, load_workbook
import requests


# Создаем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Минимальный уровень сообщений

# Форматирование записей
formatter = logging.Formatter(
    fmt='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Настраиваем запись в файл
file_handler = logging.FileHandler(
    filename=f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log",  # Имя файла с датой
    mode='a',  # 'a' - дописывать в конец файла (по умолчанию)
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

# Добавляем обработчик в логгер
logger.addHandler(file_handler)



# Функция для сохранения аудио в файл
def save_audio_to_file(audio_data, file_name="recorded_audio"):
    with wave.open(f'sounds/{file_name}.wav', 'wb') as wf:
        # Параметры для записи
        wf.setnchannels(1)  # Один канал (моно)
        wf.setsampwidth(2)  # Ширина сэмпла (16 бит)
        wf.setframerate(16000)  # Частота дискретизации
        wf.writeframes(audio_data)

def main():
    data_as = {
        'КНБК': ['каин пока', 'кэнт пока', 'кэн пока', 'кнопок пока', 'кн пока',
                 'квн пока', 'кэн пока', 'кнп поклон', 'крем пока', 'к клыка', 'кем пока', 'кэнт бока', 'карен пока',
                 'руками быка', 'кнб быка', 'каин бока', 'энд бокам', 'карен бока'],
        'СПО': ['эспоо', 'спама', 'без по его'],
        "ГИС": ['дис', 'гид', 'гис'],
        'Обслуживание БУ': ['обслуживание бэйл', 'обслуживание был',
                            'обслуживание б у', 'обслуживание бы у'],
        'ЗБС': ['зэ бэст', 'за без'],
    }

    # Инициализация модели Vosk
    model_path = "vosk-model-small-ru-0.22"
    try:
        model = Model(model_path)
    except Exception as e:
        logger.error("Ошибка загрузки модели Vosk: %s", e)
        sys.exit(1)

    recognizer = KaldiRecognizer(model, 16000)

    # Инициализация аудиопотока
    mic = pyaudio.PyAudio()
    try:
        stream = mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4096  # Читать по 4096 байт
        )
    except Exception as e:
        sys.exit(1)

    # Инициализация шумоподавления
    try:
        rnn = pyrnnoise.RNNoise(sample_rate=16000)
    except Exception as e:
        logger.error("Ошибка инициализации RNNoise: %s", e)
        sys.exit(1)

    print("Говорите... (Нажмите Ctrl+C для завершения)")
    results = ''
    count_time = 0
    sound = b''
    try:
        input()
        while True:
            # Обработка аудио
            data = stream.read(4096, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.int16)

            # Сохраняем аудио в файл
            sound += data

            # Подавление шумов
            frame_size = 480
            denoised_audio = np.empty(len(audio), dtype=np.int16)

            for i in range(0, len(audio), frame_size):
                frame = audio[i:i + frame_size]
                original_length = len(frame)

                if original_length < frame_size:
                    frame = np.pad(frame, (0, frame_size - original_length), mode='constant')

                # Нормализация в float32 [-1, 1]
                frame_float = frame.astype(np.float32) / 32768.0

                try:
                    processed_frame_float = rnn(frame_float)
                except Exception as e:
                    processed_frame_float = frame_float  # Fallback

                # Масштабирование в int16
                processed_frame = (processed_frame_float * 32767).astype(np.int16)
                denoised_audio[i:i + original_length] = processed_frame[:original_length]

            # Распознавание речи
            processed_data = denoised_audio.tobytes()

            if recognizer.AcceptWaveform(processed_data):
                result = json.loads(recognizer.Result())
                text = result.get('text', '')

                if text:
                    # Применяем замены
                    modified_text = text
                    for correct_word, variants in data_as.items():
                        for variant in variants:
                            modified_text = modified_text.replace(variant, correct_word)
                    print(modified_text, end=' ') ##########
                    url = "https://127.0.0.1:8000/add"  # Замените на нужный URL
                    data = {
                        "text":modified_text
                    }
                    headers = {
                        "Content-Type": "application/json"  # Указываем, что отправляем JSON
                    }
                    response = requests.post(url, json=data, headers=headers)
                    results += modified_text + ' '
                    count_time = 0

            if results != '':
                count_time += 1
                if count_time >= 30:
                    # Получаем текущее время
                    now = datetime.now()

                    # Форматируем время в нужном виде (часы-минуты-секунды)
                    time_str = now.strftime("%H-%M-%S")
                    if 'пятнадцать этап' in results:
                        logger.warning('ОТЧЕТНОСТЬ ' + results)
                        make_otchet(results)
                    else:
                        logger.info(results)
                    save_audio_to_file(sound, time_str)
                    sound = b''
                    results = ''

    except KeyboardInterrupt:
        print("\nЗавершение работы...")
        if results:
            now = datetime.now()

            # Форматируем время в нужном виде (часы-минуты-секунды)
            time_str = now.strftime("%H-%M-%S")
            if 'пятнадцать этап' in results:
                logger.warning('ОТЧЕТНОСТЬ ' + results)
                make_otchet(results)
            else:
                logger.info(results)
            save_audio_to_file(sound, time_str)
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()


def make_otchet(data: str):
    parsed_data = parse(data)

    # Запись в JSON
    with open(f'data/{parsed_data["starttime"].replace(":", "-")}.json', 'w', encoding='utf-8') as json_file:
        json.dump(parsed_data, json_file, ensure_ascii=False, indent=4)

    print("Данные записаны в файл data_info.json")

    # Запись в CSV (добавление, если файл существует)
    csv_file = 'data/data_info.csv'

    # Проверим, существует ли файл и если нет, добавим заголовки
    file_exists = False
    try:
        with open(csv_file, 'r', encoding='utf-8'):
            file_exists = True
    except FileNotFoundError:
        pass

    # Запись данных в CSV
    with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        # Убедитесь, что fieldnames включает все ключи из parsed_data
        fieldnames = ['starttime', 'zaboy', 'stage', 'comments']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Записываем заголовки, если файл новый
        writer.writerow(parsed_data)  # Записываем данные

    print(f"Данные записаны в файл {csv_file}")

    # Запись в XLSX (добавление, если файл существует)
    xlsx_file = 'data/data_info.xlsx'

    try:
        # Пытаемся загрузить существующий файл
        wb = load_workbook(xlsx_file)
        ws = wb.active
    except FileNotFoundError:
        # Если файл не существует, создаем новый
        wb = Workbook()
        ws = wb.active
        ws.append(['starttime', 'zaboy', 'stage', 'comments'])  # Записываем заголовки

    # Добавляем данные в файл
    ws.append([parsed_data['starttime'], parsed_data['zaboy'], parsed_data['stage'], parsed_data['comments']])

    # Сохраняем изменения в файл
    wb.save(xlsx_file)

    print(f"Данные записаны в файл {xlsx_file}")

def parse(data: str):
    words = [
        "КНБК",
        "СПО",
        "бурения",
        "Промывка",
        "Проработка",
        "Вспомогательные операции",
        "Крепление",
        "Оборудование устья скважины",
        "ГИС",
        "Обслуживание БУ",
        "Управление скважиной",
        "Прочие работы",
        "Освоение",
        "ЗБС",
        "Испытание"
    ]
    data = data.split(' ')
    for i in range(len(data)-1):
        if data[i] == 'пятнадцать' and data[i+1] == 'этап':
            data = data[i+2:]
            break
    current_time = datetime.now().strftime("%H:%M:%S")
    for word in words:
        if word.lower() in data[:3]:
            # Получаем текущее время и записываем его в строку
            data_info = {
                'starttime': current_time,
                'zaboy': 1000,
                'stage': word,
                'comments': '',
            }
            return data_info
    data_info = {
            'starttime': current_time,
            'zaboy': 1000,
            'stage': 'НПВ',
            'comments': str(' '.join(data)),
        }
    return  data_info


if __name__ == "__main__":
    main()