import streamlit as st
import json
import os
import random
import shutil
from datetime import datetime
import pandas as pd

# -------------------- Dosya Yolları --------------------
DATA_FILE = "paragraflar.json"
SCORE_FILE = "puan_paragraf.json"
BACKUP_DATA_FILE = "paragraflar_backup.json"
BACKUP_SCORE_FILE = "puan_paragraf_backup.json"


# -------------------- Yardımcı Fonksiyonlar --------------------

def create_backup():
    """Veri dosyalarının backup'ını oluştur"""
    try:
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, BACKUP_DATA_FILE)
        if os.path.exists(SCORE_FILE):
            shutil.copy2(SCORE_FILE, BACKUP_SCORE_FILE)
        return True
    except Exception as e:
        st.error(f"Backup oluşturulamadı: {e}")
        return False


def restore_from_backup():
    """Backup dosyalarından verileri geri yükle"""
    try:
        if os.path.exists(BACKUP_DATA_FILE):
            shutil.copy2(BACKUP_DATA_FILE, DATA_FILE)
        if os.path.exists(BACKUP_SCORE_FILE):
            shutil.copy2(BACKUP_SCORE_FILE, SCORE_FILE)
        return True
    except Exception as e:
        st.error(f"Backup'tan geri yükleme başarısız: {e}")
        return False


def safe_save_data():
    """Verileri güvenli bir şekilde kaydet"""
    try:
        # Önce backup oluştur
        create_backup()

        if paragraflar is not None:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(paragraflar, f, ensure_ascii=False, indent=2)
        if score_data is not None:
            with open(SCORE_FILE, "w", encoding="utf-8") as f:
                json.dump(score_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Veri kaydedilirken hata: {e}")
        # Hata durumunda backup'tan geri yükle
        if restore_from_backup():
            st.warning("Backup'tan geri yükleme yapıldı.")
        return False


def initialize_default_data():
    """Varsayılan veri yapısı oluştur"""
    default_paragraflar = [
        {
            "id": 1,
            "title": "Örnek Paragraf 1",
            "paragraph": "The rapid development of technology has transformed the way we communicate. Social media platforms have connected people across the globe, making it easier to share information and maintain relationships. However, this digital revolution has also brought new challenges.",
            "turkish_translation": "Teknolojinin hızlı gelişimi iletişim şeklimizi değiştirdi. Sosyal medya platformları dünya çapında insanları birbirine bağladı, bilgi paylaşmayı ve ilişkileri sürdürmeyi kolaylaştırdı. Ancak bu dijital devrim aynı zamanda yeni zorluklar da getirdi.",
            "questions": [
                {
                    "type": "en_to_tr",
                    "question": "Social media platforms have connected people across the globe",
                    "correct_answer": "Sosyal medya platformları dünya çapında insanları birbirine bağladı",
                    "options": [
                        "Sosyal medya platformları dünya çapında insanları birbirine bağladı",
                        "Sosyal medya platformları yerel insanları birbirine bağladı",
                        "Sosyal medya platformları sadece gençleri birbirine bağladı",
                        "Sosyal medya platformları işadamlarını birbirine bağladı"
                    ]
                },
                {
                    "type": "tr_to_en",
                    "question": "Teknolojinin hızlı gelişimi iletişim şeklimizi değiştirdi",
                    "correct_answer": "The rapid development of technology has transformed the way we communicate",
                    "options": [
                        "The rapid development of technology has transformed the way we communicate",
                        "The slow development of technology has changed our communication",
                        "The rapid growth of science has transformed our communication",
                        "The rapid development of technology has improved our relationships"
                    ]
                },
                {
                    "type": "fill_blank",
                    "question": "However, this digital _____ has also brought new challenges.",
                    "correct_answer": "revolution",
                    "options": ["revolution", "evolution", "solution", "situation"]
                }
            ],
            "added_date": "2025-01-15",
            "difficulty": "intermediate"
        }
    ]

    default_score_data = {
        "total_score": 5,
        "daily": {
            "2025-01-15": {
                "score": 5,
                "questions_answered": 0,
                "correct": 0,
                "wrong": 0,
                "en_to_tr_answered": 0,
                "tr_to_en_answered": 0,
                "fill_blank_answered": 0
            }
        },
        "last_check_date": "2025-01-15",
        "questions_answered_today": 0,
        "correct_streak": 0,
        "wrong_streak": 0,
        "en_to_tr_answered": 0,
        "tr_to_en_answered": 0,
        "fill_blank_answered": 0
    }

    return default_paragraflar, default_score_data


def safe_load_data():
    """Verileri güvenli bir şekilde yükle"""
    paragraflar = []
    score_data = {
        "total_score": 0,
        "daily": {},
        "last_check_date": None,
        "questions_answered_today": 0,
        "correct_streak": 0,
        "wrong_streak": 0,
        "en_to_tr_answered": 0,
        "tr_to_en_answered": 0,
        "fill_blank_answered": 0
    }

    # Ana dosyaları yüklemeyi dene
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                paragraflar = json.load(f)
                if not paragraflar:  # Boş dosya kontrolü
                    st.warning("⚠️ Paragraflar dosyası boş, varsayılan veriler yükleniyor...")
                    paragraflar, _ = initialize_default_data()
        else:
            st.info("📝 İlk kez açılıyor, varsayılan veriler yükleniyor...")
            paragraflar, _ = initialize_default_data()

        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                loaded_score = json.load(f)
                for key in score_data.keys():
                    if key in loaded_score:
                        score_data[key] = loaded_score[key]
        else:
            _, score_data = initialize_default_data()

    except Exception as e:
        st.error(f"Ana dosyalar yüklenirken hata: {e}")

        # Backup'tan yüklemeyi dene
        try:
            if os.path.exists(BACKUP_DATA_FILE):
                with open(BACKUP_DATA_FILE, "r", encoding="utf-8") as f:
                    paragraflar = json.load(f)
                st.success("✅ Paragraflar backup'tan yüklendi!")
            else:
                paragraflar, score_data = initialize_default_data()
                st.info("🔄 Varsayılan veriler yüklendi.")

            if os.path.exists(BACKUP_SCORE_FILE):
                with open(BACKUP_SCORE_FILE, "r", encoding="utf-8") as f:
                    loaded_score = json.load(f)
                    for key in score_data.keys():
                        if key in loaded_score:
                            score_data[key] = loaded_score[key]
                st.success("✅ Puan verileri backup'tan yüklendi!")

        except Exception as backup_error:
            st.error(f"Backup'tan yükleme de başarısız: {backup_error}")
            paragraflar, score_data = initialize_default_data()
            st.warning("🆕 Yeni başlangıç verileri oluşturuldu.")

    # Veri doğrulama
    if not isinstance(paragraflar, list):
        paragraflar = []
    if not isinstance(score_data, dict):
        score_data = initialize_default_data()[1]

    return paragraflar, score_data


def generate_question(test_type, paragraf):
    """Test türüne göre soru üret"""
    if not paragraf.get("questions"):
        return None, None, None, None

    # Test türüne uygun soruları filtrele
    suitable_questions = [q for q in paragraf["questions"] if q["type"] == test_type]

    if not suitable_questions:
        return None, None, None, None

    selected_question = random.choice(suitable_questions)

    question_text = selected_question["question"]
    correct_answer = selected_question["correct_answer"]
    options = selected_question["options"].copy()
    random.shuffle(options)

    return selected_question, question_text, correct_answer, options


# -------------------- Ana Veriler --------------------
paragraflar, score_data = safe_load_data()
current_time = datetime.now()
today = current_time.date()
today_str = today.strftime("%Y-%m-%d")

# Günlük verileri kontrol et
if "daily" not in score_data:
    score_data["daily"] = {}

if score_data.get("last_check_date") != today_str:
    # Yeni gün için sıfırla
    score_data["questions_answered_today"] = 0
    score_data["last_check_date"] = today_str
    score_data["correct_streak"] = 0
    score_data["wrong_streak"] = 0
    score_data["en_to_tr_answered"] = 0
    score_data["tr_to_en_answered"] = 0
    score_data["fill_blank_answered"] = 0

if today_str not in score_data["daily"]:
    score_data["daily"][today_str] = {
        "score": 0,
        "questions_answered": 0,
        "correct": 0,
        "wrong": 0,
        "en_to_tr_answered": 0,
        "tr_to_en_answered": 0,
        "fill_blank_answered": 0
    }

safe_save_data()

# -------------------- Streamlit Arayüz --------------------

st.set_page_config(page_title="YDS Paragraf Test", page_icon="📄", layout="wide")
st.title("📄 YDS Paragraf Test Uygulaması v1.0")

# Sidebar bilgileri
with st.sidebar:
    st.markdown("### 📊 Genel Bilgiler")
    st.write(f"💰 **Toplam Puan:** {score_data['total_score']}")
    st.write(f"🕐 **Güncel Saat:** {current_time.strftime('%H:%M:%S')}")
    st.write(f"📅 **Tarih:** {today_str}")

    st.markdown("### 📈 Günlük Durum")
    bugun_soru = score_data["questions_answered_today"]
    st.write(f"❓ **Bugün çözülen:** {bugun_soru} soru")
    st.write(f"📄 **Toplam paragraf:** {len(paragraflar)}")

    # Test türü ilerlemeleri
    st.markdown("### 🎯 Test İlerlemeleri")
    en_tr_current = score_data.get("en_to_tr_answered", 0)
    tr_en_current = score_data.get("tr_to_en_answered", 0)
    fill_blank_current = score_data.get("fill_blank_answered", 0)

    st.write(f"🇺🇸➡️🇹🇷 **EN→TR:** {en_tr_current}")
    st.write(f"🇹🇷➡️🇺🇸 **TR→EN:** {tr_en_current}")
    st.write(f"📝 **Boşluk Doldurma:** {fill_blank_current}")

    # Seri durumu
    if score_data.get("correct_streak", 0) > 0:
        st.write(f"🔥 **Doğru serisi:** {score_data['correct_streak']}")

    if score_data.get("wrong_streak", 0) > 0:
        st.write(f"❌ **Yanlış serisi:** {score_data['wrong_streak']}")

# Ana menü
menu = st.sidebar.radio(
    "📋 Menü",
    ["🏠 Ana Sayfa", "📝 Testler", "📊 İstatistikler", "➕ Paragraf Ekle", "🔧 Ayarlar"],
    key="main_menu"
)

# -------------------- Ana Sayfa --------------------

if menu == "🏠 Ana Sayfa":
    st.header("🏠 Ana Sayfa")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💰 Toplam Puan", score_data['total_score'])
        st.metric("📄 Toplam Paragraf", len(paragraflar))

    with col2:
        bugun_dogru = score_data["daily"][today_str]["correct"]
        bugun_yanlis = score_data["daily"][today_str]["wrong"]
        st.metric("✅ Bugün Doğru", bugun_dogru)
        st.metric("❌ Bugün Yanlış", bugun_yanlis)

    with col3:
        if bugun_dogru + bugun_yanlis > 0:
            basari_orani = int((bugun_dogru / (bugun_dogru + bugun_yanlis)) * 100)
            st.metric("🎯 Başarı Oranı", f"{basari_orani}%")
        else:
            st.metric("🎯 Başarı Oranı", "0%")

        combo = score_data.get('correct_streak', 0)
        st.metric("🔥 Seri", combo)

    st.subheader("📊 Test Türleri Özeti")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"""
        **🇺🇸➡️🇹🇷 İngilizce → Türkçe**
        Çözülen: {en_tr_current}
        """)

    with col2:
        st.info(f"""
        **🇹🇷➡️🇺🇸 Türkçe → İngilizce**
        Çözülen: {tr_en_current}
        """)

    with col3:
        st.info(f"""
        **📝 Boşluk Doldurma**
        Çözülen: {fill_blank_current}
        """)

# -------------------- Testler --------------------

elif menu == "📝 Testler":
    st.header("📝 Testler")

    if len(paragraflar) == 0:
        st.warning("⚠️ Test çözebilmek için en az 1 paragraf olmalı!")
        st.stop()

    # Test türü seçimi
    if "selected_test_type" not in st.session_state:
        st.session_state.selected_test_type = None

    # Test türü butonları
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🇺🇸➡️🇹🇷 İngilizce → Türkçe", use_container_width=True,
                     type="primary" if st.session_state.selected_test_type == "en_to_tr" else "secondary"):
            st.session_state.selected_test_type = "en_to_tr"
            st.session_state.current_question = None

    with col2:
        if st.button("🇹🇷➡️🇺🇸 Türkçe → İngilizce", use_container_width=True,
                     type="primary" if st.session_state.selected_test_type == "tr_to_en" else "secondary"):
            st.session_state.selected_test_type = "tr_to_en"
            st.session_state.current_question = None

    with col3:
        if st.button("📝 Boşluk Doldurma", use_container_width=True,
                     type="primary" if st.session_state.selected_test_type == "fill_blank" else "secondary"):
            st.session_state.selected_test_type = "fill_blank"
            st.session_state.current_question = None

    # Test seçilmişse soruyu göster
    if st.session_state.selected_test_type:
        st.divider()

        # Mevcut soruyu kontrol et, yoksa yeni soru üret
        if "current_question" not in st.session_state or st.session_state.current_question is None:
            selected_paragraph = random.choice(paragraflar)
            result = generate_question(st.session_state.selected_test_type, selected_paragraph)

            if result[0] is None:  # Bu türde soru yoksa
                st.warning(f"Bu paragraf için {st.session_state.selected_test_type} türünde soru bulunamadı!")
                st.session_state.selected_test_type = None
                st.stop()

            st.session_state.current_question = {
                "paragraph": selected_paragraph,
                "question_obj": result[0],
                "question_text": result[1],
                "correct_answer": result[2],
                "options": result[3],
                "answered": False,
                "result_message": ""
            }

        question_data = st.session_state.current_question

        # Paragrafı göster
        st.subheader(f"📄 {question_data['paragraph']['title']}")
        with st.expander("Paragrafı Oku", expanded=True):
            st.write(question_data['paragraph']['paragraph'])

            # Türkçe çevirisini göster (sadece boşluk doldurma testinde)
            if st.session_state.selected_test_type == "fill_blank":
                with st.expander("Türkçe Çeviri"):
                    st.write(question_data['paragraph']['turkish_translation'])

        st.divider()

        # Soruyu göster
        st.subheader("Soru:")
        st.write(question_data["question_text"])

        # Cevap verilmemişse seçenekleri göster
        if not question_data["answered"]:
            selected_answer = st.radio(
                "Seçenekler:",
                question_data["options"],
                key=f"answer_radio_{st.session_state.selected_test_type}_{hash(str(question_data))}"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Cevapla", key="answer_btn", type="primary"):
                    # Cevabı işle
                    is_correct = selected_answer == question_data["correct_answer"]

                    # Sayaçları güncelle
                    score_data["questions_answered_today"] += 1
                    test_type = st.session_state.selected_test_type

                    if test_type == "en_to_tr":
                        score_data["en_to_tr_answered"] += 1
                        score_data["daily"][today_str]["en_to_tr_answered"] += 1
                    elif test_type == "tr_to_en":
                        score_data["tr_to_en_answered"] += 1
                        score_data["daily"][today_str]["tr_to_en_answered"] += 1
                    elif test_type == "fill_blank":
                        score_data["fill_blank_answered"] += 1
                        score_data["daily"][today_str]["fill_blank_answered"] += 1

                    # Basit puanlama (geliştirilecek)
                    if is_correct:
                        score_data["total_score"] += 1
                        score_data["daily"][today_str]["score"] += 1
                        score_data["daily"][today_str]["correct"] += 1
                        score_data["correct_streak"] += 1
                        score_data["wrong_streak"] = 0
                        question_data["result_message"] = "✅ Doğru! (+1 puan)"
                    else:
                        score_data["daily"][today_str]["wrong"] += 1
                        score_data["wrong_streak"] += 1
                        score_data["correct_streak"] = 0
                        question_data[
                            "result_message"] = f"❌ Yanlış! Doğru cevap: **{question_data['correct_answer']}**"

                    score_data["daily"][today_str]["questions_answered"] += 1
                    question_data["answered"] = True
                    safe_save_data()
                    st.rerun()

        # Cevap verildiyse sonucu göster
        else:
            if "✅" in question_data["result_message"]:
                st.success(question_data["result_message"])
            else:
                st.error(question_data["result_message"])

            # Sonraki soru butonu
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔄 Sonraki Soru", key="next_question", type="primary", use_container_width=True):
                    st.session_state.current_question = None
                    st.rerun()

            with col2:
                if st.button("🏠 Test Menüsüne Dön", key="back_to_menu", use_container_width=True):
                    st.session_state.selected_test_type = None
                    st.session_state.current_question = None
                    st.rerun()
    else:
        st.info("👆 Yukarıdaki butonlardan bir test türü seçin")

# -------------------- İstatistikler --------------------

elif menu == "📊 İstatistikler":
    st.header("📊 İstatistikler")

    tab1, tab2 = st.tabs(["📈 Günlük", "📊 Genel"])

    with tab1:
        st.subheader("📈 Günlük İstatistikler")
        if score_data["daily"]:
            daily_df = pd.DataFrame.from_dict(score_data["daily"], orient="index")
            daily_df.index = pd.to_datetime(daily_df.index)
            daily_df = daily_df.sort_index()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("📅 Toplam Gün", len(daily_df))
                st.metric("❓ Toplam Soru", daily_df["questions_answered"].sum())

            with col2:
                st.metric("💰 Toplam Puan", daily_df["score"].sum())
                avg_daily = daily_df["score"].mean()
                st.metric("📊 Günlük Ortalama", f"{avg_daily:.1f}")

            st.subheader("📈 Günlük Puan Grafiği")
            st.line_chart(daily_df["score"])

            st.subheader("📋 Günlük Detay Tablosu")
            st.dataframe(daily_df.iloc[::-1])
        else:
            st.info("📝 Henüz günlük veri yok.")

    with tab2:
        st.subheader("📊 Genel İstatistikler")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💰 Toplam Puan", score_data["total_score"])
            st.metric("📄 Paragraf Sayısı", len(paragraflar))

        with col2:
            total_dogru = sum(v.get("correct", 0) for v in score_data["daily"].values())
            total_yanlis = sum(v.get("wrong", 0) for v in score_data["daily"].values())
            st.metric("✅ Toplam Doğru", total_dogru)
            st.metric("❌ Toplam Yanlış", total_yanlis)

        with col3:
            if total_dogru + total_yanlis > 0:
                basari_orani = (total_dogru / (total_dogru + total_yanlis)) * 100
                st.metric("🎯 Genel Başarı", f"{basari_orani:.1f}%")
            else:
                st.metric("🎯 Genel Başarı", "0%")

            aktif_gunler = len([d for d in score_data["daily"].values() if d.get("questions_answered", 0) > 0])
            st.metric("📅 Aktif Gün", aktif_gunler)

        with col4:
            combo = score_data.get("correct_streak", 0)
            st.metric("🔥 Mevcut Seri", combo)

            total_soru = sum(v.get("questions_answered", 0) for v in score_data["daily"].values())
            st.metric("❓ Toplam Soru", total_soru)

# -------------------- Paragraf Ekle --------------------

elif menu == "➕ Paragraf Ekle":
    st.header("➕ Paragraf Ekle")

    tab1, tab2 = st.tabs(["➕ Yeni Paragraf", "📚 Paragraf Listesi"])

    with tab1:
        st.subheader("➕ Yeni Paragraf Ekle")

        with st.form("paragraf_form", clear_on_submit=True):
            title = st.text_input("📝 Paragraf Başlığı", placeholder="örn: Technology and Communication")

            paragraph = st.text_area(
                "📄 İngilizce Paragraf",
                height=150,
                placeholder="İngilizce paragrafı buraya yazın..."
            )

            turkish_translation = st.text_area(
                "🇹🇷 Türkçe Çeviri",
                height=150,
                placeholder="Paragrafın Türkçe çevirisini buraya yazın..."
            )

            difficulty = st.selectbox(
                "📊 Zorluk Seviyesi",
                ["beginner", "intermediate", "advanced"],
                index=1
            )

            submitted = st.form_submit_button("💾 Kaydet", use_container_width=True)

            if submitted:
                if title.strip() and paragraph.strip() and turkish_translation.strip():
                    # Yeni paragraf ekle
                    new_id = max([p.get("id", 0) for p in paragraflar], default=0) + 1

                    yeni_paragraf = {
                        "id": new_id,
                        "title": title.strip(),
                        "paragraph": paragraph.strip(),
                        "turkish_translation": turkish_translation.strip(),
                        "questions": [],  # Sorular ayrıca eklenecek
                        "added_date": today_str,
                        "difficulty": difficulty
                    }

                    paragraflar.append(yeni_paragraf)

                    if safe_save_data():
                        st.success(f"✅ Paragraf kaydedildi: **{title}**")
                    else:
                        st.error("❌ Kayıt sırasında hata oluştu!")
                else:
                    st.warning("⚠️ Tüm alanları doldurun.")

    with tab2:
        st.subheader("📚 Paragraf Listesi")

        if paragraflar:
            for i, paragraf in enumerate(paragraflar, 1):
                with st.expander(f"{i}. {paragraf['title']} ({paragraf.get('difficulty', 'intermediate')})"):
                    st.write("**İngilizce:**")
                    st.write(paragraf['paragraph'][:200] + "..." if len(paragraf['paragraph']) > 200 else paragraf[
                        'paragraph'])

                    st.write("**Türkçe:**")
                    st.write(
                        paragraf['turkish_translation'][:200] + "..." if len(paragraf['turkish_translation']) > 200 else
                        paragraf['turkish_translation'])

                    st.write(f"**Soru Sayısı:** {len(paragraf.get('questions', []))}")
                    st.write(f"**Eklenme Tarihi:** {paragraf.get('added_date', 'Bilinmiyor')}")
        else:
            st.info("📝 Henüz eklenmiş paragraf yok.")

# -------------------- Ayarlar --------------------

elif menu == "🔧 Ayarlar":
    st.header("🔧 Ayarlar")

    tab1, tab2 = st.tabs(["💾 Veri Yönetimi", "ℹ️ Bilgi"])

    with tab1:
        st.subheader("💾 Veri Yönetimi")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Backup İşlemleri:**")
            if st.button("💾 Manuel Backup Oluştur", use_container_width=True):
                if create_backup():
                    st.success("✅ Backup başarıyla oluşturuldu!")
                else:
                    st.error("❌ Backup oluşturulamadı!")

            if st.button("🔄 Backup'tan Geri Yükle", use_container_width=True):
                if os.path.exists(BACKUP_DATA_FILE) and os.path.exists(BACKUP_SCORE_FILE):
                    if st.button("⚠️ Onaylıyorum", key="confirm_restore"):
                        if restore_from_backup():
                            st.success("✅ Backup'tan geri yüklendi!")
                            st.rerun()
                        else:
                            st.error("❌ Geri yükleme başarısız!")
                else:
                    st.warning("⚠️ Backup dosyası bulunamadı!")

        with col2:
            st.write("**Dosya Durumu:**")
            st.write(f"📄 Paragraf dosyası: {'✅' if os.path.exists(DATA_FILE) else '❌'}")
            st.write(f"📊 Puan dosyası: {'✅' if os.path.exists(SCORE_FILE) else '❌'}")
            st.write(f"💾 Paragraf backup: {'✅' if os.path.exists(BACKUP_DATA_FILE) else '❌'}")
            st.write(f"💾 Puan backup: {'✅' if os.path.exists(BACKUP_SCORE_FILE) else '❌'}")

            if st.button("🔄 Verileri Yenile", use_container_width=True):
                st.rerun()

        st.divider()

        st.subheader("📥 Veri İçe/Dışa Aktarma")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**📥 Veri İçe Aktarma:**")
            uploaded_paragraflar = st.file_uploader("Paragraflar JSON", type=['json'], key="upload_paragraflar")
            uploaded_puan = st.file_uploader("Puan JSON", type=['json'], key="upload_puan")

            if st.button("📥 İçe Aktar", type="primary"):
                try:
                    success_messages = []

                    if uploaded_paragraflar:
                        paragraflar_data = json.load(uploaded_paragraflar)
                        if isinstance(paragraflar_data, list):
                            paragraflar.clear()
                            paragraflar.extend(paragraflar_data)
                            success_messages.append("✅ Paragraflar içe aktarıldı!")
                        else:
                            st.error("❌ Paragraflar verisi hatalı format!")

                    if uploaded_puan:
                        puan_data = json.load(uploaded_puan)
                        if isinstance(puan_data, dict):
                            score_data.clear()
                            score_data.update(puan_data)
                            success_messages.append("✅ Puan verileri içe aktarıldı!")
                        else:
                            st.error("❌ Puan verisi hatalı format!")

                    if success_messages and (uploaded_paragraflar or uploaded_puan):
                        safe_save_data()
                        for msg in success_messages:
                            st.success(msg)
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ İçe aktarma hatası: {e}")

        with col2:
            st.write("**📤 Veri Dışa Aktarma:**")

            if st.button("📤 Paragrafları İndir", use_container_width=True):
                paragraflar_json = json.dumps(paragraflar, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ paragraflar.json İndir",
                    paragraflar_json,
                    "paragraflar_backup.json",
                    "application/json"
                )

            if st.button("📤 Puanları İndir", use_container_width=True):
                puan_json = json.dumps(score_data, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ puan.json İndir",
                    puan_json,
                    "puan_paragraf_backup.json",
                    "application/json"
                )

        st.divider()

        st.subheader("⚠️ Tehlikeli İşlemler")
        st.warning("Bu işlemler geri alınamaz!")

        if st.button("🗑️ Tüm Verileri Sıfırla", type="secondary"):
            if st.button("⚠️ EMİNİM, SİL!", key="confirm_reset"):
                paragraflar.clear()
                score_data.clear()
                score_data.update({
                    "total_score": 0,
                    "daily": {},
                    "last_check_date": None,
                    "questions_answered_today": 0,
                    "correct_streak": 0,
                    "wrong_streak": 0,
                    "en_to_tr_answered": 0,
                    "tr_to_en_answered": 0,
                    "fill_blank_answered": 0
                })
                if safe_save_data():
                    st.success("✅ Tüm veriler sıfırlandı!")
                    st.rerun()

    with tab2:
        st.subheader("ℹ️ Uygulama Bilgileri")

        st.write("**🔧 Versiyon:** 1.0 - Temel İskelet")
        st.write("**📅 Oluşturma Tarihi:** Bugün")

        st.markdown("### ✨ Özellikler:")
        st.success("""
        ✅ **Mevcut Özellikler:**
        • Paragraf ekleme ve listeleme
        • 3 farklı test türü (EN→TR, TR→EN, Boşluk Doldurma)
        • Temel puanlama sistemi
        • Günlük ve genel istatistikler
        • Veri yedekleme ve geri yükleme
        • Güvenli veri kaydetme sistemi

        🔄 **Planlanan Özellikler:**
        • Gelişmiş puanlama sistemi
        • Günlük hedefler
        • Combo sistemi
        • Zorluk seviyesine göre puanlama
        • Soru ekleme arayüzü
        • Paragraf düzenleme
        """)

        st.write("**🎯 Test Türleri:**")
        st.info("""
        • **EN→TR:** İngilizce cümle veriliyor, Türkçe karşılığı bulunuyor
        • **TR→EN:** Türkçe cümle veriliyor, İngilizce karşılığı bulunuyor  
        • **Boşluk Doldurma:** Cümlede boş bırakılan kelime tamamlanıyor
        """)

        st.write("**💾 Veri Güvenliği:**")
        st.info("""
        • Otomatik backup sistemi
        • Hata durumunda backup'tan geri yükleme
        • JSON formatında veri saklama
        • Manuel veri dışa/içe aktarma imkanı
        """)

# Son satırda eksik kapanış parantezi eklendi