from unittest.mock import patch, MagicMock

from app.services.retriever_service import retrieve


class _FakeVector(list):
    """Giả lập numpy array tối thiểu — chỉ cần .tolist()."""
    def tolist(self):
        return list(self)


def _make_mock_model():
    model = MagicMock()
    model.encode.return_value = [_FakeVector([0.1, 0.2, 0.3])]
    return model


@patch("app.services.retriever_service.search")
@patch("app.services.retriever_service._get_model")
def test_retrieve_happy_path_maps_chunks_correctly(mock_get_model, mock_search):
    """Happy path: search() trả kết quả thô -> retrieve() dịch đúng sang
    RetrievedChunk với đủ field."""
    mock_get_model.return_value = _make_mock_model()
    mock_search.return_value = [
        {
            "score": 0.85,
            "payload": {
                "title": "Chính sách Mật khẩu Nội bộ",
                "content": "Độ dài tối thiểu 12 ký tự...",
                "document_id": 1,
            },
        }
    ]

    results = retrieve("Mật khẩu cần bao nhiêu ký tự?", user_role="employee", top_k=3)

    assert len(results) == 1
    assert results[0].title == "Chính sách Mật khẩu Nội bộ"
    assert results[0].content == "Độ dài tối thiểu 12 ký tự..."
    assert results[0].document_id == 1
    assert results[0].score == 0.85


@patch("app.services.retriever_service.search")
@patch("app.services.retriever_service._get_model")
def test_retrieve_adds_query_prefix_for_e5_model(mock_get_model, mock_search):
    """Xác nhận retrieve() LUÔN thêm tiền tố 'query: ' bắt buộc theo quy ước
    model multilingual-e5-small — bảo vệ bằng test, không chỉ review bằng mắt."""
    mock_get_model.return_value = _make_mock_model()
    mock_search.return_value = []

    retrieve("MFA là gì?", user_role="employee", top_k=3)

    model_instance = mock_get_model.return_value
    called_texts = model_instance.encode.call_args.args[0]
    assert called_texts == ["query: MFA là gì?"]


@patch("app.services.retriever_service.search")
@patch("app.services.retriever_service._get_model")
def test_retrieve_passes_user_role_through_to_search(mock_get_model, mock_search):
    """Xác nhận role truyền nguyên vẹn xuống search() — điểm nối giữa
    retriever và cơ chế lọc RBAC."""
    mock_get_model.return_value = _make_mock_model()
    mock_search.return_value = []

    retrieve("Câu hỏi bất kỳ", user_role="security_manager", top_k=5)

    call_kwargs = mock_search.call_args.kwargs
    assert call_kwargs["user_role"] == "security_manager"
    assert call_kwargs["top_k"] == 5


@patch("app.services.retriever_service.search")
@patch("app.services.retriever_service._get_model")
def test_retrieve_empty_question_does_not_crash(mock_get_model, mock_search):
    """Edge case: câu hỏi rỗng ('') — không được raise exception."""
    mock_get_model.return_value = _make_mock_model()
    mock_search.return_value = []

    results = retrieve("", user_role="employee", top_k=3)

    assert results == []


@patch("app.services.retriever_service.search")
@patch("app.services.retriever_service._get_model")
def test_retrieve_invalid_role_returns_empty_not_error(mock_get_model, mock_search):
    """Edge case: role không hợp lệ/không tồn tại (ví dụ JWT chứa role đã bị
    xóa khỏi hệ thống) — KHÔNG được crash, chỉ đơn giản không có chunk nào khớp."""
    mock_get_model.return_value = _make_mock_model()
    mock_search.return_value = []

    results = retrieve("Có tài liệu nào không?", user_role="nonexistent_role", top_k=3)

    assert results == []
    call_kwargs = mock_search.call_args.kwargs
    assert call_kwargs["user_role"] == "nonexistent_role"