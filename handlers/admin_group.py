from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.reply import get_keyboard, del_kbd


admin_group_router = Router()
admin_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]), IsAdmin())
admin_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "List of products",
    "Add a product",
    "Change product",
    "Remove product",
    "Exit",
    placeholder="Select an action:",
    sizes=(1, 3, 1)
)

CANCEL_KB = get_keyboard(
    "Cancel",
    sizes=(1, )
)

CANCEL_BACK_KB = get_keyboard(
    "Cancel",
    "Back",
    sizes=(2, )
)



@admin_group_router.message(Command("admin"))
async def add_product(message: types.Message):
    await message.answer("What you want to do?", reply_markup=ADMIN_KB)


@admin_group_router.message(F.text == "Exit")
async def starring_at_product(message: types.Message):
    await message.answer("Exiting the admin panel...", reply_markup=del_kbd)


@admin_group_router.message(F.text == "Change product")
async def change_product(message: types.Message):
    await message.answer("Select product to be change")


@admin_group_router.message(F.text == "Remove product")
async def delete_product(message: types.Message):
    await message.answer("Select product(s) to be remove")





#Код ниже для машины состояний (FSM)

@admin_group_router.message(StateFilter('*'), F.text == "Cancel")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    # Если нет активного состояния, завершаем работу 
    if current_state is None:
        return 0
    await state.clear()
    await message.answer("Cancellation...", reply_markup=ADMIN_KB)


@admin_group_router.message(StateFilter('*'), F.text == "Back")
async def back_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            if previous == AddProduct.name:
                await message.answer(AddProduct.texts[previous.state], reply_markup=CANCEL_KB)
            else:
                try:
                    await message.answer(AddProduct.texts[previous.state], reply_markup=CANCEL_BACK_KB)
                except AttributeError:
                    return 0 
            return 0
        previous = step
        


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()

    texts = {
        'AddProduct:name' : 'Введите название товара:',
        'AddProduct:description': 'Введите описание товара:',
        'AddProduct:price': 'Введите стоимость товара:',
    }


# FSM
# StateFilter() - Проверка на активное состояние
@admin_group_router.message(StateFilter(None), F.text == "Add a product")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer("Введите название товара:", reply_markup=CANCEL_KB)
    # Входим в активное состояние для получения AddProduct.name
    await state.set_state(AddProduct.name)

# Проверка на активное состояние AddProduct.name
@admin_group_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    # Обновляем данные для Addproduct.name
    await state.update_data(name=message.text)
    await message.answer("Введите описание товара:", reply_markup=CANCEL_BACK_KB)
    # Входим в активное состояние для получения AddProduct.description
    await state.set_state(AddProduct.description)

# Проверка на активное состояние AddProduct.decription
@admin_group_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите стоимость товара:", reply_markup=CANCEL_BACK_KB)
    await state.set_state(AddProduct.price) # Встаём в ожидании ввода price


@admin_group_router.message(AddProduct.price, F.text) # Если пользователь в состоянии price и отправляет текст
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Загрузите изображение товара:", reply_markup=CANCEL_BACK_KB)
    await state.set_state(AddProduct.image)


@admin_group_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext):
    '''
    Изображения на серверах телеграмма обрабатывается в разных разрешениях и перечисленны они в 
    списке message.photo[]
    '''
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
    # Полученные данные ввиде dict (Словаря)
    data = await state.get_data()
    await message.answer(str(data))
    # Очистка состояния пользователя
    await state.clear()
    