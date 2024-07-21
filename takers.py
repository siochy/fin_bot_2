from aiogram import types, Router
from aiogram.filters import StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import sql_for_bot as sql
from states import Insert


rt = Router()

buttons_start = ('purchase', 'balance', 'savings', 'save', 'income', 'take', 'statistics')
buttons_sti = ('save', 'income', 'take')


# group of handlers for purchases
@rt.message(StateFilter(None), F.text.lower() == 'purchase')
async def purchase_handler(message: types.Message, state: FSMContext):
    """handle message 'purchase' and start to take data\n
    about this purchase: name, cost"""

    user = str(message.from_user.id)
    user_db_id = await sql.user_check(user)

    await state.update_data(user_id=user_db_id)
    await message.answer('Insert name of purchased', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Insert.insert_purch)


@rt.message(Insert.insert_purch, F.text)
async def purchase_handle_prod(message: types.Message, state: FSMContext):
    """handle name of purchase and move forward"""

    await state.update_data(prod=message.text.lower())
    await message.answer('Insert cost', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Insert.insert_cost)


@rt.message(Insert.insert_cost, F.text.replace('.', '').isdigit())
async def purchase_handle_summ(message: types.Message, state: FSMContext):
    """handle cost of purchase and summarize data\n
    calculate changes of balance and then record all of this to db"""

    summ = abs(float(message.text))
    data = await state.get_data()
    user_db_id = data['user_id']
    product = data['prod']
    balance = await sql.get_balance_savings(user_db_id, 'balance')
    new_bal_sav = await sql.calc_new_bs(product, balance, 0, summ)
    balance = new_bal_sav[0]

    builder = ReplyKeyboardBuilder()
    for button in buttons_start:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(3)

    await message.answer('Acknowledged', reply_markup=builder.as_markup(resize_keyboard=True))
    await sql.insert_into_pcs(user_db_id, product, summ)
    await sql.insert_into_bs(user_db_id, 'balance', balance)
    await state.clear()


@rt.message(Insert.insert_cost)
async def cost_error(message: types.Message):
    """answer if typed cost is not number"""

    await message.answer('Insert number like 100, 890.13\nOr click /cancel',
                         reply_markup=types.ReplyKeyboardRemove())
# end of group


# group of handlers for save, income, take
@rt.message(StateFilter(None), F.text.lower().in_(buttons_sti))
async def sti_handler(message: types.Message, state: FSMContext):
    """handle 'save', 'income', 'take' and start taking data for db"""

    table = message.text.lower()

    await state.update_data(table=table)
    await message.answer('Insert summ', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Insert.insert_sti)


@rt.message(Insert.insert_sti, F.text.replace('.', '').isdigit())
async def sti_handle_summ(message: types.Message, state: FSMContext):
    """handle summ of 'save', 'income', 'take'\n
    calculate balance and savings and then record\n
    name of change, summ of it, new balance and savings into db"""

    summ = abs(float(message.text))
    user = str(message.from_user.id)

    user_db_id = await sql.user_check(user)
    data = await state.get_data()
    table = data['table']
    balance = await sql.get_balance_savings(user_db_id, 'balance')
    savings = await sql.get_balance_savings(user_db_id, 'savings')
    new_bal_sav = await sql.calc_new_bs(table, balance, savings, summ)
    balance, savings = new_bal_sav

    builder = ReplyKeyboardBuilder()
    for button in buttons_start:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(3)

    await message.answer('Acknowledged', reply_markup=builder.as_markup(resize_keyboard=True))
    await sql.insert_into_sti(user_db_id, table, summ)
    await sql.insert_into_bs(user_db_id, 'balance', balance)
    await sql.insert_into_bs(user_db_id, 'savings', savings)
    await state.clear()


@rt.message(Insert.insert_sti)
async def sti_error(message: types.Message):
    """answer if typed summ is not number"""

    await message.answer('Insert number like 100, 890.13\nOr click /cancel',
                         reply_markup=types.ReplyKeyboardRemove())
# end of group
