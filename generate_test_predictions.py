import os
import pandas as pd
import json
from rag_system import SimpleSHLRecommender


def generate_test_predictions():
    """
    Generate assessment predictions for the test dataset
    and save them in the required CSV format.
    """

    print("📊 Loading test dataset...")

    # Load test queries from Excel
    test_df = pd.read_excel(
        "Gen_AI Dataset.xlsx",
        sheet_name="Test-Set"
    )

    print(f"✅ Loaded {len(test_df)} test queries")

    # Initialize RAG system
    print("🚀 Initializing RAG system...")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    rag_system = SimpleSHLRecommender(gemini_api_key=GEMINI_API_KEY)

    predictions = []

    # Process each query one by one
    for index, row in test_df.iterrows():
        query = row["Query"]

        try:
            # Generate top-K recommendations
            recommendations = rag_system.recommend(
                query,
                k=10
            )

            # Extract only URLs as required by evaluation format
            prediction_entry = {
                "query": query,
                "predictions": [
                    rec["url"] for rec in recommendations
                ]
            }

            predictions.append(prediction_entry)
            print(f"✅ Processed query {index + 1}: {query[:60]}...")

        except Exception as error:
            # Fail-safe: still record the query
            print(f"❌ Error processing query {index + 1}: {error}")
            predictions.append({
                "query": query,
                "predictions": []
            })

    # Save predictions to CSV
    output_df = pd.DataFrame(predictions)
    output_df.to_csv(
        "test_predictions.csv",
        index=False
    )

    print("\n🎉 Prediction generation completed!")
    print(f"📁 Output saved to: test_predictions.csv")
    print(f"📌 Total queries processed: {len(predictions)}")


# --------------------------------------------------
# Script Entry Point
# --------------------------------------------------

if __name__ == "__main__":
    generate_test_predictions()
