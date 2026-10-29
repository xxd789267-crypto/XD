
import os
import sys
import time
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

import discord


# Render için arka plan web sunucusu
def run_dummy_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"Web sunucusu aktif: {port}")
    server.serve_forever()


threading.Thread(target=run_dummy_server, daemon=True).start()


# Ortam değişkenleri
TOKEN = os.getenv("SELF_TOKEN")
KANAL_STR = os.getenv("SELF_BILDIRIM_KANALI", "")
TARGET_STR = os.getenv("TARGET_ID", "")

if not TOKEN:
    print("HATA: SELF_TOKEN eksik!")
    sys.exit(1)

if not KANAL_STR.isdigit():
    print("HATA: SELF_BILDIRIM_KANALI eksik veya hatalı!")
    sys.exit(1)

try:
    BILDIRIM_KANALI_ID = int(KANAL_STR)
    HEDEF_KULLANICILAR = {
        int(x.strip())
        for x in TARGET_STR.split(",")
        if x.strip().isdigit()
    }
except ValueError:
    print("HATA: ID değerleri hatalı!")
    sys.exit(1)

if not HEDEF_KULLANICILAR:
    print("HATA: TARGET_ID eksik!")
    sys.exit(1)


# Discord bot ayarları
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Kullanıcı başına son mesaj zamanı ve takip görevi
son_mesaj_zamanlari = {}
takip_gorevleri = {}

SESSIZLIK_ARALIKLARI = [60, 120, 180, 240, 300]


async def sessizlik_takibi(kullanici_id, kullanici_adi):
    try:
        kanal = client.get_channel(BILDIRIM_KANALI_ID)

        if kanal is None:
            kanal = await client.fetch_channel(BILDIRIM_KANALI_ID)

        for saniye in SESSIZLIK_ARALIKLARI:
            await asyncio.sleep(saniye - (
                SESSIZLIK_ARALIKLARI[
                    SESSIZLIK_ARALIKLARI.index(saniye) - 1
                ] if saniye != 60 else 0
            ))

            # Yeni mesaj geldiyse bu görev iptal edilir.
            # Ek kontrol, eski bir görevin bildirim göndermesini önler.
            if kullanici_id not in son_mesaj_zamanlari:
                return

            gecen_sure = time.time() - son_mesaj_zamanlari[kullanici_id]

            if gecen_sure < saniye:
                return

            dakika = saniye // 60

            await kanal.send(
                f"🔕 **Sessizlik bildirimi**\n"
                f"**Kullanıcı:** {kullanici_adi} (`{kullanici_id}`)\n"
                f"**Süre:** {dakika} dakikadır mesaj göndermiyor."
            )

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Sessizlik takibi hatası: {e}")


async def hedef_mesaji(message):
    if message.author.id not in HEDEF_KULLANICILAR:
        return

    kullanici_id = message.author.id
    son_mesaj_zamanlari[kullanici_id] = time.time()

    eski_gorev = takip_gorevleri.get(kullanici_id)

    if eski_gorev and not eski_gorev.done():
        eski_gorev.cancel()

    takip_gorevleri[kullanici_id] = asyncio.create_task(
        sessizlik_takibi(kullanici_id, message.author.name)
    )

    print(f"{message.author.name} mesaj gönderdi; sessizlik sayacı sıfırlandı.")


@client.event
async def on_ready():
    print(f"Bot aktif: {client.user}")
    print(f"Takip edilen kullanıcılar: {HEDEF_KULLANICILAR}")
    print(f"Bildirim kanalı: {BILDIRIM_KANALI_ID}")


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return

    await hedef_mesaji(message)


@client.event
async def on_message_edit(before, after):
    if after.author.id == client.user.id:
        return

    await hedef_mesaji(after)


client.run(TOKEN)
