FROM node:20-alpine

WORKDIR /app

# Instala dependências primeiro (cache de layers)
COPY package.json package-lock.json* ./
RUN npm install

# Copia o restante do código
COPY . .

EXPOSE 3000

# Em desenvolvimento, roda com hot reload
CMD ["npm", "run", "dev"]
