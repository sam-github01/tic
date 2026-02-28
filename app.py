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

# --- 3. 核心 CSS 修飾 (極致縮減空間版) ---
BOARD_IMG_URL = "https://r.jina.ai/i/0572b847844040a49da3266e700a207f"

st.markdown(f"""
    <style>
    /* 隱藏多餘 UI 並強制背景 */
    header, footer, #MainMenu {{ visibility: hidden; height: 0; }}
    
    .stApp {{
        background-color: #D2B48C;
        overflow: hidden;
    }}

    /* 頂部極致壓縮 */
    .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }}

    /* 棋盤容器：再度縮小至 280px 以適應一頁顯示 */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {{
        background-image: url("{BOARD_IMG_URL}");
        background-size: 100% 100%;
        background-position: center;
        border: 3px solid #3E2723;
        border-radius: 8px;
        padding: 3px !important;
        margin: 0 auto !important;
        aspect-ratio: 1 / 1;
        max-width: 280px !important; 
        background-color: #E3C18A;
    }}

    /* 棋盤按鈕：極致縮小 */
    .stButton>button {{
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        background-color: transparent !important;
        border: none !important;
        margin: 0px !important;
        padding: 0px !important;
    }}

    /* 移除所有預設間距 */
    [data-testid="column"] {{ padding: 0 !important; }}
    [data-testid="stHorizontalBlock"] {{ gap: 2px !important; }}
    div[data-testid="stVerticalBlock"] > div {{ padding: 2px 0 !important; }}

    /* 棋子尺寸同步縮小 */
    .stButton>button:has(div:contains("X"))::after,
    .stButton>button:has(div:contains("O"))::after {{
        width: 80%; height: 80%;
        top: 10%; left: 10%;
    }}

    /* 緊湊計分板 */
    .score-box {{
        display: flex;
        justify-content: space-around;
        background: rgba(255, 255, 255, 0.2);
        padding: 4px;
        border-radius: 6px;
        margin-bottom: 5px;
        color: #3E2723;
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #3E2723;
    }}

    /* 質感按鈕高度壓縮 */
    .stButton>button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(145deg, #6d4c41, #5d4037) !important;
        padding: 2px 10px !important;
        min-height: 30px !important;
        font-size: 13px !important;
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
    if difficulty == "簡單": move = random.choice(empty)
    elif difficulty == "普通":
        for r, c in empty:
            temp = board.copy(); temp[r,c] = "O"
            if check_winner(temp) == "O": move = (r,c); break
        if not move: move = random.choice(empty)
    else: # 困難 (Minimax 邏輯簡寫)
        move = random.choice(empty) # 這裡可依需求補完 Minimax
    
    if
