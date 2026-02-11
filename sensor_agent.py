import asyncio
import json
from datetime import datetime

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from environment import DisasterEnvironment


class SensorSendBehaviour(CyclicBehaviour):
    """
    Periodically senses the environment and INFORMs the ResponseAgent.
    """
    async def run(self):
        # Update the simulated world and read percepts
        self.agent.environment.update()
        percepts = self.agent.environment.get_state()

        # Build an ACL message (INFORM)
        msg = Message(to="response@localhost")
        msg.set_metadata("performative", "inform")  # FIPA-ACL performative
        msg.set_metadata("ontology", "disaster-monitoring")
        msg.set_metadata("language", "json")
        msg.body = json.dumps(percepts)  # safer than str(percepts)

        # Send
        await self.send(msg)

        # Message log (deliverable)
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [SensorAgent] SENT (INFORM)")
        print("  To:", msg.to)
        print("  Body:", percepts)

        # Sleep based on current sampling interval (can change via REQUEST)
        await asyncio.sleep(self.agent.sampling_interval)


class SensorReceiveBehaviour(CyclicBehaviour):
    """
    Receives REQUEST messages from ResponseAgent and triggers actions.
    Example actions:
      - change_sampling: adjust how often we sense/send
      - request_snapshot: send one immediate reading
    """
    async def run(self):
        msg = await self.receive(timeout=2)
        if not msg:
            return

        performative = msg.get_metadata("performative")

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [SensorAgent] RECEIVED ({performative.upper()})")
        print("  From:", msg.sender)
        print("  Raw Body:", msg.body)

        # Only handle REQUEST in this lab task
        if performative != "request":
            print("  -> Ignored (not a REQUEST)")
            return

        # Parse request body as JSON
        try:
            data = json.loads(msg.body)
        except json.JSONDecodeError:
            print("  -> Bad REQUEST format (expected JSON)")
            return

        action = data.get("action")

        # Trigger actions based on REQUEST content
        if action == "change_sampling":
            new_interval = data.get("interval", self.agent.sampling_interval)

            # Validate interval
            if isinstance(new_interval, (int, float)) and new_interval > 0:
                self.agent.sampling_interval = float(new_interval)
                print(f"  -> Sampling interval updated to {self.agent.sampling_interval}s")

                # OPTIONAL: inform the ResponseAgent that we accepted the request
                ack = Message(to="response@localhost")
                ack.set_metadata("performative", "inform")
                ack.set_metadata("language", "json")
                ack.body = json.dumps({
                    "status": "ok",
                    "info": f"Sampling interval set to {self.agent.sampling_interval}s"
                })
                await self.send(ack)
            else:
                print("  -> Invalid interval value")

        elif action == "request_snapshot":
            # Send one immediate reading
            self.agent.environment.update()
            percepts = self.agent.environment.get_state()

            snapshot = Message(to="response@localhost")
            snapshot.set_metadata("performative", "inform")
            snapshot.set_metadata("ontology", "disaster-monitoring")
            snapshot.set_metadata("language", "json")
            snapshot.body = json.dumps(percepts)
            await self.send(snapshot)

            print("  -> Snapshot sent immediately:", percepts)

        else:
            print("  -> Unknown action requested:", action)


class SensorAgent(Agent):
    async def setup(self):
        print(f"[{self.jid}] SensorAgent started")

        # Environment + default sampling interval
        self.environment = DisasterEnvironment()
        self.sampling_interval = 5  # seconds (ResponseAgent can REQUEST to change this)

        # Add both behaviours
        self.add_behaviour(SensorSendBehaviour())
        self.add_behaviour(SensorReceiveBehaviour())
