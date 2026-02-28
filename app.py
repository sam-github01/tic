#井字遊戲 app3.py
import streamlit as st
import numpy as np
import random
import time
import base64
import os

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
    # 若找不到圖片的備用顏色
    bg_style = 'background-color: #DEB887;'

# --- 4. 核心 CSS 修飾 (完美九宮格排版) ---
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{ visibility: hidden; height: 0; }}
    
    .stApp {{
        background-color: #D2B48C;
        overflow: hidden;
    }}

    .block-container {{
        padding-top: 0.5rem !important;
        max-width: 100% !important;
    }}

    /* --- 核心：完美九宮格框架 --- */
    /* 找到包含棋盤按鈕的容器，套用背景並消除所有間距 */
    div[data-testid="stVerticalBlock"]:has(button[data-testid="stBaseButton-secondary"]) {{
        {bg_style}
        background-size: 100% 100%;
        background-position: center;
        border: 2px solid #3E2723;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.4);
        margin: 0 auto !important;
        max-width: 300px !important;
        aspect-ratio: 1 / 1;
        
        /* 徹底消除 Streamlit 的行列間距 */
        gap: 0 !important; 
        padding: 0 !important;
    }}

    /* 消除行 (Row) 的垂直間距 */
    div[data-testid="stVerticalBlock"]:has(button[data-testid="stBaseButton-secondary"]) > .element-container {{
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* 消除列 (Column) 的水平間距 */
    div[data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    div[data-testid="column"] {{
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
        border-radius: 0 !important; /* 確保感應區是方形的九宮格 */
        padding: 0 !important;
        margin: 0 !important;
        min-height: unset !important;
        transition: background-color 0.2s ease;
    }}

    /* 懸停時方形微亮，清楚提示九宮格位置 */
    button[data-testid="stBaseButton-secondary"]:hover {{
        background-color: rgba(255, 255, 255, 0.15) !important;
    }}

    /* 下子後隱藏背景色 */
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
    
    /* 白子 */
    button[data-testid="stBaseButton-secondary"]:has(div:contains("X"))::after {{
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #f0f0f0 40%, #bdbdbd 100%);
        box-shadow: 2px 3px 5px rgba(0,0,0,0.4);
    }}
    
    /* 黑子 */
    button[data-testid="stBaseButton-secondary"]:has(div:contains("O"))::after {{
        background: radial-gradient(circle at 35% 35%, #666 0%, #1a1a1a 50%, #000 100%);
        box-shadow: 2px 3px 5px rgba(0,0,0,0.5);
    }}

    /* --- UI 其他組件 --- */
    .score-box {{
        text-align: center;
        background: rgba(0, 0, 0, 0.05);
        padding: 4px;
        margin-bottom: 8px;
        color: #3E2723;
        font-weight: bold;
        font-size: 13px;
        border-radius: 6px;
    }}

    button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(145deg, #6d4c41, #5d4037) !important;
        height: 32px !important;
        min-height: 32px !important;
        line-height: 32px !important;
        font-size: 13px !important;
        padding: 0 10px !important;
        border-radius: 6px !important;
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

# --- 6. UI 渲染 ---
st.markdown("<h5 style='text-align: center; color: #3E2723; margin: 0;'>🀄 圍棋風井字戰</h5>", unsafe_allow_html=True)
st.markdown(f"""<div class="score-box">白: {st.session_state.score_player} | 平: {st.session_state.score_draw} | 黑: {st.session_state.score_cpu}</div>""", unsafe_allow_html=True)

c1, c2 = st.columns([1.5, 1])
with c1:
    difficulty = st.selectbox("難度", ["簡單", "普通", "困難"], index=1, label_visibility="collapsed")
with c2:
    if st.button("重開", use_container_width=True, type="primary"):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()

if st.session_state.turn == "O" and st.session_state.winner is None:
    time.sleep(0.4)
    computer_move(difficulty)
    st.rerun()

# 棋盤渲染區 (將被 CSS 自動轉換為完美九宮格)
board_area = st.container()
with board_area:
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            val = st.session_state.board[i, j]
            cols[j].button(val if val != "" else " ", key=f"btn{i}{j}", on_click=handle_click, args=(i, j))

if st.session_state.winner:
    msg = "🤝 和局！" if st.session_state.winner == "Tie" else ("⚪ 白勝！" if st.session_state.winner == "X" else "⚫ 黑勝！")
    st.markdown(f"<p style='text-align: center; color: #3E2723; font-weight: bold; margin: 5px 0; font-size:15px;'>{msg}</p>", unsafe_allow_html=True)
    if st.button("下一局", use_container_width=True, type="primary"):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()
