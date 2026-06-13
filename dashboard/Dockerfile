# Build stage
FROM node:20-alpine AS build

WORKDIR /app

ENV DIRECTORY dashboard

COPY $DIRECTORY/package*.json ./
RUN npm clean-install

COPY ./$DIRECTORY ./
RUN npm run build

# Serve stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY dashboard/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
