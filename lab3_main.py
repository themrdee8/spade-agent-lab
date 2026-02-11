import asyncio
from sensor_agent import SensorAgent
from response_agent import ResponseAgent

async def main():
    sensor = SensorAgent("sensor@localhost", None)
    response = ResponseAgent("response@localhost", None)

    await sensor.start()
    await response.start()

    sensor.presence.set_available()
    response.presence.set_available()

    await asyncio.sleep(40)

    await sensor.stop()
    await response.stop()

if __name__ == "__main__":
    asyncio.run(main())
