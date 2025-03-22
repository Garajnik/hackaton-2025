import time
from vosk import Model, KaldiRecognizer
import pyaudio
import numpy as np
import pyrnnoise
import sys
import json
import logging
from datetime import datetime

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
    try:
        input()
        while True:
            # Обработка аудио
            data = stream.read(4096, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.int16)

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
                    print(modified_text, end=' ')
                    results += modified_text + ' '
                    count_time = 0

            if results != '':
                count_time += 1
                if count_time >= 30:
                    if 'пятнадцать этап' in results:
                        logger.warning('ОТЧЕТНОСТЬ ' + results)
                        parse(results)
                    else:
                        logger.info(results)
                    results = ''

    except KeyboardInterrupt:
        print("\nЗавершение работы...")
        if results:
            if 'пятнадцать этап' in results:
                logger.warning('ОТЧЕТНОСТЬ ' + results)
                parse(results)
            else:
                logger.info(results)
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()


def parse(data: str):
    data = data.split(' ')

    print()
    print()
    print (data[2] + ' : ' + ' '.join(data[3:]))


if __name__ == "__main__":
    main()