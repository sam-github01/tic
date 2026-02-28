#井字遊戲 app3.py
import streamlit as st
import numpy as np
import random
import time

# 1. 手機版視窗配置
st.set_page_config(
    page_title="圍棋井字棋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 初始化遊戲狀態與計分板 ---
if 'board' not in st.session_state:
    st.session_state.board = np.full((3, 3), "")
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'turn' not in st.session_state:
    st.session_state.turn = "X"

# 初始化計分板
if 'score_player' not in st.session_state:
    st.session_state.score_player = 0
if 'score_cpu' not in st.session_state:
    st.session_state.score_cpu = 0
if 'score_draw' not in st.session_state:
    st.session_state.score_draw = 0

# --- 3. 手機版專屬 CSS (包含計分板樣式) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        background-color: #E3C18A;
        background-image: radial-gradient(circle, #f0d5a7 0%, #d4a76a 100%);
    }
    .block-container {
        padding-top: 1rem !important;
        max-width: 400px !important;
    }

    /* 計分板容器樣式 */
    .score-container {
        background-color: rgba(74, 49, 33, 0.1);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #5D4037;
    }
    .score-item {
        text-align: center;
        font-weight: bold;
        color: #3E2723;
    }

    /* 棋盤容器 */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background-color: #D2B48C;
        border: 4px solid #5D4037;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.3);
        border-radius: 8px;
    }

    /* 按鈕與棋子樣式 */
    .stButton>button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        background-color: transparent !important;
        border: 1px solid #5D4037 !important;
        border-radius: 0px !important;
        position: relative;
    }
    .stButton>button:has(div:contains("X"))::after {
        content: ''; position: absolute; width: 80%; height: 80%; top: 10%; left: 10%;
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #e0e0e0 100%);
        border-radius: 50%; box-shadow: 2px 4px 6px rgba(0,0,0,0.3);
    }
    .stButton>button:has(div:contains("O"))::after {
        content: ''; position: absolute; width: 80%; height: 80%; top: 10%; left: 10%;
        background: radial-gradient(circle at 30% 30%, #444 0%, #000 100%);
        border-radius: 50%; box-shadow: 2px 4px 6px rgba(0,0,0,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 遊戲邏輯與計分更新 ---
def check_winner(board):
    for i in range(3):
        if board[i,0] == board[i,1] == board[i,2] != "": return board[i,0]
        if board[0,i] == board[1,i] == board[2,i] != "": return board[0,i]
    if board[0,0] == board[1,1] == board[2,2] != "": return board[0,0]
    if board[0,2] == board[1,1] == board[2,0] != "": return board[0,2]
    if "" not in board: return "Tie"
    return None

def update_scores(winner):
    if winner == "X":
        st.session_state.score_player += 1
    elif winner == "O":
        st.session_state.score_cpu += 1
    elif winner == "Tie":
        st.session_state.score_draw += 1

# Minimax 演算法 (困難模式)
def minimax(board, is_maximizing):
    res = check_winner(board)
    if res == "O": return 1
    if res == "X": return -1
    if res == "Tie": return 0
    if is_maximizing:
        best_score = -float('inf'); scores = [minimax(board, False) if board[i,j] == "" else -10 for i,j in [(r,c) for r in range(3) for c in range(3)]]
        # 簡化版邏輯僅供結構參考，實際執行使用下方展開式
        best_val = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i,j] == "":
                    board[i,j] = "O"; val = minimax(board, False); board[i,j] = ""; best_val = max(best_val, val)
        return best_val
    else:
        best_val = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i,j] == "":
                    board[i,j] = "X"; val = minimax(board, True); board[i,j] = ""; best_val = min(best_val, val)
        return best_val

def computer_move(difficulty):
    board = st.session_state.board
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r, c] == ""]
    if not empty_cells: return
    move = None
    if difficulty == "簡單":
        move = random.choice(empty_cells)
    elif difficulty == "普通":
        for r, c in empty_cells:
            temp = board.copy(); temp[r,c] = "O"
            if check_winner(temp) == "O": move = (r,c); break
        if not move: move = random.choice(empty_cells)
    else: # 困難
        best = -float('inf')
        for r, c in empty_cells:
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

# --- 5. UI 實作 ---
st.markdown("<h2 style='text-align: center; color: #3E2723; margin-bottom: 0;'>圍棋風格井字戰</h2>", unsafe_allow_html=True)

# 計分板 UI
st.markdown(f"""
<div class="score-container">
    <div style="display: flex; justify-content: space-around;">
        <div class="score-item">玩家(白)<br><span style="font-size: 20px;">{st.session_state.score_player}</span></div>
        <div class="score-item">平局<br><span style="font-size: 20px;">{st.session_state.score_draw}</span></div>
        <div class="score-item">電腦(黑)<br><span style="font-size: 20px;">{st.session_state.score_cpu}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# 難度與重置
c1, c2 = st.columns([2, 1])
with c1:
    difficulty = st.selectbox("等級", ["簡單", "普通", "困難"], label_visibility="collapsed")
with c2:
    if st.button("清空戰績"):
        st.session_state.score_player = 0
        st.session_state.score_cpu = 0
        st.session_state.score_draw = 0
        st.rerun()

# 電腦移動
if st.session_state.turn == "O" and st.session_state.winner is None:
    time.sleep(0.5)
    computer_move(difficulty)
    st.rerun()

# 棋盤
for i in range(3):
    cols = st.columns(3, gap="small")
    for j in range(3):
        content = st.session_state.board[i, j]
        cols[j].button(content if content != "" else " ", key=f"b{i}{j}", on_click=handle_click, args=(i, j))

# 結果與下一局
if st.session_state.winner:
    msg = "🤝 和局！" if st.session_state.winner == "Tie" else ("⚪ 你贏了！" if st.session_state.winner == "X" else "⚫ 電腦贏了！")
    st.markdown(f"<h3 style='text-align: center; color: #3E2723;'>{msg}</h3>", unsafe_allow_html=True)
    if st.button("開始下一局", use_container_width=True):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()
