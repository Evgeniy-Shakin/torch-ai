from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from filters.chat_types import ChatTypeFilter
from database import control_db as db
from keyboards.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))
WEB_APP_URL = 'https://evgeniy-shakin.github.io/torch-ai/'



class Registration(StatesGroup):
    waiting_for_name = State()



@user_private_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user = db.is_registered(message.from_user.id)
    if user:
        user_name, coins = user
        await message.answer(f"Привет, {user_name}!",
                            reply_markup=get_keyboard(
                            "Профиль",
                            "Рейтинг",
                            "Открыть Torch",
                            placeholder="Выберите ниже",
                            sizes=(2, 2)
                            ))
    else:
        await message.answer("Привет! Как тебя зовут?")
        await state.set_state(Registration.waiting_for_name)


# Первый запуск и регестрация
@user_private_router.message(Registration.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.text.strip()
    db.save_user(user_id, user_name)
    
    await message.answer(f"Добро пожаловать, {user_name}!",
                         reply_markup=get_keyboard(
                            "Профиль",
                            "Рейтинг",
                            "Открыть Torch",
                            placeholder="Выберите ниже",
                            sizes=(2, 2)
                         ))
    await state.clear()


@user_private_router.message(F.text == "Открыть Torch")
async def delete_product(message: types.Message):
    torch_kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть Torch", web_app=types.WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer("Страница доступна", reply_markup=torch_kbd)


@user_private_router.message(F.text == "Профиль")
async def delete_product(message: types.Message):
    await message.answer(f"Имя: {db.get_name(message.from_user.id)}\nTorch coin: {db.get_coin(message.from_user.id)}\nМесто в рейтинге: {db.get_user_rank(message.from_user.id)}")


@user_private_router.message(F.text == "Рейтинг")
async def delete_product(message: types.Message):
    top_list = db.get_top_rank()
    await message.answer(top_list)

