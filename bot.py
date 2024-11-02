import os
from time import sleep

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User, BotCommand, KeyboardButton, ReplyKeyboardMarkup

from dotenv import load_dotenv

from database.orm import get_new_articles, get_article_by_header, set_article_readed
from settings.settings import message_footer

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

router = Router()


async def set_commands_menu(bot: Bot):
    await bot.delete_my_commands()
    main_menu_commands = [BotCommand(
                            command='/start',
                            description='Запуск бота')
                        ]
    await bot.set_my_commands(main_menu_commands)
    return None


# Этот классический хэндлер будет срабатывать на команду /start
@dp.message(CommandStart())
async def command_start_process(message: Message):
    text = 'Bot started'
    request_button = KeyboardButton(text='Получить статьи')
    keyboard = ReplyKeyboardMarkup(keyboard=[[request_button]], resize_keyboard=True)
    await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')


@dp.message(F.text == 'Получить статьи')
async def process_request_articles_answer(message: Message):
    new_articles = get_new_articles()
    for article in new_articles:
        article_header = article.header
        article_header_original = article.header_original
        # article_text = article.text
        article_text_short = article.text_short
        article_source_url = article.source_url
        image_urls_list = article.image_urls.split(', ')
        text = f'{article_header}\n\n{article_text_short}\n\n{message_footer}'
        await message.answer(text=text, parse_mode='HTML')
        await message.answer(text=f'Источник статьи: {article_source_url}')
        for index, image_url in enumerate(image_urls_list):
            await message.answer(text=f'Изображение {index + 1}: {image_url}')
        article_id = get_article_by_header(article_header_original)
        set_article_readed(article_id)
        sleep(3)


def main():
    dp.startup.register(set_commands_menu)
    dp.include_router(router)
    dp.run_polling(bot)


if __name__ == '__main__':
    main()