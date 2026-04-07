"""
PostgreSQL 异步操作基础
使用 asyncpg 库（公司技术栈）
"""

import asyncio
import asyncpg
from typing import List, Dict, Any


# ============ 1. 连接数据库 ============

async def get_connection() -> asyncpg.Connection:
    """
    获取数据库连接
    
    返回:
        asyncpg.Connection - 数据库连接对象
    """
    # 连接字符串格式：postgresql://用户：密码@主机：端口/数据库
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="your_password",
        database="test_db"
    )
    return conn


# ============ 2. 基础 CRUD 操作 ============

async def create_table(conn: asyncpg.Connection):
    """
    创建示例表：users
    
    参数:
        conn: asyncpg.Connection - 数据库连接
    """
    # 执行 DDL 语句
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ 表 users 创建成功")


async def insert_user(conn: asyncpg.Connection, name: str, email: str, age: int = None) -> int:
    """
    插入用户数据
    
    参数:
        conn: asyncpg.Connection - 数据库连接
        name: str - 姓名
        email: str - 邮箱
        age: int - 年龄（可选）
        
    返回:
        int - 新插入的用户 ID
    """
    # $1, $2, $3 是占位符，防止 SQL 注入
    row = await conn.fetchrow(
        """
        INSERT INTO users (name, email, age)
        VALUES ($1, $2, $3)
        RETURNING id
        """,
        name, email, age
    )
    return row["id"]


async def get_user_by_id(
    conn: asyncpg.Connection, 
    user_id: int
) -> Dict[str, Any]:
    """
    根据 ID 查询用户
    
    参数:
        conn: asyncpg.Connection - 数据库连接
        user_id: int - 用户 ID
        
    返回:
        Dict[str, Any] - 用户数据字典
    """
    row = await conn.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        user_id
    )
    if row:
        return dict(row)  # asyncpg.Record → dict
    return None


async def get_all_users(
    conn: asyncpg.Connection
) -> List[Dict[str, Any]]:
    """
    获取所有用户
    
    参数:
        conn: asyncpg.Connection - 数据库连接
        
    返回:
        List[Dict[str, Any]] - 用户列表
    """
    rows = await conn.fetch("SELECT * FROM users ORDER BY id")
    return [dict(row) for row in rows]


async def update_user_age(
    conn: asyncpg.Connection,
    user_id: int,
    new_age: int
) -> bool:
    """
    更新用户年龄
    
    参数:
        conn: asyncpg.Connection - 数据库连接
        user_id: int - 用户 ID
        new_age: int - 新年龄
        
    返回:
        bool - 是否更新成功
    """
    result = await conn.execute(
        """
        UPDATE users 
        SET age = $1 
        WHERE id = $2
        """,
        new_age, user_id
    )
    # execute() 返回 "UPDATE 1" 或 "UPDATE 0"
    return result == "UPDATE 1"


async def delete_user(
    conn: asyncpg.Connection,
    user_id: int
) -> bool:
    """
    删除用户
    
    参数:
        conn: asyncpg.Connection - 数据库连接
        user_id: int - 用户 ID
        
    返回:
        bool - 是否删除成功
    """
    result = await conn.execute(
        "DELETE FROM users WHERE id = $1",
        user_id
    )
    return result == "DELETE 1"


# ============ 3. 事务处理 ============

async def transfer_with_transaction(
    conn: asyncpg.Connection,
    from_user_id: int,
    to_user_id: int,
    amount: int
):
    """
    使用事务进行转账操作（示例）
    
    参数:
        conn: asyncpg.Connection - 数据库连接
        from_user_id: int - 转出用户 ID
        to_user_id: int - 转入用户 ID
        amount: int - 金额
    """
    # 开启事务
    async with conn.transaction():
        # 事务内所有操作要么全部成功，要么全部回滚
        await conn.execute(
            "UPDATE accounts SET balance = balance - $1 WHERE user_id = $2",
            amount, from_user_id
        )
        await conn.execute(
            "UPDATE accounts SET balance = balance + $1 WHERE user_id = $2",
            amount, to_user_id
        )
        # 如果这里抛出异常，前面两个 UPDATE 会自动回滚


# ============ 4. 连接池（生产环境推荐） ============

async def create_pool() -> asyncpg.Pool:
    """
    创建连接池
    
    返回:
        asyncpg.Pool - 连接池对象
    """
    pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="postgres",
        password="your_password",
        database="test_db",
        min_size=5,      # 最小连接数
        max_size=20      # 最大连接数
    )
    return pool


async def query_with_pool(pool: asyncpg.Pool):
    """
    使用连接池查询
    
    参数:
        pool: asyncpg.Pool - 连接池
    """
    # 从连接池获取连接，用完后自动归还
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users")
        return [dict(row) for row in rows]


# ============ 5. 主程序：完整示例 ============

async def main():
    """
    主函数：演示完整 CRUD 流程
    """
    print("=" * 60)
    print("PostgreSQL 异步操作示例")
    print("=" * 60)
    
    # 1. 获取连接
    print("\n【1】连接数据库...")
    conn = await get_connection()
    print("✅ 连接成功")
    
    # 2. 创建表
    print("\n【2】创建表...")
    await create_table(conn)
    
    # 3. 插入数据
    print("\n【3】插入用户...")
    user_id = await insert_user(conn, "张三", "zhangsan@example.com", 25)
    print(f"✅ 插入成功，用户 ID: {user_id}")
    
    user_id = await insert_user(conn, "李四", "lisi@example.com", 30)
    print(f"✅ 插入成功，用户 ID: {user_id}")
    
    # 4. 查询单个用户
    print("\n【4】查询用户 ID=1...")
    user = await get_user_by_id(conn, 1)
    if user:
        print(f"✅ 找到用户：{user}")
    
    # 5. 查询所有用户
    print("\n【5】查询所有用户...")
    users = await get_all_users(conn)
    for u in users:
        print(f"   - {u['name']} ({u['email']})")
    
    # 6. 更新数据
    print("\n【6】更新用户 ID=1 的年龄为 26...")
    success = await update_user_age(conn, 1, 26)
    print(f"✅ 更新{'成功' if success else '失败'}")
    
    # 7. 删除数据
    print("\n【7】删除用户 ID=2...")
    success = await delete_user(conn, 2)
    print(f"✅ 删除{'成功' if success else '失败'}")
    
    # 8. 关闭连接
    print("\n【8】关闭连接...")
    await conn.close()
    print("✅ 连接已关闭")


if __name__ == "__main__":
    asyncio.run(main())
