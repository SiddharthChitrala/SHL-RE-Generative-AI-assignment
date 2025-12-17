import pandas as pd
import numpy as np
import json
import re
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

# Use scikit-learn instead of sentence-transformers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    print("Warning: Gemini not available. Using TF-IDF search only.")

class SimpleSHLRecommender:
    def __init__(self, gemini_api_key=None):
        print("Initializing Simple SHL Recommender...")
        
        # Load data
        self.assessments_df = pd.read_csv('shl_assessments.csv')
        print(f"Loaded {len(self.assessments_df)} assessments")
        
        # Create text corpus for similarity search
        self.corpus = (self.assessments_df['name'] + " " + 
                      self.assessments_df['description']).tolist()
        
        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
        print("Created TF-IDF vectors")
        
        # Initialize Gemini if available
        self.use_gemini = False
        if GEMINI_AVAILABLE and gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini = genai.GenerativeModel('gemini-pro')
                self.use_gemini = True
                print("Gemini LLM initialized")
            except:
                print("⚠️ Gemini failed. Using TF-IDF only.")
        
        # Test type mapping
        self.test_type_mapping = {
            'K': 'Knowledge & Skills',
            'P': 'Personality & Behavior',
            'A': 'Ability & Aptitude',
            'S': 'Simulations'
        }
        
        print("Recommender ready!")
    
    def search_similar(self, query: str, k: int = 20) -> List[Dict]:
        """Search for similar assessments using TF-IDF cosine similarity"""
        # Transform query to TF-IDF
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = similarities.argsort()[-k:][::-1]
        
        # Get results
        results = []
        for idx in top_indices:
            row = self.assessments_df.iloc[idx]
            results.append({
                'name': row['name'],
                'url': row['url'],
                'description': row['description'],
                'score': float(similarities[idx]),
                'index': int(idx)
            })
        
        return results
    
    def infer_attributes(self, name: str) -> Dict:
        """Infer test attributes based on assessment name"""
        name_lower = name.lower()
        
        # Determine test types
        test_types = []
        if any(word in name_lower for word in ['java', 'python', 'sql', 'javascript', 'html', 'css', 'technical', 'programming']):
            test_types.append('K')
        if any(word in name_lower for word in ['personality', 'communication', 'behavior', 'leadership']):
            test_types.append('P')
        if any(word in name_lower for word in ['cognitive', 'numerical', 'verbal', 'analytical']):
            test_types.append('A')
        
        if not test_types:
            test_types = ['K']
        
        return {
            'adaptive_support': 'Yes' if 'adaptive' in name_lower else 'No',
            'remote_support': 'Yes',
            'duration': 40,  # Default
            'test_type': [self.test_type_mapping.get(t, t) for t in test_types]
        }
    
    def recommend(self, query: str, k: int = 10, max_duration: int | None = None, preferred_test_types: List[str] = None) -> List[Dict]:
        """Main recommendation function with filtering, boosting and safer diversification."""
        print(f"Processing query: {query[:80]}...")
        preferred_test_types = preferred_test_types or []
        
        # Get candidate pool
        candidates = self.search_similar(query, k=100)
        
        # relevance threshold to mark low-quality matches
        threshold = 0.02
        
        if not candidates:
            print("No candidates found")
            return []

        # Attach inferred attributes, dedupe, and apply duration filter
        enriched = []
        seen_urls = set()
        for rec in candidates:
            attrs = self.infer_attributes(rec['name'])
            rec.update(attrs)

            # ensure score exists and is float
            rec['score'] = float(rec.get('score', 0.0))

            # avoid duplicates
            if rec['url'] in seen_urls:
                continue
            seen_urls.add(rec['url'])

            # filter by max_duration if provided
            if max_duration and rec.get('duration') and rec['duration'] > max_duration:
                continue

            # boost if preferred types
            if preferred_test_types:
                rec_types = rec.get('test_type', [])
                if any(t in rec_types for t in preferred_test_types):
                    rec['score'] += 0.15  # boost

            # mark low relevance if under threshold
            rec['low_relevance'] = rec['score'] < threshold

            enriched.append(rec)

        if not enriched:
            print("No candidates left after filtering")
            return []

        # Sort enriched by score desc
        enriched.sort(key=lambda x: x.get('score', 0.0), reverse=True)

        # Remove very low-scoring items (but keep enough items)
        threshold = 0.02
        high_quality = [r for r in enriched if r['score'] >= threshold]
        if len(high_quality) >= k:
            candidate_pool = high_quality
        else:
            # include slightly lower results to fill
            candidate_pool = enriched

        # Group by top test type and sort each group by score desc
        groups = {}
        for rec in candidate_pool:
            t0 = rec.get('test_type', ['Knowledge & Skills'])[0]
            groups.setdefault(t0, []).append(rec)
        for t in groups:
            groups[t].sort(key=lambda x: x.get('score', 0.0), reverse=True)

        # Round-robin selection but prefer groups with higher next-item score
        result = []
        while len(result) < k and any(groups.values()):
            # compute next candidates (t, next_score)
            next_items = []
            for t, lst in groups.items():
                if lst:
                    next_items.append((t, lst[0].get('score', 0.0)))
            # sort groups by the next candidate's score desc
            next_items.sort(key=lambda x: x[1], reverse=True)
            # pick one from the top group
            for t, _ in next_items:
                if not groups.get(t):
                    continue
                result.append(groups[t].pop(0))
                if len(result) >= k:
                    break
            # clean empty groups
            empty = [t for t, lst in groups.items() if not lst]
            for t in empty:
                groups.pop(t, None)

        # Final trim
        result = result[:k]
        print(f"Generated {len(result)} recommendations")
        return result

# Test
if __name__ == "__main__":
    print("Testing Simple Recommender...")
    recommender = SimpleSHLRecommender()
    
    test_query = "I need a Java developer with communication skills"
    results = recommender.recommend(test_query, k=5)
    
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['name']}")
        print(f"   Score: {r['score']:.3f}")
        print(f"   Types: {', '.join(r['test_type'])}")
        print()