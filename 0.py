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
            client.get_channel(BILDIRIM_KANALI_ID)
            or await client.fetch_channel(BILDIRIM_KANALI_ID)
        )

        await kanal.send(
            f"🔕 **Sessizlik bildirimi**\n"
            f"**Kullanıcı:** {kullanici_adi} (`{kullanici_id}`)\n"
            f"**Süre:** 1 dakikadır mesaj göndermiyor."
        )
        print(f"{kullanici_adi}: 1 dakika sessiz kaldı, bildirim gönderildi.")

    except asyncio.CancelledError:
        pass
    except Exception as hata:
        print(f"Sessizlik takibi hatası: {hata}")

async def hedef_mesaji(message):
    if message.author.id not in HEDEF_KULLANICILAR:
        return

    kullanici_id = message.author.id
    zaman = time.monotonic()
    son_mesaj_zamanlari[kullanici_id] = zaman

    eski_gorev = takip_gorevleri.get(kullanici_id)
    if eski_gorev and not eski_gorev.done():
        eski_gorev.cancel()

    takip_gorevleri[kullanici_id] = asyncio.create_task(
        sessizlik_takibi(kullanici_id, message.author.name, zaman)
    )
    print(f"{message.author.name}: mesaj alındı, 1 dakika sayacı sıfırlandı.")

@client.event
async def on_ready():
    print("=========================================")
    print(f"🤖 Bağlantı başarılı: {client.user}")
    print(f"🎯 Takip edilen ID'ler: {sorted(HEDEF_KULLANICILAR)}")
    print(f"📢 Bildirim kanalı: {BILDIRIM_KANALI_ID}")
    print("=========================================")

@client.event
async def on_message(message):
    if client.user and message.author.id == client.user.id:
        return
    await hedef_mesaji(message)

@client.event
async def on_message_edit(before, after):
    if client.user and after.author.id == client.user.id:
        return
    await hedef_mesaji(after)

client.run(TOKEN)
