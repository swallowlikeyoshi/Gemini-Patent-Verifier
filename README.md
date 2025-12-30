# Gemini Patent Verifier

**Gemini Patent Verifier**는 Gemini AI와 KIPRIS(한국특허정보원) 데이터를 결합하여 광고의 신뢰성을 분석하고 특허 주장의 진위 여부를 확인하는 도구입니다.

특히 유튜브 쇼츠 등에서 흔히 볼 수 있는 과장 광고나 허위 특허 주장을 걸러내어 사용자(특히 고령자나 청소년 등 정보 취약계층)에게 정확한 정보를 제공하는 것을 목표로 합니다.

## 🚀 주요 기능

- **🔎 KIPRIS 특허 검증**: MCP(Model Context Protocol)를 통해 KIPRIS 데이터베이스에 실시간으로 접근하여 광고에서 언급된 특허의 존재 여부와 상세 정보(출원인, 상태 등)를 확인합니다.
- **🌐 웹 그라운딩 (Google Search)**: 특허 정보 외에도 Google 검색 그라운딩을 활용하여 제품 및 광고 주장에 대한 일반적인 사실 관계를 교차 검증합니다.
- **⚠️ 자동 신뢰도 분류**: 분석 결과를 바탕으로 광고의 신뢰도를 **안전**, **주의**, **위험** 세 단계로 명확하게 분류합니다.
- **📄 상세 분석 보고서**: 특허 번호, 출원 정보, 원문 링크 및 근거가 되는 출처(Citation)를 포함한 전문적인 분석 결과를 생성합니다.

## 🛠 기술 스택

- **Model**: Google Gemini 1.5/2.0
- **SDK**: Google GenAI SDK (Python)
- **Protocol**: MCP (Model Context Protocol)
- **Database**: KIPRIS (Korea Intellectual Property Rights Information Service)
- **Environment**: Python 3.10+

## ⚙️ 설정 및 실행 방법

### 1. 환경 변수 설정
`.env` 파일을 생성하고 다음 정보를 입력합니다.
```env
API_KEY=your_gemini_api_key
# KIPRIS API 키는 MCP 서버 설정에 포함됩니다.
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
- **MCP 연동 테스트**: `python grounding_test_mcp.py`
- **목 서버 테스트**: `python mock_kipris_server.py`를 실행한 후 테스트를 진행할 수 있습니다.

## 📂 프로젝트 구조

- `grounding_test_mcp.py`: KIPRIS MCP 서버를 활용한 메인 분석 스크립트.
- `mcp_connector.py`: MCP 서버와의 연결 및 도구 호출을 담당하는 커넥터.
- `mock_kipris_server.py`: KIPRIS API 키 없이 테스트할 수 있는 목(Mock) 서버.
- `prompt.md`: 분석을 위한 정교한 시스템 프롬프트.
- `responses/`: 생성된 분석 보고서가 저장되는 디렉토리 (자동 생성).

---
*이 프로젝트는 사용자가 신중하게 정보를 소비할 수 있도록 돕는 AI 가이드라인을 제공합니다.*
