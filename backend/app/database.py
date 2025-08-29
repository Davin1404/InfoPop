from sqlmodel import SQLModel, create_engine

# 数据库连接配置
sqlite_file_name = "database.db"
sqlite_file_path = "../data"
sqlite_url = f"sqlite:///{sqlite_file_path}/{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # 这个方法会根据你定义的 SQLModel 类自动在数据库中创建表。
    # 它只会创建不存在的表，不会删除或修改已存在的表结构（比如不会自动新增字段、删除字段等）。
    # 只有当你修改了 SQLModel 类（比如新增了一个表或字段）
    # 并且希望数据库同步这些变化时，才需要重新执行一次。
    # 但注意：create_all 只会创建新表或新字段，不会自动删除旧字段或修改字段类型。
    # 如果需要复杂的结构变更，推荐用 Alembic 这类数据库迁移工具。