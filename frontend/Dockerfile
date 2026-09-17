# --- Giai đoạn 1: build ---
FROM node:20-slim AS build

WORKDIR /app

# ARG/ENV này BẮT BUỘC khai báo TRƯỚC "npm run build" — biến NEXT_PUBLIC_*
# được nhúng vào JS bundle ngay lúc build, không đọc lại được lúc container
# chạy thật. Đây là lý do KHÔNG đặt biến này trong docker-compose "environment".
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# --- Giai đoạn 2: chạy bằng Node (Next.js cần server sống, khác React tĩnh) ---
FROM node:20-slim

WORKDIR /app
ENV NODE_ENV=production

# COPY --from=build /app/public ./public
COPY --from=build /app/.next ./.next
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]