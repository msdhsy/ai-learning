"""
AI API 调用示例
支持 OpenAI 和 Claude API
"""

import asyncio
import aiohttp
import os
from typing import List, Dict, Any


# ============ 1. 配置 ============

# 从环境变量读取 API Key（推荐做法）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-key-here")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "sk-ant-your-key-here")

# API 端点
OPENAI_BASE_URL = "https://api.openai.com/v1"
CLAUDE_BASE_URL = "https://api.anthropic.com/v1"


# ============ 2. OpenAI API 调用 ============

async def chat_with_openai(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> Dict[str, Any]:
    """
    调用 OpenAI Chat Completion API
    
    参数:
        messages: List[Dict[str, str]] - 对话历史
            格式：[{"role": "user|assistant|system", "content": "..."}]
        model: str - 模型名称
        temperature: float - 随机性 (0-2)
        max_tokens: int - 最大生成 token 数
        
    返回:
        Dict[str, Any] - API 响应数据
    """
    url = f"{OPENAI_BASE_URL}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_text = await response.text()
                return {
                    "error": True,
                    "status": response.status,
                    "message": error_text
                }


async def ask_openai_simple(question: str) -> str:
    """
    简单提问（封装版）
    
    参数:
        question: str - 用户问题
        
    返回:
        str - AI 回答
    """
    messages = [
        {"role": "system", "content": "你是一个专业高效的 AI 助手。"},
        {"role": "user", "content": question}
    ]
    
    response = await chat_with_openai(messages)
    
    if "error" in response:
        return f"调用失败：{response['message']}"
    
    # 提取回答内容
    answer = response["choices"][0]["message"]["content"]
    return answer


# ============ 3. Claude API 调用 ============

async def chat_with_claude(messages: List[Dict[str, str]],model: str = "claude-sonnet-4-20250514",max_tokens: int = 1024) -> Dict[str, Any]:
    """
    调用 Claude API
    
    参数:
        messages: List[Dict[str, str]] - 对话历史
        model: str - 模型名称
        max_tokens: int - 最大生成 token 数
        
    返回:
        Dict[str, Any] - API 响应数据
    """
    url = f"{CLAUDE_BASE_URL}/messages"
    
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    # Claude 的消息格式略有不同
    # 需要分离 system 和 messages
    system_prompt = "你是一个专业高效的 AI 助手。"
    claude_messages = [
        {"role": m["role"], "content": m["content"]}for m in messages if m["role"] != "system"
    ]
    
    payload = {
        "model": model,
        "messages": claude_messages,
        "max_tokens": max_tokens,
        "system": system_prompt
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_text = await response.text()
                return {
                    "error": True,
                    "status": response.status,
                    "message": error_text
                }


async def ask_claude_simple(question: str) -> str:
    """
    简单提问 Claude（封装版）
    
    参数:
        question: str - 用户问题
        
    返回:
        str - AI 回答
    """
    messages = [
        {"role": "user", "content": question}
    ]
    
    response = await chat_with_claude(messages)
    
    if "error" in response:
        return f"调用失败：{response['message']}"
    
    # 提取回答内容
    answer = response["content"][0]["text"]
    return answer


# ============ 4. 并发调用多个 AI ============

async def compare_ai_responses(question: str) -> Dict[str, str]:
    """
    并发调用 OpenAI 和 Claude，对比回答
    
    参数:
        question: str - 用户问题
        
    返回:
        Dict[str, str] - 两个 AI 的回答
    """
    # 并发执行两个请求
    openai_task = ask_openai_simple(question)
    claude_task = ask_claude_simple(question)
    
    # 等待两个都完成
    openai_answer, claude_answer = await asyncio.gather(
        openai_task, 
        claude_task,
        return_exceptions=True
    )
    
    return {
        "openai": openai_answer if isinstance(openai_answer, str) else f"错误：{openai_answer}",
        "claude": claude_answer if isinstance(claude_answer, str) else f"错误：{claude_answer}"
    }




# ============ 5. 流式响应（进阶） ============

async def chat_with_openai_stream(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini"
):
    """
    流式调用 OpenAI（逐字输出）
    
    参数:
        messages: List[Dict[str, str]] - 对话历史
        model: str - 模型名称
        
    yield:
        str - 每次返回一个文本块
    """
    url = f"{OPENAI_BASE_URL}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": True  # 开启流式
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                # 流式响应需要逐行读取
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉 "data: " 前缀
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except:
                            pass
            else:
                error_text = await response.text()
                yield f"错误：{error_text}"


# ============ 6. 主程序：完整示例 ============

async def main():
    """
    主函数：演示 AI API 调用
    """
    print("=" * 60)
    print("AI API 调用示例")
    print("=" * 60)
    
    # 测试问题
    question = "Python 中 async 和 await 的作用是什么？用一句话解释。"
    print(f"\n问题：{question}\n")
    
    # --- 测试 OpenAI ---
    print("【1】调用 OpenAI...")
    openai_answer = await ask_openai_simple(question)
    print(f"OpenAI 回答:\n{openai_answer}\n")
    
    # --- 测试 Claude ---
    print("【2】调用 Claude...")
    claude_answer = await ask_claude_simple(question)
    print(f"Claude 回答:\n{claude_answer}\n")
    
    # --- 并发对比 ---
    print("【3】并发调用两个 AI...")
    results = await compare_ai_responses("用 3 个词形容 AI")
    print(f"OpenAI: {results['openai']}")
    print(f"Claude: {results['claude']}")
    
    # --- 流式示例 ---
    print("\n【4】流式输出（OpenAI）...")
    print("回答：", end="", flush=True)
    async for chunk in chat_with_openai_stream(
        messages=[{"role": "user", "content": "数到 5"}]
    ):
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    # 检查 API Key
    if OPENAI_API_KEY == "sk-your-key-here":
        print("⚠️  请设置 OPENAI_API_KEY 环境变量")
        print("   Windows PowerShell: $env:OPENAI_API_KEY='sk-...'")
        print("   或修改代码中的默认值\n")
    
    if CLAUDE_API_KEY == "sk-ant-your-key-here":
        print("⚠️  请设置 ANTHROPIC_API_KEY 环境变量")
        print("   Windows PowerShell: $env:ANTHROPIC_API_KEY='sk-ant-...'")
        print("   或修改代码中的默认值\n")
    
    asyncio.run(main())
