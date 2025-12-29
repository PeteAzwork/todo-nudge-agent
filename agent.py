#!/usr/bin/env python3
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ResultMessage,
    TextBlock, ToolUseBlock, ToolResultBlock, ThinkingBlock,
    CLINotFoundError, ProcessError, ClaudeSDKError
)

INITIAL_PROMPT = (
    "Read todo.md and select the first incomplete item. "
    "Prompt the user if they want to complete this task or to skip it. "
    "If they want to skip it, select the next item and prompt the user. "
    "Once a todo item is selected, generate a prompt for Claude Code to complete it."
)

def print_message(message):
    """Print human-readable output from agent messages."""
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
            elif isinstance(block, ToolUseBlock):
                print(f"[Tool: {block.name}]")
            elif isinstance(block, ToolResultBlock):
                if block.is_error:
                    print(f"[Tool Error: {block.content}]")
            elif isinstance(block, ThinkingBlock):
                print(f"[Thinking: {block.thinking[:100]}...]")

async def main():
    try:
        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits"
        )

        async with ClaudeSDKClient(options=options) as client:
            # Start with initial prompt
            await client.query(INITIAL_PROMPT)

            while True:
                # Process messages until agent completes this turn
                async for message in client.receive_response():
                    print_message(message)

                    if isinstance(message, ResultMessage):
                        if message.subtype == 'error':
                            print(f"Error: {message.result}")
                            return
                        break

                # Wait for user input
                print()
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    break

                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                # Send user response to agent
                await client.query(user_input)

    except CLINotFoundError:
        print("Error: Claude Code CLI not installed")
    except ProcessError as e:
        print(f"Tool execution failed with exit code: {e.exit_code}")
    except ClaudeSDKError as e:
        print(f"SDK error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
