"""
Python异步编程对比示例
对比 requests(串行) vs aiohttp(异步) 的性能差异
"""

import time
import requests
import asyncio
import aiohttp


# ============ 1. 串行版本 (requests) ============

def fetch_sync(url: str) -> dict:
    """
    同步获取URL数据
    
    参数:
        url: str - 要请求的URL地址
        
    返回:
        dict - 解析后的JSON数据
    """
    # requests.get() 是阻塞调用，程序在这里等待响应，什么都不做
    response = requests.get(url, timeout=10)
    # .json() 将响应体解析为Python字典
    return response.json()


def run_sync(urls: list[str]) -> list[dict]:
    """
    串行获取多个URL
    
    参数:
        urls: list[str] - URL列表
        
    返回:
        list[dict] - 每个URL的响应数据
    """
    results = []
    for url in urls:
        # 一个一个执行，前一个完成才开始后一个
        data = fetch_sync(url)
        results.append(data)
    return results


# ============ 2. 异步版本 (aiohttp) ============

async def fetch_async(session: aiohttp.ClientSession, url: str) -> dict:
    """
    异步获取URL数据
    
    参数:
        session: aiohttp.ClientSession - HTTP会话对象，复用连接池
        url: str - 要请求的URL地址
        
    返回:
        dict - 解析后的JSON数据
    """
    # session.get() 是非阻塞的，发起请求后立即返回协程
    # await 表示"这里会等待，但事件循环可以去做其他事"
    async with session.get(url) as response:
        # response.json() 也是异步的，需要await
        return await response.json()


async def run_async(urls: list[str]) -> list[dict]:
    """
    并发获取多个URL
    
    参数:
        urls: list[str] - URL列表
        
    返回:
        list[dict] - 每个URL的响应数据
    """
    # aiohttp.ClientSession 是HTTP连接池，自动管理TCP连接复用
    async with aiohttp.ClientSession() as session:
        # asyncio.gather() 并发执行所有任务
        # * 是解包操作符，把列表变成多个参数
        # 例如：gather(*[task1, task2]) 等价于 gather(task1, task2)
        tasks = [fetch_async(session, url) for url in urls]
        return await asyncio.gather(*tasks)


# ============ 3. 主程序：对比测试 ============

async def main():
    """
    主函数：对比串行和异步的性能
    """
    # 测试用的API：HTTPBin用于测试HTTP请求
    urls = [
        "https://httpbin.org/delay/1",  # 延迟1秒返回
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]
    
    print("=" * 50)
    print("测试：并发获取3个URL（每个延迟1秒）")
    print("=" * 50)
    
    # --- 串行测试 ---
    print("\n【串行版本 - requests】")
    start = time.time()
    # 同步代码不需要await，直接调用
    sync_results = run_sync(urls)
    sync_time = time.time() - start
    print(f"耗时: {sync_time:.2f}秒")  # 预期：约3秒
    
    # --- 异步测试 ---
    print("\n【异步版本 - aiohttp】")
    start = time.time()
    # 异步代码需要await，必须在async函数里
    async_results = await run_async(urls)
    async_time = time.time() - start
    print(f"耗时: {async_time:.2f}秒")  # 预期：约1秒
    
    # --- 结果对比 ---
    print("\n" + "=" * 50)
    print("性能对比")
    print("=" * 50)
    print(f"串行:  {sync_time:.2f}秒")
    print(f"异步:  {async_time:.2f}秒")
    print(f"提升:  {sync_time/async_time:.1f}x")


# ============ 4. 程序入口 ============

if __name__ == "__main__":
    # asyncio.run() 创建事件循环，运行main()协程
    # 这是异步程序的入口点
    asyncio.run(main())
