"""
DEPRECATED: `rag_system_simple.py`

This module is a duplicate of the main API implementation and is deprecated.
Importing it will raise an error to prevent accidental use. Use `app.py`
or the `rag_system.py` recommender instead.
"""

raise RuntimeError(
    "rag_system_simple.py is deprecated. Use `app.py` or the `rag_system` module instead."
)

   try:
        # Get recommendations from our system
        raw_recommendations = recommender.recommend(request.query, k=10)

        # Format response exactly as required by SHL
        formatted_assessments = []
        for rec in raw_recommendations[:10]:  # Max 10 as required
            formatted_assessments.append(AssessmentResponse(
                url=rec['url'],
                name=rec['name'],
                adaptive_support=rec.get('adaptive_support', 'No'),
                description=rec.get('description', 'SHL Assessment'),
                duration=rec.get('duration', 40),
                remote_support=rec.get('remote_support', 'Yes'),
                test_type=rec.get('test_type', ['Knowledge & Skills'])
            ))

        return RecommendationResponse(
            recommended_assessments=formatted_assessments
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )

# Root endpoint with API information

@app.get("/")
async def root():
    """API information and available endpoints"""
    return {
        "message": "SHL Assessment Recommendation API",
        "version": "1.0.0",
        "author": "SHL AI Intern Assignment",
        "endpoints": {
            "GET /": "This information",
            "GET /health": "Health check (returns status)",
            "POST /recommend": "Get assessment recommendations",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation"
        },
        "requirements": {
            "minimum_recommendations": 1,
            "maximum_recommendations": 10,
            "response_format": "JSON with specific fields",
            "input": "Natural language query or job description"
        }
    }

# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))

    print(f"\n🌐 API will be available at: http://localhost:{port}")
    print("📚 Documentation: http://localhost:{port}/docs")
    print("🩺 Health check: http://localhost:{port}/health")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True  # Auto-reload on code changes
    )
