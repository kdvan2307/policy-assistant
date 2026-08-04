# test_rbac_manual.py
from app.models.models import User, UserRole, Document
from app.utils.security import can_access_document

admin = User(role=UserRole.ADMIN)
employee = User(role=UserRole.EMPLOYEE)
doc = Document(allowed_roles=["admin", "security_manager"])

print(can_access_document(admin, doc))     # kỳ vọng True (Admin luôn qua)
print(can_access_document(employee, doc))  # kỳ vọng False (employee không có trong allowed_roles)