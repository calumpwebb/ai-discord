import asyncio


async def typing_loop(channel, interval: float = 5.0):
    """Continuously sends typing indicator until cancelled"""
    try:
        while True:
            await channel.typing()
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        raise
