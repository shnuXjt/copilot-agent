from core.brain.specialists.chat_specialist import ChatSpecialist
from core.brain.specialists.excel_specialist import ExcelSpecialist
from core.brain.specialists.search_specialist import SearchSpecialist


class SpecialistRouter:
    def __init__(self):
        self.specialists = {
            "search": SearchSpecialist(),
            "excel": ExcelSpecialist(),
            "chat": ChatSpecialist()
        }


    def route(self, skill_type: str):
        return self.specialists.get(skill_type, ChatSpecialist())

router = SpecialistRouter()