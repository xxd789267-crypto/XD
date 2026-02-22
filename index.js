const express = require('express');
const axios = require("axios");

const app = express();
const PORT = process.env.PORT || 3000;

app.get("/", (req, res) => {
  res.send("Bot kanallar arası döngüde aktif!");
});

app.listen(PORT, () => {
  console.log(`Sunucu ${PORT} portunda çalışıyor.`);
});

// Environment Değişkenleri
const token = process.env.TOKEN;
const channelIdsRaw = process.env.CHANNEL_IDS; // Virgülle ayrılmış ID'ler: "ID1,ID2"
const msg1 = process.env.MESSAGE1;
const msg2 = process.env.MESSAGE2;

// ID'leri diziye çeviriyoruz
const channelList = channelIdsRaw ? channelIdsRaw.split(',').map(id => id.trim()) : [];

let currentChannelIndex = 0;
let isFirstMessage = true;

if (!token || channelList.length === 0 || !msg1 || !msg2) {
    console.error("HATA: TOKEN, CHANNEL_IDS, MESSAGE1 veya MESSAGE2 eksik!");
} else {
    // 3 saniyede bir ana akışı başlat
    setInterval(flow, 3000);
}

// "Yazıyor..." efekti fonksiyonu
async function sendTyping(cid) {
  try {
    await axios.post(`https://discord.com/api/v9/channels/${cid}/typing`, {}, {
      headers: { "Authorization": token }
    });
  } catch (err) {
    console.error(`${cid} kanalında yazıyor gösterilemedi.`);
  }
}

async function flow() {
  // Sıradaki kanalı ve mesajı seç
  const currentChannelId = channelList[currentChannelIndex];
  const currentMessage = isFirstMessage ? msg1 : msg2;
  
  // Önce o kanalda yazıyor göster
  await sendTyping(currentChannelId);

  // Mesajı gönder
  axios.post(`https://discord.com/api/v9/channels/${currentChannelId}/messages`, {
    content: currentMessage
  }, {
    headers: {
      "Authorization": token,
      "Content-Type": "application/json"
    }
  }).then(() => {
    console.log(`✅ Kanal: ${currentChannelId} | Mesaj: "${currentMessage}"`);
    
    // Sırayı güncelle:
    // Bir sonraki sefere diğer mesajı at
    isFirstMessage = !isFirstMessage;
    
    // Bir sonraki sefere diğer kanala geç (Listenin sonuna gelince başa döner)
    currentChannelIndex = (currentChannelIndex + 1) % channelList.length;
    
  }).catch((err) => {
    console.error("❌ Mesaj hatası:", err.response?.status);
    // Hata olsa bile sıradaki kanala geçmesi için indexi artırabiliriz
    currentChannelIndex = (currentChannelIndex + 1) % channelList.length;
  });
}
