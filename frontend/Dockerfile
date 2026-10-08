FROM node:22-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
ARG VITE_FINSIGHT_AUTH_MODE=users
ENV VITE_FINSIGHT_AUTH_MODE=${VITE_FINSIGHT_AUTH_MODE}
RUN npm run build

FROM caddy:2-alpine
COPY --from=build /app/dist /srv
COPY deploy/Caddyfile /etc/caddy/Caddyfile
