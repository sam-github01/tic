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

# --- 3. 核心 CSS 修飾 (手機適配與居中優化) ---
BOARD_IMG_URL = "https://r.jina.ai/i/0572b847844040a49da3266e700a207f"

st.markdown(f"""
    <style>
    /* 隱藏多餘 UI */
    header, footer, #MainMenu {{
        visibility: hidden;
    }}
    
    .stApp {{
        background-color: #D2B48C;
        overflow-x: hidden; /* 防止水平抖動 */
    }}

    /* 限制整體容器寬度以適應手機 */
    .block-container {{
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
        width: 100vw !important;
    }}

    /* 棋盤容器：確保寬度不超過手機螢幕且居中 */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {{
        background-image: url("{BOARD_IMG_URL}");
        background-size: 100% 100%;
        background-position: center;
        background-repeat: no-repeat;
        border: 4px solid #3E2723;
        border-radius: 10px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
        padding: 4px !important;
        margin: 0 auto !important; /* 強制置中 */
        aspect-ratio: 1 / 1;
        max-width: 350px !important; /* 限制手機最大寬度 */
        background-color: #E3C18A;
    }}

    /* 棋盤按鈕：透明且響應式 */
    .stButton>button {{
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        background-color: transparent !important;
        border: none !important;
        margin: 0px !important;
        padding: 0px !important;
        position: relative;
    }}

    /* 移除 Streamlit 欄位間距 */
    [data-testid="column"] {{ padding: 0 !important; }}
    [data-testid="stHorizontalBlock"] {{ gap: 0 !important; }}

    /* --- 棋子視覺 --- */
    .stButton>button:has(div:contains("X"))::after {{
        content: ''; position: absolute; width: 85%; height: 85%;
        top: 7.5%; left: 7.5%;
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #f0f0f0 40%, #bdbdbd 100%);
        border-radius: 50%; box-shadow: 2px 3px 5px rgba(0,0,0,0.4);
        z-index: 10;
    }}

    .stButton>button:has(div:contains("O"))::after {{
        content: ''; position: absolute; width: 85%; height: 85%;
        top: 7.5%; left: 7.5%;
        background: radial-gradient(circle at 35% 35%, #666 0%, #1a1a1a 50%, #000 100%);
        border-radius: 50%; box-shadow: 2px 3px 6px rgba(0,0,0,0.5);
        z-index: 10;
    }}

    /* 計分板 */
    .score-box {{
        display: flex;
        justify-content: space-around;
        background: rgba(255, 255, 255, 0.25);
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #3E2723;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid #3E2723;
    }}

    /* 質感按鈕 */
    .stButton>button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(145deg, #6d4c41, #5d4037) !important;
        color: #fff !important;
        border-radius: 8px !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3) !important;
        height: auto !important;
        font-size: 14px !important;
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

def minimax(board, is_maximizing):
    res = check_winner(board)
    if res == "O": return 1
    if res == "X": return -1
    if res == "Tie": return 0
    empty = [(r, c) for r in range(3) for c in range(3) if board[r, c] == ""]
    if is_maximizing:
        best = -float('inf')
        for r, c in empty:
            board[r,c] = "O"; val = minimax(board, False); board[r,c] = ""; best = max(best, val)
        return best
    else:
        best = float('inf')
        for r, c in empty:
            board[r,c] = "X"; val = minimax(board, True); board[r,c] = ""; best = min(best, val)
        return best

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
    else:
        best = -float('inf')
        for r, c in empty:
            board[r,c] = "O"; s = minimax(board, False); board[r,c] = ""
            if s > best: best = s; move = (r,c)
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
st.markdown("<h4 style='text-align: center; color: #3E2723; margin: 0;'>🀄 精品圍棋井字戰</h4>", unsafe_allow_html=True)

st.markdown(f"""
<div class="score-box">
    <div>白棋: {st.session_state.score_player}</div>
    <div>平局: {st.session_state.score_draw}</div>
    <div>黑棋: {st.session_state.score_cpu}</div>
</div>
""", unsafe_allow_html=True)

col_diff, col_reset = st.columns([1.5, 1])
with col_diff:
    # index=1 代表預設選擇第二個選項，即「普通」
    difficulty = st.selectbox("難度", ["簡單", "普通", "困難"], index=1, label_visibility="collapsed")
with col_reset:
    if st.button("重開", use_container_width=True, type="primary"):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()

if st.session_state.turn == "O" and st.session_state.winner is None:
    time.sleep(0.5)
    computer_move(difficulty)
    st.rerun()

# 棋盤渲染 (使用 Container 包裹以利 CSS 置中控制)
with st.container():
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            val = st.session_state.board[i, j]
            cols[j].button(val if val != "" else " ", key=f"btn{i}{j}", on_click=handle_click, args=(i, j))

if st.session_state.winner:
    msg = "🤝 和局！" if st.session_state.winner == "Tie" else ("⚪ 白棋勝！" if st.session_state.winner == "X" else "⚫ 黑棋勝！")
    st.markdown(f"<h3 style='text-align: center; color: #3E2723; margin-top:10px;'>{msg}</h3>", unsafe_allow_html=True)
    if st.button("下一局", use_container_width=True, type="primary"):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()
