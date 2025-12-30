import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

server = Server("mock-kipris")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="patent_free_search",
            description="patent search by keyword, this tool is for korean patent search",
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {"type": "string", "description": "search keyword"},
                },
                "required": ["word"],
            },
        ),
        types.Tool(
            name="patent_search",
            description="patent search by application number, this tool is for korean patent search",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_number": {"type": "string", "description": "application number"},
                },
                "required": ["application_number"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if name == "patent_free_search":
        word = arguments.get("word", "")
        if "IGF1" in word or "성장" in word:
            return [
                types.TextContent(
                    type="text",
                    text="[검색 결과]\n1. 출원번호: 1020250001234\n발명의 명칭: 성장인자 IGF1을 포함하는 경구용 조성물 및 이의 제조 방법\n출원인: 유럽성장연구소\n상태: 등록\n요약: 본 발명은 IGF1 단백질의 체내 흡수율을 높인 경구용 조성물에 관한 것으로..."
                )
            ]
        else:
            return [types.TextContent(type="text", text="검색 결과가 없습니다.")]
            
    elif name == "patent_search":
        app_num = arguments.get("application_number", "")
        if "1020250001234" in app_num:
            return [
                types.TextContent(
                    type="text",
                    text="상세 정보: [1020250001234]\n명칭: IGF1 경구 투여 기술\n권리자: 유럽성장연구소\n등록일자: 2024-12-01\n법적 상태: 유효"
                )
            ]
        else:
            return [types.TextContent(type="text", text="해당 번호의 특허를 찾을 수 없습니다.")]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mock-kipris",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
