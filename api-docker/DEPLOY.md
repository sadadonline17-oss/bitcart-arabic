# 🚀 Bitcart Arabic - Render.com Auto-Deploy

## Instructions for Automated Deployment

### Step 1: Deploy API to Render

1. Go to: https://dashboard.render.com/select-repo
2. Connect your GitHub account
3. Select repository: `sadadonline17-oss/bitcart-arabic`
4. Configure:
   - **Name:** `bitcart-arabic-api`
   - **Root Directory:** `api-docker`
   - **Runtime:** `Docker`
   - **Plan:** `Free`

5. Click "Create Web Service"

### Step 2: Deploy Frontend

1. Go to: https://dashboard.render.com/select-repo
2. Select repository: `sadadonline17-oss/bitcart-arabic`
3. Configure:
   - **Name:** `bitcart-arabic-gateway`
   - **Root Directory:** `api-docker`
   - **Build Command:** (leave empty)
   - **Publish Directory:** `.`
   - **Plan:** `Free`

4. Click "Create Static Site"

### Step 3: Update API URL

After API deploys, copy the URL (e.g., `https://bitcart-arabic-api.onrender.com`)

Update in `payment.html` line ~275:
```javascript
API_BASE = "https://bitcart-arabic-api.onrender.com";
```

---

## API Endpoints Available

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API Info |
| GET | `/health` | Health Check |
| GET | `/rates` | BTC Exchange Rates |
| POST | `/invoices` | Create Invoice |
| GET | `/invoices/{id}` | Get Invoice |
| GET | `/invoices/{id}/check` | Check Blockchain |
| GET | `/locales/arabic` | Arabic Locales |

## Example Usage

```bash
# Create Invoice
curl -X POST https://bitcart-arabic-api.onrender.com/invoices \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","amount":100,"currency":"SAR"}'

# Check Payment
curl https://bitcart-arabic-api.onrender.com/invoices/INV-XXXXXX/check

# Get Rates
curl https://bitcart-arabic-api.onrender.com/rates
```

## Payment Flow

1. Customer enters email & amount
2. API calculates BTC amount from exchange rates
3. Customer pays via Bitcoin Testnet QR code
4. System checks blockchain for confirmation
5. Payment status updated in real-time

## Blockchain Verification

Uses Blockstream Testnet API:
- https://blockstream.info/testnet/api/address/{address}/transactions
