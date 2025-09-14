import streamlit as st
import json
import os
import random
from datetime import datetime

DATA_FILE = "paragraflar.json"
SCORE_FILE = "puan.json"

# -------------------------------
# JSON dosyalarını yükleme
# -------------------------------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        paragraflar = json.load(f)
else:
    paragraflar = []

if os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "r", encoding="utf-8") as f:
        puan = json.load(f)
else:
    puan = {"dogru": 0, "yanlis": 0, "gunluk": {}}

# -------------------------------
# Yardımcı Fonksiyonlar
# -------------------------------
def gun_anahtari():
    return datetime.now().strftime("%Y-%m-%d")

def puan_guncelle(dogru_mu: bool):
    gun = gun_anahtari()
    if gun not in puan["gunluk"]:
        puan["gunluk"][gun] = {"dogru": 0, "yanlis": 0}

    if dogru_mu:
        puan["dogru"] += 1
        puan["gunluk"][gun]["dogru"] += 1
    else:
        puan["yanlis"] += 1
        puan["gunluk"][gun]["yanlis"] += 1

    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(puan, f, ensure_ascii=False, indent=2)

# -------------------------------
# Sidebar Menü
# -------------------------------
st.sidebar.title("📑 Menü")
sayfa = st.sidebar.radio("Git:", ["🏠 Ana Sayfa", "📝 Testler", "📊 İstatistikler"])

# -------------------------------
# Ana Sayfa
# -------------------------------
if sayfa == "🏠 Ana Sayfa":
    st.title("📘 YDS Paragraf Çalışma Uygulaması")

    simdi = datetime.now().strftime("%d %B %Y - %H:%M:%S")
    st.write(f"⏰ Tarih & Saat: {simdi}")

    st.subheader("Genel İstatistikler")
    st.write(f"✅ Doğru: {puan['dogru']}")
    st.write(f"❌ Yanlış: {puan['yanlis']}")

    st.info("Menüden testlere başlayabilir veya istatistikleri görebilirsin.")

# -------------------------------
# Testler
# -------------------------------
elif sayfa == "📝 Testler":
    test_turu = st.radio("Test Türünü Seç:", ["İngilizceden Türkçeye", "Türkçeden İngilizceye"])

    if not paragraflar:
        st.warning("Henüz paragraf eklenmemiş. Lütfen paragraflar.json dosyasına içerik ekle.")
    else:
        secili_paragraf = random.choice(paragraflar)
        secili_cumle = random.choice(secili_paragraf["sentences"])

        st.subheader("Soru")
        if test_turu == "İngilizceden Türkçeye":
            st.write(secili_cumle["text"])
            secenekler = secili_cumle["choices"]
            dogru_cevap = secili_cumle["answer"]

        else:  # Türkçeden İngilizceye
            st.write(secili_cumle["answer"])
            # İngilizce şıklar üretelim (1 doğru + diğer yanlışlar)
            secenekler = [secili_cumle["text"]]
            # Yanlış şıklar için cümlenin içine karışık ekleme
            secenekler += [
                secili_cumle["text"].replace("is", "was"),
                secili_cumle["text"].replace("are", "were"),
                secili_cumle["text"].replace("the", "a")
            ]
            secenekler = list(set(secenekler))  # tekrarları sil
            dogru_cevap = secili_cumle["text"]

        random.shuffle(secenekler)
        cevap = st.radio("Doğru cevabı seç:", secenekler)

        if st.button("✅ Cevabı Kontrol Et"):
            if cevap == dogru_cevap:
                st.success("Doğru!")
                puan_guncelle(True)
            else:
                st.error(f"Yanlış! Doğru cevap: {dogru_cevap}")
                puan_guncelle(False)

# -------------------------------
# İstatistikler
# -------------------------------
elif sayfa == "📊 İstatistikler":
    st.title("📊 İstatistikler")

    st.subheader("Genel Toplam")
    st.write(f"✅ Doğru: {puan['dogru']}")
    st.write(f"❌ Yanlış: {puan['yanlis']}")

    st.subheader("📅 Günlük İstatistikler")
    for tarih, deger in puan["gunluk"].items():
        st.write(f"📌 {tarih} → ✅ {deger['dogru']} | ❌ {deger['yanlis']}")
