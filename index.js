const express = require('express');
const axios = require("axios");
const app = express();
const PORT = process.env.PORT || 3000;

app.get("/", (req, res) => {
  res.send("100 WPM Beklemesiz Sistem Aktif!");
});

app.listen(PORT, () => {
  console.log(`Sunucu ${PORT} portunda aktif.`);
});

const TOKEN = process.env.TOKEN; 
const CHANNEL_IDS = process.env.CHANNEL_IDS;
const MESSAGE = process.env.MESSAGE; // Tek mesaj

if (!TOKEN || !CHANNEL_IDS || !MESSAGE) {
    console.error("HATA: TOKEN, CHANNEL_IDS veya MESSAGE eksik!");
} else {
    const channelList = CHANNEL_IDS.split(",").map(c => c.trim());
    
    async function startProcess() {
        console.log("Sistem başlatıldı: 100 WPM ve 0 Bekleme Süresi.");
        
        while (true) { 
            for (const channelId of channelList) {
                try {
                    // 1. "Yazıyor..." animasyonu
                    await axios.post(
                        `https://discord.com/api/v9/channels/${channelId}/typing`,
                        {},
                        { headers: { "Authorization": TOKEN } }
                    );

                    // 2. 100 WPM HESABI: Harf başına 120ms bekleme
                    const typingTime = MESSAGE.length * 120;
                    console.log(`[${channelId}] Yazılıyor: ${Math.round(typingTime)}ms`);
                    
                    await new Promise(resolve => setTimeout(resolve, typingTime));

                    // 3. Mesajı Gönder
                    await axios.post(
                        `https://discord.com/api/v9/channels/${channelId}/messages`,
                        { content: MESSAGE },
                        { headers: { "Authorization": TOKEN } }
                    );

                    console.log(`[${channelId}] ✅ Mesaj Atıldı. Beklemeden sıradaki işleme geçiliyor.`);
                    
                    // BEKLEME SÜRESİ KALDIRILDI - Hemen döngü başına döner

                } catch (err) {
                    if (err.response?.status === 429) {
                        const retryAfter = (err.response.data.retry_after * 1000) || 5000;
                        console.error(`[${channelId}] ⚠️ Rate Limit! ${Math.round(retryAfter/1000)}sn zorunlu mola.`);
                        await new Promise(resolve => setTimeout(resolve, retryAfter));
                    } else {
                        console.error(`[${channelId}] ❌ Hata: ${err.response?.status}. Sonraki kanala geçiliyor.`);
                    }
                }
            }
        }
    }
    startProcess();
}
