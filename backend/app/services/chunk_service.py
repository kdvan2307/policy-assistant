import re


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """Chia text thành các đoạn (chunk) theo SỐ TỪ, có phần chồng lấn (overlap)
    giữa các chunk liên tiếp để không mất ngữ cảnh ở ranh giới.

    Đơn vị đo là số từ (đơn giản, không cần tokenizer riêng ở bước này) —
    tokenizer thật của LLM sẽ dùng khi ghép prompt ở Bước 12.
    """
    normalized = re.sub(r"\n{3,}", "\n\n", text.strip())
    words = normalized.split()

    if len(words) <= chunk_size:
        return [normalized] if normalized else []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap  # lùi lại để chunk sau chồng lấn với chunk trước

    return chunks