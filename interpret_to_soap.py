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

# 读取 interpret_text.json
try:
    with open("interpret_text.json", "r", encoding="utf-8") as f:
        interpret_data = json.load(f)
    print("Successfully read interpret_text.json file")
except FileNotFoundError:
    raise FileNotFoundError("interpret_text.json file not found, please run interpret_call_content.py to generate it")

# 构建 SOAP note prompt
soap_prompt = f"""
请根据以下结构化医学信息，生成一份标准的 SOAP note（英文）：\n\n结构化信息：\n{json.dumps(interpret_data, ensure_ascii=False, indent=2)}\n\nSOAP note 要求：\nS（Subjective）：主观信息，直接引用原始主诉和症状描述。\nO（Objective）：客观信息，标准化医学术语和体征。\nA（Assessment）：根据症状和体征，给出可能的诊断或评估。\nP（Plan）：给出合理的下一步计划或建议。\n\n请严格按照 SOAP 四段输出，内容简明、专业。\n"""

response = client.chat.completions.create(
    model="gpt-4",  # 或 "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "You are a medical assistant that writes SOAP notes based on structured medical data."},
        {"role": "user", "content": soap_prompt}
    ],
    temperature=0.1
)

soap_note = response.choices[0].message.content
print("\nSOAP note:\n")
print(soap_note)

# 保存为 soap_note.txt
with open("soap_note.txt", "w", encoding="utf-8") as f:
    f.write(soap_note)
print("\nSOAP note saved to: soap_note.txt")

# 创建 HTML 格式的 SOAP note
def create_html_soap_note(soap_content):
    """将 SOAP note 转换为格式化的 HTML"""
    
    # 分割 SOAP note 内容
    lines = soap_content.split('\n')
    html_content = []
    current_section = None
    
    html_content.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOAP Note</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f8f9fa;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 25px;
            padding: 15px;
            border-left: 4px solid #3498db;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .section-header {
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .section-content {
            color: #34495e;
            padding-left: 10px;
        }
        .subjective { border-left-color: #e74c3c; }
        .objective { border-left-color: #f39c12; }
        .assessment { border-left-color: #27ae60; }
        .plan { border-left-color: #9b59b6; }
        .section-icon {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 50%;
        }
        .subjective .section-icon { background-color: #e74c3c; }
        .objective .section-icon { background-color: #f39c12; }
        .assessment .section-icon { background-color: #27ae60; }
        .plan .section-icon { background-color: #9b59b6; }
        .timestamp {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 SOAP Note</h1>
""")
    
    # 解析 SOAP note 内容
    current_section_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检测 SOAP 节标题
        if line.upper().startswith('S:') or line.upper().startswith('SUBJECTIVE'):
            if current_section:
                html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
                html_content.append('        </div>')
            current_section = 'subjective'
            html_content.append(f'        <div class="section {current_section}">')
            html_content.append('            <div class="section-header">')
            html_content.append('                <div class="section-icon"></div>')
            html_content.append('                Subjective (主观信息)')
            html_content.append('            </div>')
            current_section_content = [line.replace('S:', '').replace('SUBJECTIVE:', '').strip()]
            
        elif line.upper().startswith('O:') or line.upper().startswith('OBJECTIVE'):
            if current_section:
                html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
                html_content.append('        </div>')
            current_section = 'objective'
            html_content.append(f'        <div class="section {current_section}">')
            html_content.append('            <div class="section-header">')
            html_content.append('                <div class="section-icon"></div>')
            html_content.append('                Objective (客观信息)')
            html_content.append('            </div>')
            current_section_content = [line.replace('O:', '').replace('OBJECTIVE:', '').strip()]
            
        elif line.upper().startswith('A:') or line.upper().startswith('ASSESSMENT'):
            if current_section:
                html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
                html_content.append('        </div>')
            current_section = 'assessment'
            html_content.append(f'        <div class="section {current_section}">')
            html_content.append('            <div class="section-header">')
            html_content.append('                <div class="section-icon"></div>')
            html_content.append('                Assessment (评估)')
            html_content.append('            </div>')
            current_section_content = [line.replace('A:', '').replace('ASSESSMENT:', '').strip()]
            
        elif line.upper().startswith('P:') or line.upper().startswith('PLAN'):
            if current_section:
                html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
                html_content.append('        </div>')
            current_section = 'plan'
            html_content.append(f'        <div class="section {current_section}">')
            html_content.append('            <div class="section-header">')
            html_content.append('                <div class="section-icon"></div>')
            html_content.append('                Plan (计划)')
            html_content.append('            </div>')
            current_section_content = [line.replace('P:', '').replace('PLAN:', '').strip()]
            
        else:
            # 添加到当前节的内容
            if current_section and line:
                current_section_content.append(line)
    
    # 添加最后一个节
    if current_section:
        html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
        html_content.append('        </div>')
    
    # 添加时间戳和结尾
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content.append(f"""        <div class="timestamp">
            Generated on {timestamp}
        </div>
    </div>
</body>
</html>""")
    
    return '\n'.join(html_content)

# 生成并保存 HTML 版本
html_soap_note = create_html_soap_note(soap_note)
with open("soap_note.html", "w", encoding="utf-8") as f:
    f.write(html_soap_note)
print("SOAP note HTML version saved to: soap_note.html")
