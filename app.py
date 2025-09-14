import streamlit as st
import json
import os
import random

DATA_FILE = "paragraflar.json"
SCORE_FILE = "puan.json"

# Paragrafları yükle
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        paragraflar = json.load(f)
else:
    paragraflar = []

# Puanları yükle
if os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "r", encoding="utf-8") as f:
        puan = json.load(f)
else:
    puan = {"dogru": 0, "yanlis": 0}

st.title("📘 YDS Paragraf Çalışma Uygulaması")

if not paragraflar:
    st.warning("Henüz paragraf eklenmemiş. Lütfen paragraflar.json dosyasına içerik ekle.")
else:
    # Rastgele paragraf ve cümle seç
    secili_paragraf = random.choice(paragraflar)
    secili_cumle = random.choice(secili_paragraf["sentences"])

    st.subheader("Cümleyi Oku 👇")
    st.write(secili_cumle["text"])

    secenekler = secili_cumle["choices"]
    random.shuffle(secenekler)

    cevap = st.radio("Doğru anlamını seç:", secenekler)

    if st.button("Cevabı Kontrol Et"):
        if cevap == secili_cumle["answer"]:
            st.success("✅ Doğru!")
            puan["dogru"] += 1
        else:
            st.error(f"❌ Yanlış! Doğru cevap: {secili_cumle['answer']}")
            puan["yanlis"] += 1

        # Puanı kaydet
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(puan, f, ensure_ascii=False, indent=2)

st.sidebar.header("📊 İstatistikler")
st.sidebar.write(f"Doğru: {puan['dogru']}")
st.sidebar.write(f"Yanlış: {puan['yanlis']}")
