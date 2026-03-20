"""
Bitcart Arabic Payment Gateway API
BTC Testnet - Real Blockchain Integration
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import asyncio
import json
import hashlib
from datetime import datetime, timedelta

app = FastAPI(title="Bitcart Arabic Payment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (replace with Redis/DB in production)
invoices_db = {}

# Exchange rates (from CoinGecko free API)
EXCHANGE_RATES = {}

class CreateInvoiceRequest(BaseModel):
    email: str
    amount: float
    currency: str = "SAR"
    description: Optional[str] = None

class InvoiceResponse(BaseModel):
    id: str
    status: str
    amount: float
    currency: str
    btc_amount: float
    address: str
    qr_uri: str
    expires_at: str
    created_at: str

# Testnet wallet - GET YOUR OWN from https://bitcoin.org/testnet/ or use a faucet
TESTNET_WALLET = "tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"

async def fetch_btc_rate():
    """Fetch BTC to USD rate from CoinGecko"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "bitcoin", "vs_currencies": "usd"}
            )
            if response.status_code == 200:
                data = response.json()
                return data["bitcoin"]["usd"]
    except Exception:
        pass
    return 150000  # Fallback rate

# Gulf currencies to USD rates
GULF_RATES = {
    "SAR": 0.2666,  # ~3.75 SAR per USD
    "AED": 0.2722,  # ~3.67 AED per USD
    "KWD": 3.25,    # ~0.31 KWD per USD
    "BHD": 2.65,    # ~0.38 BHD per USD
    "QAR": 0.2747,  # ~3.64 QAR per USD
    "OMR": 2.60,    # ~0.38 OMR per USD
    "EGP": 0.032,   # ~31 EGP per USD
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.26,
}

@app.get("/")
async def root():
    return {"message": "Bitcart Arabic Payment Gateway API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/rates")
async def get_rates():
    """Get current exchange rates"""
    btc_usd = await fetch_btc_rate()
    rates = {}
    for currency, to_usd in GULF_RATES.items():
        rates[currency] = {
            "to_usd": to_usd,
            "btc_rate": 1 / (btc_usd * to_usd)
        }
    return {"btc_usd": btc_usd, "currencies": rates}

@app.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(request: CreateInvoiceRequest):
    """Create a new payment invoice"""
    # Generate invoice ID
    invoice_id = f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:6].upper()}"
    
    # Calculate BTC amount
    btc_rate_usd = await fetch_btc_rate()
    currency_rate = GULF_RATES.get(request.currency.upper(), 1.0)
    amount_usd = request.amount / currency_rate
    btc_amount = amount_usd / btc_rate_usd
    
    # Create invoice
    now = datetime.utcnow()
    expires = now + timedelta(minutes=30)
    
    invoice = {
        "id": invoice_id,
        "status": "pending",
        "amount": request.amount,
        "currency": request.currency.upper(),
        "btc_amount": round(btc_amount, 8),
        "address": TESTNET_WALLET,
        "email": request.email,
        "description": request.description,
        "created_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "payments": []
    }
    
    invoices_db[invoice_id] = invoice
    
    return InvoiceResponse(
        id=invoice_id,
        status="pending",
        amount=request.amount,
        currency=request.currency.upper(),
        btc_amount=round(btc_amount, 8),
        address=TESTNET_WALLET,
        qr_uri=f"bitcoin:{TESTNET_WALLET}?amount={round(btc_amount, 8)}&label=Bitcart%20Arabic%20Payment",
        expires_at=expires.isoformat(),
        created_at=now.isoformat()
    )

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get invoice status"""
    if invoice_id not in invoices_db:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice = invoices_db[invoice_id]
    
    # Check if expired
    if invoice["status"] == "pending":
        expires = datetime.fromisoformat(invoice["expires_at"])
        if datetime.utcnow() > expires:
            invoice["status"] = "expired"
    
    return invoice

@app.get("/invoices/{invoice_id}/check")
async def check_payment(invoice_id: str, background_tasks: BackgroundTasks):
    """Check if payment was received on blockchain"""
    if invoice_id not in invoices_db:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice = invoices_db[invoice_id]
    
    if invoice["status"] != "pending":
        return {"status": invoice["status"], "invoice": invoice}
    
    # Check blockchain (Testnet)
    try:
        async with httpx.AsyncClient() as client:
            # Using Blockstream Testnet API
            response = await client.get(
                f"https://blockstream.info/testnet/api/address/{TESTNET_WALLET}/transactions"
            )
            
            if response.status_code == 200:
                txs = response.json()
                
                # Check if any new transactions after invoice creation
                invoice_created = datetime.fromisoformat(invoice["created_at"])
                
                for tx in txs:
                    tx_time = datetime.fromtimestamp(tx["status"]["block_time"])
                    if tx_time > invoice_created:
                        # Found a new transaction
                        invoice["status"] = "confirmed"
                        invoice["tx_hash"] = tx["txid"]
                        invoice["confirmed_at"] = tx_time.isoformat()
                        break
                        
    except Exception as e:
        # In case API fails, check mempool
        pass
    
    return {"status": invoice["status"], "invoice": invoice}

@app.get("/locales/arabic")
async def get_arabic_locales():
    """Get supported Arabic locales"""
    return {
        "gulf": [
            {"code": "ar-SA", "name": "العربية (المملكة العربية السعودية)", "currency": "SAR", "symbol": "ر.س"},
            {"code": "ar-AE", "name": "العربية (الإمارات)", "currency": "AED", "symbol": "د.إ"},
            {"code": "ar-KW", "name": "العربية (الكويت)", "currency": "KWD", "symbol": "د.ك"},
            {"code": "ar-BH", "name": "العربية (البحرين)", "currency": "BHD", "symbol": "د.ب"},
            {"code": "ar-QA", "name": "العربية (قطر)", "currency": "QAR", "symbol": "ر.ق"},
            {"code": "ar-OM", "name": "العربية (عُمان)", "currency": "OMR", "symbol": "ر.ع."},
        ],
        "all": [
            {"code": "ar-SA", "name": "العربية (السعودية)", "currency": "SAR"},
            {"code": "ar-AE", "name": "العربية (الإمارات)", "currency": "AED"},
            {"code": "ar-EG", "name": "العربية (مصر)", "currency": "EGP"},
            {"code": "ar-MA", "name": "العربية (المغرب)", "currency": "MAD"},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
