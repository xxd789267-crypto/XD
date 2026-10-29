import os
import sys
import time
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import discord

# =====================================================================
# 🌍 RENDER / UPTIME ROBOT İÇİN ARKA PLAN WEB SUNUCUSU
# =====================================================================
def run_dummy_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌍 Web sunucusu aktif: {port}")
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# =====================================================================
# 🤖 SELF-BOT - 1 DAKİKA SESSİZLİK BİLDİRİMİ
# =====================================================================

TOKEN = os.getenv("SELF_TOKEN")
KANAL_STR = os.getenv("SELF_BILDIRIM_KANALI", "")
TARGET_STR = os.getenv("TARGET_ID", "")

if not TOKEN:
    sys.exit("❌ HATA: SELF_TOKEN eksik!")
if not KANAL_STR.isdigit():
    sys.exit("❌ HATA: SELF_BILDIRIM_KANALI hatalı!")
BILDIRIM_KANALI_ID = int(KANAL_STR)

HEDEF_KULLANICILAR = {
    int(x.strip())
    for x in TARGET_STR.split(",")
    if x.strip().isdigit()
}
if not HEDEF_KULLANICILAR:
    sys.exit("❌ HATA: TARGET_ID eksik!")

client = discord.Client()

son_mesaj_zamanlari = {}
takip_gorevleri = {}

SESSIZLIK_SURESI = 60  # 1 dakika

async def sessizlik_takibi(kullanici_id, kullanici_adi, son_mesaj_zamani):
    try:
        await asyncio.sleep(SESSIZLIK_SURESI)

        if son_mesaj_zamanlari.get(kullanici_id) != son_mesaj_zamani:
            return

        kanal = (
