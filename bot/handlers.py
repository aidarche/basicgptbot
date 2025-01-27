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


async def start_handle(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.HTML)


async def help_handle(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)


async def send_to_openai(user_message: str) -> str:
    """
    Sends a message to the OpenAI API and returns its response.
    """
    response = openai.ChatCompletion.create(
        model=OPENAI_VERSION,
        messages=[
            {"role": "user", "content": user_message},
        ],
    )
    return response['choices'][0]['message']['content']


async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles text messages from users, sends them to the OpenAI API, and returns the response.
    """
    user_message = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if user_id not in USERS:
        await context.bot.send_message(chat_id=chat_id, text="Вы не являетесь разрешенным пользоветелем, обратитесь к владельцу бота")
        return

    try:
        # Use the shared function to process the message
        bot_reply = await send_to_openai(user_message)
        # Send the response back to the user
        await context.bot.send_message(chat_id=chat_id, text=bot_reply)

    except openai.error.OpenAIError:
        await update.message.reply_text("Произошла ошибка при запросе к OpenAI. Попробуйте позже.")
    except Exception:
        await update.message.reply_text("Что-то пошло не так. Пожалуйста, повторите попытку позже.")


async def voice_message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles voice messages from users:
    1. Downloads the voice message.
    2. Transcribes it into text.
    3. Sends the text to the OpenAI API.
    4. Returns the response to the user.
    """
    chat_id = update.effective_chat.id

    user_id = update.effective_user.id
    if user_id not in USERS:
        await context.bot.send_message(chat_id=chat_id, text="Вы не являетесь разрешенным пользоветелем, обратитесь к владельцу бота")
        return

    try:
        # Retrieve the voice message file
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        file_path = file.file_path

        # Download the voice message
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
            file_content = requests.get(file_path).content
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        # Convert voice to text
        with open(temp_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        user_message = transcript['text']
        await context.bot.send_message(chat_id=chat_id, text=f"Ваше сообщение: {user_message}")
        # Use the shared function to send the text to OpenAI API
        bot_reply = await send_to_openai(user_message)

        # Send the response back to the user
        await context.bot.send_message(chat_id=chat_id, text=bot_reply)

    except openai.error.OpenAIError:
        await update.message.reply_text("Произошла ошибка при обработке голосового сообщения. Попробуйте позже.")
    except Exception:
        await update.message.reply_text("Что-то пошло не так. Пожалуйста, повторите попытку позже.")
    finally:
        # Delete the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
