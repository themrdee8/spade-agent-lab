import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import ast

class ResponseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            percepts = ast.literal_eval(msg.body)
            print("[ResponseAgent] Received:", percepts)

            temperature = percepts["temperature"]
            smoke = percepts["smoke_level"]
            damage = percepts["damage_severity"]

            # FSM Logic
            if damage >= 4:
                self.agent.state = "RESCUE"
            elif temperature > 50 or smoke > 5:
                self.agent.state = "FIRE_RESPONSE"
            else:
                self.agent.state = "IDLE"

            print(f"[ResponseAgent] Current State: {self.agent.state}")

            # State Actions
            if self.agent.state == "RESCUE":
                print("Deploying rescue teams...")
            elif self.agent.state == "FIRE_RESPONSE":
                print("Dispatching fire response units...")
            else:
                print("Monitoring environment...")


class ResponseAgent(Agent):
    async def setup(self):
        print(f"[{self.jid}] ResponseAgent started")
        self.state = "IDLE"
        self.add_behaviour(ResponseBehaviour())
