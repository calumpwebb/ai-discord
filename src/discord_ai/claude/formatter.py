from discord_ai.models import AssistantMessage, TextContent, ToolUseContent, UserMessage


class EventFormatter:
    """Formats Claude events for Discord messages"""

    def format_event(self, event) -> list[str]:
        """Returns list of Discord message strings for this event"""

        if isinstance(event, AssistantMessage):
            return self._format_assistant_message(event)
        elif isinstance(event, UserMessage):
            return self._format_user_message(event)
        else:
            return []

    def _format_assistant_message(self, event: AssistantMessage) -> list[str]:
        messages = []

        for block in event.content_blocks:
            if isinstance(block, TextContent):
                messages.append(block.text)
            elif isinstance(block, ToolUseContent):
                tool_msg = f"Tool: {block.name}"
                if block.input:
                    args = ", ".join(f"{k}={v}" for k, v in block.input.items())
                    tool_msg += f" ({args})"
                messages.append(tool_msg)

        return messages

    def _format_user_message(self, event: UserMessage) -> list[str]:
        if not event.tool_use_result:
            return []

        result = event.tool_use_result
        if isinstance(result, dict):
            content = result.get("stdout", "") or str(result)
        else:
            content = str(result)

        return [f"||{content}||"]
