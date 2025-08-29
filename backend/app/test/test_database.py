from sqlmodel import Session

from database import create_db_and_tables, engine
from backend.app.models_sql import KnowledgeSource

def create_knowledge_source(
    file_name: str, file_path: str, file_type: str, file_size: int, status: str
) -> KnowledgeSource:
    knowledge_source = KnowledgeSource(
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        status=status
    )
    with Session(engine) as session:
        session.add(knowledge_source)
        session.commit()
        session.refresh(knowledge_source)
    return knowledge_source

def main():
    # 创建数据库和表
    create_db_and_tables()

    # 示例：创建一个知识库来源
    source = create_knowledge_source(
        file_name="example.txt",
        file_path="/data/example.txt",
        file_type="txt",
        file_size=1,
        status="未解析"
    )
    print(f"Created Knowledge Source: {source}")

if __name__ == "__main__":
    main()