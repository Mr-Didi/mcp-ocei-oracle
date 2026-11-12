FROM node:20-alpine
WORKDIR /app
COPY package.json index.mjs ./
RUN chmod +x index.mjs
USER node
ENTRYPOINT ["node", "index.mjs"]
