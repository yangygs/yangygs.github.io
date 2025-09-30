import sqlite3
from contextlib import contextmanager
from typing import Optional, Union, List, Tuple, Any, Iterator, Callable


class SQLExecutor:
    """SQL执行器类"""

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.cursor = connection.cursor()

    def __call__(self, sql: str, parameters: Optional[Union[tuple, dict]] = None) -> Union[List[Tuple], int]:
        """
        执行SQL语句并返回结果

        :param sql: SQL语句字符串
        :param parameters: SQL参数（元组或字典）
        :return: 查询结果列表或影响行数
        """
        try:
            if parameters:
                self.cursor.execute(sql, parameters)
            else:
                self.cursor.execute(sql)

            if sql.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return self.cursor.rowcount
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"SQL执行错误: {e}") from e


@contextmanager
def opensql(filepath: str = "database.db") -> Iterator[Callable]:
    """
    上下文管理器，用于安全地打开和关闭SQLite数据库

    使用示例:
    with opensql("mydb.db") as sql:
        results = sql("SELECT * FROM users")
        sql("INSERT INTO users (name) VALUES (?)", ("Alice",))

    :param filepath: 数据库文件路径（默认'database.db'）
    :yield: SQL执行函数
    """
    conn = None
    try:
        # 打开或创建数据库
        conn = sqlite3.connect(filepath)
        executor = SQLExecutor(conn)

        # 返回可调用对象
        yield executor

        # 正常退出时提交所有更改
        conn.commit()
    except sqlite3.Error as e:
        # 出错时回滚事务
        if conn:
            conn.rollback()
        raise RuntimeError(f"数据库错误: {e}") from e
    finally:
        # 确保关闭连接
        if conn:
            conn.close()

'''
from sql_util import opensql

# 基本用法
with opensql("mydatabase.db") as sql:
    # 创建表
    sql("""
        CREATE TABLE IF NOT EXISTS users
        (
            id
            INTEGER
            PRIMARY
            KEY,
            name
            TEXT
            NOT
            NULL,
            email
            TEXT
            UNIQUE
        )
        """)

    # 插入数据
    sql("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))

    # 查询数据
    results = sql("SELECT * FROM users")
    print("用户列表:", results)

    # 更新数据
    sql("UPDATE users SET email = ? WHERE name = ?", ("alice.new@example.com", "Alice"))

    # 再次查询
    updated = sql("SELECT * FROM users")
    print("更新后的用户:", updated)

# 自动清理：退出with块后连接自动关闭

# 使用默认数据库
with opensql() as sql:
    sql("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    sql("INSERT OR REPLACE INTO settings VALUES (?, ?)", ("theme", "dark"))

    setting = sql("SELECT value FROM settings WHERE key = ?", ("theme",))
    print("当前主题:", setting[0][0] if setting else "未设置")


# 批量操作示例
with opensql("inventory.db") as sql:
    # 创建产品表
    sql("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            stock INTEGER DEFAULT 0
        )
    """)
    
    # 批量插入产品
    products = [
        ("Laptop", 999.99, 10),
        ("Phone", 699.99, 25),
        ("Tablet", 399.99, 15)
    ]
    for product in products:
        sql("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", product)
    
    # 复杂查询
    expensive_items = sql("""
        SELECT name, price 
        FROM products 
        WHERE price > 500 
        ORDER BY price DESC
    """)
    print("高价商品:", expensive_items)
    
    # 使用事务
    try:
        sql("BEGIN TRANSACTION")
        sql("UPDATE products SET stock = stock - 1 WHERE name = ?", ("Laptop",))
        sql("INSERT INTO orders (product_id, quantity) VALUES (?, ?)", (1, 1))
        sql("COMMIT")
    except:
        sql("ROLLBACK")
        raise



'''