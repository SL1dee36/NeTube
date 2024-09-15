from moviepy.video.io.VideoFileClip import VideoFileClip

from config import Config
from models import Video, Comment, User, db
from helpers.utils import allowed_file, generate_random_name, generate_thumbnail
from flask import session, jsonify, redirect, url_for
import os
import subprocess


def save_video(file, title, description, user_id):
    """
    Сохраняет загруженное видео и создает соответствующую запись в базе данных.

    Args:
        file: Загружаемый файл.
        title (str): Название видео.
        description (str): Описание видео.
        user_id (int): ID пользователя, который загружает видео.

    Returns:
        str: Имя файла.
    """
    filename = generate_random_name() + ".mp4"
    video_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    temp_path = os.path.join(Config.UPLOAD_FOLDER, "temp_" + filename)

    file.save(video_path)


    # Заменяем исходное видео на измененное
    os.rename(temp_path, video_path)

    thumbnail_path = os.path.join(Config.THUMBNAIL_FOLDER, filename[:-4] + ".jpg")
    generate_thumbnail(video_path, thumbnail_path)

    new_video = Video(
        title=title,
        url=filename,
        description=description,
        user_id=user_id
    )
    db.session.add(new_video)
    db.session.commit()

    return filename


def increment_video_views(video):
    """
    Увеличивает количество просмотров видео.

    Args:
        video (Video): Объект видео.
    """
    video.views += 1
    db.session.commit()


def add_comment_to_video(video, current_user, content):
    """
    Добавляет комментарий к видео и возвращает созданный комментарий.

    Args:
        video (Video): Объект видео.
        current_user (User): Текущий пользователь.
        content (str): Содержимое комментария.

    Returns:
        dict: Данные созданного комментария, включая ID, содержимое и информацию о пользователе.
    """
    comment = Comment(content=content, user=current_user, video=video)
    db.session.add(comment)
    db.session.commit()

    # Возвращаем словарь с данными комментария
    return {
        "id": comment.id,
        "content": comment.content,
        "user": {
            "username": current_user.username,
            "avatar": current_user.avatar or None
        }
    }


def update_subscription(user, user_to_subscribe, subscribe=True):
    """
    Обновляет подписку пользователя.

    Args:
        user (User): Текущий пользователь.
        user_to_subscribe (User): Пользователь, на которого подписываются или отписываются.
        subscribe (bool): True для подписки, False для отписки.

    Returns:
        dict: Результат обновления подписки.
    """
    if subscribe:
        user.subscribed_to.append(user_to_subscribe)
    else:
        user.subscribed_to.remove(user_to_subscribe)

    db.session.commit()
    new_count = user_to_subscribe.subscribers.count()

    return {
        'status': 'success',
        'subscribed': subscribe,
        'subscribers': new_count
    }