import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from dotenv import load_dotenv # environment variables
from fastapi import FastAPI, File, HTTPException, Body, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, AIMessage

# Import our new AI service
from services_LLM import AIService, ModelConfig
# Import Pydantic models
from models_pydantic import ChatMessage, ChatRequest, ChatResponse
# Import database and utils
from database import create_db_and_tables
from utils_db import insert_application_logs, get_chat_history
from utils_chroma import index_document_to_chroma, delete_doc_from_chroma, get_vector_store
from utils_langchain import get_rag_chain

# Load environment variables from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# 模型配置文件路径
MODEL_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "model_config.json")

# Initialize AI service
ai_service = AIService(MODEL_CONFIG_FILE)

# Initialize database tables
create_db_and_tables()

class ConversationHistory:
    def __init__(self):
        self.conversations: Dict[str, List[ChatMessage]] = {}
    
    def add_message(self, conversation_id: str, message: ChatMessage):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        self.conversations[conversation_id].append(message)
    
    def get_messages(self, conversation_id: str) -> List[ChatMessage]:
        return self.conversations.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str):
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]

# Global conversation history
conversation_history = ConversationHistory()

app = FastAPI(
    title="LangChain Chat - InfoPoP",
    description="A simple API for interacting with LangChain chat models.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity; adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the InfoPoP Chat API!"}

@app.get("/models", response_model=List[ModelConfig])
async def get_available_models():
    """Get list of available AI models"""
    return ai_service.load_model_configs()

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Send a message to AI and get response"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get the chat model
        chat_model = ai_service.get_chat_model(request.model_name or "gpt-3.5-turbo")
        
        # Add user message to history
        user_message = ChatMessage(
            content=request.message,
            from_user=True,
            timestamp=datetime.now()
        )
        conversation_history.add_message(conversation_id, user_message)
        
        # Get conversation history for context
        messages = conversation_history.get_messages(conversation_id)
        
        # Convert to LangChain chat history format
        chat_history = []
        for msg in messages[:-1]:  # Exclude the current message
            if msg.from_user:
                chat_history.append(("human", msg.content))
            else:
                chat_history.append(("ai", msg.content))
        
        # Get AI response using RAG chain
        try:
            rag_chain = get_rag_chain(request.model_name or "gpt-3.5-turbo")
            response = await rag_chain.ainvoke({
                "input": request.message,
                "chat_history": chat_history
            })
            ai_response_content = response["answer"]
        except Exception as model_error:
            # Use AI service error handler
            raise ai_service.handle_ai_error(model_error, request.model_name or "gpt-3.5-turbo")
        
        if not ai_response_content:
            raise HTTPException(
                status_code=500, 
                detail="AI model returned empty response"
            )
        
        # Add AI message to history
        ai_message = ChatMessage(
            content=ai_response_content,
            from_user=False,
            timestamp=datetime.now()
        )
        conversation_history.add_message(conversation_id, ai_message)
        
        # Log to database
        insert_application_logs(
            session_id=conversation_id,
            user_query=request.message,
            gpt_response=ai_response_content,
            model=request.model_name or "gpt-3.5-turbo"
        )
        
        return ChatResponse(
            message=ai_response_content,
            conversation_id=conversation_id,
            model_used=request.model_name or "gpt-3.5-turbo",
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/conversation/{conversation_id}", response_model=List[ChatMessage])
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    return conversation_history.get_messages(conversation_id)

@app.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    conversation_history.clear_conversation(conversation_id)
    return {"message": "Conversation cleared successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/test-model/{model_name}")
async def test_model(model_name: str):
    """Test if a specific model is working"""
    return await ai_service.test_model(model_name)

@app.post("/upload-documents")
async def upload_and_index_documents(file: UploadFile = File(...)):
    """Endpoint to handle file uploads and index them into Chroma"""
    try:
        # Validate file type
        allowed_extensions = {".txt", ".pdf", ".docx", ".xlsx"}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Insert document record into database
        from utils_db import insert_document_record
        file_id = insert_document_record(file.filename)
        
        # Index document to Chroma vector store
        success = index_document_to_chroma(file_path, file_id)
        
        if success:
            return {
                "message": f"File '{file.filename}' uploaded and indexed successfully",
                "file_id": file_id,
                "filename": file.filename,
                "size": len(content)
            }
        else:
            # Clean up if indexing failed
            os.remove(file_path)
            from utils_db import delete_document_record
            delete_document_record(file_id)
            raise HTTPException(
                status_code=500,
                detail="Failed to index document to vector store"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file upload: {str(e)}"
        )

@app.get("/documents")
async def get_uploaded_documents():
    """Get list of all uploaded documents"""
    from utils_db import get_all_documents
    return get_all_documents()

@app.delete("/documents/{file_id}")
async def delete_document(file_id: int):
    """Delete a document from both database and vector store"""
    try:
        # Delete from Chroma vector store
        chroma_success = delete_doc_from_chroma(file_id)
        
        # Delete from database
        from utils_db import delete_document_record
        db_success = delete_document_record(file_id)
        
        if chroma_success and db_success:
            return {"message": f"Document {file_id} deleted successfully"}
        else:
            return {"message": f"Partial deletion completed for document {file_id}"}
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
