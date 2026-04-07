"""
OpenClaw Skill 开发示例
创建一个简单的天气查询Skill
"""

import asyncio
import aiohttp
from typing import Dict, Any


class WeatherSkill:
    """
    天气查询Skill类
    
    这是一个简化示例，展示Skill的基本结构
    """
    
    def __init__(self):
        """初始化Skill"""
        # API配置
        self.api_base = "https://wttr.in"
        # 支持的地点列表（实际应该更完善）
        self.supported_cities = ["beijing", "shanghai", "guangzhou", "shenzhen"]
    
    async def fetch_weather(self, city: str) -> Dict[str, Any]:
        """
        获取指定城市的天气
        
        参数:
            city: str - 城市名（英文小写）
            
        返回:
            Dict[str, Any] - 天气数据
        """
        # 构建URL，?format=j1 返回JSON格式
        url = f"{self.api_base}/{city}?format=j1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"获取失败，状态码: {response.status}"}
    
    def parse_weather(self, data: Dict[str, Any]) -> str:
        """
        解析天气数据，生成可读文本
        
        参数:
            data: Dict[str, Any] - API返回的原始数据
            
        返回:
            str - 格式化后的天气信息
        """
        if "error" in data:
            return data["error"]
        
        try:
            # 提取当前天气
            current = data["current_condition"][0]
            location = data["nearest_area"][0]
            
            city_name = location["areaName"][0]["value"]
            temp = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            humidity = current["humidity"]
            
            return f"📍 {city_name}\n🌡️ 温度: {temp}°C\n☁️ 天气: {desc}\n💧 湿度: {humidity}%"
        except (KeyError, IndexError) as e:
            return f"解析数据失败: {str(e)}"
    
    async def handle(self, query: str) -> str:
        """
        处理用户查询（Skill入口）
        
        参数:
            query: str - 用户输入，如 "北京天气"
            
        返回:
            str - 回复给用户的消息
        """
        # 简单解析：提取城市名
        # 实际应该用NLP或正则匹配
        city = query.replace("天气", "").strip().lower()
        
        if not city:
            return "请告诉我城市名，例如：北京天气"
        
        # 获取天气数据
        data = await self.fetch_weather(city)
        
        # 解析并返回
        return self.parse_weather(data)


# ============ 测试代码 ============

async def main():
    """测试Skill"""
    skill = WeatherSkill()
    
    # 测试查询
    test_queries = [
        "beijing天气",
        "shanghai天气",
        "天气",  # 错误：没有城市名
    ]
    
    for query in test_queries:
        print(f"\n用户: {query}")
        print(f"助手:\n{await skill.handle(query)}")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
