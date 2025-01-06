from lxml import etree
from googletrans import Translator

import asyncio
import re

from  aiogram.methods import EditMessageText
from aiogram.types import Message

def split_text_into_paragraphs(text, max_length=300):
    # Разбиваем текст на предложения
    sentences = re.split(r'(?<=[.!?]) +', text)
    paragraphs = []
    current_paragraph = ""

    for sentence in sentences:
        # Если добавление предложения превышает max_length, сохраняем текущий абзац
        if len(current_paragraph) > max_length:
            paragraphs.append(current_paragraph.strip())
            current_paragraph = sentence
        else:
            # Добавляем предложение в текущий абзац
            current_paragraph += " " + sentence

    # Добавляем последний абзац, если он не пуст
    if current_paragraph:
        paragraphs.append(current_paragraph.strip())

    return paragraphs


async def translate_book(book, src_lang, dest_lang, message: Message, bot):
    tree = etree.parse(book)

    root = tree.getroot()
    my_tag = "{http://www.gribuser.ru/xml/fictionbook/2.0}p"
    tags = root.findall(".//" + my_tag)

    translator = Translator()

    n = len(tags)
    counter = 0
    paragraphs = []
    paragraphs_len = 0
    progress = 0
    for tag in tags:
        text_content = "".join(tag.itertext())
        text_content = " ".join(text_content.split())
        if text_content == "":
            continue
        tag.clear()
        tag.text = text_content
        counter += 1
        if progress != int(counter / n * 100):
            await sent_progress(message, progress, bot)
        progress = int(counter / n * 100)
        cur_paragraphs = split_text_into_paragraphs(tag.text, max_length=250)
        reversed(cur_paragraphs)
        for i in range(len(cur_paragraphs)):
            cur_paragraphs[i] = (cur_paragraphs[i], tag)
        paragraphs_len += len(tag.text)
        paragraphs.extend(cur_paragraphs)

        if (paragraphs_len > 10000):
            to_translate = [paragraph[0] for paragraph in paragraphs]
            pattern = " \n "
            to_translate_str = pattern.join(to_translate)
            translated_courutine = await translator.translate(to_translate_str, dest=dest_lang, src=src_lang)
            translated = translated_courutine.text.split(pattern)

            paragraphs_len += len(translated)
            for i in range((len(paragraphs))):
                origin_par = paragraphs[i][0]
                translated_par = translated[i]
                cur_tag = paragraphs[i][1]
                emphasis = etree.Element("emphasis")
                emphasis.text = translated_par
                tpar = etree.Element("p")
                tpar.append(emphasis)
                par = etree.Element("p")
                par.text = origin_par
                cur_tag.addnext(tpar)
                cur_tag.addnext(etree.Element("empty-line"))
                cur_tag.addnext(par)
                cur_tag.addnext(etree.Element("empty-line"))

            paragraphs.clear()
            paragraphs_len = 0
    for tag in tags:
        parent = tag.getparent()
        parent.remove(tag)

    await sent_progress(message, 100, bot)
    f = open(book + "result" + ".fb2", "w", encoding="utf-8")
    xmlstr = etree.tostring(root, encoding='unicode')
    f.write(xmlstr)
    f.close()

async def sent_progress(message: Message, progress : int, bot):
    await message.edit_text(text=f"Progress: {progress}%")

if (__name__ == "__main__"):
    book = "books/book3.fb2"
    asyncio.run(translate_book(book, src_lang='pl', dest_lang='ru'))
