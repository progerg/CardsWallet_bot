from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from sqlalchemy.future import select
from data.User import User
import configparser
from keyboard.keyboard import *
from data.db_session import *
from card_decode.card_code_decode import *
from data.Shops import *
import os
import aioschedule
import asyncio
import json

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("configs.ini")

bot = Bot(token=config['Bot']['token'])
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

with open('json/message.json') as f:
    MESSAGES = json.load(f)

with open('json/button.json') as f:
    BUTTONS = json.load(f)


class Main(StatesGroup):
    main = State()


class MyCards(StatesGroup):
    main = State()


class AddCard(StatesGroup):
    name = State()
    photo = State()
    confirm = State()


@dp.message_handler(commands='start', state='*')
async def message_handler(message: types.Message, state: FSMContext):
    async with create_session() as sess:
        result = await sess.execute(select(User.user_id).where(User.user_id == message.from_user.id))
        user = result.scalars().first()
        if not user:
            msg = MESSAGES[message.from_user.language_code]['start']['1']
            user = User()
            user.user_id = message.from_user.id
            try:
                user.username = message.from_user.username
            except Exception as err:
                pass
            sess.add(user)
            await sess.commit()
        else:
            msg = MESSAGES[message.from_user.language_code]['main']['1']
        await Main.main.set()
        await message.answer(msg, reply_markup=await main(message.from_user.language_code))


@dp.message_handler(commands='add_shop', state='*')
async def message_handler(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in config['Bot']['admin'].split(';'):
        data = message.text.split()
        async with create_session() as sess:
            shop = Shops()
            shop.ru_name = data[1]
            shop.en_name = data[2]
            sess.add(shop)
            await sess.commit()


@dp.message_handler(commands='delete_shop', state='*')
async def message_handler(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in config['Bot']['admin'].split(';'):
        data = message.text.split()
        async with create_session() as sess:
            result = await sess.execute(select(Shops).where(Shops.ru_name == data[1]))
            shop = result.scalars().first()
            if shop:
                await sess.delete(shop)
                await sess.commit()


@dp.message_handler(state=Main.main)
async def message_handler(message: types.Message, state: FSMContext):
    if message.text == BUTTONS[message.from_user.language_code]['main']['1']:
        async with create_session() as sess:
            res = await sess.execute(select(User).where(User.user_id == message.from_user.id))
            user = res.scalars().first()
        await MyCards.main.set()
        msg = MESSAGES[message.from_user.language_code]['my_cards']['1']
        await message.answer(msg, reply_markup=await my_cards_inline_markup(message.from_user.language_code, user))
        # await message.answer(msg)
        msg = MESSAGES[message.from_user.language_code]['my_cards']['2']
        await message.answer(msg, reply_markup=await my_cards_reply_markup(message.from_user.language_code))
    # elif message.text == BUTTONS[message.from_user.language_code]['main']['2']:
    #     msg = MESSAGES[message.from_user.language_code]['feedback']['1']
    #     await message.answer(msg, reply_markup=await return_button(message.from_user.language_code))
    elif message.text == BUTTONS[message.from_user.language_code]['main']['3']:
        msg = MESSAGES[message.from_user.language_code]['main']['1']
        await Main.main.set()
        await message.answer(msg, reply_markup=await main(message.from_user.language_code))


@dp.message_handler(state=MyCards.main)
async def message_handler(message: types.Message, state: FSMContext):
    if message.text == BUTTONS[message.from_user.language_code]['main']['3']:
        msg = MESSAGES[message.from_user.language_code]['main']['1']
        await Main.main.set()
        await message.answer(msg, reply_markup=await main(message.from_user.language_code))
    elif message.text == BUTTONS[message.from_user.language_code]['my_cards']['1']:
        msg = MESSAGES[message.from_user.language_code]['create']['1']
        await AddCard.name.set()
        async with create_session() as sess:
            result = await sess.execute(select(Shops))
            shops = result.scalars().all()
        await message.answer(msg, reply_markup=await shop_list(message.from_user.language_code, shops))


@dp.message_handler(state=AddCard.name)
async def message_handler(message: types.Message, state: FSMContext):
    if message.text == BUTTONS[message.from_user.language_code]['main']['3']:
        msg = MESSAGES[message.from_user.language_code]['main']['1']
        await Main.main.set()
        await message.answer(msg, reply_markup=await main(message.from_user.language_code))
    elif message.text == BUTTONS[message.from_user.language_code]['my_cards']['3']:
        msg = MESSAGES[message.from_user.language_code]['my_cards']['5']
        await message.answer(msg, reply_markup=await return_button(message.from_user.language_code))
    else:
        msg = MESSAGES[message.from_user.language_code]['create']['2'].replace('{first_name}', message.from_user.first_name)
        await AddCard.photo.set()
        async with state.proxy() as data:
            data['name'] = message.text
        await message.answer(msg, reply_markup=await return_button(message.from_user.language_code))


@dp.message_handler(state=AddCard.photo, content_types=['photo'])
async def message_handler(message: types.Message, state: FSMContext):
    await MyCards.main.set()
    async with state.proxy() as data:
        shop_name = data['name']

    filenames = next(os.walk('for_temp_img/photos'), (None, None, []))[2]
    await message.photo[len(message.photo) - 1].download(destination_dir='for_temp_img')
    filenames_2 = next(os.walk('for_temp_img/photos'), (None, None, []))[2]
    last_name = list(set(filenames_2) - set(filenames))[0]

    with open(f'for_temp_img/photos/{last_name}', 'rb') as f:
        result = await do_work(f.read())
    os.remove(f'for_temp_img/photos/{last_name}')

    if result:
        msg = MESSAGES[message.from_user.language_code]['create']['3']
        msg_2 = await message.answer_photo(photo=result, caption=msg)

        async with create_session() as sess:
            res = await sess.execute(select(User).where(User.user_id == message.from_user.id))
            user = res.scalars().first()
            await user.add_card(data['name'], msg_2.photo[len(msg_2.photo) - 1].file_id, message.photo[2].file_id)
            await sess.commit()

        await state.finish()
        await MyCards.main.set()
        msg = MESSAGES[message.from_user.language_code]['my_cards']['1']
        await message.answer(msg, reply_markup=await my_cards_inline_markup(message.from_user.language_code, user))
        # await message.answer(msg)
        msg = MESSAGES[message.from_user.language_code]['my_cards']['2']
        await message.answer(msg, reply_markup=await my_cards_reply_markup(message.from_user.language_code))
    else:
        await AddCard.photo.set()
        msg = MESSAGES[message.from_user.language_code]['create']['5']
        await message.answer(msg, reply_markup=await return_button(message.from_user.language_code))


@dp.message_handler(state=AddCard.photo)
async def message_handler(message: types.Message, state: FSMContext):
    if message.text == BUTTONS[message.from_user.language_code]['main']['3']:
        msg = MESSAGES[message.from_user.language_code]['main']['1']
        await Main.main.set()
        await message.answer(msg, reply_markup=await main(message.from_user.language_code))


@dp.message_handler(state=AddCard.photo, content_types=['document', 'audio', 'video'])
async def message_handler(message: types.Message, state: FSMContext):
    msg = MESSAGES[message.from_user.language_code]['create']['4']
    await message.answer(msg)


@dp.callback_query_handler(state=MyCards.main)
async def code(callback_query: types.CallbackQuery):
    await callback_query.answer()
    if 'show' in callback_query.data:
        async with create_session() as sess:
            res = await sess.execute(select(User).where(User.user_id == callback_query.from_user.id))
            user = res.scalars().first()
        shop_name = callback_query.data.split('_')[1]
        file_id = user.cards[shop_name]['file_id']
        msg = MESSAGES[callback_query.from_user.language_code]['my_cards']['3'].replace('{shop}', shop_name)
        await bot.send_photo(chat_id=callback_query.from_user.id, photo=file_id,
                             caption=msg,
                             reply_markup=await delete_card(callback_query.from_user.language_code,
                                                            shop_name))
    elif 'delete' in callback_query.data:
        shop_name = callback_query.data.split('_')[1]
        async with create_session() as sess:
            res = await sess.execute(select(User).where(User.user_id == callback_query.from_user.id))
            user = res.scalars().first()
            await user.delete_card(shop_name)
            await sess.commit()
        msg = MESSAGES[callback_query.from_user.language_code]['my_cards']['4'].replace('{shop}', shop_name)
        await bot.send_message(chat_id=callback_query.from_user.id, text=msg)

        await MyCards.main.set()
        msg = MESSAGES[callback_query.from_user.language_code]['my_cards']['1']
        await bot.send_message(chat_id=callback_query.from_user.id, text=msg,
                               reply_markup=await my_cards_inline_markup(callback_query.from_user.language_code, user))
        msg = MESSAGES[callback_query.from_user.language_code]['my_cards']['2']
        await bot.send_message(chat_id=callback_query.from_user.id, text=msg,
                               reply_markup=await my_cards_reply_markup(callback_query.from_user.language_code))


# async def example():
#     pass
#
#
# async def scheduler():
#     aioschedule.every(5).minutes.do(example)
#     # aioschedule.every(30).seconds.do(send_test_message)
#     while True:
#         await aioschedule.run_pending()
#         await asyncio.sleep(1)


async def startup_(_):
    await global_init(user=config['DB']['login'], password=config['DB']['password'],
                      host=config['DB']['host'], port=config['DB']['port'], dbname=config['DB']['db_name'])
    # asyncio.create_task(scheduler())


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown, on_startup=startup_)