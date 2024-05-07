import json
from json import JSONDecodeError
from django.conf import settings
import os


class StateManager:
    previous_state = {}
    previous_detect = {}

    def load_state():
        filepath = os.path.join(settings.BASE_DIR, "Extras", "MiniFactory", "data.json")
        state = {}
        detect = {}

        with open(filepath) as file:
            try:
                state = json.load(file)

                detect.update({'Detected Blue': state.pop('Detected Blue')})
                detect.update({'Detected Red': state.pop('Detected Red')})
                detect.update({'Detected White': state.pop('Detected White')})

                StateManager.previous_state = state
                StateManager.previous_detect = detect
            except JSONDecodeError:
                state = StateManager.previous_state
                detect = StateManager.previous_detect

        return state, detect
