# 회의록 작성하기 귀찮아서 만든 레포

### STEP1. install dependencies
```bash
python -m venv .venv
source .venv/bin/activate # or .venv/Scripts/activate in Windows
pip install -r requirements.txt
```

### STEP2. set env file
https://console.groq.com/playground 여기에서 API key 발급받기

root에 .env 파일 생성 후 아래 내용 추가

```bash
GROQ_API_KEY=<발급받은 API KEY>
```

### STEP3. locate audio file under `recording/` folder

### STEP4. run
```bash
python run.py
```
`transcript/` 폴더에 회의록 텍스트 파일 생성됨

### STEP5. gpt 4o 모델로 요약 돌리세요

회의록 요약 기능 추가하려 했지만 무료 api 모델 쓰는 것보단 gpt 4o가 젤 잘해줘요
token 제한도 있고요

예를 들어
```text
[transcript 내용]
위 내용을 회의록 포맷으로 최대한 자세히 정리해줘.
핵심 포인트 + 디테일 이런 식으로 노션에 복사 붙여넣기 좋은 형태로 말야.