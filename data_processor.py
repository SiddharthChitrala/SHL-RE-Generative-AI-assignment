import pandas as pd
import numpy as np
import json
# Heavy dependencies (sentence-transformers, faiss) are imported lazily inside create_embeddings
# so the data extraction can run without them. This allows generating `shl_assessments.csv`
# even when the environment lacks those packages.


class SHLDataProcessor:
    """
    Handles loading SHL assessment data from Excel,
    cleaning it, and creating embeddings for retrieval (RAG).
    """

    def __init__(self, excel_path: str = "Gen_AI Dataset.xlsx"):
        """
        Initialize the data processor.

        Parameters:
        excel_path (str): Path to the Excel dataset
        """
        self.excel_path = excel_path

        # Model will be created lazily when embeddings are needed
        self.model = None
        self.embedding_model_name = "all-MiniLM-L6-v2"  # used when creating embeddings

    def load_and_process_data(self):
        """
        Load the Excel file, extract unique assessments,
        and prepare train/test data.

        Returns:
        assessments_df (DataFrame): Unique assessment details
        train_df (DataFrame): Training dataset
        test_df (DataFrame): Testing dataset
        """
        print("📊 Loading Excel dataset...")

        # Read train and test sheets
        train_df = pd.read_excel(self.excel_path, sheet_name="Train-Set")
        test_df = pd.read_excel(self.excel_path, sheet_name="Test-Set")

        print(f"✅ Loaded {len(train_df)} train samples")
        print(f"✅ Loaded {len(test_df)} test samples")

        assessments = []
        seen_urls = set()  # Used to avoid duplicate assessments

        # Extract unique assessment URLs from training data
        for _, row in train_df.iterrows():
            url = row["Assessment_url"]

            # Skip empty or duplicate URLs
            if pd.notna(url) and url not in seen_urls:
                assessment_name = self.extract_name_from_url(url)

                assessments.append({
                    "name": assessment_name,
                    "url": url,
                    "description": self.get_assessment_description(assessment_name)
                })

                seen_urls.add(url)

        # Convert list of assessments into DataFrame
        assessments_df = pd.DataFrame(assessments)
        print(f"✅ Extracted {len(assessments_df)} unique assessments")

        # Save assessments for RAG usage
        assessments_df.to_csv("shl_assessments.csv", index=False)

        # Save unique train queries (useful for evaluation)
        train_df[["Query"]].drop_duplicates().to_csv(
            "train_queries.csv", index=False
        )

        return assessments_df, train_df, test_df

    def extract_name_from_url(self, url: str) -> str:
        """
        Extract a clean, readable assessment name from the URL.

        Example:
        https://.../view/java-programming-new → Java Programming
        """
        try:
            if "/view/" in url:
                name = url.split("/view/")[-1].split("/")[0]
            else:
                name = url.split("/")[-1]

            # Clean formatting
            name = (
                name.replace("-new", "")
                    .replace("-", " ")
                    .replace("_", " ")
                    .title()
            )

            return name
        except Exception:
            # Fallback in case URL format is unexpected
            return "SHL Assessment"

    def get_assessment_description(self, name: str) -> str:
        """
        Generate a simple text description based on keywords
        found in the assessment name.
        """
        keyword_map = {
            "java": "Java programming skills assessment",
            "python": "Python programming skills test",
            "sql": "SQL database skills assessment",
            "selenium": "Selenium automation testing",
            "javascript": "JavaScript programming test",
            "html": "HTML/CSS web development skills",
            "css": "CSS styling and design skills",
            "sales": "Sales skills and aptitude assessment",
            "marketing": "Marketing skills evaluation",
            "communication": "Communication skills test",
            "personality": "Personality assessment",
            "cognitive": "Cognitive ability test",
            "analytical": "Analytical skills assessment",
            "numerical": "Numerical reasoning test",
            "verbal": "Verbal reasoning assessment",
            "leadership": "Leadership skills evaluation",
            "management": "Management skills test",
            "technical": "Technical skills assessment",
        }

        description = "SHL assessment for "
        name_lower = name.lower()

        matched_descriptions = [
            text for key, text in keyword_map.items()
            if key in name_lower
        ]

        # Limit to top 3 matched keywords to keep it concise
        if matched_descriptions:
            description += ", ".join(matched_descriptions[:3])
        else:
            description += "evaluating job-related skills"

        return description

    def create_embeddings(self, assessments_df: pd.DataFrame):
        """
        Create vector embeddings for assessments and
        store them using FAISS for similarity search.

        Returns:
        embeddings (ndarray): Generated embeddings
        index (faiss.Index): FAISS index
        """
        print("🔢 Creating embeddings...")

        # Import heavy libraries here so the rest of the script can run without them
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            raise RuntimeError(
                "sentence-transformers is required to create embeddings. "
                "Install the package or run the script with --no-embeddings to skip this step."
            ) from e

        try:
            import faiss
        except Exception as e:
            raise RuntimeError(
                "faiss is required to create and save the FAISS index. "
                "Install faiss-cpu or run the script with --no-embeddings to skip this step."
            ) from e

        # Initialize model if not already created
        if self.model is None:
            self.model = SentenceTransformer(self.embedding_model_name)

        # Combine name and description into a single text input
        texts = (
            assessments_df["name"] + ". " + assessments_df["description"]
        ).tolist()

        # Generate sentence embeddings
        embeddings = self.model.encode(
            texts, show_progress_bar=True
        )

        # Build FAISS index
        embedding_dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(embedding_dim)
        index.add(embeddings.astype("float32"))

        # Persist embeddings and FAISS index
        np.save("assessments_embeddings.npy", embeddings)
        faiss.write_index(index, "faiss_index.bin")

        # Save metadata for retrieval
        with open("assessments_metadata.json", "w") as file:
            json.dump(
                {
                    "names": assessments_df["name"].tolist(),
                    "urls": assessments_df["url"].tolist(),
                    "descriptions": assessments_df["description"].tolist(),
                },
                file,
                indent=2
            )

        print(f"✅ Created embeddings for {len(texts)} assessments")
        print(f"✅ FAISS index dimension: {embedding_dim}")

        return embeddings, index


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process SHL dataset and optionally create embeddings")
    parser.add_argument(
        "--no-embeddings",
        action="store_true",
        help="Skip creating embeddings and FAISS index (useful when heavy deps are not installed)"
    )

    args = parser.parse_args()

    # Initialize processor
    processor = SHLDataProcessor()

    # Load and clean data
    assessments_df, train_df, test_df = processor.load_and_process_data()

    # Optionally create embeddings
    if not args.no_embeddings:
        try:
            embeddings, index = processor.create_embeddings(assessments_df)
        except Exception as e:
            print(f"⚠️ Failed to create embeddings: {e}")
            print("You can re-run the script with --no-embeddings to skip embedding creation.")

    print("\n📋 Sample Assessments:")
    print(assessments_df.head())
