import os
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue,
)

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "policy_documents"
VECTOR_SIZE = 384

_client: QdrantClient | None = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL)
    return _client


def ensure_collection() -> None:
    client = _get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        return
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def upsert_chunk(
    document_id: int, chunk_index: int, title: str, content: str,
    embedding: list[float], allowed_roles: list[str],
) -> str:
    client = _get_client()
    point_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"doc-{document_id}-chunk-{chunk_index}"))
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                    "title": title,
                    "content": content,
                    "allowed_roles": allowed_roles,
                },
            )
        ],
    )
    return point_id


def search(query_embedding: list[float], top_k: int = 5, user_role: str | None = None) -> list[dict]:
    """Tìm top_k chunk gần nhất, CHỈ trong số chunk mà user_role được phép xem.

    user_role=None hoặc "admin" -> không áp filter, tìm trên toàn bộ collection
    (nhất quán với can_access_document ở Bước 4: Admin luôn xem được mọi tài liệu).
    """
    client = _get_client()

    query_filter = None
    if user_role and user_role != "admin":
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="allowed_roles",
                    match=MatchValue(value=user_role),
                )
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=top_k,
    )
    return [{"score": point.score, "payload": point.payload} for point in results.points]