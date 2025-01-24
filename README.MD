## Telegram Bot with OpenAI Integration

This is a basic Telegram bot that connects to the OpenAI API. The bot can handle text and voice messages, sending user inputs to OpenAI and returning responses.

You can try our main bot with a wide range of features, such as image generation, dialogue context saving, voice message support, model selection, and much more. Many of these features are available for free at the following link: [intellectivebot]("https://t.me/intellectivebot").

### Features

- Handle text messages and send them to OpenAI API for response.
- Handle voice messages, convert them to text using OpenAI’s Whisper, and send the text to OpenAI API.
- Modular code structure for easy extensibility.

### Installation and Setup

#### 1. Clone the Repository


    git clone https://github.com/your-repo/telegram-openai-bot.git
    cd basicgptbot  

#### 2. Install Python Dependencies  

Make sure you have Python 3.8+ installed. Then, install the required dependencies:


    pip install -r requirements.txt

#### 3. Create a .env File  

Create a .env file from the example file provided:  

    cp .env.example .env

Edit the .env file to add your credentials:

    TELEGRAM_TOKEN=your_telegram_bot_token
    OPENAI_API_KEY=your_openai_api_key
    OPENAI_VERSION=model_name
    USERS=telegram_id,

- Replace your_telegram_bot_token with your Telegram bot token obtained from BotFather.
- Replace your_openai_api_key with your OpenAI API key.
- Replace model_name with OpenAI model which you want to use, for example `4o` or `o1-preview`.
- Replace telegram_id with your allowed Telegram IDs. Only these users will have access to your bot.

#### 4. Run the Bot

Run the bot using the following command:

    python bot/main.py

## Usage

1. Start the bot in Telegram by finding it with the username you set up via BotFather.
2. Send text messages to get responses from OpenAI.
3. Send voice messages to receive transcriptions and responses.

## Notes

- Ensure your .env file is correctly configured before running the bot.
- s project is designed for educational purposes and can be extended to include more advanced functionality.

Feel free to contribute or raise issues on GitHub! 🎉