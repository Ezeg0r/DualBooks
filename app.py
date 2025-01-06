import asyncio
import json

from aiogram import Dispatcher, Bot, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter
from aiogram.utils.formatting import Text, Bold

import os

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import keyboards as kb

from aiogram.types import FSInputFile
from translator import translate_book

TOKEN = "8176188324:AAGHunI835gbVAEETCh8bHygsW3yE-c76pc"

dp = Dispatcher()

bot = Bot(token=TOKEN)


class GetFile(StatesGroup):
    file = State()



@dp.message(F.content_type == ContentType.DOCUMENT)
async def get_file_handler(message: Message, state: FSMContext):
    await state.clear()

    file_id = message.document.file_id
    if not message.document.file_name.endswith('.fb2'):
        content = Text(Text("Отправьте файл в формате ", Bold("fb2"), "!"))
        await message.answer(**content.as_kwargs())
    else:

        await bot.download(file_id, file_id + ".fb2")

        await state.set_state(GetFile.file)
        await state.update_data(file_name = file_id + ".fb2")

        await message.answer("Файл получен!\nВыберете язык на котором хотите видеть параллельный перевод:", reply_markup=kb.languages)
#
@dp.message(F.text.in_({"English", "Russian", "Polish", "Belarusian"}), GetFile.file)
async def translate_file_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    sent_message = await message.answer(f"Вы выбрали {message.text} язык!", reply_markup=kb.remove_keyboard)
    progress_message = await message.answer("Porgress: 0%")
    lang = message.text
    if (lang == "English"): lang = "en"
    if (lang == "Russian"): lang = "ru"
    if (lang == "Polish"): lang = "pl"
    if (lang == "Belarusian"): lang = "be"
    try:
        await translate_book(data["file_name"], src_lang="auto", dest_lang=lang, message=progress_message, bot=bot)
        book = FSInputFile(data["file_name"] + "result" + ".fb2", filename="book.fb2")
        await message.answer_document(document=book, reply_to_message_id=sent_message.message_id)
        await delete_file_async(data["file_name"] + "result" + ".fb2")
    except Exception as error:
        await message.answer(f"Ошибка при переводе: {error}")
    await delete_file_async(data['file_name'])


async def delete_file_async(file_path):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, os.remove, file_path)

async def main():

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())