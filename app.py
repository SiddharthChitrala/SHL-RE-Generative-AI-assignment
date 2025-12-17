from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware

from rag_system import SimpleSHLRecommender

app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="AI-powered assessment recommendation system",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender
print("Initializing SHL Recommender...")
try:
    # Use environment variable or hardcode your key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_KEY_HERE")
    recommender = SimpleSHLRecommender(gemini_api_key=GEMINI_API_KEY)
    print("Recommender initialized")
except Exception as e:
    print(f"Error: {e}")
    recommender = None

# Request models
class QueryRequest(BaseModel):
    query: str
    max_duration: Optional[int] = None
    preferred_test_types: Optional[List[str]] = None

class AssessmentResponse(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]
    score: Optional[float] = None
    low_relevance: Optional[bool] = False

class RecommendationResponse(BaseModel):
    recommended_assessments: List[AssessmentResponse]

# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_assessments(request: QueryRequest):
    if recommender is None:
        raise HTTPException(status_code=503, detail="Recommender not available")
    
    try:
        # Get recommendations with filters
        raw_recs = recommender.recommend(
            request.query,
            k=10,
            max_duration=request.max_duration,
            preferred_test_types=request.preferred_test_types or []
        )
        
        # Format response
        formatted_recs = []
        for rec in raw_recs:
            formatted_recs.append(AssessmentResponse(
                url=rec['url'],
                name=rec['name'],
                adaptive_support=rec.get('adaptive_support', 'No'),
                description=rec.get('description', 'SHL Assessment'),
                duration=rec.get('duration', 40),
                remote_support=rec.get('remote_support', 'Yes'),
                test_type=rec.get('test_type', ['Knowledge & Skills']),
                score=rec.get('score'),
                low_relevance=rec.get('low_relevance', False)
            ))
        
        return RecommendationResponse(
            recommended_assessments=formatted_recs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "SHL Assessment API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "POST /recommend": "Get recommendations"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Use import string 'app:app' so uvicorn can enable reload/workers correctly
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)