import datetime

from aiogram import types, Router
from aiogram.filters import StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import sql_for_bot as sql
from states import Insert


rt = Router()
MESSAGE_MAX_LENGTH = 4096

buttons_start = ('purchase', 'balance', 'savings', 'save', 'income', 'take', 'statistics')
buttons_bs = ('balance', 'savings')
buttons_stat = ('top of purchases', 'list of purchases', 'balance per day')
buttons_stat_per = ('this month', 'previous month', 'all period')


@rt.message(F.text.lower().in_(buttons_bs))
async def bal_sav_handler(message: types.Message):
    """handle messages 'balance' and 'savings'\n
    and return balance or savings of this user from db"""

    user = str(message.from_user.id)
    user_db_id = await sql.user_check(user)
    table = message.text
    summ = await sql.get_balance_savings(user_db_id, table)
    mess = f'{table.capitalize()}: {round(summ, 2)}'

    builder = ReplyKeyboardBuilder()
    for button in buttons_start:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(3)

    await message.answer(mess, reply_markup=builder.as_markup(resize_keyboard=True))


# group of handlers for statistics
@rt.message(StateFilter(None), F.text.lower() == 'statistics')
async def stats_handler(message: types.Message, state: FSMContext):
    """start command that returns statistics about purchases and balance"""

    user = str(message.from_user.id)
    user_db_id = await sql.user_check(user)

    builder = ReplyKeyboardBuilder()
    for button in buttons_stat:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(2)

    await state.update_data(user_id=user_db_id)
    await message.answer('Type', reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Insert.insert_stat)


@rt.message(Insert.insert_stat, F.text.lower().in_(buttons_stat))
async def stats_handler_next(message: types.Message, state: FSMContext):
    """deciding what type of stats user needs"""

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='This month'))
    builder.add(types.KeyboardButton(text='Previous month'))
    if message.text.lower() == 'top of purchases':
        builder.add(types.KeyboardButton(text='All period'))
    builder.adjust(2)

    await state.update_data(stat=message.text.lower())
    await message.answer('Period', reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Insert.insert_stat_next)


@rt.message(Insert.insert_stat)
async def stats_error_type(message: types.Message):
    """show answer if user wrong with buttons"""

    builder = ReplyKeyboardBuilder()
    for button in buttons_stat:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(2)

    await message.answer('Use buttons, please\nOr click /cancel',
                         reply_markup=builder.as_markup(resize_keyboard=True))


@rt.message(Insert.insert_stat_next, F.text.lower().in_(buttons_stat_per))
async def stats_period(message: types.Message, state: FSMContext):
    """deciding what period user needs"""

    period = message.text.lower()
    date1 = str()
    date2 = str()

    if period == 'this month':
        today = datetime.date.today()
        date1 = today.strftime('%Y-%m-01')
        date2 = today.strftime('%Y-%m-31')
    elif period == 'previous month':
        today = datetime.date.today()
        first = today.replace(day=1)
        last = first - datetime.timedelta(days=1)
        date1 = last.strftime('%Y-%m-01')
        date2 = last.strftime('%Y-%m-31')
    elif period == 'all period':
        date1 = '1970-01-01'
        date2 = '2050-12-31'

    data = await state.get_data()
    user = int(data['user_id'])

    records = tuple()
    result = str()

    if data['stat'].lower() == 'top of purchases':
        records = await sql.top_purchases(user, date1, date2, 10)
        for record in records:
            # 0 - product, 1 - sum of it
            result += f'{record[0]} {record[1]}\n'

    elif data['stat'].lower() == 'list of purchases':
        records = await sql.purchases_period(user, date1, date2)
        for record in records:
            # 0 - date, 1 - product, 2 - cost of it
            result += f'{record[0]} {record[1]} {record[2]}\n'

    elif data['stat'].lower() == 'balance per day':
        records = await sql.balance_savings_period(user, 'balance', date1, date2)
        for record in records:
            # 0 - date, 1 - balance at this date
            result += f'{record[0]} {record[1]}\n'

    if not result:
        result = 'No records at this period'

    builder = ReplyKeyboardBuilder()
    for button in buttons_start:
        builder.add(types.KeyboardButton(text=button.capitalize()))
    builder.adjust(3)

    # message could be too long for telegram so there is calculating parts of so long message
    if len(result) >= MESSAGE_MAX_LENGTH:
        count = len(result) // MESSAGE_MAX_LENGTH + 1
        first = 0
        last = MESSAGE_MAX_LENGTH
        for i in range(count):
            await message.answer(result[first:last], reply_markup=builder.as_markup(resize_keyboard=True))
            first = last
            last = last + MESSAGE_MAX_LENGTH
    else:
        await message.answer(result, reply_markup=builder.as_markup(resize_keyboard=True))

    await state.clear()


@rt.message(Insert.insert_stat_next)
async def stats_error_period(message: types.Message, state: FSMContext):
    """show answer if user wrong with buttons"""

    data = await state.get_data()
    stat = data['stat']
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='This month'))
    builder.add(types.KeyboardButton(text='Previous month'))
    if stat.lower() == 'top of purchases':
        builder.add(types.KeyboardButton(text='All period'))
    builder.adjust(2)

    await message.answer('Use buttons, please\nOr click /cancel',
                         reply_markup=builder.as_markup(resize_keyboard=True))
