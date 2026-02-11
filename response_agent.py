import json
from datetime import datetime

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message


class ResponseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return

        performative = msg.get_metadata("performative")

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [ResponseAgent] RECEIVED ({performative.upper()})")
        print("  From:", msg.sender)
        print("  Raw Body:", msg.body)

        # We expect INFORM percepts (Lab requirement)
        if performative != "inform":
            print("  -> Ignored (not an INFORM)")
            return

        # Parse percepts
        try:
            percepts = json.loads(msg.body)
        except json.JSONDecodeError:
            print("  -> Bad INFORM format (expected JSON)")
            return

        print("  Parsed Percepts:", percepts)

        # Extract values
        temperature = percepts.get("temperature", 0)
        smoke = percepts.get("smoke_level", 0)
        damage = percepts.get("damage_severity", 0)

        # FSM logic (same as Lab 3, just cleaner)
        if damage >= 4:
            self.agent.state = "RESCUE"
        elif temperature > 50 or smoke > 5:
            self.agent.state = "FIRE_RESPONSE"
        else:
            self.agent.state = "IDLE"

        print(f"  -> FSM State: {self.agent.state}")

        # State actions (triggered by message content)
        if self.agent.state == "RESCUE":
            print("  ACTION: Deploying rescue teams...")
        elif self.agent.state == "FIRE_RESPONSE":
            print("  ACTION: Dispatching fire response units...")
        else:
            print("  ACTION: Monitoring environment...")

        # ---- ACL MESSAGE EXCHANGE BACK (INFORM) ----
        # Inform sensor what state we are in (shows two-way INFORM exchange)
        state_msg = Message(to="sensor@localhost")
        state_msg.set_metadata("performative", "inform")
        state_msg.set_metadata("language", "json")
        state_msg.body = json.dumps({
            "state": self.agent.state,
            "note": "Current response state based on latest percepts"
        })
        await self.send(state_msg)

        print(f"  SENT (INFORM) -> SensorAgent | state={self.agent.state}")

        # ---- REQUEST (trigger sensor action) ----
        # If dangerous, request faster sampling + request snapshot
        if self.agent.state in ["RESCUE", "FIRE_RESPONSE"]:
            # 1) Request faster sampling (e.g., every 2 seconds)
            req_sampling = Message(to="sensor@localhost")
            req_sampling.set_metadata("performative", "request")
            req_sampling.set_metadata("language", "json")
            req_sampling.body = json.dumps({
                "action": "change_sampling",
                "interval": 2
            })
            await self.send(req_sampling)
            print("  SENT (REQUEST) -> change_sampling to 2s")

            # 2) Request an immediate snapshot
            req_snapshot = Message(to="sensor@localhost")
            req_snapshot.set_metadata("performative", "request")
            req_snapshot.set_metadata("language", "json")
            req_snapshot.body = json.dumps({
                "action": "request_snapshot"
            })
            await self.send(req_snapshot)
            print("  SENT (REQUEST) -> request_snapshot")


class ResponseAgent(Agent):
    async def setup(self):
        print(f"[{self.jid}] ResponseAgent started")
        self.state = "IDLE"
        self.add_behaviour(ResponseBehaviour())
