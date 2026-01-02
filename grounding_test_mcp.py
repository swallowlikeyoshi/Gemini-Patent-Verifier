import asyncio
import os
import json
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv
from mcp_connector import get_kipris_connector

class GeminiDebugLogger:
    def __init__(self):
        self.steps = []
        self.gemini_api_call_count = 0
        self.kipris_api_call_count = 0
        self.start_time = datetime.now()
        self.total_tokens = None

    def log_api_call(self, role, content=None, function_calls=None):
        if role == "model":
            self.gemini_api_call_count += 1
        
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "function_calls": function_calls,
            "turn": self.gemini_api_call_count if role == "model" else 0
        }
        self.steps.append(entry)

    def log_tool_result(self, tool_name, result):
        self.kipris_api_call_count += 1
        self.steps.append({
            "role": "tool",
            "tool_name": tool_name,
            "result": result,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "turn": self.gemini_api_call_count
        })

    def set_usage(self, usage):
        self.total_tokens = usage

    def generate_report(self):
        report = [
            "# Gemini API Flow Debug Log",
            f"- **Date**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Total Gemini API Calls**: {self.gemini_api_call_count}",
        ]
        
        if self.total_tokens:
            report.append(f"- **Token Usage**: Prompt: {self.total_tokens.prompt_token_count}, Candidates: {self.total_tokens.candidates_token_count}, Total: {self.total_tokens.total_token_count}")
        
        report.append("\n## 💬 Communication Flow\n")
        
        for step in self.steps:
            role = step['role']
            time = step['timestamp']
            
            if role == "user":
                report.append(f"### 👤 User (Input) *[{time}]*")
                report.append(f"```text\n{step['content']}\n```\n")
            
            elif role == "model":
                turn_label = f" (Turn {step['turn']})" if step['turn'] > 0 else ""
                report.append(f"### 🤖 Gemini Response{turn_label} *[{time}]*")
                
                # Show text part if exists
                if step['content']:
                    report.append(f"**Thought/Draft**:\n\n{step['content']}\n")
                
                # Show function calls if exists
                if step['function_calls']:
                    report.append("#### 🛠️ Tool Usage (Function Calls)")
                    for fc in step['function_calls']:
                        args_json = json.dumps(fc.args, indent=2, ensure_ascii=False)
                        report.append(f"- **Tool**: `{fc.name}`")
                        report.append(f"- **Arguments**:\n```json\n  {args_json}\n```")
                report.append("---")

            elif role == "tool":
                report.append(f"### 📥 Tool Result (`{step['tool_name']}`) *[{time}]*")
                # Truncate very long tool results for readability
                res_str = str(step['result'])
                if len(res_str) > 2000:
                    res_str = res_str[:2000] + "... (truncated)"
                report.append(f"```json\n{res_str}\n```\n")

        return "\n".join(report)

    def save(self, folder="debug"):
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        filename = f"api_flow_{self.start_time.strftime('%Y%m%d_%H%M%S')}.md"
        path = os.path.join(folder, filename)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.generate_report())
        
        return path

# PROMPT_1 with patent grounding instructions
PROMPT_1 = """
1. 당신은 광고 신뢰성 분석의 전문가입니다. 사용자로부터 받은 광고의 스크립트를 분석하여 광고와 제품의 신뢰성을 평가합니다. 사용자는 유튜브 쇼츠에서 시청한 광고의 스크립트를 제공합니다. 평가한 결과를 사용자에게 전달해야 합니다.

2. 광고 신뢰성 분석을 통해 광고가 과장되었는지, 사실에 기반했는지, 또는 오해의 소지가 있는지를 평가합니다. 
광고에서 제품에 대한 특허를 언급하는 부분이 있다면, 제공된 'patent_search' 또는 'patent_keyword_search' 등 KIPRIS 관련 도구를 사용하여 해당 특허가 실제로 존재하는지 반드시 확인하세요. 
또한 일반적인 정보 확인을 위해 "Google 검색 그라운딩"도 함께 활용하세요.

3. 답변은 텍스트 형식으로 제공하세요.

4. 답변은 전문적이고 간결한 어조로 설명하세요. 답변은 사용자에게 전달됩니다. 온화한 어조를 유지하세요.

5. 사용자는 디지털 정보에 취약한 고령자, 또는 광고에 쉽게 현혹되는 일반 소비자, 또는 청소년일 수 있습니다. 이 점을 고려하여 답변을 작성하세요.

6. 광고 스크립트를 바탕으로 다음과 같은 답변 형식을 제공하세요.
 - 광고의 신뢰성을 범주화하여 제시하세요(위험, 안전, 주의).
 - 광고 스크립트의 문제점을 간략화해서 제시하세요.
 - KIPRIS 도구를 통해 확인한 특허 정보(존재 여부, 특허 번호, 출원인 등)를 상세히 제시하세요.
 - 검색 그라운딩으로 확인한 정보는 출처와 함께 제시하세요(링크 포함).

7. 이후 내용은 광고 스크립트입니다. 스크립트를 기반으로 위 지시사항에 따라 답변을 작성하세요.
"""

SCRIPT = "제발 키 키우려고 이상한 짓 좀 하지 마세요. 키 167 아빠인 제가 두 아들 180까지 키우고 조카들도 전부 180 이상으로 키우는 중인데 이것만 더 빨리 알았어도 우리 와이프도 덜 고생하고 아들들 키도 훨씬 더 많이 컸을 거예요. 지금 제가 다시 성장기인 두 아들을 키우는 시절로 돌아간다면 아이들의 성장판이 조금이라도 열려 있다면 무조건 이것부터 할 거예요. IGF1 직접 먹이기. 몸 말도 안 되는 소린가 싶으시죠? IGF1이 몸 안에 많을수록 키가 쭉쭉 크는 건 부모라면 다들 알고 계실 테고 조금 늘리겠다고 연간 2천만 원짜리 성장 주사도 고민해 보셨을 테니까요. 그때 그걸 먹인다니 네. 이제 무조건 먹이셔야 큽니다. IGF1는 단백질이라 먹자마자 위에서 분해가 되기에 성장판까지 닿지 못해서 성장 주사를 무릎에 꽂는 방법밖에 없었지만 이젠 유럽 특허 기술로 IGF1을 먹는게 가능해졌어요. 더 대박인 건요. 주사로 인위로 늘리는게 아닌 성장기 권장량에 맞게 뼈밀도에 천천히 작용되다 보니 키가 그냥 클뿐 아니라 안전하게 180도 가능해요. 이미 유럽에선 천연 성장 주사로 검증돼서 엄청나게 먹이고 있는데 조만간 한국에서도 엄청나게 먹이실 것 같아서 미리 주의를 주자면 이게 성장 주사만큼 효과는 엄청난데 부작용은 없고 접근성은 너무 좋아졌다 보니 이미 키 큰 아이들에게도 욕심으로 막 먹이고 싶으실 거예요. 절대 그러지 마세요. 이미 키가 작은 아이들도 너무 잘 크니까 이미 IGF1이 많은 키큰 아이들한테 과성장을 유도할 수 있거든요. 저희 아이들에겐. 국내 유일하게 식약처 인증받은 먹는 성장인자 IGF업을 먹여 왔었는데 IGF업 말고도 유럽 제품을 직구해서 드시는 것도 좋아요. 혹시 아이 키 때문에 고민인 분들은 성장 주사 말고 이거부터 6개월 정도 꾸준히 먹여 보세요. 차원이 다르게 클 겁니다."

async def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    client = genai.Client(api_key=api_key)

    # 1. Start KIPRIS MCP Connector
    connector = await get_kipris_connector()
    kipris_tools = await connector.get_gemini_tools()

    # 2. Add Google Search grounding tool
    google_search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # 3. Combine tools
    # Removed Google Search tool because it conflicts with custom function calling (error 400)
    config = types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=kipris_tools)]
    )

    full_prompt = f"{PROMPT_1}\n\n[광고 스크립트]:\n{SCRIPT}"
    history = [types.Content(role="user", parts=[types.Part(text=full_prompt)])]
    
    print("\nStart history: ", history, '\n')

    # Init Logger
    logger = GeminiDebugLogger()
    logger.log_api_call("user", full_prompt)

    print("Gemini에게 요청을 보내는 중(KIPRIS 특허 검색 도구 포함)...")
    
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=history,
            config=config
        )
        
        # Log first model response (could be text or tool call)
        res_text = response.text if response.candidates[0].content.parts and any(p.text for p in response.candidates[0].content.parts) else "[Tool Call Only]"
        logger.log_api_call("model", res_text, 
                           function_calls=[p.function_call for p in response.candidates[0].content.parts if p.function_call])

        current_response = response
        max_turns = 10
        turn_count = 0
        total_usage = response.usage_metadata

        while turn_count < max_turns and current_response.candidates[0].content.parts and any(p.function_call for p in current_response.candidates[0].content.parts):
            turn_count += 1
            # Add model's response (containing function calls) to history
            history.append(current_response.candidates[0].content)
            
            tool_parts = []
            for part in current_response.candidates[0].content.parts:
                if part.function_call:
                    name = part.function_call.name
                    args = part.function_call.args
                    print(f"로그: 도구 호출 중 - {name}({args})")
                    
                    # Execute MCP tool
                    result = await connector.call_tool(name, args)
                    
                    # Extract text content from result
                    content_text = ""
                    if hasattr(result, 'content') and isinstance(result.content, list):
                        content_text = "\n".join([c.text for c in result.content if hasattr(c, 'text')])
                    else:
                        content_text = str(result)

                    # Log Tool Result
                    logger.log_tool_result(name, content_text)

                    # Format result for Gemini
                    tool_parts.append(types.Part.from_function_response(
                        name=name,
                        response={"result": content_text}
                    ))
            
            if tool_parts:
                # Add tool responses to history with 'tool' role
                history.append(types.Content(role="tool", parts=tool_parts))
                
                # Continue generating based on accumulated history
                current_response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=history,
                    config=config
                )
                
                # IMPORTANT: Accumulate Usage
                if current_response.usage_metadata:
                    total_usage.prompt_token_count += current_response.usage_metadata.prompt_token_count
                    total_usage.candidates_token_count += current_response.usage_metadata.candidates_token_count
                    total_usage.total_token_count += current_response.usage_metadata.total_token_count

                # IMPORTANT: Log EVERY response from Gemini inside the loop
                inner_text = current_response.text if current_response.candidates[0].content.parts and any(p.text for p in current_response.candidates[0].content.parts) else "[Tool Call Only]"
                logger.log_api_call("model", inner_text,
                                   function_calls=[p.function_call for p in current_response.candidates[0].content.parts if p.function_call])
            else:
                break
        
        if turn_count >= max_turns:
            print(f"경고: 최대 도구 호출 횟수({max_turns})에 도달하여 루프를 종료합니다.")

        final_text = current_response.text if current_response.candidates[0].content.parts and any(p.text for p in current_response.candidates[0].content.parts) else "분석 결과를 생성하지 못했습니다."
        print("\n[최종 분석 결과]\n")
        print(final_text)

        # Citation handling
        text_with_citations = add_citations(current_response)
        
        # Finalize Usage and Log
        logger.set_usage(total_usage)
        debug_path = logger.save()
        print(f"\n[Debug] 상세 API 호출 흐름이 저장되었습니다: {debug_path}")

        save_response_to_file(current_response.usage_metadata, PROMPT_1, text_with_citations)

    finally:
        await connector.disconnect()
        print("로그: MCP 커넥터가 종료되었습니다.")


def add_citations(response):
    text = response.text
    if not response.candidates[0].grounding_metadata:
        return text
    
    metadata = response.candidates[0].grounding_metadata
    if not hasattr(metadata, 'grounding_supports') or not metadata.grounding_supports:
        return text

    supports = metadata.grounding_supports
    chunks = metadata.grounding_chunks

    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if support.grounding_chunk_indices:
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")
            citation_string = ", ".join(citation_links)
            text = text[:end_index] + " " + citation_string + text[end_index:]

    return text

def save_response_to_file(token_usage, prompt_text, response_text, folder_path="responses"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    existing_files = os.listdir(folder_path)
    file_count = len(existing_files)
    new_file_name = f"{file_count + 1}.md"
    new_file_path = os.path.join(folder_path, new_file_name)
    text = f"TokensUsage:\n{token_usage}\n\nPrompt:\n{prompt_text}\n\nResponse:\n{response_text}"
    with open(new_file_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Response saved to {new_file_path}")

if __name__ == "__main__":
    print("Start main")
    asyncio.run(main())
