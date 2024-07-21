from aiogram.fsm.state import StatesGroup, State


class Insert(StatesGroup):
    """just class for taking data from user\n
    step by step and not full at once"""

    insert_purch = State()
    insert_cost = State()
    insert_sti = State()
    insert_stat = State()
    insert_stat_next = State()