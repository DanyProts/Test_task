from aiogram.fsm.state import State, StatesGroup

class ChannelStates(StatesGroup):
    adding: State = State()
    removing: State = State()