# Build stage
FROM node:20-alpine AS build

WORKDIR /app

ENV DIRECTORY dashboard

# Vite inlines env vars at build time
ARG VITE_DATA_API_HOST
ENV VITE_DATA_API_HOST=$VITE_DATA_API_HOST

COPY $DIRECTORY/package*.json ./
RUN npm clean-install

COPY ./$DIRECTORY ./
RUN npm run build

# Serve stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# SPA fallback: serve index.html for client-side routes
RUN printf 'server {\n\
    listen 80;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
