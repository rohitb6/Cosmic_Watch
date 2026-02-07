"""
Chatbot routes for AI-powered asteroid assistance
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.chatbot_service import ChatbotService
from app.schemas.schemas import ChatMessageRequest, ChatMessageResponse, ConversationResponse
from app.models.models import User

router = APIRouter(prefix="/chat", tags=["chatbot"])


# In-memory storage for conversations (can be moved to database for persistence)
conversations = {}


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI chatbot
    Receives intelligent responses about asteroids and NEO monitoring
    """
    try:
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid4())
        
        if conversation_id not in conversations:
            conversations[conversation_id] = {
                "user_id": user_id,
                "messages": [],
                "created_at": datetime.now(timezone.utc),
                "last_message_at": datetime.now(timezone.utc)
            }
        
        # Verify user owns this conversation
        if conversations[conversation_id]["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this conversation"
            )
        
        # Add user message to history
        conversation = conversations[conversation_id]
        conversation["messages"].append({
            "role": "user",
            "content": request.message
        })
        
        # Get AI response
        response_text = await ChatbotService.get_ai_response(
            db,
            request.message,
            conversation["messages"][:-1]  # Exclude the message we just added
        )
        
        # Add assistant response to history
        conversation["messages"].append({
            "role": "assistant",
            "content": response_text
        })
        
        conversation["last_message_at"] = datetime.now(timezone.utc)
        
        return ChatMessageResponse(
            response=response_text,
            conversation_id=conversation_id,
            timestamp=datetime.now(timezone.utc)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full conversation history"""
    
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conv = conversations[conversation_id]
    
    # Verify ownership
    if conv["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation"
        )
    
    return ConversationResponse(
        conversation_id=conversation_id,
        messages=conv["messages"],
        created_at=conv["created_at"],
        last_message_at=conv["last_message_at"]
    )


@router.get("/conversations", response_model=list)
def list_conversations(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user's conversations"""
    
    user_conversations = [
        {
            "conversation_id": conv_id,
            "created_at": conv["created_at"],
            "last_message_at": conv["last_message_at"],
            "message_count": len(conv["messages"]),
            "preview": conv["messages"][0]["content"][:100] if conv["messages"] else ""
        }
        for conv_id, conv in conversations.items()
        if conv["user_id"] == user_id
    ]
    
    return sorted(user_conversations, key=lambda x: x["last_message_at"], reverse=True)


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conv = conversations[conversation_id]
    
    # Verify ownership
    if conv["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation"
        )
    
    del conversations[conversation_id]
    
    return {"message": "Conversation deleted successfully"}
