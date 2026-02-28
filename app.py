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

# --- 2. 初始化狀態 (保持不變) ---
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

# --- 3. 核心 CSS 修修優化 ---
st.markdown("""
    <style>
    /* 隱藏多餘 UI */
    header, footer, #MainMenu {visibility: hidden;}
    
    .stApp {
        background-color: #D2B48C; /* 深木色背景 */
    }

    .block-container {
        padding-top: 1rem !important;
        max-width: 450px !important; /* 適合手機寬度 */
    }

    /* 棋盤格線設計 */
    .stButton>button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        border-radius: 0px !important;
        margin: 0px !important;
        /* 使用漸層畫出十字線 */
        background: 
            linear-gradient(to right, transparent 49%, #3E2723 50%, #3E2723 51%, transparent 52%),
            linear-gradient(to bottom, transparent 49%, #3E2723 50%, #3E2723 51%, transparent 52%) !important;
        background-color: #E3C18A !important; /* 棋盤木頭色 */
        border: 0.5px solid rgba(62, 39, 35, 0.3) !important;
        position: relative;
    }

    /* 移除 Streamlit 預設按鈕間距 */
    [data-testid="column"] {
        padding: 0 !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }

    /* --- 強化黑白棋子視覺 --- */
    
    /* 白子 (玩家 X) - 增加珍珠般的光澤 */
    .stButton>button:has(div:contains("X"))::after {
        content: '';
        position: absolute;
        width: 85%; height: 85%;
        top: 7.5%; left: 7.5%;
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #f0f0f0 40%, #bdbdbd 100%);
        border-radius: 50%;
        box-shadow: 3px 5px 8px rgba(0,0,0,0.4), inset -2px -2px 5px rgba(0,0,0,0.1);
        z-index: 10;
    }

    /* 黑子 (電腦 O) - 增加曜石般的光澤 */
    .stButton>button:has(div:contains("O"))::after {
        content: '';
        position: absolute;
        width: 85%; height: 85%;
        top: 7.5%; left: 7.5%;
        background: radial-gradient(circle at 35% 35%, #666666 0%, #1a1a1a 50%, #000000 100%);
        border-radius: 50%;
        box-shadow: 3px 5px 10px rgba(0,0,0,0.5), inset -1px -1px 3px rgba(255,255,255,0.2);
        z-index: 10;
    }

    /* 計分板與文字 */
    .score-box {
        display: flex;
        justify-content: space-around;
        background: rgba(0,0,0,0.1);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        color: #3E2723;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 邏輯函數 (與前版本一致) ---
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
    if difficulty == "簡單":
        move = random.choice(empty)
    elif difficulty == "普通":
        for r, c in empty:
            temp = board.copy(); temp[r,c] = "O"
            if check_winner(temp) == "O": move = (r,c); break
        if not move: move = random.choice(empty)
    else: # 困難
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
st.markdown("<h3 style='text-align: center; color: #3E2723;'>🀄 圍棋風井字戰</h3>", unsafe_allow_html=True)

# 計分板
st.markdown(f"""
<div class="score-box">
    <div>白棋 (你): {st.session_state.score_player}</div>
    <div>平局: {st.session_state.score_draw}</div>
    <div>黑棋 (電): {st.session_state.score_cpu}</div>
</div>
""", unsafe_allow_html=True)

# 控制區
col_diff, col_reset = st.columns([2, 1])
with col_diff:
    difficulty = st.selectbox("難度", ["簡單", "普通", "困難"], label_visibility="collapsed")
with col_reset:
    if st.button("重開", use_container_width=True):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()

# 電腦思考
if st.session_state.turn == "O" and st.session_state.winner is None:
    time.sleep(0.5)
    computer_move(difficulty)
    st.rerun()

# --- 繪製棋盤 ---
# 棋盤本體
board_placeholder = st.container()
with board_placeholder:
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            val = st.session_state.board[i, j]
            cols[j].button(val if val != "" else " ", key=f"btn{i}{j}", on_click=handle_click, args=(i, j))

# 勝負顯示
if st.session_state.winner:
    msg = "🤝 和局！" if st.session_state.winner == "Tie" else ("⚪ 白棋勝！" if st.session_state.winner == "X" else "⚫ 黑棋勝！")
    st.markdown(f"<h2 style='text-align: center; color: #3E2723; margin-top:10px;'>{msg}</h2>", unsafe_allow_html=True)
    if st.button("下一局", use_container_width=True):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()
