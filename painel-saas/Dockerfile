FROM node:18-alpine AS build

WORKDIR /app

# Copia apenas os arquivos de dependência para cachear o layer de instalação
COPY painel-saas/package*.json ./
RUN npm install

# Copia o código fonte e os arquivos de configuração
COPY painel-saas/ .

# Argumentos de build necessários para o Vite (injetados no tempo de compilação)
ARG VITE_API_URL
ARG VITE_VAPID_PUBLIC_KEY
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_VAPID_PUBLIC_KEY=$VITE_VAPID_PUBLIC_KEY

RUN npm run build

# Estágio final com Nginx para servir o conteúdo estático de forma otimizada
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Configuração para suportar SPA (redireciona rotas inexistentes para o index.html)
RUN echo 'server { listen 80; location / { root /usr/share/nginx/html; index index.html; try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]