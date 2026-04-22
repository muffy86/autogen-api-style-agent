"""Switzerland Public AI Ecosystem - Swiss-based AI Providers and Resources.

Switzerland has a strong privacy-focused AI ecosystem with world-class research
and ethical AI development. This module integrates Swiss AI providers.

Resources:
- ETH Zurich AI Center: https://ai.ethz.ch
- IDSIA (Dalle Molle Institute): https://idsia.ch
- Swisscom AI: https://www.swisscom.ch/ai
- LatticeFlow AI: https://latticeflow.ai
- FAIR (Franco-Swiss AI Research): https://www.epfl.ch/labs/fair/
"""

from __future__ import annotations

from typing import Any

PROVIDERS = {
    "eth_zurich": {
        "name": "ETH Zurich AI Center",
        "description": "World-leading AI research at ETH Zurich",
        "url": "https://ai.ethz.ch",
        "models": ["eth-llm", "swiss-llm"],
        "location": "Zurich, Switzerland",
        "privacy": "GDPR compliant, Swiss data residency",
        "api_docs": "https://ai.ethz.ch/docs",
    },
    "idsia": {
        "name": "IDSIA - Dalle Molle Institute",
        "description": "Pioneering AI/ML research since 1988",
        "url": "https://idsia.ch",
        "specialties": ["neural networks", "reinforcement learning", "RNNs"],
        "location": "Manno, Ticino, Switzerland",
        "privacy": "Privacy-preserving AI research",
        "api_docs": "https://idsia.ch/research",
    },
    "swisscom_ai": {
        "name": "Swisscom AI",
        "description": "Switzerland's telecom AI services",
        "url": "https://www.swisscom.ch/ai",
        "models": ["swisscom-gpt", "swisscom-ocr"],
        "location": "Bern, Switzerland",
        "privacy": "Swiss data law compliant",
        "api_docs": "https://developer.swisscom.ch/ai",
    },
    "latticeflow": {
        "name": "LatticeFlow AI",
        "description": "Enterprise AI platform from Zurich",
        "url": "https://latticeflow.ai",
        "models": ["lattice-vision", "lattice-nlp"],
        "location": "Zurich, Switzerland",
        "privacy": "GDPR, EU AI Act compliant",
        "api_docs": "https://docs.latticeflow.ai",
    },
    "epfl_fair": {
        "name": "EPFL FAIR Lab",
        "description": "Foundations of Adaptive and Intelligent Robots",
        "url": "https://www.epfl.ch/labs/fair",
        "specialties": ["robotics", "vision", "language"],
        "location": "Lausanne, Switzerland",
        "privacy": "Academic research standards",
        "api_docs": "https://fair.epfl.ch",
    },
    "zero_ai": {
        "name": "Zero AI",
        "description": "Privacy-first Swiss AI startup",
        "url": "https://zero.ai",
        "models": ["zero-chat", "zero-code"],
        "location": "Geneva, Switzerland",
        "privacy": "End-to-end encryption, Swiss hosting",
        "api_docs": "https://docs.zero.ai",
    },
    "deepmind_zurich": {
        "name": "Google DeepMind Zurich",
        "description": "DeepMind's European AI research hub",
        "url": "https://deepmind.google/locations/zurich",
        "location": "Zurich, Switzerland",
        "privacy": "Google privacy framework",
        "api_docs": "https://deepmind.google",
    },
    "ora": {
        "name": "Ora AI",
        "description": "Swiss conversational AI",
        "url": "https://ora.ai",
        "models": ["ora-assistant"],
        "location": "Zurich, Switzerland",
        "privacy": "GDPR compliant",
        "api_docs": "https://ora.ai/developers",
    },
}

INSTITUTIONS = {
    "eth_ai_center": {
        "name": "ETH Zurich AI Center",
        "url": "https://ai.ethz.ch",
        "focus": ["foundation models", "robotics", "healthcare AI"],
    },
    "epfl_ai": {
        "name": "EPFL AI Initiative",
        "url": "https://www.epfl.ch/research/ai",
        "focus": ["ML", "NLP", "computer vision"],
    },
    "uni_zurich_ml": {
        "name": "University of Zurich ML Group",
        "url": "https://ml.informatik.uzh.ch",
        "focus": ["machine learning", "deep learning"],
    },
    "idsia": {
        "name": "IDSIA",
        "url": "https://idsia.ch",
        "focus": ["deep learning", "time series"],
    },
}

GRANTS = {
    "swiss_ai_fund": {
        "name": "Swiss AI Fund",
        "url": "https://swiss-ai.ch",
        "description": "Funding for AI startups in Switzerland",
    },
    "innosuisse": {
        "name": "Innosuisse",
        "url": "https://www.innosuisse.ch",
        "description": "Swiss Innovation Agency",
    },
    "euro_hpc": {
        "name": "EuroHPC Switzerland",
        "url": "https://eth-cscs.ch",
        "description": "European HPC resources",
    },
}


class SwissAIClient:
    """Client for Swiss AI providers."""

    def __init__(self, provider: str, api_key: str | None = None):
        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")
        self.provider = provider
        self.config = PROVIDERS[provider]
        self.api_key = api_key

    def get_models(self) -> list[str]:
        """Get available models for provider."""
        return self.config.get("models", [])

    def get_info(self) -> dict[str, Any]:
        """Get provider information."""
        return {
            "name": self.config["name"],
            "description": self.config["description"],
            "url": self.config["url"],
            "privacy": self.config.get("privacy", "N/A"),
            "location": self.config.get("location", "N/A"),
            "models": self.get_models(),
        }


def list_all_providers() -> list[dict[str, Any]]:
    """List all Swiss AI providers."""
    return [
        {
            "id": k,
            "name": v["name"],
            "description": v["description"],
            "privacy": v.get("privacy", ""),
            "location": v.get("location", ""),
        }
        for k, v in PROVIDERS.items()
    ]


def list_institutions() -> list[dict[str, Any]]:
    """List Swiss AI research institutions."""
    return [{"id": k, "name": v["name"], "url": v["url"], "focus": v["focus"]}
            for k, v in INSTITUTIONS.items()]


def list_grants() -> list[dict[str, Any]]:
    """List Swiss AI funding opportunities."""
    return [{"id": k, "name": v["name"], "url": v["url"], "description": v["description"]}
            for k, v in GRANTS.items()]


def get_swiss_stats() -> dict[str, Any]:
    """Get Swiss AI ecosystem statistics."""
    return {
        "providers": len(PROVIDERS),
        "institutions": len(INSTITUTIONS),
        "funding_programs": len(GRANTS),
        "highlights": [
            "Home to world-leading AI research at ETH Zurich and EPFL",
            "Strict data privacy laws (Swiss DSG, GDPR compliant)",
            "Neutral data hosting with Swiss infrastructure",
            "Strong fintech + healthcare AI ecosystem",
        ],
    }