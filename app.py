#井字遊戲 app2.py
import streamlit as st
import numpy as np
import random

# 設定頁面配置，適合手機瀏覽
st.set_page_config(page_title="圍棋風井字戰", layout="centered")

# --- 初始化遊戲狀態 (與之前相同) ---
if 'board' not in st.session_state:
    st.session_state.board = np.full((3, 3), "")
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'turn' not in st.session_state:
    st.session_state.turn = "X"  # 玩家先手 (將顯示為白棋)

# --- 進階 CSS 樣式注入：打造圍棋風格 ---
# 這裡是最核心的視覺修改
st.markdown("""
    <style>
    /* 1. 全局背景顏色 (選擇一個類似淺木色的顏色) */
    .stApp {
        background-color: #F3E5AB; 
    }

    /* 2. 標題和文字顏色 */
    h1, p, div {
        color: #4A3121 !important; /* 深棕色文字 */
    }

    /* 3. 棋盤區域的容器 (用來畫格線) */
    [data-testid="stHorizontalBlock"] {
        background-color: #DEB887; /* 棋盤格本身的木頭色 */
        border: 2px solid #4A3121;
        padding: 5px;
        border-radius: 5px;
    }

    /* 4. Streamlit 按鈕基礎樣式 (透明化，自訂大小) */
    .stButton>button {
        width: 100%;
        height: 100px; /* 手機上較好點擊的高度 */
        background-color: transparent !important; /* 透明背景，顯示下方的木紋 */
        border: 1px solid #4A3121 !important; /* 棋盤格線 */
        border-radius: 0px !important; /* 方形格 */
        color: transparent !important; /* 隱藏原本的 "X" 或 "O" 文字 */
        position: relative;
        transition: background-color 0.3s;
    }

    /* 滑鼠懸停時的微小變化 (對手機影響較小，但對桌面友好) */
    .stButton>button:hover {
        background-color: rgba(74, 49, 33, 0.1) !important;
    }

    /* 5. 定義白棋 (玩家 X) - 使用 CSS 偽元素 ::after */
    .stButton>button:has(div:contains("X"))::after {
        content: '';
        position: absolute;
        top: 10px; left: 10px; right: 10px; bottom: 10px;
        background: radial-gradient(circle at 30% 30%, #ffffff, #d0d0d0); /* 立體感白棋 */
        border-radius: 50%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }

    /* 6. 定義黑棋 (電腦 O) - 使用 CSS 偽元素 ::after */
    .stButton>button:has(div:contains("O"))::after {
        content: '';
        position: absolute;
        top: 10px; left: 10px; right: 10px; bottom: 10px;
        background: radial-gradient(circle at 30% 30%, #444444, #000000); /* 立體感黑棋 */
        border-radius: 50%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.4);
    }

    /* 7. 下拉選單和按鈕的特殊修正 (防止被全局樣式影響) */
    .stSelectbox div[data-baseweb="select"] {
        background-color: white !important;
    }
    
    /* 修正重新開始按鈕的樣式，不要讓它變成棋子 */
    [data-testid="stSidebar"] .stButton>button, 
    div.stButton:not([data-testid="stHorizontalBlock"] div) > button {
        background-color: #4A3121 !important;
        color: white !important;
        height: auto !important;
        border-radius: 5px !important;
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 遊戲邏輯函數 (與之前完全相同) ---
def check_winner(board):
    for i in range(3):
        if board[i,0] == board[i,1] == board[i,2] != "": return board[i,0]
        if board[0,i] == board[1,i] == board[2,i] != "": return board[0,i]
    if board[0,0] == board[1,1] == board[2,2] != "": return board[0,0]
    if board[0,2] == board[1,1] == board[2,0] != "": return board[0,2]
    if "" not in board: return "Tie"
    return None

def minimax(board, is_maximizing):
    res = check_winner(board)
    if res == "O": return 1 # 黑棋贏
    if res == "X": return -1 # 白棋贏
    if res == "Tie": return 0
    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i,j] == "":
                    board[i,j] = "O"
                    score = minimax(board, False)
                    board[i,j] = ""
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i,j] == "":
                    board[i,j] = "X"
                    score = minimax(board, True)
                    board[i,j] = ""
                    best_score = min(score, best_score)
        return best_score

def computer_move(difficulty):
    board = st.session_state.board
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r, c] == ""]
    if not empty_cells: return
    move = None
    if difficulty == "簡單":
        move = random.choice(empty_cells)
    elif difficulty == "普通":
        for r, c in empty_cells:
            temp_board = board.copy()
            temp_board[r, c] = "O"
            if check_winner(temp_board) == "O":
                move = (r, c)
                break
        if not move: move = random.choice(empty_cells)
    elif difficulty == "困難":
        best_score = -float('inf')
        for r, c in empty_cells:
            board[r, c] = "O"
            score = minimax(board, False)
            board[r, c] = ""
            if score > best_score:
                best_score = score
                move = (r, c)
    if move:
        st.session_state.board[move[0], move[1]] = "O"
        st.session_state.winner = check_winner(st.session_state.board)
        st.session_state.turn = "X"

def handle_click(r, c):
    if st.session_state.board[r, c] == "" and st.session_state.winner is None:
        st.session_state.board[r, c] = "X"
        st.session_state.winner = check_winner(st.session_state.board)
        if st.session_state.winner is None:
            st.session_state.turn = "O"

# --- UI 介面 ---
st.title("圍棋風井字戰")
st.write("玩家：白棋 ⚪ | 電腦：黑棋 ⚫")

difficulty = st.selectbox("選擇難度", ["簡單", "普通", "困難"])

if st.session_state.turn == "O" and st.session_state.winner is None:
    # 這裡加入一個微小的延遲，讓電腦看起來像在思考
    import time
    with st.spinner('電腦思考中...'):
        time.sleep(0.5)
    computer_move(difficulty)
    st.rerun()

# --- 繪制棋盤 ---
# 我們將其封裝在一個 container 中以便應用 CSS 樣式
board_container = st.container()

with board_container:
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            # 雖然按鈕上顯示的是文字 "X" 或 "O"，但 CSS 會隱藏文字並顯示棋子圖案
            content = st.session_state.board[i, j]
            cols[j].button(content if content != "" else " ", key=f"btn-{i}-{j}", on_click=handle_click, args=(i, j))

# --- 顯示結果與重新開始 ---
if st.session_state.winner:
    st.markdown("---") # 分隔線
    if st.session_state.winner == "Tie":
        st.info("和局！")
    else:
        wn = "白棋 (玩家)" if st.session_state.winner == "X" else "黑棋 (電腦)"
        st.success(f"🎉 贏家是: {wn}")
    
    # 這個按鈕不會被棋盤樣式影響
    if st.button("重新開始新局"):
        st.session_state.board = np.full((3, 3), "")
        st.session_state.winner = None
        st.session_state.turn = "X"
        st.rerun()
