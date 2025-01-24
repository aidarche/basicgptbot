import tempfile

import openai
import requests
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ContextTypes
from telegram import Update
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_VERSION = os.getenv("OPENAI_VERSION")
openai.api_key = OPENAI_API_KEY
USERS = list(map(int, os.getenv("USERS", "").split(",")))


WELCOME_MESSAGE = '''
Привет! Я <b>ChatGPT</b> бот, с помощью которого ты можешь общаться с ИИ
'''

HELP_MESSAGE = '''
Просто напиши мне сообщение и тебе ответит ИИ
'''


async def start_handle(update: Update, context: CallbackContext):

    reply_text = WELCOME_MESSAGE
    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)


async def help_handle(update: Update, context: CallbackContext):

    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)


async def send_to_openai(user_message: str) -> str:
    """
    Отправляет сообщение в OpenAI API и возвращает ответ.
    """
    response = openai.ChatCompletion.create(
        model=OPENAI_VERSION,  # Укажите модель
        messages=[
            {"role": "user", "content": user_message},
        ],
    )
    return response['choices'][0]['message']['content']


async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает текстовые сообщения пользователей, отправляет их в OpenAI API и возвращает ответ.
    """
    user_message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id not in USERS:
        await context.bot.send_message(chat_id=chat_id, text="Вы не являетесь разрешенным пользоветелем, обратитесь к владельцу бота")
        return

    try:
        # Используем общую функцию для обработки сообщения
        bot_reply = await send_to_openai(user_message)
        # Отправляем ответ пользователю
        await context.bot.send_message(chat_id=chat_id, text=bot_reply)

    except openai.error.OpenAIError:
        await update.message.reply_text("Произошла ошибка при запросе к OpenAI. Попробуйте позже.")
    except Exception:
        await update.message.reply_text("Что-то пошло не так. Пожалуйста, повторите попытку позже.")


async def voice_message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает голосовые сообщения пользователей:
    1. Загружает голосовое сообщение.
    2. Расшифровывает его в текст.
    3. Отправляет текст в OpenAI API.
    4. Возвращает ответ пользователю.
    """
    chat_id = update.effective_chat.id

    user_id = update.effective_user.id
    if user_id not in USERS:
        await context.bot.send_message(chat_id=chat_id, text="Вы не являетесь разрешенным пользоветелем, обратитесь к владельцу бота")
        return

    try:
        # Получение файла голосового сообщения
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        file_path = file.file_path

        # Скачиваем голосовое сообщение
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
            file_content = requests.get(file_path).content
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        # Преобразуем голос в текст
        with open(temp_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        user_message = transcript['text']
        await context.bot.send_message(chat_id=chat_id, text=f"Ваше сообщение: {user_message}")
        # Используем общую функцию для отправки текста в OpenAI API
        bot_reply = await send_to_openai(user_message)

        # Отправляем ответ пользователю
        await context.bot.send_message(chat_id=chat_id, text=bot_reply)

    except openai.error.OpenAIError:
        await update.message.reply_text("Произошла ошибка при обработке голосового сообщения. Попробуйте позже.")
    except Exception:
        await update.message.reply_text("Что-то пошло не так. Пожалуйста, повторите попытку позже.")
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
