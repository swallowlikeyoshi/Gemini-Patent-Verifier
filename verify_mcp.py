import asyncio
from mcp_connector import get_kipris_connector

async def verify():
    try:
        connector = await get_kipris_connector()
        tools = await connector.get_gemini_tools()
        print("\nAvailable tools for Gemini:\n")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        await connector.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
