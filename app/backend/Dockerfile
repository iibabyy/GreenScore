# Dockerfile for backend service
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install


# Expose port
EXPOSE 3001
