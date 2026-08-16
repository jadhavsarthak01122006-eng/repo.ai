from datetime import datetime
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

async def triage_issue_with_ai(title: str, description: str, photo_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Use multimodal LLM to categorize and prioritize the issue.
    Returns category, department, confidence score, and severity estimate.
    """
    
    # Fallback rules engine if AI is not configured
    fallback_categories = {
        "pothole": ("Roads Department", 4),
        "garbage": ("Sanitation Department", 3),
        "streetlight": ("Electricity Department", 2),
        "drain": ("Water Department", 3),
        "graffiti": ("Public Works", 2),
    }
    
    # Check for keywords as fallback
    text_lower = f"{title} {description}".lower()
    for keyword, (dept, severity) in fallback_categories.items():
        if keyword in text_lower:
            return {
                "suggested_category": keyword,
                "suggested_department": dept,
                "confidence": 0.7,
                "severity_estimate": severity,
                "is_duplicate": False,
                "duplicate_candidate_id": None
            }
    
    # Default fallback
    return {
        "suggested_category": "general",
        "suggested_department": "Public Works",
        "confidence": 0.3,
        "severity_estimate": 2,
        "is_duplicate": False,
        "duplicate_candidate_id": None
    }
    
    # TODO: Implement actual AI call when API key is available
    # Example implementation with OpenAI-style API:
    """
    if not settings.AI_API_KEY:
        return fallback_logic()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.AI_API_ENDPOINT or "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.AI_API_KEY}"},
            json={
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Categorize this civic issue: {title}. Description: {description}"},
                            {"type": "image_url", "image_url": {"url": photo_url}} if photo_url else {}
                        ]
                    }
                ],
                "max_tokens": 300
            }
        )
        # Parse response and extract category, department, confidence
    """

async def check_for_duplicates(db: Any, latitude: float, longitude: float, 
                                title: str, description: str, 
                                radius_meters: float = 50.0) -> Optional[int]:
    """
    Check for duplicate reports within a radius using spatial queries and text similarity.
    Returns the ID of a potential duplicate if found.
    """
    from sqlalchemy import text
    from datetime import timedelta
    
    # Query for recent reports within radius (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    query = text("""
        SELECT id, title, description 
        FROM issue_reports 
        WHERE ST_DWithin(
            location,
            ST_MakePoint(:lon, :lat)::geography,
            :radius
        )
        AND status NOT IN ('rejected', 'verified')
        AND created_at > :cutoff
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    results = db.execute(query, {
        "lon": longitude,
        "lat": latitude,
        "radius": radius_meters,
        "cutoff": seven_days_ago
    }).fetchall()
    
    # Simple text similarity check (TODO: use pgvector for embeddings)
    from difflib import SequenceMatcher
    
    input_text = f"{title} {description}".lower()
    for row in results:
        existing_text = f"{row.title} {row.description}".lower()
        similarity = SequenceMatcher(None, input_text, existing_text).ratio()
        if similarity > 0.7:  # 70% similarity threshold
            return row.id
    
    return None
