"""
课后作业答案：添加错误处理和API Key认证
"""

import time
import asyncio
import aiohttp


async def fetch_with_auth(session: aiohttp.ClientSession, url: str, api_key: str = None) -> dict:
    """
    带认证和错误处理的异步请求
    
    参数:
        session: aiohttp.ClientSession - HTTP会话
        url: str - 请求地址
        api_key: str - 可选的API密钥
        
    返回:
        dict - 响应数据，失败返回包含error信息的字典
    """
    # 构建请求头
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        headers["X-API-Key"] = api_key
    
    try:
        # timeout=aiohttp.ClientTimeout(total=10) 设置10秒超时
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            # 检查HTTP状态码
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "error": True,
                    "status": response.status,
                    "message": f"HTTP错误: {response.status}"
                }
    except asyncio.TimeoutError:
        # 超时错误
        return {"error": True, "message": "请求超时"}
    except aiohttp.ClientError as e:
        # 网络错误（DNS失败、连接拒绝等）
        return {"error": True, "message": f"网络错误: {str(e)}"}
    except Exception as e:
        # 其他未知错误
        return {"error": True, "message": f"未知错误: {str(e)}"}


async def run_async_with_error_handling(urls: list[str], api_key: str = None) -> list[dict]:
    """
    带错误处理的并发请求
    
    参数:
        urls: list[str] - URL列表
        api_key: str - 可选的API密钥
        
    返回:
        list[dict] - 每个URL的响应或错误信息
    """
    async with aiohttp.ClientSession() as session:
        # 创建任务列表
        tasks = [fetch_with_auth(session, url, api_key) for url in urls]
        # gather() 默认会等待所有任务完成，即使有错误也不会中断
        return await asyncio.gather(*tasks)


async def main():
    """
    主函数：测试5个URL，包含错误处理
    """
    urls = [
        "https://httpbin.org/delay/1",           # 正常，延迟1秒
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/404",        # 404错误
        "https://httpbin.org/status/500",        # 500错误
        "https://httpbin.org/delay/1",
    ]
    
    print("=" * 60)
    print("测试：5个URL（含错误情况）")
    print("=" * 60)
    
    start = time.time()
    results = await run_async_with_error_handling(urls, api_key="test-key-123")
    total_time = time.time() - start
    
    print(f"\n总耗时: {total_time:.2f}秒\n")
    
    # 打印每个结果
    for i, (url, result) in enumerate(zip(urls, results), 1):
        print(f"[{i}] {url}")
        if result.get("error"):
            print(f"    ❌ {result['message']}")
        else:
            print(f"    ✅ 成功")
        print()


if __name__ == "__main__":
    asyncio.run(main())
