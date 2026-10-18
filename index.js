const express = require('express');
const axios = require("axios");
const app = express();
const PORT = process.env.PORT || 3000;

app.get("/", (req, res) => {
  res.send("5 Saniye Aralıklı Sistem Aktif!");
});

app.listen(PORT, () => {
  console.log(`Sunucu ${PORT} portunda aktif.`);
});

const TOKEN = process.env.TOKEN; 
const CHANNEL_IDS = process.env.CHANNEL_IDS;
const MESSAGE = process.env.MESSAGE;

if (!TOKEN || !CHANNEL_IDS || !MESSAGE) {
    console.error("HATA: TOKEN, CHANNEL_IDS veya MESSAGE eksik!");
} else {
    const channelList = CHANNEL_IDS.split(",").map(c => c.trim());
    
    async function startProcess() {
        console.log("Sistem başlatıldı: Her 5 saniyede bir mesaj gönderilecek.");
        
        while (true) {  
            for (const channelId of channelList) {
                try {
                    // Mesajı Gönder
                    await axios.post(
                        `https://discord.com/api/v9/channels/${channelId}/messages`,
                        { content: MESSAGE },
                        { headers: { "Authorization": TOKEN } }
                    );

                    console.log(`[${channelId}] ✅ Mesaj Atıldı. 5 saniye bekleniyor...`);
                    
                    // 5 Saniye Bekleme Süresi (5000 milisaniye)
                    await new Promise(resolve => setTimeout(resolve, 5000));

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
