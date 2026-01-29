import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message


class ListenerBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            print(f"[{self.agent.jid}] received: {msg.body}")

            # Prevent infinite ping-pong
            if msg.body == "Pong!":
                return

            reply = Message(to=str(msg.sender))
            reply.body = "Pong!"
            await self.send(reply)


class SendOnceBehaviour(OneShotBehaviour):
    async def run(self):
        msg = Message(to="agent2@localhost")
        msg.body = "Hello from Agent1"
        await self.send(msg)
        print("[agent1] sent message")


class SimpleAgent(Agent):
    async def setup(self):
        print(f"[{self.jid}] started")
        self.add_behaviour(ListenerBehaviour())


async def main():
    agent1 = SimpleAgent("agent1@localhost", None)
    agent2 = SimpleAgent("agent2@localhost", None)

    await agent1.start()
    await agent2.start()

    agent1.presence.set_available()
    agent2.presence.set_available()

    await asyncio.sleep(5)

    agent1.add_behaviour(SendOnceBehaviour())

    await asyncio.sleep(15)

    await agent1.stop()
    await agent2.stop()


if __name__ == "__main__":
    asyncio.run(main())