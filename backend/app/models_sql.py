from datetime import datetime
from typing import List
from sqlmodel import SQLModel, Field, Relationship, create_engine

# 知识库来源
class KnowledgeSource(SQLModel, table=True):
    __tablename__ = "knowledge_source"

    id: int | None = Field(default=None, primary_key=True, description="唯一标识")
    file_name: str = Field(description="文件名")
    file_path: str = Field(description="本地路径")
    file_type: str = Field(description="文件类型，如txt/pdf/docx/xlsx等")
    file_size: int = Field(description="文件大小(MB)")
    import_time: datetime | None = Field(default_factory=datetime.now, description="导入时间")
    status: str = Field(description="已解析/未解析/解析失败等")


# 知识库与标签多对多关联表
class KnowledgeBaseTagLink(SQLModel, table=True):
    __tablename__ = "knowledge_base_tag_link"

    knowledge_base_id: int | None = Field(
        default=None, foreign_key="knowledge_base.id", primary_key=True
    )
    tag_id: int | None = Field(
        default=None, foreign_key="tags.id", primary_key=True
    )


# 知识库标签表
class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(description="标签名")
    description: str | None = Field(default=None, description="描述")
    # user_id: int | None = Field(default=None, foreign_key="user.id", description="所属用户")  # Commented out - user table doesn't exist yet

    # 知识库与标签的多对多关系
    knowledge_bases: list["KnowledgeBase"] = Relationship(
        back_populates="tags", link_model=KnowledgeBaseTagLink
    )


# 知识库表
class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge_base"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(description="条目标题")
    # document_id: int | None = Field(default=None, foreign_key="document.id")  # Commented out - document table doesn't exist yet
    content: str = Field(description="条目内容")
    start_pos: int | None = Field(default=None, description="在文档中的起始位置/章节 - 可选")
    end_pos: int | None = Field(default=None, description="结束位置/章节 - 可选")
    embedding: bytes | None = Field(default=None)
    create_time: datetime | None = Field(default_factory=datetime.now)
    update_time: datetime | None = Field(default_factory=datetime.now)
    # history_ref: int | None = Field(default=None, foreign_key="history.id")  # Commented out - history table doesn't exist yet

    # 知识库与标签的多对多关系
    tags: list[Tag] = Relationship(
        back_populates="knowledge_bases", link_model=KnowledgeBaseTagLink
    )