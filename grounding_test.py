from google import genai
from google.genai import types

from dotenv import load_dotenv
import os

def main(prompt_text=PROMPT_1):
    
    load_dotenv()

    client = genai.Client(api_key=os.getenv("API_KEY"))

    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt_text,
        config=config
    )

    print(response.text)

    # Assuming response with grounding metadata
    text_with_citations = add_citations(response)
    print(text_with_citations)

    save_response_to_file(response.usage_metadata, PROMPT_1, text_with_citations)

    return


SCRIPT = "제발 키 키우려고 이상한 짓 좀 하지 마세요. 키 167 아빠인 제가 두 와드 180까지 키우고 조카들도 전부 180 이상으로 키우는 중인데 이것만 더 빨리 알았어도 우리 와이프도 덜 고생하고 아들들 키도 훨씬 더 많이 컸을 거예요. 지금 지금 제가 다시 성장기인 두 아들을 키우는 시절로 돌아간다면 아이들의 성장판이 조금이라도 열려 있다면 무조건 이것부터 할 거예요. IGF1 직접 먹이기. 몸 말도 안 되는 소린가 싶으시죠? IGF1이 몸 안에 많을수록 키가 쭉쭉 크는 건 부모라면 다들 알고 계실 테고 조금 늘리겠다고 연애 2천만 원짜리 성장 주사도 고민해 보셨을 테니까요. 그때 그걸 먹인다니 네. 이제 무조건 먹이셔야 큽니다. IGF1는 단백질이라 먹자마자 위에서 분해가 되기에 섬장판까지 다르지 못해서 선장 주사를 무릎에 꽂는 방법밖에 없었지만 이젠 유럽 특허 기술로 IGF의 후원을 먹는게 가능해졌어요. 더 대박인 건요. 주사로 인위로 늘리는게 아닌 성장기 권장량에 맞게 뼈밀도에 천천히 작용되다 보니 키가 그냥 클뿐 아니라 안전하게 180도 가능해요. 이미 유럽에선 천연 성장 주사로 검중돼서 엄청나게 먹이고 있는데 조만간 한국에서도 엄청나게 먹이실 것 같아서 미리 주의를 주자면 이게 성장 주사만큼 효과는 엄청난데 부작용은 없고 접근성은 너무 좋아졌다 보니 이미 키 큰 아이들에게도 욕심으로 막 먹이고 싶으실 거예요. 절대 그러지 마세요. 이미 키가 작은 아이들도 너무 잘 크니까 이미 IGF1이 많은 키큰 아이들한테 과성장을 유도할 수 있거든요. 저희 아이들에겐. 국내 유일하게 식약체 인증받은 먹는 성장인자 IGF업을 먹여 왔었는데 IGF업 말고도 유럽 제품을 직구해서 드시는 것도 좋아요. 혹시 아이 키 때문에 고민인 분들은 성장 주사 말고 이거부터 6개월 정도 꾸준히 먹여 보세요. 차원이 다르게 클 겁니다."

PROMPT_1 = f"""

1. 당신은 광고 신뢰성 분석의 전문가입니다. 사용자로부터 받은 광고의 스크립트를 분석하여 광고와 제품의 신뢰성을 평가합니다. 사용자는 유튜브 쇼츠에서 시청한 광고의 스크립트를 제공합니다. 평가한 결과를 사용자에게 전달해야 합니다.

2. 광고 신뢰성 분석을 통해 광고가 과장되었는지, 사실에 기반했는지, 또는 오해의 소지가 있는지를 평가합니다. 광고에서 제품에 대한 특허를 언급하는 부분이 있다면, 해당 특허가 실제로 존재하는지 "검색 그라운딩"을 통해 확인하세요.

3. 답변은 텍스트 형식으로 제공하세요.

4. 답변은 전문적이고 간결한 어조로 설명하세요. 답변은 사용자에게 전달됩니다. 온화한 어조를 유지하세요.

5. 사용자는 디지털 정보에 취약한 고령자, 또는 광고에 쉽게 현혹되는 일반 소비자, 또는 청소년일 수 있습니다. 이 점을 고려하여 답변을 작성하세요.

6. 광고 스크립트를 바탕으로 다음과 같은 답변 형식을 제공하세요.
 - 광고의 신뢰성을 범주화하여 제시하세요(위험, 안전, 주의).
 - 광고 스크립트의 문제점을 간략화해서 제시하세요.
 - 검색 그라운딩을 통해 확인한 특허 정보(존재 여부, 특허 번호 등)를 제시하세요.
 - 검색 그라운딩으로 확인한 정보는 출처화 함께 제시하세요(링크 포함).

7. 이후 내용은 광고 스크립트입니다. 스크립트를 기반으로 위 지시사항에 따라 답변을 작성하세요.

{SCRIPT}
"""

PROMPT_2 = f"""

{SCRIPT}
"""

def add_citations(response):
    text = response.text

    if not response.candidates[0].grounding_metadata:
        return text
    
    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks

    # Sort supports by end_index in descending order to avoid shifting issues when inserting.
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if support.grounding_chunk_indices:
            # Create citation string like [1](link1)[2](link2)
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    return text

# 답변 내용들을 폴더에 차례차례 txt 파일로 저장하는 코드를 작성해줘
# 저장할 때마다 새로운 파일을 설정해줘. 1.txt, 2.txt, 3.txt ...
def save_response_to_file(token_usage, prompt_text, response_text, folder_path="responses"):
    # 폴더가 없으면 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 현재 폴더 내의 파일 개수를 세서 새로운 파일 이름 생성
    existing_files = os.listdir(folder_path)
    file_count = len(existing_files)
    new_file_name = f"{file_count + 1}.md"
    new_file_path = os.path.join(folder_path, new_file_name)

    text = f"TokensUsage:\n{token_usage}\n\nPrompt:\n{prompt_text}\n\nResponse:\n{response_text}"

    # 응답 내용을 파일에 저장
    with open(new_file_path, "w", encoding="utf-8") as file:
        file.write(text)

    print(f"Response saved to {new_file_path}")


if __name__ == "__main__":
    main()