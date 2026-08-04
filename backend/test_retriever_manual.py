from app.services.retriever_service import retrieve

QUESTION = "Quy trình xử lý khi có sự cố bảo mật xảy ra như thế nào?"

for role in ["guest", "employee", "security_manager", "admin"]:
    print(f"=== Role: {role} ===")
    results = retrieve(QUESTION, user_role=role, top_k=3)

    if not results:
        print("  Không tìm thấy tài liệu nào được phép xem cho role này.\n")
        continue

    for r in results:
        print(f"  [score={r.score:.3f}] {r.title}")
        print(f"    {r.content[:80]}...")
    print()