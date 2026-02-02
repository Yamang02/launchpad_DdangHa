# ===== Build =====
# yarn workspaces 모노레포 — root context 필요
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json yarn.lock ./
COPY apps/frontend/package.json ./apps/frontend/
RUN yarn install --frozen-lockfile

COPY apps/frontend ./apps/frontend
WORKDIR /app/apps/frontend
RUN yarn build

# ===== Runtime =====
FROM nginx:alpine

RUN apk add --no-cache curl

COPY --from=builder /app/apps/frontend/dist /usr/share/nginx/html
COPY apps/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
