import streamlit as st
import requests
import time
import random
import json
import os
from datetime import datetime

st.set_page_config(page_title="친한친구 끝말잇기 톡", page_icon="💬", layout="wide")

# ==========================================
# 💾 데이터 영구 저장 및 불러오기 (JSON 파일 기반)
# ==========================================
SAVE_FILE = "user_data.json"

def load_user_data():
    default_data = {
        "points": 0,
        "score": 0,
        "high_score": 0,
        "inventory": ["🐣 끝말잇기 병아리", "🐱 귀여운 고양이", "기본 프레임"],
        "equipped_theme": "기본",
        "equipped_avatar": "🐱 귀여운 고양이",
        "equipped_frame": "기본 프레임",
        "equipped_title": "🐣 끝말잇기 병아리",
        "stats": {"wins": 0, "losses": 0, "total_games": 0},
        "history": []
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in default_data.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            return default_data
    return default_data

def save_user_data():
    data = {
        "points": st.session_state.points,
        "score": st.session_state.score,
        "high_score": st.session_state.high_score,
        "inventory": st.session_state.inventory,
        "equipped_theme": st.session_state.equipped_theme,
        "equipped_avatar": st.session_state.equipped_avatar,
        "equipped_frame": st.session_state.equipped_frame,
        "equipped_title": st.session_state.equipped_title,
        "stats": st.session_state.stats,
        "history": st.session_state.history
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if "data_loaded" not in st.session_state:
    saved_data = load_user_data()
    st.session_state.points = saved_data["points"]
    st.session_state.score = saved_data["score"]
    st.session_state.high_score = saved_data["high_score"]
    st.session_state.inventory = saved_data["inventory"]
    st.session_state.equipped_theme = saved_data["equipped_theme"]
    st.session_state.equipped_avatar = saved_data["equipped_avatar"]
    st.session_state.equipped_frame = saved_data["equipped_frame"]
    st.session_state.equipped_title = saved_data["equipped_title"]
    st.session_state.stats = saved_data["stats"]
    st.session_state.history = saved_data["history"]
    st.session_state.data_loaded = True

# 📈 상위 몇 % (랭킹 산정 로직)
def calculate_percentile():
    score = st.session_state.high_score
    wins = st.session_state.stats["wins"]
    rating = (score * 3) + (wins * 20) + (st.session_state.points * 0.5)
    
    if rating >= 1000: return "상위 0.1% (천상계) 👑"
    elif rating >= 600: return "상위 1.0% (랭커) 💎"
    elif rating >= 350: return "상위 5.0% (마스터) 🔥"
    elif rating >= 200: return "상위 15.0% (다이아) ✨"
    elif rating >= 100: return "상위 30.0% (골드) 🥇"
    elif rating >= 40: return "상위 50.0% (실버) 🥈"
    else: return "상위 85.0% (브론즈) 🥉"

# ==========================================
# 🎨 사이드바 메뉴 대형화 & 테마 CSS
# ==========================================
st.markdown("""
<style>
    /* 사이드바 너비 및 글자 크기 확대 */
    [data-testid="stSidebar"] {
        min-width: 320px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 12px 18px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        background-color: rgba(255, 255, 255, 0.05);
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.15);
        transform: translateX(4px);
    }
    .point-badge {
        background: linear-gradient(135deg, #facc15, #eab308);
        color: #000;
        padding: 15px;
        border-radius: 16px;
        text-align: center;
        font-size: 26px;
        font-weight: 900;
        box-shadow: 0 4px 15px rgba(250, 204, 21, 0.4);
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧪 원소 주기율표 데이터 (1~118 전 원소)
# ==========================================
ELEMENTS_DATA = [
    (1, "H", "수소", "기체", "비금속"), (2, "He", "헬륨", "기체", "비활성기체"),
    (3, "Li", "리튬", "고체", "알칼리금속"), (4, "Be", "베릴륨", "고체", "알칼리토금속"),
    (5, "B", "붕소", "고체", "준금속"), (6, "C", "탄소", "고체", "비금속"),
    (7, "N", "질소", "기체", "비금속"), (8, "O", "산소", "기체", "비금속"),
    (9, "F", "플루오린", "기체", "할로젠"), (10, "Ne", "네온", "기체", "비활성기체"),
    (11, "Na", "나트륨", "고체", "알칼리금속"), (12, "Mg", "마그네슘", "고체", "알칼리토금속"),
    (13, "Al", "알루미늄", "고체", "전이후금속"), (14, "Si", "규소", "고체", "준금속"),
    (15, "P", "인", "고체", "비금속"), (16, "S", "황", "고체", "비금속"),
    (17, "Cl", "염소", "기체", "할로젠"), (18, "Ar", "아르곤", "기체", "비활성기체"),
    (19, "K", "칼륨", "고체", "알칼리금속"), (20, "Ca", "칼슘", "고체", "알칼리토금속"),
    (21, "Sc", "스칸듐", "고체", "전이금속"), (22, "Ti", "티타늄", "고체", "전이금속"),
    (23, "V", "바나듐", "고체", "전이금속"), (24, "Cr", "크롬", "고체", "전이금속"),
    (25, "Mn", "망가니즈", "고체", "전이금속"), (26, "Fe", "철", "고체", "전이금속"),
    (27, "Co", "코발트", "고체", "전이금속"), (28, "Ni", "니켈", "고체", "전이금속"),
    (29, "Cu", "구리", "고체", "전이금속"), (30, "Zn", "아연", "고체", "전이금속"),
    (31, "Ga", "갈륨", "고체", "전이후금속"), (32, "Ge", "저마늄", "고체", "준금속"),
    (33, "As", "비소", "고체", "준금속"), (34, "Se", "셀레늄", "고체", "비금속"),
    (35, "Br", "브로민", "액체", "할로젠"), (36, "Kr", "크립톤", "기체", "비활성기체"),
    (37, "Rb", "루비듐", "고체", "알칼리금속"), (38, "Sr", "스트론튬", "고체", "알칼리토금속"),
    (39, "Y", "이트륨", "고체", "전이금속"), (40, "Zr", "지르코늄", "고체", "전이금속"),
    (41, "Nb", "나이오븀", "고체", "전이금속"), (42, "Mo", "몰리브데넘", "고체", "전이금속"),
    (43, "Tc", "테크네튬", "고체", "전이금속"), (44, "Ru", "루테늄", "고체", "전이금속"),
    (45, "Rh", "로듐", "고체", "전이금속"), (46, "Pd", "팔라듐", "고체", "전이금속"),
    (47, "Ag", "은", "고체", "전이금속"), (48, "Cd", "카드뮴", "고체", "전이금속"),
    (49, "In", "인듐", "고체", "전이후금속"), (50, "Sn", "주석", "고체", "전이후금속"),
    (51, "Sb", "안티몬", "고체", "준금속"), (52, "Te", "텔루륨", "고체", "준금속"),
    (53, "I", "아이오딘", "고체", "할로젠"), (54, "Xe", "제논", "기체", "비활성기체"),
    (55, "Cs", "세슘", "고체", "알칼리금속"), (56, "Ba", "바륨", "고체", "알칼리토금속"),
    (57, "La", "란타넘", "고체", "란타넘족"), (58, "Ce", "세륨", "고체", "란타넘족"),
    (59, "Pr", "프라세오디뮴", "고체", "란타넘족"), (60, "Nd", "네오디뮴", "고체", "란타넘족"),
    (61, "Pm", "프로메튬", "고체", "란타넘족"), (62, "Sm", "사마륨", "고체", "란타넘족"),
    (63, "Eu", "유로퓸", "고체", "란타넘족"), (64, "Gd", "가돌리늄", "고체", "란타넘족"),
    (65, "Tb", "테르븀", "고체", "란타넘족"), (66, "Dy", "디스프로슘", "고체", "란타넘족"),
    (67, "Ho", "홀뮴", "고체", "란타넘족"), (68, "Er", "에르븀", "고체", "란타넘족"),
    (69, "Tm", "툴륨", "고체", "란타넘족"), (70, "Yb", "이테르븀", "고체", "란타넘족"),
    (71, "Lu", "루테튬", "고체", "란타넘족"), (72, "Hf", "하프늄", "고체", "전이금속"),
    (73, "Ta", "탄탈럼", "고체", "전이금속"), (74, "W", "텅스텐", "고체", "전이금속"),
    (75, "Re", "레늄", "고체", "전이금속"), (76, "Os", "오스뮴", "고체", "전이금속"),
    (77, "Ir", "이리듐", "고체", "전이금속"), (78, "Pt", "백금", "고체", "전이금속"),
    (79, "Au", "금", "고체", "전이금속"), (80, "Hg", "수은", "액체", "전이금속"),
    (81, "Tl", "탈륨", "고체", "전이후금속"), (82, "Pb", "납", "고체", "전이후금속"),
    (83, "Bi", "비스무트", "고체", "전이후금속"), (84, "Po", "폴로늄", "고체", "전이후금속"),
    (85, "At", "아스타틴", "고체", "할로젠"), (86, "Rn", "라돈", "기체", "비활성기체"),
    (87, "Fr", "프랑슘", "고체", "알칼리금속"), (88, "Ra", "라듐", "고체", "알칼리토금속"),
    (89, "Ac", "악티늄", "고체", "악티늄족"), (90, "Th", "토륨", "고체", "악티늄족"),
    (91, "Pa", "프로트악티늄", "고체", "악티늄족"), (92, "U", "우라늄", "고체", "악티늄족"),
    (93, "Np", "넵튜늄", "고체", "악티늄족"), (94, "Pu", "플루토늄", "고체", "악티늄족"),
    (95, "Am", "아메리슘", "고체", "악티늄족"), (96, "Cm", "퀴륨", "고체", "악티늄족"),
    (97, "Bk", "버클륨", "고체", "악티늄족"), (98, "Cf", "캘리포늄", "고체", "악티늄족"),
    (99, "Es", "아인슈타이늄", "고체", "악티늄족"), (100, "Fm", "페르븀", "고체", "악티늄족"),
    (101, "Md", "멘델레븀", "고체", "악티늄족"), (102, "No", "노벨륨", "고체", "악티늄족"),
    (103, "Lr", "로렌슘", "고체", "악티늄족"), (104, "Rf", "러더포듐", "고체", "전이금속"),
    (105, "Db", "더브늄", "고체", "전이금속"), (106, "Sg", "시보귬", "고체", "전이금속"),
    (107, "Bh", "보륨", "고체", "전이금속"), (108, "Hs", "하슘", "고체", "전이금속"),
    (109, "Mt", "마이트너륨", "고체", "전이금속"), (110, "Ds", "다름슈타튬", "고체", "전이금속"),
    (111, "Rg", "뢴트게늄", "고체", "전이금속"), (112, "Cn", "코페르니슘", "고체", "전이금속"),
    (113, "Nh", "니호늄", "고체", "전이후금속"), (114, "Fl", "플레로븀", "고체", "전이후금속"),
    (115, "Mc", "모스코븀", "고체", "전이후금속"), (116, "Lv", "리버모륨", "고체", "전이후금속"),
    (117, "Ts", "테네신", "고체", "할로젠"), (118, "Og", "오가네손", "기체", "비활성기체")
]

# ==========================================
# 📖 풍부한 실전 한방 단어 사전 데이터
# ==========================================
RICH_KILLER_DICTIONARY = {
    "가": [("가돌리늄", "화학원소 (64번) - '늄'으로 끝나 방어 불가"), ("가녘", "가장자리/끝을 뜻하는 고어 - '녘' 공격"), ("갈륨", "화학원소 (31번) - 대표 한방단어"), ("가솔린", "연료 - '린' 공격")],
    "나": [("나트륨", "화학원소 (11번) - 대표적인 한방 공격단어"), ("나이오븀", "화학원소 (41번) - '븀' 공격 단어"), ("나프탈렌", "방충제 - '렌' 공격"), ("나이지리아", "국가명 - '아' 공격")],
    "다": [("다름슈타튬", "화학원소 (110번) - '튬' 공격 단어"), ("디스프로슘", "화학원소 (66번) - '슘' 공격 단어"), ("디클로로메탄", "화학물질 - '탄' 공격")],
    "라": [("라듐", "화학원소 (88번) - '듐' 한방단어"), ("라돈", "화학원소 (86번) - '돈' 공격"), ("란타넘", "화학원소 (57번) - '넘' 공격"), ("라이프치히", "독일 지명 - '히' 공격")],
    "마": [("마그네슘", "화학원소 (12번) - 강력한 '슘' 공격"), ("마이트너륨", "화학원소 (109번) - '륨' 공격"), ("마요네즈", "식품 - '즈' 공격")],
    "바": [("바륨", "화학원소 (56번) - '륨' 한방단어"), ("바나듐", "화학원소 (23번) - '듐' 한방단어"), ("버클륨", "화학원소 (97번) - '륨' 한방단어"), ("바셀린", "보습제 - '린' 공격")],
    "사": [("사마륨", "화학원소 (62번) - '륨' 한방단어"), ("산기슭", "산의 밑자락 - 강력한 '슭' 한방단어"), ("사이클로트론", "입자가속기 - '론' 공격")],
    "아": [("알루미늄", "화학원소 (13번) - 대표 한방 단어"), ("아인슈타이늄", "화학원소 (99번) - '늄' 한방단어"), ("아스타틴", "화학원소 (85번) - '틴' 공격"), ("아메리슘", "화학원소 (95번) - '슘' 공격")],
    "자": [("지르코늄", "화학원소 (40번) - '늄' 한방단어"), ("저마늄", "화학원소 (32번) - '늄' 한방단어"), ("자일리톨", "감미료 - '톨' 공격")],
    "차": [("차표", "승차권 - '표' 공격"), ("차이코프스키", "인물명 - '키' 공격"), ("차지키", "음식 - '키' 공격")],
    "카": [("칼륨", "화학원소 (19번) - '륨' 한방단어"), ("칼슘", "화학원소 (20번) - '슘' 한방단어"), ("카드뮴", "화학원소 (48번) - '뮴' 한방단어"), ("캘리포늄", "화학원소 (98번) - '늄' 한방단어")],
    "타": [("티타늄", "화학원소 (22번) - '늄' 한방단어"), ("테크네튬", "화학원소 (43번) - '튬' 한방단어"), ("텔루륨", "화학원소 (52번) - '륨' 한방단어"), ("테르븀", "화학원소 (65번) - '븀' 한방단어")],
    "파": [("팔라듐", "화학원소 (46번) - '듐' 한방단어"), ("플루토늄", "화학원소 (94번) - '늄' 한방단어"), ("프랑슘", "화학원소 (87번) - '슘' 한방단어"), ("페르븀", "화학원소 (100번) - '븀' 한방단어")],
    "하": [("하프늄", "화학원소 (72번) - '늄' 한방단어"), ("하슘", "화학원소 (108번) - '슘' 한방단어"), ("해질녘", "노을 지는 때 - 강력한 '녘' 한방단어"), ("홀뮴", "화학원소 (67번) - '뮴' 한방단어")]
}

ALL_KILLER_WORDS = [item[0] for words in RICH_KILLER_DICTIONARY.values() for item in words]

# ==========================================
# 🎮 게임 로직 함수
# ==========================================
STARTING_WORDS = ["바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "무지개", "사과", "바나나", "강아지", "고양이", "태양"]

def is_valid_korean_word(word):
    url = f"https://dict.naver.com/api/search/autocomplete?query={word}&st=11111"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            for item_group in items:
                for item in item_group:
                    if item[0][0] == word:
                        return True
    except Exception:
        pass
    return True

def get_allowed_initials(char):
    allowed = [char]
    code = ord(char) - 0xAC00
    if 0 <= code <= 11172:
        initial = code // (21 * 28)
        medial = (code % (21 * 28)) // 28
        final = code % 28
        if initial == 2 and medial in [2, 6, 8, 12, 18, 20]:
            allowed.append(chr(0xAC00 + (11 * 21 * 28) + (medial * 28) + final))
        elif initial == 5:
            if medial in [0, 1, 4, 7, 9, 14, 15, 16, 17, 21]:
                allowed.append(chr(0xAC00 + (2 * 21 * 28) + (medial * 28) + final))
            else:
                allowed.append(chr(0xAC00 + (11 * 21 * 28) + (medial * 28) + final))
    return allowed

def get_bot_response_word(start_chars, used_words, difficulty="보통"):
    clean_used = [w.strip() for w in used_words]
    candidates = []
    
    for sc in start_chars:
        url = f"https://dict.naver.com/api/search/autocomplete?query={sc}&st=11111"
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                for item_group in items:
                    for item in item_group:
                        w = item[0][0].strip()
                        if len(w) >= 2 and w[0] in start_chars and w not in clean_used:
                            if difficulty != "매우 어려움" and w in ALL_KILLER_WORDS:
                                continue
                            candidates.append(w)
        except Exception:
            pass

    candidates = list(set(candidates))
    if not candidates:
        return None

    if difficulty == "쉬움":
        short_words = [w for w in candidates if len(w) == 2]
        return random.choice(short_words) if short_words else random.choice(candidates)
    elif difficulty == "매우 어려움":
        killer = [w for w in candidates if w in ALL_KILLER_WORDS]
        return random.choice(killer) if killer else random.choice(candidates)
    else:
        return random.choice(candidates)

def record_game_result(is_win, reason, final_score):
    st.session_state.stats["total_games"] += 1
    if is_win: st.session_state.stats["wins"] += 1
    else: st.session_state.stats["losses"] += 1

    if final_score > st.session_state.high_score:
        st.session_state.high_score = final_score

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.history.insert(0, {
        "time": now_str,
        "result": "승리 🏆" if is_win else "패배 ❌",
        "reason": reason,
        "score": final_score
    })
    save_user_data()

def reset_game():
    first_word = random.choice(STARTING_WORDS)
    st.session_state.chat_history = [
        {"role": "bot", "text": f"안녕! 나랑 끝말잇기 한판 하자! 🎈\n첫 단어는 **'{first_word}'**이야! **'{first_word[-1]}'**(으)로 시작해줘!"}
    ]
    st.session_state.last_word = first_word
    st.session_state.used_words = [first_word]
    st.session_state.game_over = False
    st.session_state.turn_start_time = time.time()

if "chat_history" not in st.session_state:
    reset_game()

# ==========================================
# 📌 대형 사이드바 (상단 포인트 전용 표시)
# ==========================================
st.sidebar.markdown(f"""
<div class="point-badge">
    💰 {st.session_state.points} P
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("메뉴 이동", [
    "💬 끝말잇기 톡", 
    "👤 내 프로필",
    "🛒 상점 (꾸미기)",
    "🧪 원소 주기율표",
    "📖 한방단어 대사전"
])

# ==========================================
# 1. 💬 끝말잇기 톡
# ==========================================
if menu == "💬 끝말잇기 톡":
    st.title(f"💬 {st.session_state.equipped_title} 의 끝말잇기")

    game_mode = st.sidebar.radio("🎮 게임 모드:", ["☕ 일반 모드", "⏱️ 타임어택 모드"])
    normal_difficulty = "보통"
    
    if game_mode == "☕ 일반 모드":
        normal_difficulty = st.sidebar.select_slider("⚙️ 난이도:", options=["쉬움", "보통", "어려움", "매우 어려움"], value="보통")
    else:
        difficulty = st.sidebar.selectbox("타임어택 난이도", ["🟢 쉬움 (15초)", "🟡 보통 (10초)", "🔴 어려움 (5초)"])
        time_limit = 15 if "쉬움" in difficulty else 10 if "보통" in difficulty else 5
        elapsed_time = time.time() - st.session_state.turn_start_time
        remaining_time = max(0, int(time_limit - elapsed_time))
        
        if not st.session_state.game_over:
            st.warning(f"⏱️ 남은 시간: **{remaining_time}초**")
            if remaining_time <= 0:
                st.session_state.game_over = True
                st.session_state.chat_history.append({"role": "bot", "text": "⏰ 시간 초과! 내가 이겼어! 😜"})
                record_game_result(False, "타임어택 시간 초과", st.session_state.score)
                st.rerun()

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["text"])
        else:
            st.chat_message("assistant", avatar="🤖").write(msg["text"])

    last_char = st.session_state.last_word[-1]
    allowed_chars = get_allowed_initials(last_char)
    allowed_str = '/'.join(allowed_chars)

    if not st.session_state.game_over:
        user_input = st.chat_input(f"'{allowed_str}'(으)로 시작하는 단어 입력...")
        if user_input:
            user_input_clean = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "text": user_input_clean})

            chat_keywords = ["두 번", "두번", "중복", "또", "아까", "썼잖아", "말했어", "반칙"]
            is_conversation = (" " in user_input_clean) or any(kw in user_input_clean for kw in chat_keywords)

            if is_conversation and len(user_input_clean) > 3:
                used_list = st.session_state.used_words
                has_bot_duplicated = len(used_list) != len(set(used_list))

                if any(kw in user_input_clean for kw in ["두 번", "두번", "중복", "또"]):
                    if has_bot_duplicated:
                        st.session_state.chat_history.append({"role": "bot", "text": "헐... 진짜 중복이었네?! 😭 네 승리! 🎉 (+50P)"})
                        st.session_state.score += 30
                        st.session_state.points += 50
                        st.session_state.game_over = True
                        record_game_result(True, "상대 봇 중복 적발 승리", st.session_state.score)
                    else:
                        st.session_state.chat_history.append({"role": "bot", "text": f"어?? 나 중복 안 썼는데?! 😜 **'{allowed_str}'**(으)로 이어서 입력해줘!"})
                else:
                    st.session_state.chat_history.append({"role": "bot", "text": f"게임 계속하자! 다음 차례는 **'{allowed_str}'**!"})
            
            else:
                if len(user_input_clean) < 2:
                    st.session_state.chat_history.append({"role": "bot", "text": "두 글자 이상의 단어만 쓸 수 있어! ❌"})
                    st.session_state.game_over = True
                    record_game_result(False, "한 글자 입력 실수", st.session_state.score)
                elif user_input_clean[0] not in allowed_chars:
                    st.session_state.chat_history.append({"role": "bot", "text": f"글자가 맞지 않아! **'{allowed_str}'**(으)로 시작해줘! 😜"})
                    st.session_state.game_over = True
                    record_game_result(False, "첫 글자 불일치", st.session_state.score)
                elif user_input_clean in st.session_state.used_words:
                    st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'**은(는) 중복 단어야! 패배! ㅋㅋㅋ"})
                    st.session_state.game_over = True
                    record_game_result(False, "중복 단어 사용", st.session_state.score)
                elif not is_valid_korean_word(user_input_clean):
                    st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'**은(는) 사전에 없는 단어야! 😅"})
                    st.session_state.game_over = True
                    record_game_result(False, "존재하지 않는 단어 사용", st.session_state.score)
                else:
                    st.session_state.used_words.append(user_input_clean)
                    st.session_state.last_word = user_input_clean

                    if user_input_clean in ALL_KILLER_WORDS:
                        st.session_state.chat_history.append({"role": "bot", "text": f"와... **'{user_input_clean}'**?! 😱 강력한 한방단어라 받아칠 수 없어! 네 승리! 🎉 (+100P)"})
                        st.session_state.score += 50
                        st.session_state.points += 100
                        st.session_state.game_over = True
                        record_game_result(True, f"한방단어('{user_input_clean}') 성공", st.session_state.score)
                        st.balloons()
                    else:
                        bot_next_chars = get_allowed_initials(user_input_clean[-1])
                        bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, normal_difficulty)

                        if bot_word is None:
                            st.session_state.chat_history.append({"role": "bot", "text": f"아... **'{user_input_clean[-1]}'**(으)로 시작하는 단어가 없어! 네가 이겼어! 👏 (+50P)"})
                            st.session_state.score += 30
                            st.session_state.points += 50
                            st.session_state.game_over = True
                            record_game_result(True, "AI 단어 고갈 승리", st.session_state.score)
                        else:
                            st.session_state.used_words.append(bot_word)
                            st.session_state.last_word = bot_word
                            st.session_state.score += 10
                            st.session_state.points += 5
                            st.session_state.turn_start_time = time.time()
                            save_user_data()

                            st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'** 받아서 난 **'{bot_word}'**! 다음은 **'{bot_word[-1]}'**!"})
            st.rerun()

    if st.session_state.game_over:
        st.button("🔄 새로운 단어로 다시 시작!", on_click=reset_game)

# ==========================================
# 2. 👤 내 프로필
# ==========================================
elif menu == "👤 내 프로필":
    st.title("👤 내 플레이어 프로필")
    
    stats = st.session_state.stats
    total, wins, losses = stats["total_games"], stats["wins"], stats["losses"]
    win_rate = (wins / total * 100) if total > 0 else 0.0
    percentile = calculate_percentile()

    frame_style = "border: 2px solid #555; background: #1e1e1e;"
    if st.session_state.equipped_frame == "🔥 불타는 아우라 프레임":
        frame_style = "border: 3px solid #ff4500; box-shadow: 0 0 20px #ff4500; background: linear-gradient(135deg, #1f0d08, #3a150d);"
    elif st.session_state.equipped_frame == "💎 다이아몬드 프레임":
        frame_style = "border: 3px solid #00ffff; box-shadow: 0 0 20px #00ffff; background: linear-gradient(135deg, #091f2c, #0a334a);"
    elif st.session_state.equipped_frame == "🌌 은하수 아우라 프레임":
        frame_style = "border: 3px solid #a855f7; box-shadow: 0 0 20px #a855f7; background: linear-gradient(135deg, #1e0b36, #3b0764);"

    st.markdown(f"""
    <div style="padding: 30px; border-radius: 20px; {frame_style} text-align: center; margin-bottom: 25px;">
        <div style="font-size: 65px; margin-bottom: 5px;">{st.session_state.equipped_avatar.split()[0]}</div>
        <div style="font-size: 16px; font-weight: bold; color: #ffd700; background: rgba(255,215,0,0.15); display: inline-block; padding: 6px 16px; border-radius: 12px; margin-bottom: 10px;">
            {st.session_state.equipped_title}
        </div>
        <h1 style="margin: 5px 0; color: #ffffff;">{st.session_state.equipped_avatar.split()[1] if len(st.session_state.equipped_avatar.split()) > 1 else '플레이어'}</h1>
        <div style="font-size: 18px; color: #38bdf8; font-weight: bold; margin-bottom: 20px;">
            📈 랭킹 평가: {percentile}
        </div>
        <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 20px 0;">
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
                <div style="font-size: 14px; color: #aaa;">전적</div>
                <div style="font-size: 22px; font-weight: bold; color: #fff;">{total}전 {wins}승 {losses}패</div>
            </div>
            <div>
                <div style="font-size: 14px; color: #aaa;">승률</div>
                <div style="font-size: 22px; font-weight: bold; color: #4ade80;">{win_rate:.1f}%</div>
            </div>
            <div>
                <div style="font-size: 14px; color: #aaa;">최고 점수</div>
                <div style="font-size: 22px; font-weight: bold; color: #facc15;">{st.session_state.high_score}점</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 🛒 상점 (꾸미기)
# ==========================================
elif menu == "🛒 상점 (꾸미기)":
    st.title("🛒 포인트 상점 & 꾸미기")
    st.write(f"현재 보유 포인트: **{st.session_state.points} P**")

    shop_items = {
        "🤖 메카 로봇": {"price": 100, "type": "아바타", "desc": "강력한 AI 로봇 프로필 아바타"},
        "🥷 전설의 닌자": {"price": 150, "type": "아바타", "desc": "신속한 단어 공격의 닌자"},
        "🐉 골드 드래곤": {"price": 250, "type": "아바타", "desc": "황금 빛을 품은 드래곤 아바타"},
        "🔥 불타는 아우라 프레임": {"price": 200, "type": "프레임", "desc": "붉게 불타는 프로필 아우라"},
        "💎 다이아몬드 프레임": {"price": 250, "type": "프레임", "desc": "영롱하게 빛나는 시안 빛 프레임"},
        "⚔️ 끝말잇기 패왕": {"price": 150, "type": "칭호", "desc": "상대를 순식간에 제압하는 칭호"},
        "🧠 두뇌 풀가동": {"price": 150, "type": "칭호", "desc": "모든 단어를 꿰뚫는 천재의 칭호"}
    }

    cols = st.columns(2)
    for idx, (item_name, info) in enumerate(shop_items.items()):
        with cols[idx % 2]:
            st.subheader(f"{item_name}")
            st.caption(f"분류: {info['type']} | 가격: {info['price']} P")
            st.write(info['desc'])
            
            is_owned = item_name in st.session_state.inventory
            if is_owned:
                st.success("이미 보유 중인 아이템")
            else:
                if st.button(f"구매하기 ({info['price']} P)", key=f"buy_{item_name}"):
                    if st.session_state.points >= info["price"]:
                        st.session_state.points -= info["price"]
                        st.session_state.inventory.append(item_name)
                        save_user_data()
                        st.success("구매 완료!")
                        st.rerun()
                    else:
                        st.error("포인트가 부족합니다!")
            st.divider()

# ==========================================
# 4. 🧪 원소 주기율표 (복원 및 강화)
# ==========================================
elif menu == "🧪 원소 주기율표":
    st.title("🧪 원소 주기율표 (Periodic Table)")
    st.caption("끝말잇기 핵심 한방 단어의 보고! 1번부터 118번까지 전체 원소 데이터입니다.")

    search_q = st.text_input("🔍 원소 이름 또는 기호 검색 (예: 나트륨, Na, 헬륨)", "")

    filtered_elements = [
        e for e in ELEMENTS_DATA 
        if search_q.lower() in e[1].lower() or search_q in e[2] or search_q == str(e[0])
    ]

    st.markdown("### 📌 끝말잇기 공격용 주요 원소")
    st.info("💡 끝말잇기 한방 단어 예시: **나트륨, 칼륨, 칼슘, 마그네슘, 베릴륨, 리튬, 티타늄, 가돌리늄, 알루미늄** 등")

    # 주기율표 카드 그리드 출력
    cols_per_row = 6
    for i in range(0, len(filtered_elements), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, elem in enumerate(filtered_elements[i:i+cols_per_row]):
            num, sym, name, state, category = elem
            is_killer = name.endswith(("륨", "늄", "튬", "슘", "뮴"))
            bg_color = "rgba(239, 68, 68, 0.2)" if is_killer else "rgba(255, 255, 255, 0.05)"
            border_color = "#ef4444" if is_killer else "#4b5563"

            with cols[j]:
                st.markdown(f"""
                <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 10px; padding: 12px; text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 11px; color: #888;">{num}</div>
                    <div style="font-size: 22px; font-weight: bold; color: #38bdf8;">{sym}</div>
                    <div style="font-size: 15px; font-weight: bold; margin-top: 4px;">{name}</div>
                    <div style="font-size: 11px; color: #aaa; margin-top: 4px;">{category} | {state}</div>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# 5. 📖 한방단어 대사전 (대폭 강화)
# ==========================================
elif menu == "📖 한방단어 대사전":
    st.title("📖 실전 끝말잇기 한방단어 대사전")
    st.caption("상대방을 한 번에 제압할 수 있는 강력한 끝단어 공격 목록입니다.")

    consonants = list(RICH_KILLER_DICTIONARY.keys())
    tabs = st.tabs(consonants)

    for idx, con in enumerate(consonants):
        with tabs[idx]:
            st.subheader(f"📌 '{con}' 초성 시작 한방 단어")
            words_list = RICH_KILLER_DICTIONARY[con]
            
            for word, desc in words_list:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"💥 **{word}**")
                with col2:
                    st.caption(desc)
                st.divider()
