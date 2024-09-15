# utils.py

import random
import string
from flask import session
from fuzzywuzzy import process, fuzz
from moviepy.editor import VideoFileClip
from PIL import Image

from config import Config
from models import User, Video  # Импортируйте модель User



def allowed_file(filename):
    """Проверяет, является ли файл допустимого формата."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def generate_thumbnail(video_path, thumbnail_path):
    """
    Генерирует миниатюру видео, сохраняя ее в нужном размере и соотношении сторон.

    Args:
        video_path (str): Путь к видеофайлу.
        thumbnail_path (str): Путь для сохранения миниатюры.
    """
    video = VideoFileClip(video_path)
    frame = video.get_frame(t=0.0)
    image = Image.fromarray(frame)
    width, height = image.size

    # Обрезка для сохранения соотношения 16:9
    if width / height != 16 / 9:
        crop_width = width if width > height else int(height * 16 / 9)
        crop_height = int(crop_width * 9 / 16) if width > height else height
        left_offset = (width - crop_width) // 2
        top_offset = (height - crop_height) // 2
        image = image.crop((left_offset, top_offset, left_offset + crop_width, top_offset + crop_height))

    # Сжатие до 1280x720, если необходимо
    if width > 1280 or height > 720:
        image = image.resize((1280, 720))

    image.save(thumbnail_path)


def generate_random_name(length=10):
    """Генерирует случайное имя заданной длины из букв и цифр."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def get_current_user():
    """Возвращает текущего пользователя на основе данных сессии."""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def search_videos(search_query, videos):
    """
    Выполняет нечеткий поиск видео по названию.

    Args:
        search_query (str): Поисковый запрос.
        videos (list): Список видео объектов.

    Returns:
        list: Список найденных видео.
    """
    # Получаем заголовки видео для поиска
    video_titles = [(video, video.title) for video in videos]

    # Выполняем нечеткий поиск по названиям видео
    matches = process.extract(search_query, [title for video, title in video_titles], scorer=fuzz.token_sort_ratio)

    # Оставляем только те результаты, где совпадение больше или равно 20
    search_results = [video for (video, title), score in zip(video_titles, matches) if score[1] >= 20]

    return search_results
