import streamlit as st
import time

# URL & Page Settings (Английское техническое имя для корректных ссылок в Chrome)
st.set_page_config(page_title="broken-poster-game", page_icon="🎨", layout="centered")

# Стилизация под современное приложение (крупные контрастные кнопки)
st.markdown("""
    <style>
    .stButton>button {
        background-color: #6C5CE7 !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: 2px solid #a29bfe !important;
        width: 100%;
        height: 60px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00CEC9 !important;
        border-color: #81ecec !important;
        transform: scale(1.02);
    }
    .mafia-card {
        background-color: #2d3436;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #6c5ce7;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Инициализация состояний игры
if 'game_stage' not in st.session_state:
    st.session_state.game_stage = "START"
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_case' not in st.session_state:
    st.session_state.current_case = 0

# Абсолютно безопасная база социальных тем (Без политики, без СССР, без войны)
CASES = [
    {
        "original": "«Береги природу — разделяй отходы правильно!» (Тема: Экология и чистая планета)",
        "corrupted": "«Разделяй доходы правильно — забирай всё себе!»",
        "options": [
            "Мафия полностью перекрасила фон плаката",
            "Мафия подменила буквы в словах, превратив заботу о планете в эгоизм (Правильный ответ) 🌟",
            "Текст изменился из-за сбоя принтера"
        ],
        "correct_idx": 1,
        "clue": "Анализ 'Магического взгляда': Картинка с зелёным деревом и контейнерами осталась прежней! Изменился только текст. Это доказывает: визуальный образ на плакате сильнее слов, ведь люди всё равно понимают, что речь об экологии!"
    },
    {
        "original": "«Книга — лучший гаджет! Читай и развивай свой разум!» (Тема: Образование и чтение)",
        "corrupted": "«Книга — лишний гаджет! Закрой её и иди спать!»",
        "options": [
            "Мафия совершила тонкое буквенное искажение всего одного слова (Правильный ответ) 🌟",
            "Это официальный плакат от мебельной фабрики",
            "Плакат просто слишком старый"
        ],
        "correct_idx": 0,
        "clue": "Анализ 'Магического взгляда': Мафия изменила всего одну букву («лучший» на «лишний»), чтобы полностью сломать мотивацию. Это подтверждает, как важно защищать смысл информации!"
    },
    {
        "original": "«Здоровый сон — залог успеха на уроках! Спи не менее 8 часов!» (Тема: Здоровье и ЗОЖ)",
        "corrupted": "«Здоровый слон — залог успеха на дорогах! Спи не менее 100 часов!»",
        "options": [
            "Мафия добавила абсурдные элементы и запутала цифры (Правильный ответ) 🌟",
            "Это плакат для водителей в зоопарке",
            "Текст перепутал сам дизайнер"
        ],
        "correct_idx": 0,
        "clue": "Анализ 'Магического взгляда': Исказители превратили важный совет по здоровью в шутку. Но благодаря логике зала, обман мгновенно раскрыт!"
    }
]

# --- СЦЕНА 1: СТАРТ ИГРЫ ---
if st.session_state.game_stage == "START":
    st.title("🔮 Интерактивная игра: Сломанный плакат")
    st.subheader("Психологический эксперимент для защиты индивидуального проекта")
    
    st.markdown(
        "<div class='mafia-card'>"
        "<h4>🕵️‍♂️ Внимание, город засыпает... Просыпается МАФИЯ!</h4>"
        "<p>Тайные <b>Исказители смыслов</b> заколдовали современные мотивирующие плакаты школы и города. "
        "Они переврали тексты про экологию, чтение и здоровье, чтобы запутать людей! Но у нас есть <b>Магический взгляд логики</b>.</p>"
        "<p><b>Правила:</b> Играем ровно 5 минут. Ограничений по игрокам нет — голосует весь зал одновременно! "
        "Мы должны включить критическое мышление и разоблачить уловки мафии!</p>"
        "</div>", 
        unsafe_allow_html=True
    )
    
    if st.button("🔥 ВКЛЮЧИТЬ МАГИЧЕСКИЙ ВЗГЛЯД И НАЧАТЬ"):
        st.session_state.game_stage = "PLAYING"
        st.session_state.timer_start = time.time()
        st.session_state.current_case = 0
        st.session_state.score = 0
        st.rerun()

# --- СЦЕНА 2: ИГРОВОЙ ПРОЦЕСС ---
elif st.session_state.game_stage == "PLAYING":
    st.title("🕵️‍♂️ Идет расследование...")
    
    # Визуальный таймер на 5 минут
    elapsed = time.time() - st.session_state.timer_start
    remaining = max(0, 300 - int(elapsed))
    mins, secs = divmod(remaining, 60)
    st.sidebar.metric("⏳ Время до конца расследования", f"{mins:02d}:{secs:02d}")
    
    if remaining <= 0:
        st.session_state.game_stage = "FINAL"
        st.rerun()
        
    idx = st.session_state.current_case
    if idx < len(CASES):
        st.write(f"### 📢 Случай №{idx + 1}:")
        st.info(f"📋 **Оригинальный посыл плаката:** {CASES[idx]['original']}")
        st.error(f"❌ **То, что видит город после чар Мафии:** {CASES[idx]['corrupted']}")
        
        st.write("---")
        st.markdown("#### 🗳️ Голосование зала! Какую уловку применила Мафия? (Включите Магический взгляд):")
        
        # Кнопки вариантов ответа
        for o_idx, option in enumerate(CASES[idx]["options"]):
            if st.button(option, key=f"opt_{idx}_{o_idx}"):
                if o_idx == CASES[idx]["correct_idx"]:
                    st.session_state.score += 1
                    st.success("🌟 ПРАВИЛЬНО! Мафия разоблачена чарами логики!")
                else:
                    st.error("❌ Мимо! Мафия запутала следствие, но магический взгляд раскрывает истину:")
                
                st.write(f"ℹ️ **{CASES[idx]['clue']}**")
                time.sleep(4) # Пауза для прочтения вывода
                st.session_state.current_case += 1
                st.rerun()
    else:
        st.session_state.game_stage = "FINAL"
        st.rerun()

# --- СЦЕНА 3: ФИНАЛ И ВЫВОД ДЛЯ ЗАЩИТЫ ПРОЕКТА ---
else:
    st.title("🏆 РЕЗУЛЬТАТЫ СЛЕДСТВИЯ")
    st.subheader("Мафия Исказителей полностью разгромлена силой критического мышления!")
    
    st.metric("📊 Разоблачено уловок Мафии:", f"{st.session_state.score} из {len(CASES)}")
    
    st.markdown(
        "<div class='mafia-card' style='border-left-color: #00CEC9;'>"
        "<h3>🧠 Главный вывод для защиты индивидуального проекта:</h3>"
        "<p style='font-size: 18px; line-height: 1.6;'>"
        "Наша игра со множеством зрителей одновременно доказала: в современном мире текстовая информация "
        "легко уязвима для искажений (эффект 'сломанного телефона'). Текст можно легко переписать или подделать. <br><br>"
        "Но почему <b>социальный плакат имеет огромную общественную и культурную значимость</b>? "
        "Потому что его <b>визуальный образ (дизайн, графика, цвет) невозможно мгновенно подменить</b>. "
        "Позитивный и яркий рисунок плаката врезается в память человека напрямую, формируя правильные ценности (ЗОЖ, экология, культура), "
        "минуя текстовые искажения. Это делает плакат важнейшим и вечным инструментом визуальной коммуникации в обществе!</p>"
        "</div>", 
        unsafe_allow_html=True
    )
    
    if st.button("🔄 Начать новую игру"):
        st.session_state.game_stage = "START"
        st.rerun()
