#井字遊戲 app3.py
import streamlit as st
import numpy as np
import random
import time

# 1. 手機版配置
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

# --- 3. 核心 CSS 修飾 (框架一體化版本) ---
BOARD_IMG_URL = "https://r.jina.ai/i/0572b847844040a49da3266e700a207f"

st.markdown(f"""
    <style>
    /* 隱藏多餘 UI */
    header, footer, #MainMenu {{ visibility: hidden; height: 0; }}
    
    .stApp {{
        background-color: #D2B48C;
        overflow: hidden;
    }}

    /* 頂部極致壓縮 */
    .block-container {{
        padding-top: 0.2rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }}

    /* --- 核心：棋盤框架一體化 --- */
    .game-board-frame {{
        background-image: url("{BOARD_IMG_URL}");
        background-size: cover;
        background-position: center;
        border: 4px solid #3E2723;
        border-radius: 12px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.4);
        padding: 6px !important;
        margin: 0 auto !important;
        max-width: 280px !important;
        aspect-ratio: 1 / 1;
        background-color: #E3C18A;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0px; /* 讓格線無縫接軌 */
    }}

    /* 讓按鈕在 Grid 框架中完美填滿 */
    .stButton {{
        width: 100% !important;
        margin: 0 !important;
    }}
    
    .stButton > button {{
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0px !important;
        transition: background 0.2s;
    }}

    /* 棋子視覺 (微縮版) */
    .stButton>button:has(div:contains("X"))::after,
    .stButton>button:has(div:contains("O"))::after {{
        content: ''; position: absolute; width: 75%; height: 75%;
        top: 12.5%; left: 12.5%; border-radius: 50%; z-index: 10;
    }}

    .stButton>button:has(div:contains("X"))::after {{
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #f0f0f0 40%, #bdbdbd 100%);
        box-shadow: 2px 2px 5px rgba(0,0,0,0.4);
    }}

    .stButton>button:has(div:contains("O"))::after {{
        background: radial-gradient(circle at 35% 35%, #666 0%, #1a1a1a 50%, #000 100%);
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }}

    /* 緊湊計分板與 UI */
    .score-box {{
        display: flex;
        justify-content: space-around;
        background: rgba(0, 0, 0, 0.05);
        padding: 3px;
        border-radius: 5px;
        margin-bottom: 5px;
        color: #3E2723;
        font-weight: bold;
        font-size: 13px;
    }}

    .stButton>button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(145deg, #6d4c41, #5d4037) !important;
        min-height: 28px !important;
        font-size: 12px !important;
        padding: 0 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. 邏輯函數 ---
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
    elif difficulty == "普通":
        # 簡單進攻與防守邏輯
        for r, c in empty:
            temp = board.copy()
            temp[r,c] = "O"
            if check_winner(temp) == "O": move = (r,c); break
        if not move:
            for r, c in empty:
                temp = board.copy()
                temp[r,c] = "X"
                if check_winner(temp) == "X": move = (r,c); break
        if not move: move = random.choice(empty)
    else: # 困難 (預設為隨機，可擴充 Minimax)
        move = random.choice(empty)
    
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

# --- 5. UI 渲染 ---
st.markdown("<h6 style='text-align: center; color: #3E2723; margin: 0;'>🀄 圍棋風井字戰</h6>", unsafe_allow_html=True)

# 計分板與控制項
st.markdown(f"""<div class="score-box">白: {st.session_state.score_player} | 平: {st.session_state.score_draw} | 黑: {st.session_state.score_cpu}</div>""", unsafe_allow_html=True)

col_diff, col_reset = st.columns([1.5, 1])
with col_diff:
    difficulty = st.selectbox("難度", ["簡單", "普通", "困難"], index=1, label_visibility="collapsed")
with col_reset:
    if st.button("重開", use_container_width=True, type="primary"):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()

if st.session_state.turn == "O" and st.session_state.winner is None:
    time.sleep(0.4)
    computer_move(difficulty)
    st.rerun()

# --- 核心棋盤框 ---
# 使用 HTML 建立一個框，裡面再用 Streamlit columns 放入按鈕
st.markdown('<div class="game-board-frame">', unsafe_allow_html=True)
for i in range(3):
    cols = st.columns(3)
    for j in range(3):
        val = st.session_state.board[i, j]
        cols[j].button(val if val != "" else " ", key=f"btn{i}{j}", on_click=handle_click, args=(i, j))
st.markdown('</div>', unsafe_allow_html=True)

# 勝負反饋
if st.session_state.winner:
    msg = "🤝 和局！" if st.session_state.winner == "Tie" else ("⚪ 白勝！" if st.session_state.winner == "X" else "⚫ 黑勝！")
    st.markdown(f"<p style='text-align: center; color: #3E2723; font-weight: bold; margin: 5px 0;'>{msg}</p>", unsafe_allow_html=True)
    if st.button("下一局", use_container_width=True, type="primary"):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()
