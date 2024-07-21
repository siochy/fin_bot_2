from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import sql_for_bot as sql

rt = Router()
buttons_start = ('purchase', 'balance', 'savings', 'save', 'income', 'take', 'statistics')


@rt.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """check user at start. if it's not in db then create record\n"""

    user = str(message.from_user.id)
    check = await sql.user_check(user)
    if not check:
        await sql.create_user(user)

    builder = ReplyKeyboardBuilder()
    for button in buttons_start:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(3)

    await message.answer(text='Choose', reply_markup=builder.as_markup(resize_keyboard=True))


@rt.message(Command(commands='help'))
async def help_handler(message: types.Message):
    """a few words if click 'help'"""

    mess = ('There is a site where you also can see more statistics and graphics\n' +
            'huilo.com\n' +
            'If you have any questions text me - @sioh4')

    builder = ReplyKeyboardBuilder()
    for button in buttons_start:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(3)

    await message.answer(mess, reply_markup=builder.as_markup(resize_keyboard=True))


@rt.message(Command(commands='cancel'))
async def cancel_state(message: types.Message, state: FSMContext):
    """Cancel inserting purchase, save, take, income, statistics"""

    builder = ReplyKeyboardBuilder()
    for button in buttons_start:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(3)

    await state.clear()
    await message.answer('Cancelled', reply_markup=builder.as_markup(resize_keyboard=True))
