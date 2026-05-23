# ── Stage 1: build ────────────────────────────────────────────────────────────
# Выбран multi-stage подход (node→nginx в одном файле) вместо frontend-builder
# сервиса + shared volume. Причина: shared volume создаёт race condition — nginx
# стартует до того, как frontend-builder заканчивает копирование файлов.
# Здесь статика baked-in в образ — nginx получает готовые файлы немедленно.
FROM node:20-alpine AS builder
WORKDIR /app

# Копируем манифесты отдельным слоем — кешируется пока зависимости не меняются
COPY package.json package-lock.json ./
RUN npm ci

# Копируем исходники и собираем (Vite возьмёт .env.production автоматически)
COPY . .
RUN npm run build

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM nginx:alpine AS runtime
# Копируем собранную статику в nginx html root
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
# nginx.conf монтируется bind-mount'ом в docker-compose (proxy_pass на backend)
