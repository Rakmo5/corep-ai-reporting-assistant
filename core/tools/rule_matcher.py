import numpy as np


class RuleMatcher:
    """
    Matches COREP fields to most relevant rules using embeddings.
    """

    FIELD_DESCRIPTIONS = {
        "cet1": "Common Equity Tier 1 capital",
        "at1": "Additional Tier 1 capital",
        "tier1": "Tier 1 capital CET1 plus AT1",
        "tier2": "Tier 2 capital instruments",
        "total": "Total regulatory capital",
        "rwa": "Risk weighted assets",
        "cet1_ratio": "CET1 capital divided by RWA",
        "tier1_ratio": "Tier 1 capital divided by RWA",
        "total_ratio": "Total capital divided by RWA"
    }

    @staticmethod
    def cosine_similarity(a, b):
        return np.dot(a, b) / (
            np.linalg.norm(a) * np.linalg.norm(b) + 1e-8
        )

    @classmethod
    def match_fields(cls, embedder, store, chunks, top_k=2):
        """
        Returns best matching rule for each field.
        """

        matches = {}

        for field, desc in cls.FIELD_DESCRIPTIONS.items():

            # Embed field description
            field_vec = embedder.embed([desc])[0]

            # Get top-k rule indices
            indices = store.search(field_vec, top_k=top_k)

            best_rules = [chunks[i] for i in indices]

            matches[field] = best_rules

        return matches
