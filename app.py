import streamlit as st
import json
import os
import random
import shutil
import zipfile
from datetime import datetime
import pandas as pd

# -------------------- Dosya Yolları --------------------
DATA_FILE = "paragraflar.json"
SCORE_FILE = "puan_paragraf.json"
BACKUP_DATA_FILE = "paragraflar_backup.json"
BACKUP_SCORE_FILE = "puan_paragraf_backup.json"
WORDS_FILE = "kelimeler.json"
SYNONYM_FILE = "es_anlamli.json"  # Eş anlamlı kelimeler

# -------------------- Varsayılan Kelimeler --------------------
DEFAULT_WORDS = [
    "communication", "technology", "environment", "education", "health",
    "development", "research", "society", "economy", "culture",
    "innovation", "sustainable", "effective", "significant", "essential",
    "analyze", "improve", "create", "discover", "implement",
    "challenge", "opportunity", "solution", "benefit", "impact",
    "global", "modern", "traditional", "digital", "natural",
    "popular", "successful", "important", "necessary", "possible"
]

# -------------------- Varsayılan Eş Anlamlı Kelimeler --------------------
DEFAULT_SYNONYMS = [
    {
        "id": 1,
        "type": "synonym",
        "question": "Which of the following expressions refer to 'important'?",
        "options": ["unusual", "weird", "crucial", "essential", "significant"],
        "correct_answers": ["crucial", "essential", "significant"],
        "solution": "'Important' means 'crucial, essential, significant'."
    },
    {
        "id": 2,
        "type": "synonym",
        "question": "Which of the following expressions refer to 'strange'?",
        "options": ["weird", "unusual", "hazardous", "beneficial", "peculiar"],
        "correct_answers": ["weird", "unusual", "peculiar"],
        "solution": "'Strange' is synonymous with 'weird, unusual, peculiar'."
    },
    {
        "id": 3,
        "type": "synonym",
        "question": "Which of the following expressions refer to 'required'?",
        "options": ["essential", "fundamental", "hazardous", "needed", "urgent"],
        "correct_answers": ["essential", "fundamental", "needed"],
        "solution": "'Required' means something that is essential, fundamental, or needed."
    },
    {
        "id": 4,
        "type": "synonym",
        "question": "Which of the following expressions refer to 'huge'?",
        "options": ["tiny", "immense", "giant", "stable", "consistent"],
        "correct_answers": ["immense", "giant"],
        "solution": "'Huge' means very big, similar to 'immense' or 'giant'."
    },
    {
        "id": 5,
        "type": "meaning",
        "question": "Which of the following expressions have a 'negative meaning'?",
        "options": ["hazardous", "beneficial", "distinct", "invaluable", "disappointing"],
        "correct_answers": ["hazardous", "disappointing"],
        "solution": "'Hazardous' (dangerous) and 'disappointing' carry negative meanings."
    }
]


# -------------------- Yardımcı Fonksiyonlar --------------------

def load_synonyms():
    """Eş anlamlı kelimeler dosyasını yükle"""
    try:
        if os.path.exists(SYNONYM_FILE):
            with open(SYNONYM_FILE, "r", encoding="utf-8") as f:
                synonyms = json.load(f)
                return synonyms if isinstance(synonyms, list) and synonyms else DEFAULT_SYNONYMS
        else:
            # Varsayılan eş anlamlı kelimeleri kaydet
            with open(SYNONYM_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SYNONYMS, f, ensure_ascii=False, indent=2)
            return DEFAULT_SYNONYMS
    except Exception as e:
        st.error(f"Eş anlamlı kelimeler yüklenirken hata: {e}")
        return DEFAULT_SYNONYMS


def save_synonyms(synonyms):
    """Eş anlamlı kelimeleri kaydet"""
    try:
        with open(SYNONYM_FILE, "w", encoding="utf-8") as f:
            json.dump(synonyms, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Eş anlamlı kelimeler kaydedilirken hata: {e}")
        return False


def load_words():
    """Kelimeler dosyasını yükle"""
    try:
        if os.path.exists(WORDS_FILE):
            with open(WORDS_FILE, "r", encoding="utf-8") as f:
                words = json.load(f)
                return words if isinstance(words, list) and words else DEFAULT_WORDS
        else:
            # Varsayılan kelimeleri kaydet
            with open(WORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_WORDS, f, ensure_ascii=False, indent=2)
            return DEFAULT_WORDS
    except Exception as e:
        st.error(f"Kelimeler yüklenirken hata: {e}")
        return DEFAULT_WORDS


def save_words(words):
    """Kelimeleri kaydet"""
    try:
        with open(WORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Kelimeler kaydedilirken hata: {e}")
        return False


def generate_sentence_question(words, question_type):
    """Kelimelerden cümle soruları üret"""
    if not words or len(words) < 3:
        return None, None, None, None

    # Rastgele 2-3 kelime seç
    selected_words = random.sample(words, min(random.randint(2, 3), len(words)))

    # Basit cümle şablonları
    sentence_templates = {
        "en_to_tr": [
            f"Modern {selected_words[0]} helps people communicate better.",
            f"The {selected_words[0]} of {selected_words[1] if len(selected_words) > 1 else 'society'} is very important.",
            f"We need to {selected_words[0]} our {selected_words[1] if len(selected_words) > 1 else 'skills'}.",
            f"This {selected_words[0]} creates new opportunities.",
            f"Effective {selected_words[0]} requires good planning."
        ],
        "tr_to_en": [
            f"Modern {selected_words[0]} insanların daha iyi iletişim kurmasına yardımcı olur.",
            f"{selected_words[1] if len(selected_words) > 1 else 'Toplumun'} {selected_words[0]}'si çok önemlidir.",
            f"{selected_words[1] if len(selected_words) > 1 else 'Becerilerimizi'} {selected_words[0]} etmemiz gerekiyor.",
            f"Bu {selected_words[0]} yeni fırsatlar yaratır.",
            f"Etkili {selected_words[0]} iyi planlama gerektirir."
        ],
        "fill_blank": [
            f"Modern _____ helps people communicate better.",
            f"The importance of _____ is very significant.",
            f"We need to _____ our knowledge and skills.",
            f"This new _____ creates many opportunities.",
            f"Effective communication requires good _____."
        ]
    }

    try:
        if question_type == "en_to_tr":
            question = random.choice(sentence_templates["en_to_tr"])
            correct_answer = question  # Türkçe çeviri olacak (basitleştirilmiş)

            # Genel çeviri şablonu
            if "helps people communicate better" in question:
                word = question.split()[1]  # Modern'dan sonraki kelime
                correct_answer = f"Modern {word} insanların daha iyi iletişim kurmasına yardımcı olur."

            options = [
                correct_answer,
                f"Eski {selected_words[0]} insanları ayırır.",
                f"Basit {selected_words[0]} kimseye yardım etmez.",
                f"Karmaşık {selected_words[0]} sorun yaratır."
            ]

        elif question_type == "tr_to_en":
            question = f"Modern {selected_words[0]} insanların daha iyi iletişim kurmasına yardımcı olur."
            correct_answer = f"Modern {selected_words[0]} helps people communicate better."
            options = [
                correct_answer,
                f"Old {selected_words[0]} separates people.",
                f"Simple {selected_words[0]} helps nobody.",
                f"Complex {selected_words[0]} creates problems."
            ]

        elif question_type == "fill_blank":
            templates = [
                ("Modern _____ helps people communicate better.", selected_words[0]),
                ("The importance of _____ is very significant.", selected_words[0]),
                ("We need to _____ our knowledge and skills.", "improve"),
                ("This new _____ creates many opportunities.", selected_words[0]),
                ("Effective communication requires good _____.", "planning")
            ]

            template, answer = random.choice(templates)
            question = template
            correct_answer = answer

            # Yanlış seçenekler üret
            wrong_options = [w for w in selected_words if w != answer]
            if len(wrong_options) < 3:
                wrong_options.extend(["solution", "method", "system", "process", "result"])

            options = [correct_answer] + random.sample(wrong_options, 3)

        random.shuffle(options)
        return question, question, correct_answer, options

    except Exception as e:
        st.error(f"Cümle sorusu üretirken hata: {e}")
        return None, None, None, None


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


def create_zip_backup():
    """ZIP formatında tam backup oluştur"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"yds_backup_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Ana dosyaları ekle
            if os.path.exists(DATA_FILE):
                zipf.write(DATA_FILE)
            if os.path.exists(SCORE_FILE):
                zipf.write(SCORE_FILE)
            if os.path.exists(WORDS_FILE):
                zipf.write(WORDS_FILE)
            if os.path.exists(SYNONYM_FILE):
                zipf.write(SYNONYM_FILE)
                
            # Backup dosyalarını da ekle
            if os.path.exists(BACKUP_DATA_FILE):
                zipf.write(BACKUP_DATA_FILE)
            if os.path.exists(BACKUP_SCORE_FILE):
                zipf.write(BACKUP_SCORE_FILE)
                
            # Meta bilgi dosyası
            meta_info = {
                "backup_date": timestamp,
                "version": "3.0",
                "files": ["paragraflar.json", "puan_paragraf.json", "kelimeler.json", "es_anlamli.json"]
            }
            
            zipf.writestr("backup_info.json", json.dumps(meta_info, ensure_ascii=False, indent=2))
            
        return zip_filename
    except Exception as e:
        st.error(f"ZIP backup oluşturulamadı: {e}")
        return None


def restore_from_zip(zip_file):
    """ZIP dosyasından veri geri yükle"""
    try:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            zipf.extractall(".")
        return True
    except Exception as e:
        st.error(f"ZIP'ten geri yükleme başarısız: {e}")
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
            "difficulty": "intermediate",
            "used_questions": []  # Kullanılan soruları takip et
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
                "fill_blank_answered": 0,
                "sentence_test_answered": 0,  # Cümle testi sayacı
                "synonym_test_answered": 0    # Eş anlamlı kelime testi sayacı
            }
        },
        "last_check_date": "2025-01-15",
        "questions_answered_today": 0,
        "correct_streak": 0,
        "wrong_streak": 0,
        "en_to_tr_answered": 0,
        "tr_to_en_answered": 0,
        "fill_blank_answered": 0,
        "sentence_test_answered": 0,  # Cümle testi sayacı
        "synonym_test_answered": 0    # Eş anlamlı kelime testi sayacı
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
        "fill_blank_answered": 0,
        "sentence_test_answered": 0,  # Yeni sayaç
        "synonym_test_answered": 0    # Yeni sayaç
    }

    # Ana dosyaları yüklemeyi dene
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                paragraflar = json.load(f)
                if not paragraflar:  # Boş dosya kontrolü
                    st.warning("⚠️ Paragraflar dosyası boş, varsayılan veriler yükleniyor...")
                    paragraflar, _ = initialize_default_data()

                # Eski verilere used_questions ekle
                for paragraf in paragraflar:
                    if "used_questions" not in paragraf:
                        paragraf["used_questions"] = []
        else:
            st.info("📝 İlk kez açılıyor, varsayılan veriler yükleniyor...")
            paragraflar, _ = initialize_default_data()

        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                loaded_score = json.load(f)
                for key in score_data.keys():
                    if key in loaded_score:
                        score_data[key] = loaded_score[key]

                # Eski verilere yeni sayaçları ekle
                if "sentence_test_answered" not in score_data:
                    score_data["sentence_test_answered"] = 0
                if "synonym_test_answered" not in score_data:
                    score_data["synonym_test_answered"] = 0

                # Günlük verilere de yeni sayaçları ekle
                for daily_data in score_data.get("daily", {}).values():
                    if "sentence_test_answered" not in daily_data:
                        daily_data["sentence_test_answered"] = 0
                    if "synonym_test_answered" not in daily_data:
                        daily_data["synonym_test_answered"] = 0
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


def generate_paragraph_question(test_type, paragraf):
    """Paragraf testleri için soru üret (aynı paragraftan birden fazla soru)"""
    if not paragraf.get("questions"):
        return None, None, None, None

    # Test türüne uygun soruları filtrele
    suitable_questions = [q for q in paragraf["questions"] if q["type"] == test_type]

    if not suitable_questions:
        return None, None, None, None

    # Kullanılmamış soruları bul
    used_questions = paragraf.get("used_questions", [])
    unused_questions = []

    for i, question in enumerate(suitable_questions):
        question_key = f"{test_type}_{i}"
        if question_key not in used_questions:
            unused_questions.append((i, question, question_key))

    # Eğer tüm sorular kullanıldıysa, sıfırla
    if not unused_questions:
        # Bu test türü için kullanılan soruları sıfırla
        paragraf["used_questions"] = [q for q in used_questions if not q.startswith(f"{test_type}_")]
        unused_questions = [(i, question, f"{test_type}_{i}") for i, question in enumerate(suitable_questions)]

    if not unused_questions:
        return None, None, None, None

    # Rastgele kullanılmamış soru seç
    question_index, selected_question, question_key = random.choice(unused_questions)

    question_text = selected_question["question"]
    correct_answer = selected_question["correct_answer"]
    options = selected_question["options"].copy()
    random.shuffle(options)

    return selected_question, question_text, correct_answer, options, question_key


def generate_synonym_question(synonyms):
    """Eş anlamlı kelime sorusu üret"""
    if not synonyms:
        return None, None, None, None, None
    
    selected_question = random.choice(synonyms)
    
    question_text = selected_question["question"]
    correct_answers = selected_question["correct_answers"]
    options = selected_question["options"].copy()
    solution = selected_question.get("solution", "")
    
    # Seçenekleri karıştır
    random.shuffle(options)
    
    return selected_question, question_text, correct_answers, options, solution


# -------------------- Ana Veriler --------------------
paragraflar, score_data = safe_load_data()
words = load_words()  # Kelimeleri yükle
synonyms = load_synonyms()  # Eş anlamlı kelimeleri yükle

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
    score_data["sentence_test_answered"] = 0
    score_data["synonym_test_answered"] = 0

if today_str not in score_data["daily"]:
    score_data["daily"][today_str] = {
        "score": 0,
        "questions_answered": 0,
        "correct": 0,
        "wrong": 0,
        "en_to_tr_answered": 0,
        "tr_to_en_answered": 0,
        "fill_blank_answered": 0,
        "sentence_test_answered": 0,
        "synonym_test_answered": 0
    }

safe_save_data()

# -------------------- Streamlit Arayüz --------------------

st.set_page_config(page_title="YDS Test Uygulaması", page_icon="📄", layout="wide")
st.title("📄 YDS Test Uygulaması v3.0")

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
    st.write(f"📝 **Kelime sayısı:** {len(words)}")
    st.write(f"🔗 **Eş anlamlı soru:** {len(synonyms)}")

    # Test türü ilerlemeleri
    st.markdown("### 🎯 Test İlerlemeleri")
    en_tr_current = score_data.get("en_to_tr_answered", 0)
    tr_en_current = score_data.get("tr_to_en_answered", 0)
    fill_blank_current = score_data.get("fill_blank_answered", 0)
    sentence_current = score_data.get("sentence_test_answered", 0)
    synonym_current = score_data.get("synonym_test_answered", 0)

    st.write(f"🇺🇸➡️🇹🇷 **EN→TR:** {en_tr_current}")
    st.write(f"🇹🇷➡️🇺🇸 **TR→EN:** {tr_en_current}")
    st.write(f"📝 **Boşluk Doldurma:** {fill_blank_current}")
    st.write(f"✏️ **Cümle Testi:** {sentence_current}")
    st.write(f"🔗 **Eş Anlamlı:** {synonym_current}")

    # Seri durumu
    if score_data.get("correct_streak", 0) > 0:
        st.write(f"🔥 **Doğru serisi:** {score_data['correct_streak']}")

    if score_data.get("wrong_streak", 0) > 0:
        st.write(f"❌ **Yanlış serisi:** {score_data['wrong_streak']}")

# Ana menü
menu = st.sidebar.radio(
    "📋 Menü",
    ["🏠 Ana Sayfa", "📝 Paragraf Testleri", "✏️ Cümle Testleri", "🔗 Eş Anlamlı Testler", "📊 İstatistikler", "➕ İçerik Ekle", "🔧 Ayarlar"],
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
        **📄 Paragraf Testleri**
        • 🇺🇸➡️🇹🇷 EN→TR: {en_tr_current}
        • 🇹🇷➡️🇺🇸 TR→EN: {tr_en_current}
        • 📝 Boşluk: {fill_blank_current}
        """)

    with col2:
        st.info(f"""
        **✏️ Cümle Testleri**
        • Toplam Çözülen: {sentence_current}
        • Kelime Sayısı: {len(words)}
        """)

    with col3:
        st.info(f"""
        **🔗 Eş Anlamlı Testler**
        • Toplam Çözülen: {synonym_current}
        • Soru Sayısı: {len(synonyms)}
        """)

# -------------------- Paragraf Testleri --------------------

elif menu == "📝 Paragraf Testleri":
    st.header("📝 Paragraf Testleri")

    if len(paragraflar) == 0:
        st.warning("⚠️ Test çözebilmek için en az 1 paragraf olmalı!")
        st.stop()

    # Test türü seçimi
    if "selected_paragraph_test_type" not in st.session_state:
        st.session_state.selected_paragraph_test_type = None

    # Test türü butonları
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🇺🇸➡️🇹🇷 İngilizce → Türkçe", use_container_width=True,
                     type="primary" if st.session_state.selected_paragraph_test_type == "en_to_tr" else "secondary"):
            st.session_state.selected_paragraph_test_type = "en_to_tr"
            st.session_state.current_paragraph_question = None

    with col2:
        if st.button("🇹🇷➡️🇺🇸 Türkçe → İngilizce", use_container_width=True,
                     type="primary" if st.session_state.selected_paragraph_test_type == "tr_to_en" else "secondary"):
            st.session_state.selected_paragraph_test_type = "tr_to_en"
            st.session_state.current_paragraph_question = None

    with col3:
        if st.button("📝 Boşluk Doldurma", use_container_width=True,
                     type="primary" if st.session_state.selected_paragraph_test_type == "fill_blank" else "secondary"):
            st.session_state.selected_paragraph_test_type = "fill_blank"
            st.session_state.current_paragraph_question = None

    # Test seçilmişse soruyu göster
    if st.session_state.selected_paragraph_test_type:
        st.divider()

        # Mevcut soruyu kontrol et, yoksa yeni soru üret
        if "current_paragraph_question" not in st.session_state or st.session_state.current_paragraph_question is None:
            # Eğer aktif paragraf varsa ondan soru bul, yoksa yeni paragraf seç
            if "active_paragraph" not in st.session_state or st.session_state.active_paragraph is None:
                st.session_state.active_paragraph = random.choice(paragraflar)

            result = generate_paragraph_question(st.session_state.selected_paragraph_test_type,
                                                 st.session_state.active_paragraph)

            if result is None or result[0] is None:  # Bu türde soru yoksa
                st.warning(
                    f"Bu paragraf için {st.session_state.selected_paragraph_test_type} türünde soru kalmadı! Yeni paragraf seçiliyor...")
                st.session_state.active_paragraph = random.choice(paragraflar)
                result = generate_paragraph_question(st.session_state.selected_paragraph_test_type,
                                                     st.session_state.active_paragraph)

                if result is None or result[0] is None:
                    st.error("Hiçbir paragrafta bu türde soru bulunamadı!")
                    st.session_state.selected_paragraph_test_type = None
                    st.stop()

            st.session_state.current_paragraph_question = {
                "paragraph": st.session_state.active_paragraph,
                "question_obj": result[0],
                "question_text": result[1],
                "correct_answer": result[2],
                "options": result[3],
                "question_key": result[4],
                "answered": False,
                "result_message": ""
            }

        question_data = st.session_state.current_paragraph_question

        # Paragrafı göster
        st.subheader(f"📄 {question_data['paragraph']['title']}")
        with st.expander("Paragrafı Oku", expanded=True):
            st.write(question_data['paragraph']['paragraph'])

            # Türkçe çevirisini göster (sadece boşluk doldurma testinde)
            if st.session_state.selected_paragraph_test_type == "fill_blank":
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
                key=f"paragraph_answer_radio_{st.session_state.selected_paragraph_test_type}_{hash(str(question_data))}"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Cevapla", key="paragraph_answer_btn", type="primary"):
                    # Cevabı işle
                    is_correct = selected_answer == question_data["correct_answer"]

                    # Kullanılan soruyu işaretle
                    if question_data["question_key"] not in question_data["paragraph"]["used_questions"]:
                        question_data["paragraph"]["used_questions"].append(question_data["question_key"])

                    # Sayaçları güncelle
                    score_data["questions_answered_today"] += 1
                    test_type = st.session_state.selected_paragraph_test_type

                    if test_type == "en_to_tr":
                        score_data["en_to_tr_answered"] += 1
                        score_data["daily"][today_str]["en_to_tr_answered"] += 1
                    elif test_type == "tr_to_en":
                        score_data["tr_to_en_answered"] += 1
                        score_data["daily"][today_str]["tr_to_en_answered"] += 1
                    elif test_type == "fill_blank":
                        score_data["fill_blank_answered"] += 1
                        score_data["daily"][today_str]["fill_blank_answered"] += 1

                    # Puanlama
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
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔄 Aynı Paragraf - Sonraki Soru", key="next_paragraph_question", type="primary",
                             use_container_width=True):
                    st.session_state.current_paragraph_question = None
                    # Aktif paragrafı koruyarak devam et
                    st.rerun()

            with col2:
                if st.button("📄 Yeni Paragraf", key="new_paragraph", use_container_width=True):
                    st.session_state.current_paragraph_question = None
                    st.session_state.active_paragraph = None  # Yeni paragraf seçilsin
                    st.rerun()

            with col3:
                if st.button("🏠 Test Menüsüne Dön", key="back_to_paragraph_menu", use_container_width=True):
                    st.session_state.selected_paragraph_test_type = None
                    st.session_state.current_paragraph_question = None
                    st.session_state.active_paragraph = None
                    st.rerun()
    else:
        st.info("👆 Yukarıdaki butonlardan bir paragraf test türü seçin")

# -------------------- Cümle Testleri --------------------

elif menu == "✏️ Cümle Testleri":
    st.header("✏️ Cümle Testleri")
    st.info("Bu testlerde kelimelerinizden oluşturulan cümleler kullanılır.")

    if len(words) == 0:
        st.warning("⚠️ Test çözebilmek için en az 3 kelime olmalı!")
        st.stop()

    # Test türü seçimi
    if "selected_sentence_test_type" not in st.session_state:
        st.session_state.selected_sentence_test_type = None

    # Test türü butonları
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🇺🇸➡️🇹🇷 Cümle Çevirisi (EN→TR)", use_container_width=True,
                     type="primary" if st.session_state.selected_sentence_test_type == "sentence_en_to_tr" else "secondary"):
            st.session_state.selected_sentence_test_type = "sentence_en_to_tr"
            st.session_state.current_sentence_question = None

    with col2:
        if st.button("🇹🇷➡️🇺🇸 Cümle Çevirisi (TR→EN)", use_container_width=True,
                     type="primary" if st.session_state.selected_sentence_test_type == "sentence_tr_to_en" else "secondary"):
            st.session_state.selected_sentence_test_type = "sentence_tr_to_en"
            st.session_state.current_sentence_question = None

    with col3:
        if st.button("📝 Cümle Boşluk Doldurma", use_container_width=True,
                     type="primary" if st.session_state.selected_sentence_test_type == "sentence_fill_blank" else "secondary"):
            st.session_state.selected_sentence_test_type = "sentence_fill_blank"
            st.session_state.current_sentence_question = None

    # Test seçilmişse soruyu göster
    if st.session_state.selected_sentence_test_type:
        st.divider()

        # Mevcut soruyu kontrol et, yoksa yeni soru üret
        if "current_sentence_question" not in st.session_state or st.session_state.current_sentence_question is None:
            # Test türünü dönüştür (sentence_ prefix'ini kaldır)
            test_type = st.session_state.selected_sentence_test_type.replace("sentence_", "")
            result = generate_sentence_question(words, test_type)

            if result[0] is None:  # Soru üretilemezse
                st.error("Cümle sorusu üretilemiyor! Kelime listesini kontrol edin.")
                st.session_state.selected_sentence_test_type = None
                st.stop()

            st.session_state.current_sentence_question = {
                "question_obj": result[0],
                "question_text": result[1],
                "correct_answer": result[2],
                "options": result[3],
                "answered": False,
                "result_message": ""
            }

        question_data = st.session_state.current_sentence_question

        # Kelime listesini göster
        with st.expander("📝 Kullanılan Kelimeler", expanded=False):
            # Son 10 kelimeyi göster
            recent_words = words[-10:] if len(words) >= 10 else words
            st.write(", ".join(recent_words))
            if len(words) > 10:
                st.write(f"... ve {len(words) - 10} kelime daha")

        st.divider()

        # Soruyu göster
        st.subheader("Soru:")
        st.write(question_data["question_text"])

        # Cevap verilmemişse seçenekleri göster
        if not question_data["answered"]:
            selected_answer = st.radio(
                "Seçenekler:",
                question_data["options"],
                key=f"sentence_answer_radio_{st.session_state.selected_sentence_test_type}_{hash(str(question_data))}"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Cevapla", key="sentence_answer_btn", type="primary"):
                    # Cevabı işle
                    is_correct = selected_answer == question_data["correct_answer"]

                    # Sayaçları güncelle
                    score_data["questions_answered_today"] += 1
                    score_data["sentence_test_answered"] += 1
                    score_data["daily"][today_str]["sentence_test_answered"] += 1

                    # Puanlama (cümle testleri için aynı puanlama)
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
                if st.button("🔄 Sonraki Cümle Sorusu", key="next_sentence_question", type="primary",
                             use_container_width=True):
                    st.session_state.current_sentence_question = None
                    st.rerun()

            with col2:
                if st.button("🏠 Test Menüsüne Dön", key="back_to_sentence_menu", use_container_width=True):
                    st.session_state.selected_sentence_test_type = None
                    st.session_state.current_sentence_question = None
                    st.rerun()
    else:
        st.info("👆 Yukarıdaki butonlardan bir cümle test türü seçin")

        # Kelime listesi önizlemesi
        st.subheader("📝 Kelimeleriniz")
        if words:
            # Kelimeleri 5'erli gruplar halinde göster
            cols = st.columns(5)
            for i, word in enumerate(words):
                with cols[i % 5]:
                    st.write(f"• {word}")
                if (i + 1) % 10 == 0:  # Her 10 kelimede bir boşluk bırak
                    st.write("")
        else:
            st.info("Henüz kelime eklenmemiş.")

# -------------------- Eş Anlamlı Testler --------------------

elif menu == "🔗 Eş Anlamlı Testler":
    st.header("🔗 Eş Anlamlı Kelime Testleri")
    st.info("Bu testlerde birden fazla doğru seçenek olabilir. Tüm doğru seçenekleri işaretleyin.")

    if len(synonyms) == 0:
        st.warning("⚠️ Test çözebilmek için en az 1 eş anlamlı kelime sorusu olmalı!")
        st.stop()

    # Mevcut soruyu kontrol et, yoksa yeni soru üret
    if "current_synonym_question" not in st.session_state or st.session_state.current_synonym_question is None:
        result = generate_synonym_question(synonyms)

        if result[0] is None:  # Soru üretilemezse
            st.error("Eş anlamlı kelime sorusu üretilemiyor!")
            st.stop()

        st.session_state.current_synonym_question = {
            "question_obj": result[0],
            "question_text": result[1],
            "correct_answers": result[2],
            "options": result[3],
            "solution": result[4],
            "answered": False,
            "selected_answers": [],
            "result_message": ""
        }

    question_data = st.session_state.current_synonym_question

    # Soruyu göster
    st.subheader("Soru:")
    st.write(question_data["question_text"])

    # Cevap verilmemişse seçenekleri göster
    if not question_data["answered"]:
        st.write("**Seçenekler:** (Birden fazla seçenek işaretleyebilirsiniz)")
        
        selected_options = []
        for option in question_data["options"]:
            if st.checkbox(option, key=f"synonym_option_{option}_{hash(str(question_data))}"):
                selected_options.append(option)

        question_data["selected_answers"] = selected_options

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Cevapla", key="synonym_answer_btn", type="primary"):
                # Cevabı işle
                correct_answers_set = set(question_data["correct_answers"])
                selected_answers_set = set(question_data["selected_answers"])
                
                is_correct = correct_answers_set == selected_answers_set

                # Sayaçları güncelle
                score_data["questions_answered_today"] += 1
                score_data["synonym_test_answered"] += 1
                score_data["daily"][today_str]["synonym_test_answered"] += 1

                # Puanlama
                if is_correct:
                    score_data["total_score"] += 2  # Eş anlamlı testler 2 puan
                    score_data["daily"][today_str]["score"] += 2
                    score_data["daily"][today_str]["correct"] += 1
                    score_data["correct_streak"] += 1
                    score_data["wrong_streak"] = 0
                    question_data["result_message"] = "✅ Doğru! (+2 puan)"
                else:
                    score_data["daily"][today_str]["wrong"] += 1
                    score_data["wrong_streak"] += 1
                    score_data["correct_streak"] = 0
                    correct_answers_str = ", ".join(question_data["correct_answers"])
                    question_data["result_message"] = f"❌ Yanlış! Doğru cevaplar: **{correct_answers_str}**"

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

        # Çözümü göster
        if question_data["solution"]:
            with st.expander("💡 Çözüm"):
                st.write(question_data["solution"])

        # Seçilen ve doğru cevapları karşılaştır
        with st.expander("📊 Cevap Analizi"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Sizin Seçtikleriniz:**")
                if question_data["selected_answers"]:
                    for answer in question_data["selected_answers"]:
                        if answer in question_data["correct_answers"]:
                            st.write(f"✅ {answer}")
                        else:
                            st.write(f"❌ {answer}")
                else:
                    st.write("Hiçbir seçenek işaretlenmedi")
            
            with col2:
                st.write("**Doğru Cevaplar:**")
                for answer in question_data["correct_answers"]:
                    st.write(f"✅ {answer}")

        # Sonraki soru butonu
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Sonraki Soru", key="next_synonym_question", type="primary",
                         use_container_width=True):
                st.session_state.current_synonym_question = None
                st.rerun()

        with col2:
            if st.button("🏠 Ana Menüye Dön", key="back_to_main_menu", use_container_width=True):
                st.session_state.current_synonym_question = None
                st.rerun()

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

        # Test türlerine göre istatistikler
        st.subheader("📊 Test Türleri İstatistikleri")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📄 Paragraf Testleri:**")
            st.write(f"🇺🇸➡️🇹🇷 EN→TR: {score_data.get('en_to_tr_answered', 0)}")
            st.write(f"🇹🇷➡️🇺🇸 TR→EN: {score_data.get('tr_to_en_answered', 0)}")
            st.write(f"📝 Boşluk Doldurma: {score_data.get('fill_blank_answered', 0)}")

        with col2:
            st.markdown("**✏️ Cümle Testleri:**")
            st.write(f"✏️ Toplam Cümle Testi: {score_data.get('sentence_test_answered', 0)}")
            st.write(f"📝 Kelime Sayısı: {len(words)}")

        with col3:
            st.markdown("**🔗 Eş Anlamlı Testler:**")
            st.write(f"🔗 Toplam Eş Anlamlı: {score_data.get('synonym_test_answered', 0)}")
            st.write(f"📚 Soru Sayısı: {len(synonyms)}")

# -------------------- İçerik Ekle --------------------

elif menu == "➕ İçerik Ekle":
    st.header("➕ İçerik Ekle")

    tab1, tab2, tab3, tab4 = st.tabs(["➕ Yeni Paragraf", "🔗 Eş Anlamlı Soru", "📚 İçerik Listesi", "📝 Kelime Yönetimi"])

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
                        "difficulty": difficulty,
                        "used_questions": []  # Kullanılan soruları takip et
                    }

                    paragraflar.append(yeni_paragraf)

                    if safe_save_data():
                        st.success(f"✅ Paragraf kaydedildi: **{title}**")
                    else:
                        st.error("❌ Kayıt sırasında hata oluştu!")
                else:
                    st.warning("⚠️ Tüm alanları doldurun.")

    with tab2:
        st.subheader("🔗 Yeni Eş Anlamlı Soru Ekle")

        with st.form("synonym_form", clear_on_submit=True):
            question_text = st.text_input(
                "❓ Soru Metni", 
                placeholder="Which of the following expressions refer to 'important'?"
            )

            test_type = st.selectbox(
                "🎯 Test Türü",
                ["synonym", "meaning"],
                format_func=lambda x: "Eş Anlamlı Kelime" if x == "synonym" else "Anlam Testi"
            )

            st.write("**Seçenekler:** (Her satıra bir seçenek)")
            options_text = st.text_area(
                "Seçenekler",
                height=120,
                placeholder="unusual\nweird\ncrucial\nessential\nsignificant"
            )

            st.write("**Doğru Cevaplar:** (Virgül ile ayırın)")
            correct_answers_text = st.text_input(
                "Doğru Cevaplar",
                placeholder="crucial, essential, significant"
            )

            solution_text = st.text_area(
                "💡 Çözüm Açıklaması",
                height=80,
                placeholder="'Important' means 'crucial, essential, significant'."
            )

            submitted_synonym = st.form_submit_button("💾 Soru Ekle", use_container_width=True)

            if submitted_synonym:
                if question_text.strip() and options_text.strip() and correct_answers_text.strip():
                    # Seçenekleri işle
                    options = [opt.strip() for opt in options_text.strip().split('\n') if opt.strip()]
                    correct_answers = [ans.strip() for ans in correct_answers_text.strip().split(',') if ans.strip()]

                    # Doğru cevapların seçeneklerde olup olmadığını kontrol et
                    if all(ans in options for ans in correct_answers):
                        new_id = max([q.get("id", 0) for q in synonyms], default=0) + 1

                        yeni_soru = {
                            "id": new_id,
                            "type": test_type,
                            "question": question_text.strip(),
                            "options": options,
                            "correct_answers": correct_answers,
                            "solution": solution_text.strip() or f"Doğru cevaplar: {', '.join(correct_answers)}"
                        }

                        synonyms.append(yeni_soru)

                        if save_synonyms(synonyms):
                            st.success(f"✅ Eş anlamlı soru kaydedildi!")
                        else:
                            st.error("❌ Kayıt sırasında hata oluştu!")
                    else:
                        st.error("❌ Doğru cevaplar seçenekler arasında bulunmuyor!")
                else:
                    st.warning("⚠️ Soru metni, seçenekler ve doğru cevaplar alanlarını doldurun.")

    with tab3:
        st.subheader("📚 İçerik Listesi")

        # Paragraflar
        if paragraflar:
            st.write("**📄 Paragraflar:**")
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
                    st.write(f"**Kullanılan Sorular:** {len(paragraf.get('used_questions', []))}")
                    st.write(f"**Eklenme Tarihi:** {paragraf.get('added_date', 'Bilinmiyor')}")

                    # Kullanılan soruları sıfırla butonu
                    if paragraf.get('used_questions', []):
                        if st.button(f"🔄 Soruları Sıfırla", key=f"reset_questions_{paragraf['id']}"):
                            paragraf['used_questions'] = []
                            safe_save_data()
                            st.success("✅ Bu paragrafın kullanılan soruları sıfırlandı!")
                            st.rerun()

        # Eş anlamlı sorular
        if synonyms:
            st.write("**🔗 Eş Anlamlı Sorular:**")
            for i, soru in enumerate(synonyms, 1):
                with st.expander(f"{i}. {soru['question'][:50]}... ({soru['type']})"):
                    st.write(f"**Soru:** {soru['question']}")
                    st.write(f"**Seçenekler:** {', '.join(soru['options'])}")
                    st.write(f"**Doğru Cevaplar:** {', '.join(soru['correct_answers'])}")
                    if soru.get('solution'):
                        st.write(f"**Çözüm:** {soru['solution']}")

                    # Soru silme butonu
                    if st.button(f"🗑️ Sil", key=f"delete_synonym_{soru['id']}"):
                        synonyms.remove(soru)
                        if save_synonyms(synonyms):
                            st.success("✅ Soru silindi!")
                            st.rerun()

        if not paragraflar and not synonyms:
            st.info("📝 Henüz eklenmiş içerik yok.")

    with tab4:
        st.subheader("📝 Kelime Yönetimi")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"**Mevcut kelime sayısı:** {len(words)}")

            # Yeni kelime ekleme
            with st.form("add_word_form"):
                new_word = st.text_input("Yeni Kelime Ekle", placeholder="örn: innovation")
                if st.form_submit_button("➕ Ekle"):
                    if new_word.strip() and new_word.strip().lower() not in [w.lower() for w in words]:
                        words.append(new_word.strip().lower())
                        if save_words(words):
                            st.success(f"✅ Kelime eklendi: **{new_word.strip()}**")
                            st.rerun()
                    elif new_word.strip().lower() in [w.lower() for w in words]:
                        st.warning("⚠️ Bu kelime zaten mevcut!")
                    else:
                        st.warning("⚠️ Geçerli bir kelime girin!")

            # Toplu kelime ekleme
            with st.form("bulk_add_words"):
                bulk_words = st.text_area("Toplu Kelime Ekleme (virgül ile ayırın)",
                                          placeholder="word1, word2, word3")
                if st.form_submit_button("📝 Toplu Ekle"):
                    if bulk_words.strip():
                        new_words = [w.strip().lower() for w in bulk_words.split(",") if w.strip()]
                        added_count = 0
                        for word in new_words:
                            if word and word not in [w.lower() for w in words]:
                                words.append(word)
                                added_count += 1

                        if save_words(words):
                            st.success(f"✅ {added_count} kelime eklendi!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Kelime girin!")

        with col2:
            # Kelime silme
            if words:
                selected_word = st.selectbox("Silmek için kelime seçin:", words)
                if st.button("🗑️ Kelimeyi Sil", type="secondary"):
                    words.remove(selected_word)
                    if save_words(words):
                        st.success(f"✅ Kelime silindi: **{selected_word}**")
                        st.rerun()

            # Tüm kelimeleri sıfırla
            if st.button("🔄 Varsayılanlara Dön", type="secondary"):
                if st.button("⚠️ EMİNİM!", key="reset_words_confirm"):
                    words.clear()
                    words.extend(DEFAULT_WORDS)
                    if save_words(words):
                        st.success("✅ Kelimeler varsayılana döndürüldü!")
                        st.rerun()

        # Kelime listesi
        st.subheader("📋 Mevcut Kelimeler")
        if words:
            # 5 sütunlu gösterim
            cols = st.columns(5)
            for i, word in enumerate(words):
                with cols[i % 5]:
                    st.write(f"• {word}")
        else:
            st.info("Henüz kelime eklenmemiş.")

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

            if st.button("📦 ZIP Backup İndir", use_container_width=True, type="primary"):
                zip_filename = create_zip_backup()
                if zip_filename:
                    with open(zip_filename, "rb") as f:
                        st.download_button(
                            "⬇️ ZIP Backup İndir",
                            f.read(),
                            zip_filename,
                            "application/zip"
                        )
                    # Geçici dosyayı temizle
                    try:
                        os.remove(zip_filename)
                    except:
                        pass
                    st.success("✅ ZIP backup hazırlandı!")

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
            st.write(f"📝 Kelime dosyası: {'✅' if os.path.exists(WORDS_FILE) else '❌'}")
            st.write(f"🔗 Eş anlamlı dosyası: {'✅' if os.path.exists(SYNONYM_FILE) else '❌'}")
            st.write(f"💾 Paragraf backup: {'✅' if os.path.exists(BACKUP_DATA_FILE) else '❌'}")
            st.write(f"💾 Puan backup: {'✅' if os.path.exists(BACKUP_SCORE_FILE) else '❌'}")

            if st.button("🔄 Verileri Yenile", use_container_width=True):
                st.rerun()

        st.divider()

        st.subheader("📥 Veri İçe/Dışa Aktarma")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**📥 Veri İçe Aktarma:**")
            
            # ZIP dosyası yükleme
            uploaded_zip = st.file_uploader("ZIP Backup Yükle", type=['zip'], key="upload_zip")
            if uploaded_zip and st.button("📦 ZIP'ten Geri Yükle", type="primary"):
                try:
                    with open("temp_backup.zip", "wb") as f:
                        f.write(uploaded_zip.getvalue())
                    
                    if restore_from_zip("temp_backup.zip"):
                        # Verileri yeniden yükle
                        global paragraflar, score_data, words, synonyms
                        paragraflar, score_data = safe_load_data()
                        words = load_words()
                        synonyms = load_synonyms()
                        st.success("✅ ZIP backup'tan başarıyla geri yüklendi!")
                        st.rerun()
                    else:
                        st.error("❌ ZIP'ten geri yükleme başarısız!")
                    
                    # Geçici dosyayı temizle
                    try:
                        os.remove("temp_backup.zip")
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"❌ ZIP işleme hatası: {e}")

            st.divider()
            
            uploaded_paragraflar = st.file_uploader("Paragraflar JSON", type=['json'], key="upload_paragraflar")
            uploaded_puan = st.file_uploader("Puan JSON", type=['json'], key="upload_puan")
            uploaded_words = st.file_uploader("Kelimeler JSON", type=['json'], key="upload_words")
            uploaded_synonyms = st.file_uploader("Eş Anlamlı JSON", type=['json'], key="upload_synonyms")

            if st.button("📥 JSON Dosyalarını İçe Aktar"):
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

                    if uploaded_words:
                        words_data = json.load(uploaded_words)
                        if isinstance(words_data, list):
                            words.clear()
                            words.extend(words_data)
                            save_words(words)
                            success_messages.append("✅ Kelimeler içe aktarıldı!")
                        else:
                            st.error("❌ Kelimeler verisi hatalı format!")

                    if uploaded_synonyms:
                        synonyms_data = json.load(uploaded_synonyms)
                        if isinstance(synonyms_data, list):
                            synonyms.clear()
                            synonyms.extend(synonyms_data)
                            save_synonyms(synonyms)
                            success_messages.append("✅ Eş anlamlı sorular içe aktarıldı!")
                        else:
                            st.error("❌ Eş anlamlı verisi hatalı format!")

                    if success_messages:
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

            if st.button("📤 Kelimeleri İndir", use_container_width=True):
                words_json = json.dumps(words, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ kelimeler.json İndir",
                    words_json,
                    "kelimeler_backup.json",
                    "application/json"
                )

            if st.button("📤 Eş Anlamlıları İndir", use_container_width=True):
                synonyms_json = json.dumps(synonyms, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ es_anlamli.json İndir",
                    synonyms_json,
                    "es_anlamli_backup.json",
                    "application/json"
                )

        st.divider()

        st.subheader("⚠️ Tehlikeli İşlemler")
        st.warning("Bu işlemler geri alınamaz!")

        col1, col2, col3 = st.columns(3)

        with col1:
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
                        "fill_blank_answered": 0,
                        "sentence_test_answered": 0,
                        "synonym_test_answered": 0
                    })
                    if safe_save_data():
                        st.success("✅ Tüm veriler sıfırlandı!")
                        st.rerun()

        with col2:
            if st.button("🔄 Tüm Soruları Sıfırla", type="secondary"):
                if st.button("⚠️ EMİNİM, SIFIRLA!", key="confirm_reset_questions"):
                    for paragraf in paragraflar:
                        paragraf["used_questions"] = []
                    if safe_save_data():
                        st.success("✅ Tüm paragrafların kullanılan soruları sıfırlandı!")
                        st.rerun()

        with col3:
            if st.button("🔗 Eş Anlamlıları Sıfırla", type="secondary"):
                if st.button("⚠️ EMİNİM, VARSAYILAN!", key="confirm_reset_synonyms"):
                    synonyms.clear()
                    synonyms.extend(DEFAULT_SYNONYMS)
                    if save_synonyms(synonyms):
                        st.success("✅ Eş anlamlı sorular varsayılana döndürüldü!")
                        st.rerun()

    with tab2:
        st.subheader("ℹ️ Uygulama Bilgileri")

        st.write("**🔧 Versiyon:** 3.0 - Eş Anlamlı Kelime Testleri")
        st.write("**📅 Güncelleme Tarihi:** Bugün")

        st.markdown("### ✨ Yeni Özellikler:")
        st.success("""
        🆕 **v3.0 Güncellemeleri:**
        • Eş anlamlı kelime testleri (çoklu seçim)
        • ZIP formatında backup sistemi
        • Gelişmiş çözüm açıklamaları
        • Cevap analizi görünümü
        • Eş anlamlı soru ekleme arayüzü
        • Çoklu doğru seçenek desteği

        ✅ **v2.0 Özellikler:**
        • Aynı paragraftan birden fazla soru çözme
        • Cümle testleri sistemi
        • Kelime tabanlı cümle soruları
        • Kullanılan soru takip sistemi
        • Gelişmiş kelime yönetimi

        📊 **Temel Özellikler:**
        • Paragraf ekleme ve listeleme
        • 3 farklı paragraf test türü
        • 3 farklı cümle test türü  
        • Eş anlamlı kelime testleri
        • Detaylı istatistikler
        • Güvenli veri yönetimi
        """)

        st.write("**🎯 Test Türleri:**")

        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            **📄 Paragraf Testleri:** (1 puan)
            • **EN→TR:** İngilizce cümle → Türkçe karşılık
            • **TR→EN:** Türkçe cümle → İngilizce karşılık  
            • **Boşluk Doldurma:** Eksik kelime tamamlama

            **✏️ Cümle Testleri:** (1 puan)
            • **Cümle EN→TR:** Kelime tabanlı çeviri
            • **Cümle TR→EN:** Kelime tabanlı çeviri
            • **Cümle Boşluk:** Kelime seçimi
            """)

        with col2:
            st.info("""
            **🔗 Eş Anlamlı Testler:** (2 puan)
            • **Çoklu Seçim:** Birden fazla doğru seçenek
            • **Synonym:** Eş anlamlı kelime bulma
            • **Meaning:** Anlam kategorisi belirleme
            • **Çözüm Açıklaması:** Detaylı açıklama
            • **Cevap Analizi:** Seçim karşılaştırması
            """)

        st.write("**💾 Backup Sistemi:**")
        st.info("""
        • **ZIP Backup:** Tüm dosyaları tek dosyada
        • **JSON Export:** Ayrı ayrı veri dışa aktarma
        • **Otomatik Backup:** Her kayıtta otomatik
        • **Geri Yükleme:** ZIP veya JSON'dan geri yükleme
        • **Versiyonlama:** Backup meta bilgileri
        """)

        st.write("**🎮 Kullanım İpuçları:**")
        st.success("""
        • Eş anlamlı testlerde birden fazla seçenek işaretleyin
        • ZIP backup ile tüm verilerinizi tek dosyada saklayın  
        • Çözüm açıklamalarını okuyarak öğrenin
        • Cevap analizi ile hatalarınızı görün
        • Düzenli backup almayı unutmayın
        """)

# -------------------- Son --------------------
