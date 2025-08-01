from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 获取 API 密钥
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Cannot find OPENAI_API_KEY, please set the environment variable or provide it in the .env file")

client = OpenAI(api_key=api_key)

# 从本地文件读取转录文本
try:
    with open("transcribed_text.txt", "r", encoding="utf-8") as file:
        transcript = file.read().strip()
    print("Successfully read transcribed_text.txt file")
except FileNotFoundError:
    # 如果文件不存在，使用默认示例
    transcript = "The patient reports persistent headaches, occasional dizziness, and blurry vision."
    print("Warning: transcribed_text.txt file not found, using default example text")

# 构建结构化 prompt
structured_prompt = f"""
Extract the following from the transcript:
1. Original symptom descriptions.
2. Standardized medical terms.
3. Possible conditions (based on symptoms).
Return output in JSON.
Transcript:
"{transcript}"

Expected format:
{{
  "symptom_raw": [...],
  "symptom_standardized": [...],
  "possible_conditions": [...]
}}
"""

# 使用新版 OpenAI API 生成结果
response = client.chat.completions.create(
    model="gpt-4",  # 或者使用 "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "You are a medical assistant that extracts and standardizes symptoms from patient transcripts."},
        {"role": "user", "content": structured_prompt}
    ],
    temperature=0.1  # 降低随机性以获得更确定性的回答
)

# 打印结果 - 新API的访问方式有所不同
print(response.choices[0].message.content)

# 如果需要解析 JSON 输出，并保存到 interpret_text.json 文件
try:
    result_json = json.loads(response.choices[0].message.content)
    print("\nParsed JSON:")
    print(json.dumps(result_json, indent=2))
    # 保存到 interpret_text.json
    with open("interpret_text.json", "w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    print("\nSuccessfully saved parsed result to: interpret_text.json")
except json.JSONDecodeError:
    print("\nWarning: Response could not be parsed as JSON")