# Build Stage
FROM node:20-alpine AS builder
WORKDIR /app

# Copy root package files
COPY package*.json ./

# Copy workspace package.json files (needed for npm install to link workspaces)
COPY packages/chat/package.json ./packages/chat/
COPY packages/shared/package.json ./packages/shared/
COPY packages/shell/package.json ./packages/shell/
COPY packages/upload/package.json ./packages/upload/

RUN npm install
COPY . .
RUN npm run build

# Production Stage
FROM nginx:alpine
# Copy the built shell app to nginx (assuming shell is the main entry)
COPY --from=builder /app/packages/shell/dist /usr/share/nginx/html
# Also copy remotes if they are needed in the same origin
COPY --from=builder /app/packages/chat/dist /usr/share/nginx/html/chat
COPY --from=builder /app/packages/upload/dist /usr/share/nginx/html/upload

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
