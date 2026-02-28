#井字遊戲 app3.py
import streamlit as st
import numpy as np
import random
import time
import base64
import os

# 1. 頁面配置 (建議在電腦或橫向手機畫面觀看最佳)
st.set_page_config(
    page_title="精品圍棋井字戰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 初始化狀態 ---
if 'board' not in st.session_state:
    st.session_state.board = np.full((3, 3), "")
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'turn' not in st.session_state:
    st.session_state.turn = "X"
if 'score_player' not in st.session_state:
    st.session_state.score_player = 0
if 'score_cpu' not in st.session_state:
    st.session_state.score_cpu = 0
if 'score_draw' not in st.session_state:
    st.session_state.score_draw = 0

# --- 3. 讀取背景圖 (fl.png) ---
def get_base64_image(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            data = f.read()
            return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    return ""

bg_img = get_base64_image("fl.png")
if bg_img:
    bg_style = f'background-image: url("{bg_img}");'
else:
    bg_style = 'background-color: #DEB887;'

# --- 4. 核心 CSS 修飾 (左右分區版) ---
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{ visibility: hidden; height: 0; }}
    
    .stApp {{
        background-color: #D2B48C;
        overflow-x: hidden;
    }}

    .block-container {{
        padding-top: 1rem !important;
        max-width: 600px !important; /* 稍微放寬總寬度以容納左右兩欄 */
    }}

    /* --- 左側 UI 區塊樣式 --- */
    .score-box {{
        display: flex;
        flex-direction: column;
        align-items: center;
        background: rgba(0, 0, 0, 0.05);
        padding: 8px;
        margin-bottom: 15px;
        color: #3E2723;
        font-weight: bold;
        font-size: 14px;
        border-radius: 8px;
        border: 1px dashed #3E2723;
    }}

    button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(145deg, #6d4c41, #5d4037) !important;
        min-height: 35px !important;
        font-size: 14px !important;
        border-radius: 6px !important;
        margin-top: 5px !important;
    }}

    /* --- 右側：完美九宮格框架 --- */
    div[data-testid="stVerticalBlock"]:has(button[data-testid="stBaseButton-secondary"]) {{
        {bg_style}
        background-size: 100% 100%;
        background-position: center;
        border: 3px solid #3E2723;
        box-shadow: 0px 3px 10px rgba(0,0,0,0.4);
        margin: 0 auto !important;
        
        /* 棋盤大小設定 */
        max-width: 160px !important; 
        aspect-ratio: 1 / 1;
        
        gap: 0 !important; 
        padding: 0 !important;
    }}

    /* 精準消除「棋盤內部」的間距，不影響左側 UI */
    div[data-testid="stVerticalBlock"]:has(button[data-testid="stBaseButton-secondary"]) div[data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(button[data-testid="stBaseButton-secondary"]) div[data-testid="column"] {{
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* --- 九宮格按鈕本身 --- */
    button[data-testid="stBaseButton-secondary"] {{
        width: 100% !important;
        height: 100% !important;
        aspect-ratio: 1 / 1 !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        min-height: unset !important;
        transition: background-color 0.2s ease;
    }}

    button[data-testid="stBaseButton-secondary"]:hover {{
        background-color: rgba(255, 255, 255, 0.15) !important;
    }}

    button[data-testid="stBaseButton-secondary"]:has(div:contains("X")),
    button[data-testid="stBaseButton-secondary"]:has(div:contains("O")) {{
        background-color: transparent !important;
    }}

    /* --- 棋子視覺 --- */
    button[data-testid="stBaseButton-secondary"]:has(div:contains("X"))::after,
    button[data-testid="stBaseButton-secondary"]:has(div:contains("O"))::after {{
        content: ''; position: absolute; 
        width: 76%; height: 76%; 
        top: 12%; left: 12%; 
        border-radius: 50%; z-index: 10;
    }}
    
    button[data-testid="stBaseButton-secondary"]:has(div:contains("X"))::after {{
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #f0f0f0 40%, #bdbdbd 100%);
        box-shadow: 1px 1px 3px rgba(0,0,0,0.4);
    }}
    
    button[data-testid="stBaseButton-secondary"]:has(div:contains("O"))::after {{
        background: radial-gradient(circle at 35% 35%, #666 0%, #1a1a1a 50%, #000 100%);
        box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. 邏輯函數 ---
def check_winner(board):
    for i in range(3):
        if board[i,0] == board[i,1] == board[i,2] != "": return board[i,0]
        if board[0,i] == board[1,i] == board[2,i] != "": return board[0,i]
    if board[0,0] == board[1,1] == board[2,2] != "": return board[0,0]
    if board[0,2] == board[1,1] == board[2,0] != "": return board[0,2]
    if "" not in board: return "Tie"
    return None

def update_scores(winner):
    if winner == "X": st.session_state.score_player += 1
    elif winner == "O": st.session_state.score_cpu += 1
    elif winner == "Tie": st.session_state.score_draw += 1

def computer_move(difficulty):
    board = st.session_state.board
    empty = [(r, c) for r in range(3) for c in range(3) if board[r, c] == ""]
    if not empty: return
    move = None
    if difficulty == "簡單":
        move = random.choice(empty)
    elif difficulty == "普通" or difficulty == "困難":
        for r, c in empty:
            temp = board.copy(); temp[r,c] = "O"
            if check_winner(temp) == "O": move = (r,c); break
        if not move:
            for r, c in empty:
                temp = board.copy(); temp[r,c] = "X"
                if check_winner(temp) == "X": move = (r,c); break
        if not move: move = random.choice(empty)
    
    if move:
        st.session_state.board[move[0], move[1]] = "O"
        win = check_winner(st.session_state.board)
        if win:
            st.session_state.winner = win
            update_scores(win)
        st.session_state.turn = "X"

def handle_click(r, c):
    if st.session_state.board[r, c] == "" and st.session_state.winner is None:
        st.session_state.board[r, c] = "X"
        win = check_winner(st.session_state.board)
        if win:
            st.session_state.winner = win
            update_scores(win)
        else:
            st.session_state.turn = "O"

# --- 6. UI 佈局 (左右雙框) ---
st.markdown("<h4 style='text-align: center; color: #3E2723; margin-bottom: 20px;'>🀄 圍棋風井字戰</h4>", unsafe_allow_html=True)

# 執行電腦回合 (放置在渲染前確保邏輯同步)
if st.session_state.turn == "O" and st.session_state.winner is None:
    time.sleep(0.4)
    computer_move(st.session_state.get('diff_key', "普通"))
    st.rerun()

# 建立左右兩欄
left_ui, right_board = st.columns([1, 1.2], gap="large")

# 左側：控制與計分框架
with left_ui:
    st.markdown(f"""
    <div class="score-box">
        <span style="font-size: 16px;">🏆 戰績表</span>
        <hr style="width: 80%; border-color: #3E2723; margin: 5px 0;">
        <span>⚪ 玩家: {st.session_state.score_player}</span>
        <span>🤝 平局: {st.session_state.score_draw}</span>
        <span>⚫ 電腦: {st.session_state.score_cpu}</span>
    </div>
    """, unsafe_allow_html=True)

    difficulty = st.selectbox("選擇難度", ["簡單", "普通", "困難"], index=1, key='diff_key')
    
    if st.button("🔄 重開此局", use_container_width=True, type="primary"):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()

    if st.session_state.winner:
        msg = "🤝 和局！" if st.session_state.winner == "Tie" else ("⚪ 白棋獲勝！" if st.session_state.winner == "X" else "⚫ 黑棋獲勝！")
        st.markdown(f"<div style='text-align: center; color: #3E2723; font-weight: bold; margin-top: 15px; font-size:16px; background: rgba(255,255,255,0.3); padding: 5px; border-radius: 5px;'>{msg}</div>", unsafe_allow_html=True)
        if st.button("▶️ 下一局", use_container_width=True, type="primary"):
            st.session_state.board = np.full((3, 3), "")
            st.session_state.winner = None
            st.session_state.turn = "X"
            st.rerun()

# 右側：棋盤專屬框架
with right_board:
    board_area = st.container()
    with board_area:
        for i in range(3):
            cols = st.columns(3)
            for j in range(3):
                val = st.session_state.board[i, j]
                cols[j].button(val if val != "" else " ", key=f"btn{i}{j}", on_click=handle_click, args=(i, j))
