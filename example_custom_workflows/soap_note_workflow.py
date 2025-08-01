
import subprocess
import json

class SoapNoteWorkflow:
    """
    自动化：音频转录            soap_note = response2.choices[0].message.content
            with open(soap_file, "w", encoding="utf-8") as f:
                f.write(soap_note)
            
            # 创建 HTML 格式的 SOAP note
            html_soap_note = self._create_html_soap_note(soap_note)
            html_soap_file = "soap_note.html"
            with open(html_soap_file, "w", encoding="utf-8") as f:
                f.write(html_soap_note)
                
        except Exception as e:
            return {"status": "failed", "error": f"SOAP note 生成失败: {e}"}

        return {
            "status": "completed",
            "soap_note_file": soap_file,
            "soap_note_html_file": html_soap_file, -> SOAP note 生成
    """

    async def execute_workflow(self, initial_input, executor, session_id=None):
        """
        initial_input: dict, 需包含 'mp3_file'（音频文件名）
        """
        mp3_file = initial_input.get("mp3_file", "Record_test.mp3")
        wav_file = "converted.wav"
        transcript_file = "transcribed_text.txt"
        interpret_file = "interpret_text.json"
        soap_file = "soap_note.txt"

        # 步骤1：mp3转wav
        try:
            subprocess.run([
                "ffmpeg", "-i", mp3_file, "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", wav_file
            ], check=True)
        except Exception as e:
            return {"status": "failed", "error": f"ffmpeg conversion failed: {e}"}

        # 步骤2：调用 Google Speech-to-Text
        try:
            from speech_to_text import transcribe_speech
            transcript = transcribe_speech(wav_file)
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript)
        except Exception as e:
            return {"status": "failed", "error": f"Speech-to-text conversion failed: {e}"}

        # 步骤3：结构化症状（OpenAI）
        try:
            from interpret_call_content import client as openai_client
            with open(transcript_file, "r", encoding="utf-8") as f:
                transcript = f.read().strip()
            structured_prompt = f"""
Extract the following from the transcript:
1. Original symptom descriptions.
2. Standardized medical terms.
3. Possible conditions (based on symptoms).
Return output in JSON.
Transcript:
"{transcript}"
"""
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical assistant that extracts and standardizes symptoms from patient transcripts."},
                    {"role": "user", "content": structured_prompt}
                ],
                temperature=0.1
            )
            result_json = json.loads(response.choices[0].message.content)
            with open(interpret_file, "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return {"status": "failed", "error": f"Symptom structuring failed: {e}"}

        # 步骤4：生成SOAP note
        try:
            soap_prompt = f"""
请根据以下结构化医学信息，生成一份标准的 SOAP note（英文）：\n\n结构化信息：\n{json.dumps(result_json, ensure_ascii=False, indent=2)}\n\nSOAP note 要求：\nS（Subjective）：主观信息，直接引用原始主诉和症状描述。\nO（Objective）：客观信息，标准化医学术语和体征。\nA（Assessment）：根据症状和体征，给出可能的诊断或评估。\nP（Plan）：给出合理的下一步计划或建议。\n\n请严格按照 SOAP 四段输出，内容简明、专业。\n"""
            response2 = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical assistant that writes SOAP notes based on structured medical data."},
                    {"role": "user", "content": soap_prompt}
                ],
                temperature=0.1
            )
            soap_note = response2.choices[0].message.content
            with open(soap_file, "w", encoding="utf-8") as f:
                f.write(soap_note)
            
            # 创建 HTML 格式的 SOAP note
            html_soap_note = self._create_html_soap_note(soap_note)
            html_soap_file = "soap_note.html"
            with open(html_soap_file, "w", encoding="utf-8") as f:
                f.write(html_soap_note)
                
        except Exception as e:
            return {"status": "failed", "error": f"SOAP note 生成失败: {e}"}

        return {
            "status": "completed",
            "soap_note_file": soap_file,
            "soap_note_html_file": html_soap_file,
            "soap_note": soap_note
        }

    def _create_html_soap_note(self, soap_content):
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
                
            # 检测 SOAP 节标题 - 支持多种格式
            if (line.upper().startswith('S:') or 
                line.upper().startswith('SUBJECTIVE') or 
                line.upper().startswith('S (SUBJECTIVE)')):
                if current_section:
                    html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
                    html_content.append('        </div>')
                current_section = 'subjective'
                html_content.append(f'        <div class="section {current_section}">')
                html_content.append('            <div class="section-header">')
                html_content.append('                <div class="section-icon"></div>')
                html_content.append('                Subjective')
                html_content.append('            </div>')
                # 提取内容，去除标题部分
                content = line
                for prefix in ['S:', 'SUBJECTIVE:', 'S (SUBJECTIVE):']:
                    if content.upper().startswith(prefix):
                        content = content[len(prefix):].strip()
                        break
                current_section_content = [content] if content else []
                
            elif (line.upper().startswith('O:') or 
                  line.upper().startswith('OBJECTIVE') or 
                  line.upper().startswith('O (OBJECTIVE)')):
                if current_section:
                    html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
                    html_content.append('        </div>')
                current_section = 'objective'
                html_content.append(f'        <div class="section {current_section}">')
                html_content.append('            <div class="section-header">')
                html_content.append('                <div class="section-icon"></div>')
                html_content.append('                Objective')
                html_content.append('            </div>')
                # 提取内容，去除标题部分
                content = line
                for prefix in ['O:', 'OBJECTIVE:', 'O (OBJECTIVE):']:
                    if content.upper().startswith(prefix):
                        content = content[len(prefix):].strip()
                        break
                current_section_content = [content] if content else []
                
            elif (line.upper().startswith('A:') or 
                  line.upper().startswith('ASSESSMENT') or 
                  line.upper().startswith('A (ASSESSMENT)')):
                if current_section:
                    html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
                    html_content.append('        </div>')
                current_section = 'assessment'
                html_content.append(f'        <div class="section {current_section}">')
                html_content.append('            <div class="section-header">')
                html_content.append('                <div class="section-icon"></div>')
                html_content.append('                Assessment')
                html_content.append('            </div>')
                # 提取内容，去除标题部分
                content = line
                for prefix in ['A:', 'ASSESSMENT:', 'A (ASSESSMENT):']:
                    if content.upper().startswith(prefix):
                        content = content[len(prefix):].strip()
                        break
                current_section_content = [content] if content else []
                
            elif (line.upper().startswith('P:') or 
                  line.upper().startswith('PLAN') or 
                  line.upper().startswith('P (PLAN)')):
                if current_section:
                    html_content.append(f'            <div class="section-content">{"<br>".join(current_section_content)}</div>')
                    html_content.append('        </div>')
                current_section = 'plan'
                html_content.append(f'        <div class="section {current_section}">')
                html_content.append('            <div class="section-header">')
                html_content.append('                <div class="section-icon"></div>')
                html_content.append('                Plan')
                html_content.append('            </div>')
                # 提取内容，去除标题部分
                content = line
                for prefix in ['P:', 'PLAN:', 'P (PLAN):']:
                    if content.upper().startswith(prefix):
                        content = content[len(prefix):].strip()
                        break
                current_section_content = [content] if content else []
                
            else:
                # 添加到当前节的内容
                if current_section and line and not line.upper().startswith('SOAP NOTE'):
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

    def get_input_type(self):
        return dict

    def get_output_type(self):
        return dict