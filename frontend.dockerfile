FROM node:20-alpine AS build
WORKDIR /app
COPY ui/package*.json ./
RUN npm ci
COPY ui ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Healthcheck for frontend
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD wget --spider -q http://localhost || exit 1