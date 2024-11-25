# from openai import OpenAI
import base64
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import os
import json
import subprocess
import logging


# 获取环境变量
api_key = os.getenv("OPENAI_API_KEY")
organization_id = os.getenv("organization_id")

if not api_key or not organization_id:
    raise ValueError("API key or organization ID not set in environment variables.")


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(data):
    """
    带重试机制的函数，调用 OpenAI API
    """ 
    try:
        data_json = json.dumps(data)
    except Exception as json_error:
        logging.error(f"数据序列化为 JSON 失败: {json_error}")
        raise ValueError("无法序列化数据为 JSON 格式") from json_error
    # 构建 curl 命令
    command = [
        "curl", "https://api.openai.com/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", f"OpenAI-Organization: {organization_id}",
        "-d", data_json
    ]

    try:
        # 调用 subprocess
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)

        if result.returncode != 0:
            logging.error(f"curl 命令失败，错误: {result.stderr}")
            raise RuntimeError(f"curl 命令执行失败: {result.stderr}")

        # 验证返回结果是否是 JSON 格式
        try:
            response = json.loads(result.stdout)
            logging.info("curl 命令执行成功，返回 JSON 响应")
            return response
        except json.JSONDecodeError as e:
            logging.error(f"解析 JSON 响应失败: {e}")
            raise RuntimeError(f"解析 JSON 响应失败: {e}")

    except subprocess.TimeoutExpired as e:
        logging.error(f"curl 命令超时: {e}")
        try:
            result.kill()
        except Exception as kill_error:
            logging.error(f"终止超时进程失败: {kill_error}")
        raise RuntimeError(f"curl 命令超时: {e}") from e

    except Exception as e:
        logging.error(f"未知错误: {e}")
        raise RuntimeError(f"未知错误: {e}")



def gpt_infer(system, text, image_list, model="gpt-4o-2024-08-06", max_tokens=600, response_format=None):

    user_content = []
    image_len = 0
    print("indices of images saved:")
    for i, image in enumerate(image_list):
        if image is not None:
            print(i)
            image_len += 1
            assert image_len <= 20,'Exceed image limit and stop!'
            user_content.append(
                {
                    "type": "text",
                    "text": f"Image {i}:"
                },
            )

            # with open(image, "rb") as image_file:
            #     image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            image_message = {
                     "type": "image_url",
                     "image_url": {
                         "url": f"data:image/jpeg;base64,{image}",
                         "detail": "low"
                     }
                 }
            user_content.append(image_message)

    user_content.append(
        {
            "type": "text",
            "text": text
        }
    )

    messages = [
        {"role": "system",
         "content": system
         },
        {"role": "user",
         "content": user_content
         }
    ]

    try:
        # 构建请求数据
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0
        }
        # 如果指定了 response_format，则处理该逻辑
        if response_format:
            data["response_format"] = response_format


        # 调用 GPT 接口（带重试逻辑）
        response = completion_with_backoff(data)

        # 验证 response 格式
        if not isinstance(response, dict):
            raise ValueError("API 返回的数据格式无效")

        if "choices" not in response or not response["choices"]:
            raise ValueError(f"API 返回的响应中缺少 'choices'，完整响应为: {response}")
        
        total_tokens = response["usage"]["total_tokens"]
        
        return response["choices"][0]["message"]["content"], total_tokens
        
        # answer = response.choices[0].message.content
        # tokens = response.usage

        # return answer, tokens

    except (KeyError, IndexError) as e:
        raise ValueError(f"解析 GPT 响应内容失败: {e}, 完整响应为: {response}")


    # if response_format:
    #     chat_message = completion_with_backoff(model=model, messages=messages, temperature=0, max_tokens=max_tokens, response_format=response_format)
    # else:
    #     chat_message = completion_with_backoff(model=model, messages=messages, temperature=0, max_tokens=max_tokens)

    # print(chat_message)
    # answer = chat_message.choices[0].message.content
    # tokens = chat_message.usage

    # return answer, tokens



def gpt_caption(system, text, image, model="gpt-4o-2024-08-06", max_tokens=600, response_format=None):

    user_content = []

    user_content.append(
        {
            "type": "text",
            "text": f"Image :"
        },
    )

    image_message = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}",
                    "detail": "low"
                }
            }
    user_content.append(image_message)

    user_content.append(
        {
            "type": "text",
            "text": text
        }
    )

    messages = [
        {"role": "system",
         "content": system
         },
        {"role": "user",
         "content": user_content
         }
    ]

    try:
        # 构建请求数据
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0
        }
        # 如果指定了 response_format，则处理该逻辑
        if response_format:
            data["response_format"] = response_format


        # 调用 GPT 接口（带重试逻辑）
        response = completion_with_backoff(data)

        # 验证 response 格式
        if not isinstance(response, dict):
            raise ValueError("API 返回的数据格式无效")
        
        total_tokens = response["usage"]["total_tokens"]
        
        return response["choices"][0]["message"]["content"], total_tokens
        
        # answer = response.choices[0].message.content
        # tokens = response.usage

        # return answer, tokens

    except (KeyError, IndexError) as e:
        raise ValueError(f"解析 GPT 响应内容失败: {e}, 完整响应为: {response}")
