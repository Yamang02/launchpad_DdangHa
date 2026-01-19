FROM node:18-alpine

WORKDIR /app

# Yarn 설치
RUN apk add --no-cache yarn

# 의존성 설치
COPY package.json yarn.lock* ./
RUN yarn install --frozen-lockfile

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 개발 모드 실행
CMD ["yarn", "dev", "--host", "0.0.0.0"]
