import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from environment import DisasterEnvironment
from event_logger import log_event

class SensorBehaviour(CyclicBehaviour):
    async def run(self):
        self.agent.environment.update()
        percepts = self.agent.environment.get_state()

        log_event(percepts)

        # Simple reactions
        if percepts["temperature"] > 50:
            print("[SensorAgent] High temperature detected!")

        if percepts["smoke_level"] > 5:
            print("[SensorAgent] Dangerous smoke levels!")

        if percepts["damage_severity"] >= 4:
            print("[SensorAgent] Severe structural damage!")

        await asyncio.sleep(5)


class SensorAgent(Agent):
    async def setup(self):
        print(f"[{self.jid}] SensorAgent started")
        self.environment = DisasterEnvironment()
        self.add_behaviour(SensorBehaviour())


async def main():
    agent = SensorAgent("sensor@localhost", None)
    await agent.start()
    agent.presence.set_available()

    await asyncio.sleep(30)

    await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())