import random

class DisasterEnvironment:
    def __init__(self):
        self.temperature = 25
        self.smoke_level = 0
        self.damage_severity = 0

    def update(self):
        """Simulate changes in the environment"""
        self.temperature += random.randint(-1, 3)
        self.smoke_level += random.randint(0, 2)
        self.damage_severity += random.randint(0, 1)

        # Cap values
        self.temperature = min(self.temperature, 100)
        self.smoke_level = min(self.smoke_level, 10)
        self.damage_severity = min(self.damage_severity, 5)

    def get_state(self):
        """Return current percepts"""
        return {
            "temperature": self.temperature,
            "smoke_level": self.smoke_level,
            "damage_severity": self.damage_severity
        }