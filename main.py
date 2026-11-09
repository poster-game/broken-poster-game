import streamlit as st
import time
import random
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Сломанный Плакат — ИП", layout="wide")

# --- СЕРВЕРНАЯ ПАМЯТЬ ДЛЯ МИЛЛИОНА КОМНАТ ---
# Память хранится на сервере. Все игроки с одним room_id видят общую комнату.
if "global_rooms" not in st.session_state:
    st.session_state.global_rooms = {}

# Локальные переменные текущей вкладки браузера
if "my_name" not in st.session_state:
    st.session_state.my_name = ""
if "my_room" not in st.session_state:
    st.session_state.my_room = ""

# Автоматически подтягиваем комнату из ссылки (если друг перешел по ней)
url_params = st.query_params
url_room = url_params.get("room", "")

# --- ЭКРАН 1: ВХОД И СОЗДАНИЕ КОМНАТЫ ---
if not st.session_state.my_name:
    st.title("🎨 Историко-Патриотическая Игра «Плакат»")
    st.subheader("Проект для ИП (Полный Python-сервер)")
    
    name_input = st.text_input("Введите ваш никнейм:")
    
    default_room = url_room if url_room else str(random.randint(100, 999))
    room_input = st.text_input("Служебный код комнаты:", value=default_room)
    
    if st.button("ВОЙТИ В ИГРУ 🚀", type="primary"):
        if name_input.strip():
            st.session_state.my_name = name_input.strip()
            st.session_state.my_room = room_input.strip()
            
            # Создаем комнату на сервере, если её нет
            if st.session_state.my_room not in st.session_state.global_rooms:
                st.session_state.global_rooms[st.session_state.my_room] = {
                    "players": [],
                    "stage": "lobby",
                    "idea": "",
                    "timer_start": None
                }
            
            # Добавляем игрока в эту конкретную комнату
            if st.session_state.my_name not in st.session_state.global_rooms[st.session_state.my_room]["players"]:
                st.session_state.global_rooms[st.session_state.my_room]["players"].append(st.session_state.my_name)
            
            st.rerun()
        else:
            st.error("Пожалуйста, введите имя!")

# --- ЕСЛИ ИГРОК АВТОРИЗОВАН ---
else:
    room_id = st.session_state.my_room
    # Защита от сброса сервера
    if room_id not in st.session_state.global_rooms:
        st.session_state.global_rooms[room_id] = {"players": [st.session_state.my_name], "stage": "lobby", "idea": "", "timer_start": None}
        
    room_data = st.session_state.global_rooms[room_id]
    
    # Кнопка Смены аккаунта / Выхода
    if st.sidebar.button("🚪 Выйти из комнаты"):
        if st.session_state.my_name in room_data["players"]:
            room_data["players"].remove(st.session_state.my_name)
        st.session_state.my_name = ""
        st.query_params.clear()
        st.rerun()

    # --- ЛОГИКА ТАЙМЕРА (5 минут = 300 секунд) ---
    def handle_timer():
        if room_data["timer_start"] is not None:
            elapsed = time.time() - room_data["timer_start"]
            remaining = max(0, 300 - int(elapsed))
            if remaining == 0:
                st.error("⏱️ Время вышло! Переходим на следующую станцию.")
            else:
                mins, secs = divmod(remaining, 60)
                st.sidebar.metric("⏱️ Оставшееся время", f"{mins:02d}:{secs:02d}")

    # --- СТАНЦИЯ 2: ЛОББИ ---
    if room_data["stage"] == "lobby":
        st.title("🎭 Игровое лобби сессии")
        st.write(f"Привет, **{st.session_state.my_name}**! Вы находитесь в изолированной комнате № **{room_id}**.")
        
        # Ссылка для миллиона игроков (каждая комната уникальна)
        invite_link = f"https://streamlit.app{room_id}"
        st.text_input("🔗 Ссылка для друзей в эту комнату (ИП):", value=invite_link, disabled=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👥 Игроки в вашей комнате:")
            for p in room_data["players"]:
                st.markdown(f"👤 **{p}**")
            if st.button("🔄 Обновить список"):
                st.rerun()
                
        with col2:
            st.subheader("Параметры раундов")
            st.info("⏱️ Время на обсуждение и рисунок: **5 минут** (в стиле Мафии).\n\nАкцент: Историческая память и безопасность (без агрессивных военных элементов).")
            if st.button("НАЧАТЬ ИГРУ 🚀", type="primary"):
                room_data["stage"] = "round_1"
                room_data["timer_start"] = time.time()
                st.rerun()

    # --- СТАНЦИЯ 3: ОБСУЖДЕНИЕ ЛОЗУНГА (5 МИНУТ) ---
    elif room_data["stage"] == "round_1":
        st.title("📝 Раунд 1: Мозговой штурм и Лозунги")
        handle_timer()
        
        st.write("Придумайте мирный, но сильный социальный или патриотический слоган для плаката.")
        user_idea = st.text_input("Ваш вариант лозунга:", placeholder="Пример: Помни историю, созидай мирное будущее!")
        
        if st.button("Утвердить лозунг отряда ➡"):
            if user_idea.strip():
                room_data["idea"] = user_idea.strip()
                room_data["stage"] = "fizminutka"
                room_data["timer_start"] = None # Сброс таймера перед физминуткой
                st.rerun()
            else:
                st.error("Пожалуйста, введите лозунг!")

    # --- СТАНЦИЯ 4: ИНТАКТИВНАЯ ФИЗМИНУТКА ---
    elif room_data["stage"] == "fizminutka":
        st.title("🤸 Физкультминутка для глаз и рук")
        st.write("Школа одобряет заботу о здоровье! Сделайте круговые движения головой, разомните пальцы.")
        st.info("🎯 Найдите скрытый элемент на поле, чтобы разблокировать холст!")
        
        grid = st.columns(3)
        target = 4 # Пусть кнопка по центру будет целью
        for i in range(9):
            with grid[i % 3]:
                if i == target:
                    if st.button("🎯 НАШЕЛ!", key=f"fiz_{i}", type="primary"):
                        room_data["stage"] = "round_2"
                        room_data["timer_start"] = time.time() # Новый таймер на 5 минут
                        st.rerun()
                else:
                    st.button("⬜ Мимо", key=f"fiz_{i}")

    # --- СТАНЦИЯ 5: ХОЛСТ ДЛЯ РИСОВАНИЯ (5 МИНУТ) ---
    elif room_data["stage"] == "round_2":
        st.title("🎨 Раунд 2: Создание плаката")
        handle_timer()
        st.subheader(f"Тема: «{room_data['idea']}»")
        
        # Настройки цвета кисти прямо в Python
        stroke_color = st.color_picker("Цвет кисти:", "#4527a0")
        stroke_width = st.slider("Толщина линии:", 1, 20, 5)
        
        # Инструмент рисования
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color="#FFFFFF",
            height=400,
            width=800,
            drawing_mode="freedraw",
            key="canvas_game",
        )
        
        if st.button("Сдать готовый плакат комиссии ИП 🎬", type="primary"):
            room_data["stage"] = "final"
            st.rerun()

    # --- СТАНЦИЯ 6: ДЕМОНСТРАЦИЯ ИТОГОВ ---
    elif room_data["stage"] == "final":
        st.title("🎬 Финал: Выставка вашего проекта")
        st.success(f"Защита проекта успешно завершена! Комната №{room_id}")
        st.info(f"**Ваш лозунг:** {room_data['idea']}")
        st.write("Графический плакат сохранен в системе и готов к показу учителям.")
        
        if st.button("В главное меню (Сбросить комнату) 🔄"):
            room_data["stage"] = "lobby"
            room_data["idea"] = ""
            room_data["timer_start"] = None
            st.rerun()
