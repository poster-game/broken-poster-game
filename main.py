import streamlit as st
import time
import random
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Сломанный Плакат", layout="wide")

# МАСКИРОВКА ИНТЕРФЕЙСА: Скрываем панели Streamlit
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stDecoration"] {visibility: hidden;}
        button[title="View source"] {display:none;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# 🔥 НАСТОЯЩАЯ ГЛОБАЛЬНАЯ ПАМЯТЬ СЕРВЕРА (вне сессий браузера)
if not hasattr(st, "_global_game_rooms"):
    st._global_game_rooms = {}

if "my_name" not in st.session_state:
    st.session_state.my_name = ""
if "my_room" not in st.session_state:
    st.session_state.my_room = ""

url_params = st.query_params
url_room = url_params.get("room", "")

# --- ЭКРАН 1: АВТОРИЗАЦИЯ ---
if not st.session_state.my_name:
    st.title("🎨 Игра «Сломанный Плакат»")
    
    name_input = st.text_input("Введите ваш никнейм:")
    default_room = url_room if url_room else str(random.randint(100, 999))
    room_input = st.text_input("Код комнаты:", value=default_room)
    
    if st.button("ВОЙТИ 🚀", type="primary"):
        if name_input.strip():
            user_name = name_input.strip()
            room_id = room_input.strip()
            
            st.session_state.my_name = user_name
            st.session_state.my_room = room_id
            
            # Инициализация комнаты на сервере
            if room_id not in st._global_game_rooms:
                st._global_game_rooms[room_id] = {
                    "players": [],
                    "bots": [],
                    "stage": "lobby",
                    "game_mode": "Обычный плакат",
                    "idea": "",
                    "canvas_data": None,
                    "timer_start": None
                }
            
            if user_name not in st._global_game_rooms[room_id]["players"]:
                st._global_game_rooms[room_id]["players"].append(user_name)
            
            st.rerun()
        else:
            st.error("Введите имя!")

# --- ИГРОВОЙ ИНТЕРФЕЙС ---
else:
    room_id = st.session_state.my_room
    
    # Защита от сброса
    if room_id not in st._global_game_rooms:
        st._global_game_rooms[room_id] = {"players": [st.session_state.my_name], "bots": [], "stage": "lobby", "game_mode": "Обычный плакат", "idea": "", "canvas_data": None, "timer_start": None}
        
    room_data = st._global_game_rooms[room_id]
    
    # Железный создатель: самый первый в списке на сервере
    if room_data["players"]:
        current_host = room_data["players"][0]
    else:
        current_host = st.session_state.my_name
    
    if st.sidebar.button("🚪 Выйти"):
        if st.session_state.my_name in room_data["players"]:
            room_data["players"].remove(st.session_state.my_name)
        st.session_state.my_name = ""
        st.query_params.clear()
        st.rerun()

    def handle_timer():
        if room_data["timer_start"] is not None:
            elapsed = time.time() - room_data["timer_start"]
            remaining = max(0, 300 - int(elapsed))
            mins, secs = divmod(remaining, 60)
            st.sidebar.metric("⏱️ Оставшееся время", f"{mins:02d}:{secs:02d}")

    # --- 1. ЛОББИ ---
    if room_data["stage"] == "lobby":
        st.title("🎭 Лобби игры")
        st.write(f"Вы в комнате: **{room_id}**")
        st.write(f"👑 Создатель комнаты: **{current_host}**")
        
        st.query_params["room"] = room_id
        st.info("📢 Чтобы позвать друга в эту комнату, скопируйте всю ссылку из адресной строки вашего браузера на самом верху экрана!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👥 Участники:")
            for p in room_data["players"]:
                if p == current_host:
                    st.markdown(f"👤 **{p}** 👑 *(Создатель)*")
                else:
                    st.markdown(f"👤 **{p}**")
            if st.button("🔄 Обновить список игроков"):
                st.rerun()
                
        with col2:
            st.subheader("Настройки раунда")
            
            # Проверка прав создателя
            if st.session_state.my_name == current_host:
                room_data["game_mode"] = st.radio("Режим игры:", ["Обычный плакат", "Слепой плагиат", "Тайный исказитель"])
                st.info("⏱️ Время на раунд: 5 минут.")
                
                if st.button("НАЧАТЬ ИГРУ 🚀", type="primary"):
                    total_players = len(room_data["players"])
                    if total_players % 2 != 0:
                        room_data["bots"] = ["Бот-Ассистент"]
                    else:
                        room_data["bots"] = []
                        
                    room_data["stage"] = "round_1"
                    room_data["timer_start"] = time.time()
                    st.rerun()
            else:
                st.markdown(f"**Выбранный режим:** {room_data['game_mode']}")
                st.info("⏱️ Время на раунд: 5 минут.")
                st.warning("⏳ Ожидание, пока создатель комнаты запустит игру...")
                if st.button("🔄 Проверить старт игры"):
                    st.rerun()

    # --- 2. РАУНД 1: ЛОЗУНГ ---
    elif room_data["stage"] == "round_1":
        st.title("📝 Раунд 1: Придумайте тему плаката")
        handle_timer()
        
        user_idea = st.text_input("Введите фразу, которую должен нарисовать следующий игрок:", placeholder="Например: Кот на космическом корабле")
        
        if st.button("Готово ➡"):
            if user_idea.strip():
                room_data["idea"] = user_idea.strip()
                room_data["stage"] = "mini_game"
                room_data["timer_start"] = None
                st.rerun()
            else:
                st.error("Пожалуйста, введите текст!")

    # --- 3. ПАРНАЯ МИНИ-ИГРА ---
    elif room_data["stage"] == "mini_game":
        st.title("⚡ Парный перерыв: Синхронизация")
        st.write("Пока остальные игроки дописывают фразы, найдите парный цвет!")
        
        if len(room_data["bots"]) > 0:
            st.caption("🤖 Ваш напарник в этом раунде: Бот. Он готов к игре.")
            
        colors = ["🔴", "🔵", "🟢", "🟡", "🔴", "🔵", "🟢", "🟡", "🟣"]
        grid = st.columns(3)
        for i in range(9):
            with grid[i % 3]:
                if st.button(f"{colors[i]} Элемент {i+1}", key=f"pair_{i}"):
                    st.success("Элемент активирован!")
                    
        if st.button("Перейти к рисованию 🎨", type="primary"):
            room_data["stage"] = "round_2"
            room_data["timer_start"] = time.time()
            st.rerun()

    # --- 4. РАУНД 2: РИСОВАНИЕ ---
    elif room_data["stage"] == "round_2":
        st.title("🎨 Раунд 2: Время рисовать")
        handle_timer()
        st.subheader(f"Ваше задание: Нарисуйте «{room_data['idea']}»")
        
        stroke_color = st.color_picker("Выбор цвета:", "#000000")
        stroke_width = st.slider("Толщина кисти:", 1, 30, 5)
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color="#FFFFFF",
            height=400,
            width=700,
            drawing_mode="freedraw",
            key="gartic_canvas",
        )
        
        if st.button("Отправить рисунок 🎬", type="primary"):
            room_data["canvas_data"] = canvas_result.image_data
            room_data["stage"] = "final"
            st.rerun()

    # --- 5. ФИНАЛ: РЕЗУЛЬТАТЫ ---
    elif room_data["stage"] == "final":
        st.title("🎬 Результаты игры")
        st.subheader(f"Режим проведения: {room_data['game_mode']}")
        
        st.markdown(f"### 🔤 Начальная идея от игроков:")
        st.info(f"«{room_data['idea']}»")
        
        if len(room_data["bots"]) > 0:
            st.markdown("### 🤖 Вклад ИИ-Помощника:")
            st.caption("Бот успешно продублировал концепт и передал ход по цепочке результатов.")
            
        st.markdown("### 🖼️ Что получилось в итоге:")
        if room_data["canvas_data"] is not None:
            st.image(room_data["canvas_data"], caption="Итоговый плакат раунда")
        else:
            st.warning("Игрок оставил холст пустым.")
            
        if st.button("Играть снова 🔄"):
            room_data["stage"] = "lobby"
            room_data["idea"] = ""
            room_data["canvas_data"] = None
            room_data["bots"] = []
            st.query_params["room"] = room_id
            st.rerun()
