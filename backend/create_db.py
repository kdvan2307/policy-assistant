from app.database.database import Base, engine
from app.models import models  # import để SQLAlchemy biết các model đã định nghĩa

Base.metadata.create_all(bind=engine)
print("Đã tạo xong 6 bảng trong PostgreSQL.")