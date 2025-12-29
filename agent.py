#!/usr/bin/env python3
import asyncio
from claude_agent_sdk import (
    query, ClaudeAgentOptions, AssistantMessage, ResultMessage,
    TextBlock, ToolUseBlock, ToolResultBlock, ThinkingBlock,
    CLINotFoundError, ProcessError, ClaudeSDKError
)

async def main():
    try:
        # Agentic loop: streams messages as Claude works
        async for message in query(
            prompt="Read todo.md and select the first incomplete item. Prompt the user if they want to complete this task or to skip it. If they want to skip it, select the next item and prompt the user. Once a todo item is selected, can you generate a Prompt for Claude code to complete.",
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Edit", "Glob"],  # Tools Claude can use
                permission_mode="acceptEdits"            # Auto-approve file edits
            )
        ):
            # Print human-readable output
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                    elif isinstance(block, ToolUseBlock):
                        print(f"Tool: {block.name}")
                    elif isinstance(block, ToolResultBlock):
                        if block.is_error:
                            print(f"Tool Error: {block.content}")
                        else:
                            print(f"Tool Result: {block.content}")
                    elif isinstance(block, ThinkingBlock):
                        print(f"Thinking: {block.thinking}")
            elif isinstance(message, ResultMessage):
                print(f"Done: {message.subtype}")

    except CLINotFoundError:
        print("Error: Claude Code CLI not installed")
    except ProcessError as e:
        print(f"Tool execution failed with exit code: {e.exit_code}")
    except ClaudeSDKError as e:
        print(f"SDK error: {e}")

if __name__ == "__main__":
    asyncio.run(main())