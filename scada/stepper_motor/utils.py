import json
from json import JSONDecodeError
from django.conf import settings
import os


class StateManager:
    previous_state = {}

    def load_state():
        filepath = os.path.join(settings.BASE_DIR, "Extras", "StepperMotor", "data.json")
        state = {}

        with open(filepath) as file:
            try:
                state = json.load(file)
                StateManager.previous_state = state
            except JSONDecodeError:
                state = StateManager.previous_state

        return state
