import asyncio


async def typing_loop(channel, interval: int = 5):
    """Continuously sends typing indicator until cancelled"""
    try:
        while True:
            await channel.trigger_typing()
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        raise
