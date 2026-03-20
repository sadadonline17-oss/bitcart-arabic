# 🚀 دليل النشر على Render.com

## الخطوة 1: إنشاء حساب
1. اذهب إلى https://render.com
2. سجل دخول بـ GitHub
3. احصل على 750 ساعة شهرياً مجاناً

## الخطوة 2: نشر API

### 2.1 من Render Dashboard:
1. اضغط **"New +"** > **"Web Service"**
2. اختر **"Build and deploy from a Git repository"**
3. اربط مستودع GitHub
4. الإعدادات:
   - **Name:** `bitcart-arabic-api`
   - **Region:** Frankfurt (Europe)
   - **Branch:** `main`
   - **Root Directory:** `api-docker`
   - **Runtime:** `Docker`
   - **Plan:** `Free`

### 2.2 Environment Variables:
اضف هذه المتغيرات:
```
BITCART_ENV=production
BITCART_CRYPTOS=btc,eth,ltc
```

### 2.3 Deploy:
- اضغط **"Create Web Service"**
- انتظر حتى يكتمل البناء (~5 دقائق)

## الخطوة 3: نشر Frontend

### 3.1 من Render Dashboard:
1. اضغط **"New +"** > **"Static Site"**
2. اربط نفس المستودع
3. الإعدادات:
   - **Name:** `bitcart-arabic-gateway`
   - **Region:** Frankfurt
   - **Branch:** `main`
   - **Root Directory:** `api-docker`
   - **Build Command:** (اتركها فارغة)
   - **Publish Directory:** `.`

### 3.2 Redirect/Rewrite:
أضف ملف `static.json` في `api-docker/`:

```json
{
  "redirects": [
    { "source": "/(.*)", "destination": "/payment.html" }
  ]
}
```

## الخطوة 4: تحديث API URL

بعد نشر API، انسخ الـ URL (مثل: `https://bitcart-arabic-api.onrender.com`)

عدّل في `payment.html`:
```javascript
let API_BASE = "https://your-api-url.onrender.com";
```

## الخطوة 5: إعداد PostgreSQL (اختياري)

من Render:
1. **"New +"** > **"PostgreSQL"**
2. **Name:** `bitcart-db`
3. **Plan:** `Free`

انسخ `Internal Database URL` وأضفه كـ Environment Variable:
```
DATABASE_URL=postgres://...
```

## 🌐 الروابط بعد النشر

- **Frontend:** `https://bitcart-arabic-gateway.onrender.com`
- **API:** `https://bitcart-arabic-api.onrender.com`
- **API Docs:** `https://bitcart-arabic-api.onrender.com/docs`

## ⚠️ ملاحظات مهمة

### Bitcoin Testnet
- المحفظة الافتراضية على Testnet (ليست حقيقية)
- استخدم https://bitcoin.org/testnet للحصول على عملات تجريبية
- أو https://coinfaucet.eu/faucet/btc-testnet/

### للإنتاج الحقيقي
1. استبدل `TESTNET_WALLET` بمحفظة حقيقية
2. فعّل HTTPS
3. أضف قاعدة بيانات PostgreSQL
4. فعّل Redis للتخزين المؤقت

## 📁 هيكل الملفات

```
bitcart-arabic/
├── api-docker/
│   ├── main.py          # FastAPI Backend
│   ├── payment.html     # Payment Gateway Frontend
│   ├── Dockerfile       # Production Docker
│   ├── Dockerfile.dev   # Development Docker
│   └── requirements.txt
├── demo/
│   └── payment-gateway-live.html  # Demo version
├── render.yaml          # Render Blueprint
└── README.md
```

## 🔗 API Endpoints

```
GET  /                    - API Info
GET  /health             - Health Check
GET  /rates              - Exchange Rates
POST /invoices           - Create Invoice
GET  /invoices/{id}      - Get Invoice
GET  /invoices/{id}/check - Check Payment
GET  /locales/arabic     - Arabic Locales
```

## 💡 نصائح

1. **Cold Start:** Render Free tier يتوقف بعد 15 دقيقة inactivity
2. **Keep Alive:** استخدم https://uptimerobot.com/ لإبقاء الخدمة تعمل
3. **Monitoring:** فعّل Render Analytics لمراقبة الأداء

---

**صُنع بـ ❤️ للعرب**
