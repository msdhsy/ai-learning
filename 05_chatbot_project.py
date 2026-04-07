"""
综合练习：AI 对话机器人
整合今日所学：异步 + PostgreSQL + AI API
"""

import asyncio
import asyncpg
import aiohttp
import os
from datetime import datetime
from typing import List, Dict, Any


# ============ 配置 ============

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-key-here")
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "your_password",
    "database": "chatbot_db"
}


# ============ 数据库层 ============

async def init_db(pool: asyncpg.Pool):
    """
    初始化数据库：创建表
    """
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100),
                role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 数据库表初始化完成")


async def save_message(
    pool: asyncpg.Pool,
    user_id: str,
    role: str,
    content: str
):
    """
    保存一条对话消息
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO conversations (user_id, role, content)
            VALUES ($1, $2, $3)
            """,
            user_id, role, content
        )


async def get_history(
    pool: asyncpg.Pool,
    user_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    获取用户的对话历史
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, content 
            FROM conversations 
            WHERE user_id = $1 
            ORDER BY created_at DESC 
            LIMIT $2
            """,
            user_id, limit
        )
        # 反转顺序，让历史按时间正序
        return [dict(row) for row in reversed(rows)]


# ============ AI API 层 ============

async def call_openai(
    session: aiohttp.ClientSession,
    messages: List[Dict[str, str]]
) -> str:
    """
    调用 OpenAI API
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "max_tokens": 1024
    }
    
    async with session.post(url, headers=headers, json=payload) as response:
        if response.status == 200:
            data = await response.json()
            return data["choices"][0]["message"]["content"]
        else:
            error = await response.text()
            return f"API 错误：{error}"


# ============ 业务逻辑层 ============

class ChatBot:
    """
    对话机器人
    """
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.session = None
    
    async def start(self):
        """
        启动机器人：创建 HTTP 会话
        """
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        """
        停止机器人：关闭 HTTP 会话
        """
        if self.session:
            await self.session.close()
    
    async def chat(self, user_id: str, user_message: str) -> str:
        """
        处理用户对话
        
        流程：
        1. 保存用户消息到数据库
        2. 获取对话历史
        3. 调用 OpenAI API
        4. 保存 AI 回复到数据库
        5. 返回 AI 回复
        """
        # 1. 保存用户消息
        await save_message(self.pool, user_id, "user", user_message)
        
        # 2. 获取历史（最近 10 条）
        history = await get_history(self.pool, user_id, limit=10)
        
        # 3. 构建消息列表
        messages = [
            {"role": "system", "content": "你是一个专业高效的 AI 助手。"}
        ] + history
        
        # 4. 调用 AI
        ai_response = await call_openai(self.session, messages)
        
        # 5. 保存 AI 回复
        await save_message(self.pool, user_id, "assistant", ai_response)
        
        return ai_response


# ============ 主程序 ============

async def main():
    """
    主函数：演示完整流程
    """
    print("=" * 60)
    print("AI 对话机器人 - 综合练习")
    print("=" * 60)
    
    # 1. 创建连接池
    print("\n【1】连接数据库...")
    pool = await asyncpg.create_pool(**DB_CONFIG)
    print("✅ 连接成功")
    
    # 2. 初始化数据库
    print("\n【2】初始化数据库...")
    await init_db(pool)
    
    # 3. 启动机器人
    print("\n【3】启动机器人...")
    bot = ChatBot(pool)
    await bot.start()
    print("✅ 机器人就绪")
    
    # 4. 模拟对话
    print("\n【4】模拟对话...")
    
    # 第一轮
    user_msg = "Python 中 async 和 await 的作用是什么？"
    print(f"\n用户：{user_msg}")
    response = await bot.chat("user_001", user_msg)
    print(f"AI: {response[:100]}...")  # 只显示前 100 字
    
    # 第二轮
    user_msg = "能给我一个简单的例子吗？"
    print(f"\n用户：{user_msg}")
    response = await bot.chat("user_001", user_msg)
    print(f"AI: {response[:100]}...")
    
    # 5. 查看历史
    print("\n【5】查看对话历史...")
    history = await get_history(pool, "user_001")
    print(f"共 {len(history)} 条记录")
    for msg in history:
        role = "用户" if msg["role"] == "user" else "AI"
        print(f"  {role}: {msg['content'][:50]}...")
    
    # 6. 清理
    print("\n【6】关闭资源...")
    await bot.stop()
    pool.close()
    await pool.wait_closed()
    print("✅ 已关闭")
    
    print("\n" + "=" * 60)
    print("练习完成！")
    print("=" * 60)


if __name__ == "__main__":
    # 检查配置
    if OPENAI_API_KEY == "sk-your-key-here":
        print("⚠️  请设置 OPENAI_API_KEY")
    if DB_CONFIG["password"] == "your_password":
        print("⚠️  请配置数据库密码")
    
    asyncio.run(main())
