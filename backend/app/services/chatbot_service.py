"""
AI Chatbot service for Cosmic Watch
Provides intelligent responses about asteroids and NEO monitoring
"""
from typing import List, Optional
from datetime import datetime, timezone
import httpx
import json
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Asteroid
from app.schemas.schemas import AsteroidDetailResponse


class ChatMessage:
    """Represents a chat message"""
    def __init__(self, role: str, content: str):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class ChatbotService:
    """Handle AI chatbot interactions for asteroid monitoring"""
    
    @staticmethod
    def get_system_prompt(db: Session) -> str:
        """Generate system prompt with current asteroid statistics"""
        total_asteroids = db.query(Asteroid).count()
        hazardous_count = db.query(Asteroid).filter(Asteroid.is_hazardous == True).count()
        
        return f"""You are an expert AI assistant for Cosmic Watch, a Near-Earth Object (NEO) monitoring system.

CURRENT STATUS:
- Total Asteroids Monitored: {total_asteroids}
- Potentially Hazardous Asteroids (PHAs): {hazardous_count}
- Last NASA Sync: Today

YOUR EXPERTISE:
1. Asteroid and NEO information (names, sizes, orbital characteristics)
2. Collision risk assessment using the Cosmic Risk Index (CRI)
3. Close approach predictions and timing
4. Planetary defense and mitigation strategies
5. Asteroid classification and properties
6. Mission planning and observation recommendations

RESPONSE GUIDELINES:
- Provide accurate, scientifically-backed information
- Use metrics: diameter in km, velocity in km/h, miss distance in km
- Explain risk levels: MINIMAL (0-20), LOW (21-40), MODERATE (41-60), HIGH (61-80), CRITICAL (81-100)
- Be professional but accessible
- When users ask about specific asteroids, provide context about their last known close approach
- Offer actionable insights for monitoring and defense planning
- Correct misconceptions about asteroid impact risks

Always respond in the knowledge domain of asteroid monitoring and planetary defense."""

    @staticmethod
    async def get_ai_response(
        db: Session,
        message: str,
        conversation_history: List[dict]
    ) -> str:
        """
        Get AI response using OpenAI API
        Uses chat history for context-aware conversations
        """
        
        # If no API key, return helpful default response
        if not settings.openai_api_key:
            return ChatbotService.get_fallback_response(message, db)
        
        try:
            # Prepare system prompt with current data
            system_prompt = ChatbotService.get_system_prompt(db)
            
            # Prepare conversation messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            messages.extend(conversation_history[-6:])  # Last 3 exchanges for context
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.openai_model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500,
                        "top_p": 0.9
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return ChatbotService.get_fallback_response(message, db)
                    
        except Exception as e:
            return ChatbotService.get_fallback_response(message, db)
    
    @staticmethod
    def get_fallback_response(message: str, db: Session) -> str:
        """
        Provide intelligent responses without OpenAI
        Uses pattern matching on user queries
        """
        msg_lower = message.lower()
        
        # Asteroid status queries
        if any(word in msg_lower for word in ["how many", "total", "count", "asteroids"]):
            total = db.query(Asteroid).count()
            hazardous = db.query(Asteroid).filter(Asteroid.is_hazardous == True).count()
            return f"We are currently monitoring {total} asteroids, including {hazardous} potentially hazardous ones. This data is updated daily from NASA's NeoWs API."
        
        # Risk/hazard queries
        if any(word in msg_lower for word in ["risk", "danger", "hazard", "threat"]):
            return "Risk assessment in Cosmic Watch uses our proprietary Cosmic Risk Index (CRI), which combines: asteroid diameter (30%), velocity (25%), miss distance (25%), and hazard status (20%). A score of 81+ indicates CRITICAL risk level requiring immediate attention."
        
        # How to use queries
        if any(word in msg_lower for word in ["how do i", "how to", "use", "help"]):
            return "You can: 1) Monitor asteroids in the Dashboard, 2) View real-time NASA data in Observatory, 3) Learn about our AI risk algorithm in AI Scoring, 4) Track asteroids in Watchlist, 5) Set up alerts for approaching objects. What would you like to explore?"
        
        # CRI explanation
        if "cri" in msg_lower or "risk index" in msg_lower or "scoring" in msg_lower:
            return "The Cosmic Risk Index (CRI) is our AI-powered scoring system (0-100 scale). It calculates collision risk by analyzing: proximity to Earth, asteroid size and density, relative velocity, and known hazard classification. Higher scores indicate higher impact risk."
        
        # Observation/mission queries
        if any(word in msg_lower for word in ["observe", "mission", "telescope", "tracking"]):
            return "For optimal asteroid observation: track closest approaches using our Observatory page, monitor high-risk objects via Watchlist, and set up custom alerts. Our platform integrates with NASA's tracking data for accuracy."
        
        # Planetary defense
        if any(word in msg_lower for word in ["defense", "deflection", "mitigation", "impact", "prevent"]):
            return "Planetary defense strategies include: early detection (5-10 years advance warning), kinetic impactors for smaller objects, and gravity tractor assists. Our monitoring system provides the early warning essential for effective mitigation."
        
        # Default helpful response
        total = db.query(Asteroid).count()
        return f"I'm your Cosmic Watch AI assistant! I can help you understand the {total} asteroids we're monitoring. Ask me about specific asteroids, risk assessment, how to use our platform, or planetary defense strategies. What interests you?"
    
    @staticmethod
    def search_asteroid_info(db: Session, query: str) -> Optional[str]:
        """
        Search for asteroid info in database
        Returns formatted asteroid information if found
        """
        query_lower = query.lower()
        
        # Search by name
        asteroid = db.query(Asteroid).filter(
            Asteroid.name.ilike(f"%{query_lower}%")
        ).first()
        
        if asteroid:
            info = f"\n**{asteroid.name}** (NEO ID: {asteroid.neo_id})\n"
            info += f"Diameter: {asteroid.diameter_km:.2f} km\n" if asteroid.diameter_km else ""
            info += f"Hazardous: {'Yes ⚠️' if asteroid.is_hazardous else 'No ✓'}\n"
            info += f"Last NASA Sync: {asteroid.nasa_synced_at.strftime('%Y-%m-%d %H:%M UTC') if asteroid.nasa_synced_at else 'Not synced'}\n"
            return info
        
        return None
