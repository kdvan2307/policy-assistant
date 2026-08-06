FROM python:3.12-slim

WORKDIR /app

# Copy requirements trước để tận dụng Docker layer cache — nếu chỉ sửa code
# (không đổi requirements.txt), bước pip install không chạy lại ở các lần build sau.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]