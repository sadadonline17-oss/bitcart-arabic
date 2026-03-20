#!/bin/bash
# Bitcart Arabic - Production Deployment Script
# تشغيل: chmod +x deploy.sh && ./deploy.sh

set -e

echo "🔧 إعداد بوابة الدفع - Bitcart Arabic"
echo "======================================"

# التحقق من المتطلبات
command -v docker >/dev/null 2>&1 || { echo "❌ Docker مطلوب"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose مطلوب"; exit 1; }

# إنشاء ملف البيئة
cat > .env << 'EOF'
# إعدادات الموقع
SITE_NAME="بوابة الدفع العربية"
SITE_URL="https://your-domain.com"

# إعدادات API
BITCART_ENV=production
BITCART_HOST=0.0.0.0
BITCART_PORT=8000

# إعدادات العملة الافتراضية (عملة الخليج)
DEFAULT_CURRENCY=SAR

# العملات المشفرة المدعومة
BITCART_CRYPTOS=btc,eth,ltc

# إعدادات قاعدة البيانات
DB_HOST=postgres
DB_PORT=5432
DB_DATABASE=bitcart
DB_USER=bitcart
DB_PASSWORD=$(openssl rand -base64 32)

# إعدادات Redis
REDIS_HOST=redis
REDIS_PORT=6379

# إعدادات HTTPS
BITCART_HTTPS_ENABLED=true
BITCART_REVERSEPROXY=nginx-https

# البريد الإلكتروني للإشعارات
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# إعدادات اللغة العربية
ARABIC_LANGUAGE=enabled
ARABIC_DEFAULT_LOCALE=ar-SA
ARABIC_GULF_CURRENCIES=enabled
EOF

# إنشاء docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  api:
    image: bitcart/api:latest
    container_name: bitcart-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_DATABASE=${DB_DATABASE}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - BITCART_ENV=production
      - BITCART_CRYPTOS=${BITCART_CRYPTOS}
    volumes:
      - ./data:/data
      - ./logs:/logs
    depends_on:
      - postgres
      - redis
    networks:
      - bitcart-network

  postgres:
    image: postgres:15-alpine
    container_name: bitcart-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${DB_DATABASE}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - bitcart-network

  redis:
    image: redis:7-alpine
    container_name: bitcart-redis
    restart: unless-stopped
    networks:
      - bitcart-network

  nginx:
    image: nginx:alpine
    container_name: bitcart-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - bitcart-network

volumes:
  postgres_data:

networks:
  bitcart-network:
    driver: bridge
EOF

# إنشاء ملف nginx
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name _;
        
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /admin/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
        }
    }
}
EOF

echo "✅ تم إنشاء ملفات التكوين"
echo ""
echo "📋 الخطوات التالية:"
echo "1. قم بتعديل ملف .env بإعداداتك"
echo "2. شغّل: docker-compose up -d"
echo "3. افتح: http://your-server-ip/admin"
echo ""
echo "🚀 للنشر على الخادم:"
echo "   scp -r bitcart-deploy user@your-server:/opt/"
