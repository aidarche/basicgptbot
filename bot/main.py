from telegram import BotCommand
from telegram.ext import ApplicationBuilder, AIORateLimiter, MessageHandler, CommandHandler, filters
from dotenv import load_dotenv
import os

from handlers import start_handle, help_handle, message_handle, voice_message_handle

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


async def post_init(application):
    """
    Устанавливает команды и запускает планировщик.
    """
    # Устанавливаем команды для бота
    await application.bot.set_my_commands([
        BotCommand("/help", "Начать новый диалог"),
        BotCommand("/start", "Перезапустить бота"),
    ])


def run_bot() -> None:
    """
    Запускает бота Telegram.
    """
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=1))
        .http_version("1.1")
        .get_updates_http_version("1.1")
        .post_init(post_init)
        .connect_timeout(60)
        .build()
    )

    # Команды
    application.add_handler(CommandHandler("start", start_handle))
    application.add_handler(CommandHandler("help", help_handle))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle))
    application.add_handler(MessageHandler(filters.VOICE, voice_message_handle))

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    run_bot()