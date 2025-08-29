from sqlmodel import SQLModel, Field, Session, select
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from database import engine

# SQLModel table definitions
class ApplicationLog(SQLModel, table=True):
    __tablename__ = "application_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    user_query: str
    gpt_response: str
    model: str
    created_at: datetime = Field(default_factory=datetime.now)

class DocumentStore(SQLModel, table=True):
    __tablename__ = "document_store"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    upload_timestamp: datetime = Field(default_factory=datetime.now)

# Database operations using SQLModel ORM
def insert_application_logs(session_id: str, user_query: str, gpt_response: str, model: str) -> int:
    """Insert a new application log record"""
    with Session(engine) as session:
        log = ApplicationLog(
            session_id=session_id,
            user_query=user_query,
            gpt_response=gpt_response,
            model=model
        )
        session.add(log)
        session.commit()
        session.refresh(log)
        return log.id

def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """Get chat history for a specific session"""
    with Session(engine) as session:
        statement = select(ApplicationLog).where(
            ApplicationLog.session_id == session_id
        ).order_by(ApplicationLog.created_at)
        
        logs = session.exec(statement).all()
        
        messages = []
        for log in logs:
            messages.extend([
                {"role": "human", "content": log.user_query},
                {"role": "ai", "content": log.gpt_response}
            ])
        return messages

def insert_document_record(filename: str) -> int:
    """Insert a new document record and return its ID"""
    with Session(engine) as session:
        document = DocumentStore(filename=filename)
        session.add(document)
        session.commit()
        session.refresh(document)
        return document.id

def delete_document_record(file_id: int) -> bool:
    """Delete a document record by ID"""
    with Session(engine) as session:
        statement = select(DocumentStore).where(DocumentStore.id == file_id)
        document = session.exec(statement).first()
        
        if document:
            session.delete(document)
            session.commit()
            return True
        return False

def get_all_documents() -> List[Dict]:
    """Get all documents ordered by upload timestamp (newest first)"""
    with Session(engine) as session:
        statement = select(DocumentStore).order_by(DocumentStore.upload_timestamp.desc())
        documents = session.exec(statement).all()
        
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "upload_timestamp": doc.upload_timestamp
            }
            for doc in documents
        ]

def get_application_logs_by_session(session_id: str) -> List[ApplicationLog]:
    """Get all application logs for a specific session"""
    with Session(engine) as session:
        statement = select(ApplicationLog).where(
            ApplicationLog.session_id == session_id
        ).order_by(ApplicationLog.created_at)
        return session.exec(statement).all()

def get_recent_logs(limit: int = 10) -> List[ApplicationLog]:
    """Get recent application logs"""
    with Session(engine) as session:
        statement = select(ApplicationLog).order_by(
            ApplicationLog.created_at.desc()
        ).limit(limit)
        return session.exec(statement).all()

def delete_old_logs(days: int = 30) -> int:
    """Delete logs older than specified days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    with Session(engine) as session:
        statement = select(ApplicationLog).where(
            ApplicationLog.created_at < cutoff_date
        )
        old_logs = session.exec(statement).all()
        count = len(old_logs)
        
        for log in old_logs:
            session.delete(log)
        session.commit()
        return count