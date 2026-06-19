from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings


class StableEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self) -> None:
        pass

    def __call__(self, input: Documents) -> Embeddings:
        embeddings: list[list[float]] = []
        for text in input:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            embeddings.append([((byte / 255.0) * 2.0) - 1.0 for byte in digest])
        return embeddings

    @staticmethod
    def name() -> str:
        return "stable-sha256"

    @staticmethod
    def build_from_config(config: dict[str, Any]) -> StableEmbeddingFunction:
        return StableEmbeddingFunction()

    def get_config(self) -> dict[str, Any]:
        return {"dimensions": 32, "algorithm": "sha256-bytes"}


@dataclass
class MemoryEntry:
    id: str
    document: str
    metadata: dict


class ForeverMemory:
    """ChromaDB-backed persistent memory. One collection per namespace."""

    def __init__(self, path: Path, collection: str = "forever_memory") -> None:
        path.mkdir(parents=True, exist_ok=True)
        self._client = PersistentClient(path=str(path))
        self._collection: Collection = self._client.get_or_create_collection(
            collection,
            embedding_function=StableEmbeddingFunction(),
        )

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]

    def add(self, document: str, metadata: dict | None = None, doc_id: str | None = None) -> str:
        doc_id = doc_id or self._hash(document)
        self._collection.upsert(
            ids=[doc_id],
            documents=[document],
            metadatas=[metadata or {}],
        )
        return doc_id

    def add_many(self, entries: Iterable[MemoryEntry]) -> list[str]:
        batch = list(entries)
        if not batch:
            return []
        self._collection.upsert(
            ids=[entry.id for entry in batch],
            documents=[entry.document for entry in batch],
            metadatas=[entry.metadata for entry in batch],
        )
        return [entry.id for entry in batch]

    def query(self, text: str, n_results: int = 5) -> list[dict]:
        if self._collection.count() == 0:
            return []
        result = self._collection.query(query_texts=[text], n_results=n_results)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        ids = result.get("ids", [[]])[0]
        return [
            {"id": entry_id, "document": document, "metadata": metadata}
            for entry_id, document, metadata in zip(ids, docs, metas)
        ]

    def peek(self, limit: int = 10) -> list[dict]:
        if self._collection.count() == 0:
            return []
        result = self._collection.peek(limit=limit)
        docs = result.get("documents", [])
        metas = result.get("metadatas", [])
        ids = result.get("ids", [])
        return [
            {"id": entry_id, "document": document, "metadata": metadata}
            for entry_id, document, metadata in zip(ids, docs, metas)
        ]

    def count(self) -> int:
        return self._collection.count()
