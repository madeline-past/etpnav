import os
import subprocess
import json

def call_openai_api(prompt):

    # 获取环境变量
    api_key = os.getenv("OPENAI_API_KEY") 
    organization_id = os.getenv("organization_id") 

    if not api_key or not organization_id:
        raise ValueError("OPENAI_API_KEY and OPENAI_ORGANIZATION must be set as environment variables")

    model = "gpt-4"
    max_tokens = 150

    data = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    })

    command = [
        "curl", "https://api.openai.com/v1/chat/completions",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-H", f"OpenAI-Organization: {organization_id}",
        "-d", data
    ]

    # 使用 stdout 和 stderr 参数来捕获输出
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)

    
    if result.returncode != 0:
        raise RuntimeError(f"curl command failed with error: {result.stderr}")

    return json.loads(result.stdout)

# 示例调用
response = call_openai_api("Tell me a joke")
assistant_message = response['choices'][0]['message']['content']
print(assistant_message)