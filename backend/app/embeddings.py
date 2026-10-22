import hashlib
import json
import math
import os
import re
import unicodedata
import urllib.error
import urllib.request
from typing import Protocol


HASH_EMBEDDING_DIMENSIONS = 64
MIN_SEARCH_TOKEN_LENGTH = 2
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_EMBEDDING_BASE_URL = "https://api.openai.com/v1/embeddings"


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]:
        pass


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFC", text).casefold()
    return re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)


def searchable_tokens(text: str) -> set[str]:
    return {token for token in tokenize(text) if len(token) >= MIN_SEARCH_TOKEN_LENGTH}


class HashEmbeddingProvider:
    def __init__(self, dimensions: int = HASH_EMBEDDING_DIMENSIONS):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=2).digest()
            index = int.from_bytes(digest, "big") % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class OpenAICompatibleEmbeddingProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = DEFAULT_EMBEDDING_BASE_URL,
        timeout_seconds: float = 20.0,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    def embed(self, text: str) -> list[float]:
        payload = json.dumps({"model": self.model, "input": text}).encode("utf-8")
        request = urllib.request.Request(
            self.base_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise RuntimeError("Embedding provider request failed") from exc

        data = json.loads(body)
        embedding = data.get("data", [{}])[0].get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise RuntimeError("Embedding provider returned an invalid embedding")
        return [float(value) for value in embedding]


def get_embedding_provider() -> EmbeddingProvider:
    provider = os.environ.get("EMBEDDING_PROVIDER", "hash").strip().lower()
    if provider in {"hash", "local", "offline"}:
        return HashEmbeddingProvider()
    if provider in {"openai", "openai_compatible", "http"}:
        api_key = os.environ.get("EMBEDDING_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("EMBEDDING_API_KEY is required for HTTP embeddings")
        return OpenAICompatibleEmbeddingProvider(
            api_key=api_key,
            model=os.environ.get("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
            base_url=os.environ.get("EMBEDDING_BASE_URL", DEFAULT_EMBEDDING_BASE_URL),
        )
    raise RuntimeError(f"Unsupported EMBEDDING_PROVIDER: {provider}")


def embed_text(text: str) -> list[float]:
    return get_embedding_provider().embed(text)
