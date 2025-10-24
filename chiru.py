import streamlit as st
import pandas as pd
import random
import re
import sqlite3
from datetime import datetime
import os
from gtts import gTTS
import tempfile

# Thêm thư viện xử lý file
try:
    import PyPDF2
    from docx import Document
except ImportError:
    PyPDF2 = None
    Document = None

# TỪ ĐIỂN TIẾNG NGA - VIỆT
RUSSIAN_DICTIONARY = {
    "привет": "xin chào", "спасибо": "cảm ơn", "да": "có", "нет": "không",
    "хорошо": "tốt", "плохо": "xấu", "дом": "nhà", "книга": "sách",
    "вода": "nước", "человек": "người", "день": "ngày", "ночь": "đêm",
    "время": "thời gian", "жизнь": "cuộc sống", "год": "năm", "дело": "công việc",
    "рука": "tay", "глаз": "mắt", "город": "thành phố", "друг": "bạn",
    "стол": "bàn", "стул": "ghế", "окно": "cửa sổ", "дверь": "cửa",
}

# TỪ ĐIỂN TIẾNG TRUNG - VIỆT
CHINESE_DICTIONARY = {
    "你好": "xin chào", "谢谢": "cảm ơn", "是": "có", "不是": "không",
    "好": "tốt", "不好": "không tốt", "家": "nhà", "书": "sách",
    "水": "nước", "人": "người", "天": "ngày", "晚上": "buổi tối",
    "时间": "thời gian", "生活": "cuộc sống", "年": "năm", "工作": "công việc",
    "手": "tay", "眼睛": "mắt", "城市": "thành phố", "朋友": "bạn",
    "桌子": "bàn", "椅子": "ghế", "窗户": "cửa sổ", "门": "cửa",
    "房间": "phòng", "公寓": "căn hộ", "街道": "đường phố", "汽车": "xe hơi",
    "词": "từ", "地方": "nơi", "脸": "khuôn mặt", "女人": "phụ nữ",
    "男人": "đàn ông", "孩子": "trẻ em", "系统": "hệ thống", "数字": "số",
    "头": "đầu", "脚": "chân", "类型": "loại", "法律": "luật",
    "问题": "câu hỏi", "边": "phía", "国家": "đất nước", "世界": "thế giới",
    "情况": "tình huống", "声音": "giọng nói", "区域": "khu vực", "文章": "bài báo",
    "组": "nhóm", "公司": "công ty", "过程": "quá trình", "条件": "điều kiện",
    "结果": "kết quả", "权力": "quyền lực", "电影": "phim", "音乐": "âm nhạc",
    "剧院": "nhà hát", "语言": "ngôn ngữ", "气味": "mùi", "味道": "vị",
    "颜色": "màu sắc", "大小": "kích thước", "形状": "hình dạng", "状态": "tình trạng",
    "性质": "tính chất", "时期": "thời kỳ", "时刻": "khoảnh khắc", "目标": "mục tiêu",
    "班级": "lớp", "原因": "nguyên nhân", "结论": "kết luận", "经验": "kinh nghiệm",
    "联系": "liên kết", "水平": "mức độ", "百分比": "phần trăm", "解决": "giải pháp",
    "收入": "thu nhập", "支出": "chi phí", "银行": "ngân hàng", "钱": "tiền",
    "价格": "giá", "计划": "kế hoạch", "报告": "báo cáo", "产品": "sản phẩm",
    "技术": "công nghệ", "信息": "thông tin", "点": "điểm", "线": "đường",
    "手段": "phương tiện", "开始": "bắt đầu", "结束": "kết thúc", "部分": "phần",
    "选择": "lựa chọn", "星期": "tuần", "月": "tháng", "世纪": "thế kỷ",
    "路": "con đường", "方法": "phương pháp", "类型": "kiểu", "原则": "nguyên tắc",
    "例子": "ví dụ", "来源": "nguồn", "事实": "sự thật", "事件": "sự kiện",
    "对象": "đối tượng", "公民": "công dân", "领土": "lãnh thổ", "面积": "diện tích",
    "人口": "dân số", "预算": "ngân sách", "项目": "dự án", "程序": "chương trình",
    "组织": "tổ chức", "活动": "hoạt động", "发展": "phát triển", "市场": "thị trường",
    "企业": "doanh nghiệp", "商品": "hàng hóa", "投资": "đầu tư", "资本": "vốn",
    "资源": "tài nguyên", "利润": "lợi nhuận", "税": "thuế", "经济": "kinh tế",
    "文化": "văn hóa", "艺术": "nghệ thuật", "文学": "văn học", "科学": "khoa học",
    "教育": "giáo dục", "健康": "sức khỏe", "运动": "thể thao", "休息": "nghỉ ngơi",
    "旅行": "du lịch", "关系": "mối quan hệ", "位置": "vị trí", "功能": "chức năng",
    "结构": "cấu trúc", "内容": "nội dung", "基础": "cơ sở", "指标": "chỉ số",
    "状态": "trạng thái", "标准": "tiêu chí", "因素": "yếu tố", "动态": "động lực",
    "趋势": "xu hướng", "前景": "triển vọng", "战略": "chiến lược", "概念": "khái niệm",
    "机制": "cơ chế", "元素": "yếu tố", "单位": "đơn vị", "环境": "môi trường",
    "情况": "tình huống", "选项": "phương án", "版本": "phiên bản", "模型": "mô hình",
    "方案": "sơ đồ", "图表": "đồ thị", "图表": "biểu đồ", "表": "bảng",
    "文件": "tài liệu", "行业": "ngành", "部门": "khu vực", "方向": "hướng",
    "复杂": "phức hợp", "体积": "khối lượng", "质量": "khối lượng", "密度": "mật độ",
    "速度": "tốc độ", "压力": "áp suất", "温度": "nhiệt độ", "湿度": "độ ẩm",
    "光": "ánh sáng", "声音": "âm thanh", "振动": "rung động", "辐射": "bức xạ",
    "场": "trường", "波": "sóng", "粒子": "hạt", "原子": "nguyên tử",
    "分子": "phân tử", "物质": "chất", "材料": "vật liệu", "细节": "chi tiết",
    "节点": "nút", "块": "khối", "集合": "tổ hợp", "安装": "lắp đặt",
    "设备": "thiết bị", "工具": "công cụ", "仪器": "dụng cụ", "发动机": "động cơ",
    "发电机": "máy phát", "变压器": "máy biến áp", "继电器": "rơle", "开关": "công tắc",
    "插座": "ổ cắm", "线": "dây dẫn", "电缆": "cáp", "绝缘": "cách điện",
    "接地": "nối đất", "电压": "điện áp", "电流": "dòng điện", "电阻": "điện trở",
    "功率": "công suất", "能量": "năng lượng"
}


def init_database():
    """Khởi tạo database"""
    conn = sqlite3.connect('learning_history.db', check_same_thread=False)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS learning_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  word TEXT,
                  translation TEXT,
                  language TEXT,
                  correct_count INTEGER DEFAULT 0,
                  wrong_count INTEGER DEFAULT 0,
                  last_reviewed TIMESTAMP,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS study_sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_type TEXT,
                  language TEXT,
                  score INTEGER,
                  total_questions INTEGER,
                  session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()


def extract_text_from_pdf(file):
    """Trích xuất văn bản từ file PDF"""
    if PyPDF2 is None:
        st.error("PyPDF2 chưa được cài đặt! Hãy chạy: pip install PyPDF2")
        return ""

    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Lỗi khi đọc file PDF: {str(e)}")
        return ""


def extract_text_from_docx(file):
    """Trích xuất văn bản từ file DOCX"""
    if Document is None:
        st.error("python-docx chưa được cài đặt! Hãy chạy: pip install python-docx")
        return ""

    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Lỗi khi đọc file DOCX: {str(e)}")
        return ""


def extract_text_from_txt(file):
    """Trích xuất văn bản từ file TXT"""
    try:
        return file.read().decode('utf-8')
    except UnicodeDecodeError:
        file.seek(0)
        return file.read().decode('latin-1')
    except Exception as e:
        st.error(f"Lỗi khi đọc file TXT: {str(e)}")
        return ""


def extract_russian_words(text):
    """Trích xuất từ tiếng Nga từ văn bản"""
    russian_pattern = re.compile(r'[а-яА-ЯёЁ]{2,}')
    words = russian_pattern.findall(text)

    common_words = ['и', 'в', 'на', 'с', 'по', 'у', 'о', 'к', 'но', 'а', 'из', 'от', 'до', 'для']
    filtered_words = [word for word in words if word.lower() not in common_words]

    return list(set(filtered_words))


def extract_chinese_words(text):
    """Trích xuất từ tiếng Trung từ văn bản"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    words = chinese_pattern.findall(text)

    return list(set(words))


def detect_language(text):
    """Tự động phát hiện ngôn ngữ"""
    russian_chars = len(re.findall(r'[а-яА-ЯёЁ]', text))
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

    if chinese_chars > russian_chars:
        return "chinese"
    elif russian_chars > chinese_chars:
        return "russian"
    else:
        return "unknown"


def translate_words(words, language):
    """Dịch từ theo ngôn ngữ"""
    translations = {}

    if language == "russian":
        dictionary = RUSSIAN_DICTIONARY
    elif language == "chinese":
        dictionary = CHINESE_DICTIONARY
    else:
        return translations

    for word in words:
        if word in dictionary:
            translations[word] = dictionary[word]
        else:
            translations[word] = f"[Chưa dịch: {word}]"

    return translations


def text_to_speech(text, lang):
    """Chuyển văn bản thành giọng nói"""
    try:
        if lang == "russian":
            tts_lang = 'ru'
        elif lang == "chinese":
            tts_lang = 'zh'
        else:
            return None

        tts = gTTS(text=text, lang=tts_lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Lỗi phát âm: {str(e)}")
        return None


def create_quiz(translations, num_questions=10, language="russian"):
    """Tạo câu hỏi trắc nghiệm"""
    quiz = []
    words = list(translations.keys())

    if len(words) < 4:
        st.warning("Cần ít nhất 4 từ để tạo quiz!")
        return quiz

    lang_display = "Tiếng Nga" if language == "russian" else "Tiếng Trung"

    for _ in range(min(num_questions, len(words))):
        correct_word = random.choice(words)
        correct_answer = translations[correct_word]

        wrong_answers = []
        while len(wrong_answers) < 3:
            wrong_word = random.choice(words)
            if (wrong_word != correct_word and
                    translations[wrong_word] not in wrong_answers and
                    translations[wrong_word] != correct_answer):
                wrong_answers.append(translations[wrong_word])

        options = wrong_answers + [correct_answer]
        random.shuffle(options)

        quiz.append({
            'question': f"Từ '{correct_word}' ({lang_display}) có nghĩa là gì?",
            'options': options,
            'correct_answer': correct_answer,
            'word': correct_word,
            'language': language
        })

    return quiz


def flashcard_view(translations, language):
    """Hiển thị chế độ flashcard"""
    lang_display = "Tiếng Nga" if language == "russian" else "Tiếng Trung"
    st.subheader(f"📇 Flashcards - {lang_display}")

    if not translations:
        st.warning("Chưa có từ vựng. Hãy upload file để bắt đầu!")
        return

    if 'flashcard_index' not in st.session_state:
        st.session_state.flashcard_index = 0
    if 'show_translation' not in st.session_state:
        st.session_state.show_translation = False
    if 'known_words' not in st.session_state:
        st.session_state.known_words = set()

    words = list(translations.keys())
    current_index = st.session_state.flashcard_index
    current_word = words[current_index]
    current_translation = translations[current_word]

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(f"""
        <div style='border: 2px solid #4CAF50; border-radius: 10px; padding: 50px; text-align: center; background-color: #f9f9f9;'>
            <h1 style='color: #333; font-size: 2.5em;'>{current_word}</h1>
            <p style='color: #666; font-size: 1.2em;'>{lang_display}</p>
            {f"<h2 style='color: #4CAF50; font-size: 2em;'>{current_translation}</h2>" if st.session_state.show_translation else ""}
        </div>
        """, unsafe_allow_html=True)

        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button("🔄 Lật thẻ"):
                st.session_state.show_translation = not st.session_state.show_translation

        with col_btn2:
            if st.button("✅ Đã biết"):
                st.session_state.known_words.add(current_word)
                save_to_history(current_word, current_translation, language, True)
                st.success("Đã đánh dấu là đã biết!")

        with col_btn3:
            if st.button("🔊 Phát âm"):
                audio_file = text_to_speech(current_word, language)
                if audio_file:
                    st.audio(audio_file, format='audio/mp3')
                    os.unlink(audio_file)

        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
        with col_nav1:
            if st.button("⏮ Trước") and current_index > 0:
                st.session_state.flashcard_index -= 1
                st.session_state.show_translation = False
                st.rerun()

        with col_nav3:
            if st.button("Tiếp ⏭") and current_index < len(words) - 1:
                st.session_state.flashcard_index += 1
                st.session_state.show_translation = False
                st.rerun()

        st.write(f"Thẻ {current_index + 1} / {len(words)}")
        progress = (current_index + 1) / len(words)
        st.progress(progress)

        st.write(f"Đã biết: {len(st.session_state.known_words)} từ")


def save_to_history(word, translation, language, is_correct=True):
    """Lưu từ vào lịch sử học tập"""
    conn = sqlite3.connect('learning_history.db', check_same_thread=False)
    c = conn.cursor()

    c.execute('SELECT * FROM learning_history WHERE word = ? AND language = ?', (word, language))
    existing = c.fetchone()

    if existing:
        if is_correct:
            c.execute('''UPDATE learning_history 
                        SET correct_count = correct_count + 1, last_reviewed = ?
                        WHERE word = ? AND language = ?''', (datetime.now(), word, language))
        else:
            c.execute('''UPDATE learning_history 
                        SET wrong_count = wrong_count + 1, last_reviewed = ?
                        WHERE word = ? AND language = ?''', (datetime.now(), word, language))
    else:
        c.execute('''INSERT INTO learning_history 
                    (word, translation, language, correct_count, wrong_count, last_reviewed)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                  (word, translation, language, 1 if is_correct else 0, 0 if is_correct else 1, datetime.now()))

    conn.commit()
    conn.close()


def main():
    # Khởi tạo database
    init_database()

    st.set_page_config(
        page_title="Học Đa Ngôn Ngữ",
        page_icon="🌍",
        layout="wide"
    )

    st.title("🌍 Ứng dụng Học Đa Ngôn Ngữ")
    st.markdown("Học **Tiếng Nga** và **Tiếng Trung** qua tài liệu thực tế!")

    # Kiểm tra thư viện
    if PyPDF2 is None:
        st.warning("⚠️ Chưa cài đặt PyPDF2. Không thể đọc file PDF.")
    if Document is None:
        st.warning("⚠️ Chưa cài đặt python-docx. Không thể đọc file DOCX.")

    # Sidebar chọn ngôn ngữ
    st.sidebar.title("🌐 Chọn Ngôn Ngữ")
    selected_language = st.sidebar.radio(
        "Ngôn ngữ học:",
        ["🇷🇺 Tiếng Nga", "🇨🇳 Tiếng Trung"]
    )

    language = "russian" if selected_language == "🇷🇺 Tiếng Nga" else "chinese"
    lang_display = "Tiếng Nga" if language == "russian" else "Tiếng Trung"

    # Điều hướng
    st.sidebar.title("🎯 Điều hướng")
    app_mode = st.sidebar.selectbox(
        f"Chế độ học {lang_display}:",
        ["📤 Upload Tài liệu", "🎯 Làm Quiz", "📇 Flashcards", "📊 Thống kê"]
    )

    # Upload tài liệu
    if app_mode == "📤 Upload Tài liệu":
        st.header(f"📤 Upload Tài liệu {lang_display}")

        uploaded_file = st.file_uploader(
            f"Chọn file {lang_display}",
            type=['pdf', 'docx', 'txt'],
            help=f"Hỗ trợ PDF, DOCX, TXT chứa văn bản {lang_display}"
        )

        if uploaded_file is not None:
            # Hiển thị thông tin file
            file_details = {
                "Tên file": uploaded_file.name,
                "Loại file": uploaded_file.type,
                "Kích thước": f"{uploaded_file.size / 1024:.1f} KB"
            }
            st.write(file_details)

            # Đọc file theo loại
            with st.spinner("Đang đọc và xử lý file..."):
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    text = extract_text_from_docx(uploaded_file)
                else:
                    text = extract_text_from_txt(uploaded_file)

            if text:
                st.success("✅ Đã đọc file thành công!")

                # Tự động phát hiện ngôn ngữ
                detected_lang = detect_language(text)
                if detected_lang != language:
                    st.warning(f"⚠️ File có vẻ là {detected_lang}, nhưng bạn đang chọn {language}")

                # Hiển thị preview
                with st.expander("👀 Xem trước văn bản"):
                    preview_text = text[:1000] + "..." if len(text) > 1000 else text
                    st.text_area("Nội dung văn bản", preview_text, height=200, key="preview")

                # Trích xuất từ vựng
                if language == "russian":
                    words = extract_russian_words(text)
                else:
                    words = extract_chinese_words(text)

                if words:
                    st.info(f"🔍 Tìm thấy {len(words)} từ {lang_display}")

                    # Hiển thị một số từ tìm thấy
                    st.write("📝 Một số từ đã tìm thấy:", ", ".join(words[:20]), "..." if len(words) > 20 else "")

                    # Dịch từ
                    if st.button(f"🚀 Dịch từ vựng {lang_display}"):
                        translations = translate_words(words, language)

                        # Hiển thị kết quả
                        st.subheader(f"📚 Kết quả dịch thuật {lang_display}")
                        vocab_df = pd.DataFrame(
                            list(translations.items()),
                            columns=[lang_display, 'Tiếng Việt']
                        )
                        st.dataframe(vocab_df, use_container_width=True)

                        # Thống kê dịch thuật
                        translated_count = sum(1 for v in translations.values() if not v.startswith("[Chưa dịch:"))
                        st.success(f"✅ Đã dịch được {translated_count}/{len(words)} từ")

                        # Lưu vào session
                        st.session_state.translations = translations
                        st.session_state.current_language = language

                        # Tải xuống
                        csv = vocab_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            f"📥 Tải xuống từ vựng {lang_display}",
                            data=csv,
                            file_name=f"vocabulary_{language}.csv",
                            mime="text/csv"
                        )
                else:
                    st.error(f"❌ Không tìm thấy từ {lang_display} trong văn bản!")

    # Làm Quiz
    elif app_mode == "🎯 Làm Quiz":
        st.header(f"🎯 Làm Quiz {lang_display}")

        if 'translations' not in st.session_state or st.session_state.get('current_language') != language:
            st.warning(f"Hãy upload tài liệu {lang_display} trước!")
        else:
            translations = st.session_state.translations

            num_questions = st.slider(
                "Số câu hỏi:",
                min_value=5,
                max_value=min(20, len(translations)),
                value=10
            )

            if st.button("🎲 Tạo Quiz Mới"):
                st.session_state.quiz = create_quiz(translations, num_questions, language)
                st.session_state.quiz_answers = [None] * len(st.session_state.quiz)
                st.session_state.quiz_submitted = False

            if 'quiz' in st.session_state and st.session_state.quiz:
                st.subheader("Bài Quiz")

                for i, q in enumerate(st.session_state.quiz):
                    st.write(f"**Câu {i + 1}: {q['question']}**")

                    # Phát âm
                    col_audio, col_quiz = st.columns([1, 4])
                    with col_audio:
                        if st.button(f"🔊", key=f"audio_{i}"):
                            audio_file = text_to_speech(q['word'], language)
                            if audio_file:
                                st.audio(audio_file, format='audio/mp3')
                                os.unlink(audio_file)

                    with col_quiz:
                        user_answer = st.radio(
                            f"Chọn đáp án:",
                            q['options'],
                            key=f"quiz_{i}",
                            index=st.session_state.quiz_answers[i] if st.session_state.quiz_answers[
                                                                          i] is not None else 0
                        )
                        st.session_state.quiz_answers[i] = q['options'].index(user_answer)

                if st.button("📤 Nộp Bài"):
                    score = 0
                    for i, q in enumerate(st.session_state.quiz):
                        user_answer = q['options'][st.session_state.quiz_answers[i]]
                        if user_answer == q['correct_answer']:
                            score += 1
                            save_to_history(q['word'], q['correct_answer'], language, True)
                        else:
                            save_to_history(q['word'], q['correct_answer'], language, False)

                    st.session_state.quiz_submitted = True

                    st.success(f"🎉 Điểm của bạn: {score}/{len(st.session_state.quiz)}")

                    # Hiển thị kết quả chi tiết
                    with st.expander("📋 Xem chi tiết đáp án"):
                        for i, q in enumerate(st.session_state.quiz):
                            user_answer = q['options'][st.session_state.quiz_answers[i]]
                            is_correct = user_answer == q['correct_answer']

                            if is_correct:
                                st.write(f"✅ Câu {i + 1}: {q['correct_answer']}")
                            else:
                                st.write(
                                    f"❌ Câu {i + 1}: Đáp án của bạn: {user_answer} | Đáp án đúng: {q['correct_answer']}")

    # Flashcards
    elif app_mode == "📇 Flashcards":
        st.header(f"📇 Học với Flashcards {lang_display}")

        if 'translations' not in st.session_state or st.session_state.get('current_language') != language:
            st.warning(f"Hãy upload tài liệu {lang_display} trước!")
        else:
            flashcard_view(st.session_state.translations, language)

    # Thống kê
    elif app_mode == "📊 Thống kê":
        st.header("📊 Thống kê học tập")

        conn = sqlite3.connect('learning_history.db', check_same_thread=False)

        # Thống kê theo ngôn ngữ
        stats_df = pd.read_sql_query('''
            SELECT language, 
                   COUNT(*) as total_words,
                   SUM(correct_count) as total_correct,
                   SUM(wrong_count) as total_wrong,
                   COUNT(CASE WHEN correct_count > wrong_count THEN 1 END) as mastered_words
            FROM learning_history 
            GROUP BY language
        ''', conn)

        if not stats_df.empty:
            st.subheader("Thống kê theo ngôn ngữ")

            for _, row in stats_df.iterrows():
                lang = "Tiếng Nga" if row['language'] == 'russian' else "Tiếng Trung"
                accuracy = row['total_correct'] / (row['total_correct'] + row['total_wrong']) * 100 if (row[
                                                                                                            'total_correct'] +
                                                                                                        row[
                                                                                                            'total_wrong']) > 0 else 0

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(f"Tổng từ ({lang})", row['total_words'])
                with col2:
                    st.metric(f"Đã thuộc ({lang})", row['mastered_words'])
                with col3:
                    st.metric(f"Số câu đúng ({lang})", row['total_correct'])
                with col4:
                    st.metric(f"Tỷ lệ đúng ({lang})", f"{accuracy:.1f}%")

        conn.close()


if __name__ == "__main__":
    main()