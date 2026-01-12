import asyncio

import pytest

from discord_ai.utils.typing import typing_loop


class FakeChannel:
    def __init__(self):
        self.typing_count = 0

    async def trigger_typing(self):
        self.typing_count += 1

    async def typing(self):
        await self.trigger_typing()


@pytest.mark.asyncio
async def test_typing_loop_sends_typing_indicator():
    channel = FakeChannel()

    task = asyncio.create_task(typing_loop(channel, interval=0.1))
    await asyncio.sleep(0.25)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    assert channel.typing_count >= 2


@pytest.mark.asyncio
async def test_typing_loop_stops_on_cancel():
    channel = FakeChannel()

    task = asyncio.create_task(typing_loop(channel, interval=0.1))
    await asyncio.sleep(0.05)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    initial_count = channel.typing_count
    await asyncio.sleep(0.2)

    assert channel.typing_count == initial_count
