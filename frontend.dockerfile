# --- STAGE 1: BUILD ---
# Action: Pin to the latest specific patch release for Node 20 LTS.
# This ensures you get the latest security fixes for the Node runtime and the Alpine OS packages.
FROM node:20.19.4-alpine3.19 AS build
# Note: I'm pinning to alpine3.19 (the current release line) for stability.
WORKDIR /app

# Ensure OS packages are up-to-date right before installing dependencies
# This helps catch any OS-level CVEs that were fixed recently.
RUN apk update && apk upgrade --no-cache

COPY ui/package*.json ./
# Use 'npm ci' to ensure deterministic builds based on package-lock.json
RUN npm ci --omit=dev
# Run any internal dependency audits here
# RUN npm audit --audit-level=high || exit 1

COPY ui ./
RUN npm run build

# --- STAGE 2: PRODUCTION (Runtime) ---
# Action: Pin to a specific, stable Nginx version with its Alpine base.
# Using a specific tag like 1.25.3-alpine is safer than just 'alpine'.
FROM nginx:1.25.3-alpine3.19

# Security Best Practice: Run any final OS package updates on the final image
RUN apk update && apk upgrade --no-cache

# Security Best Practice: Run Nginx as a non-root user (Nginx images often come with the 'nginx' user pre-configured)
USER nginx

# Copy built assets
COPY --from=build --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# # Healthcheck for frontend 
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#  CMD wget --spider -q http://localhost || exit 1