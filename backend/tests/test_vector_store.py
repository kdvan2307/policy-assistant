from unittest.mock import patch, MagicMock

from app.services.vector_store import search


def _make_mock_client(payloads):
    """Tạo 1 QdrantClient giả — query_points() trả về danh sách point giả
    lập, mỗi point có .score và .payload như Qdrant thật trả về."""
    mock_client = MagicMock()
    mock_points = []
    for payload in payloads:
        point = MagicMock()
        point.score = 0.9
        point.payload = payload
        mock_points.append(point)

    mock_result = MagicMock()
    mock_result.points = mock_points
    mock_client.query_points.return_value = mock_result
    return mock_client


@patch("app.services.vector_store._get_client")
def test_search_admin_bypasses_role_filter(mock_get_client):
    """Happy path RBAC: role admin -> KHÔNG được áp bất kỳ Filter nào."""
    mock_client = _make_mock_client([{"title": "Tài liệu A", "allowed_roles": ["admin"]}])
    mock_get_client.return_value = mock_client

    search(query_embedding=[0.1, 0.2, 0.3], top_k=3, user_role="admin")

    call_kwargs = mock_client.query_points.call_args.kwargs
    assert call_kwargs["query_filter"] is None


@patch("app.services.vector_store._get_client")
def test_search_employee_applies_role_filter(mock_get_client):
    """Edge case quan trọng nhất: role KHÔNG phải admin -> PHẢI được áp
    Filter đúng theo allowed_roles."""
    mock_client = _make_mock_client([{"title": "Tài liệu B", "allowed_roles": ["employee"]}])
    mock_get_client.return_value = mock_client

    search(query_embedding=[0.1, 0.2, 0.3], top_k=3, user_role="employee")

    call_kwargs = mock_client.query_points.call_args.kwargs
    query_filter = call_kwargs["query_filter"]

    assert query_filter is not None
    condition = query_filter.must[0]
    assert condition.key == "allowed_roles"
    assert condition.match.value == "employee"


@patch("app.services.vector_store._get_client")
def test_search_none_role_no_filter(mock_get_client):
    """Edge case: user_role=None -> không áp filter (giống hành vi admin).
    An toàn vì API /chat luôn truyền role thật từ token, không bao giờ None."""
    mock_client = _make_mock_client([])
    mock_get_client.return_value = mock_client

    search(query_embedding=[0.1, 0.2, 0.3], top_k=3, user_role=None)

    call_kwargs = mock_client.query_points.call_args.kwargs
    assert call_kwargs["query_filter"] is None


@patch("app.services.vector_store._get_client")
def test_search_returns_correct_score_and_payload_shape(mock_get_client):
    """Xác nhận search() dịch đúng point.score/point.payload sang dict thuần."""
    mock_client = _make_mock_client([{"title": "Chính sách Mật khẩu", "content": "..."}])
    mock_get_client.return_value = mock_client

    results = search(query_embedding=[0.1, 0.2, 0.3], top_k=3, user_role="admin")

    assert len(results) == 1
    assert results[0]["score"] == 0.9
    assert results[0]["payload"]["title"] == "Chính sách Mật khẩu"