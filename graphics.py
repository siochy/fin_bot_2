import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

import sql_for_bot as sql


async def daily_graph(user: int, user_tg_id: str) -> None:
    """create graphic plot that shows daily purchases"""

    x = list()
    y = list()
    data = await sql.daily_sum(user, 'purchases')
    for i in data:
        x.append(i[0])  # date
        y.append(i[1])  # sum

    fig, ax = plt.subplots(figsize=(8.54, 4.8))
    plt.title('Spent Per Day')
    plt.plot(x, y)

    # dates could too many be so need to show only months
    months = mdates.MonthLocator()
    days = mdates.DayLocator()
    form = mdates.DateFormatter('%Y-%m')
    
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(form)
    ax.xaxis.set_minor_locator(days)

    # create user's folder if it doesn't exist
    try:
        os.mkdir(f'media/{user_tg_id}')
    except FileExistsError:
        pass

    file_name = f'{user_tg_id}/daily.jpeg'
    plt.savefig(f'media/{file_name}')
    plt.cla()


async def top_purchases_graph(user: int, user_tg_id: str, date1: str, date2: str) -> None:
    """create graphic bar that shows top of purchases based on sum for every purchase"""

    x = list()
    y = list()
    data = await sql.top_purchases(user, date1, date2, 30)
    for i in data:
        x.append(i[0][0:7])  # product
        y.append(i[1])  # sum

    plt.figure(figsize=(8.54, 7))
    plt.xticks(rotation=90)
    plt.title('Top Purchases')
    plt.bar(x, y)

    # create user's folder if it doesn't exist
    try:
        os.mkdir(f'media/{user_tg_id}')
    except FileExistsError:
        pass

    file_name = f'{user_tg_id}/top.jpeg'
    plt.savefig(f'media/{file_name}')
    plt.cla()


async def monthly_inc_sav_graph(user: int, user_tg_id: str) -> None:
    """create graphic double bar with income and savings per month"""

    x1 = list()
    x2 = list()
    y1 = list()
    y2 = list()

    data_income = dict(await sql.monthly_sum(user, 'income'))
    data_take = dict(await sql.monthly_sum(user, 'take'))
    data_save = dict(await sql.monthly_sum(user, 'save'))

    diff1 = set(data_income) ^ set(data_save)
    diff2 = set(data_save) ^ set(data_take)
    diff = tuple(diff1 | diff2)

    for i in diff:
        if i not in tuple(data_take):
            data_take[i] = 0
        if i not in tuple(data_income):
            data_income[i] = 0
        if i not in tuple(data_save):
            data_save[i] = 0

    for j in data_income:
        x1.append(j)
        y1.append(data_income[j])

    subtract = list()
    for k in data_save:
        s = data_save[k] - data_take[k]
        subtract.append((k, s))

    for f in subtract:
        x2.append(f[0])
        y2.append(f[1])

    plt.figure(figsize=(8.54, 7))
    plt.title('Income and Savings per Month')
    plt.bar(x1, y1, width=0.4, align='edge')
    plt.bar(x2, y2, width=-0.4, align='edge')
    plt.legend(('Income', 'Savings'))

    # create user's folder if it doesn't exist
    try:
        os.mkdir(f'media/{user_tg_id}')
    except FileExistsError:
        pass

    file_name = f'{user_tg_id}/income_save.jpeg'
    plt.savefig(f'media/{file_name}')
    plt.cla()
