from aiogram.fsm.state import State, StatesGroup

class ChannelStates(StatesGroup):
    adding: State = State()
    change: State = State()
    