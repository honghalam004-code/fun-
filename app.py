import streamlit as st
import requests
import time
import random
import json
import os
from datetime import datetime

st.set_page_config(page_title="친한친구 끝말잇기 톡", page_icon="💬", layout="wide")

# ==========================================
# 💾 데이터 영구 저장 및 불러오기
# ==========================================
SAVE_FILE = "user_data.json"

def load_user_data():
    default_data = {
        "user_name": "플레이어",
        "points": 500,
        "score": 0,
        "high_score": 0,
        "inventory": ["🐣 끝말잇기 병아리", "⚡ 뇌섹남", "기본 프레임"],
        "equipped_theme": "기본",
        "equipped_avatar": "⚡ 뇌섹남",
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
        "user_name": st.session_state.user_name,
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
    st.session_state.user_name = saved_data["user_name"]
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
# 🎨 사이드바 메뉴 대형화 CSS
# ==========================================
st.markdown("""
<style>
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
# 🧪 백업 단어 사적 (API 장애 대응용)
# ==========================================
BACKUP_DICTIONARY = {
    "자": ["자전거", "자동차", "자연", "자유", "자석", "자라", "자두", "자존심", "자물쇠", "자주색"],
    "가": ["가방", "가수", "가구", "가을", "가면", "가족", "가위"],
    "나": ["나비", "나무", "나눔", "나라", "나침반"],
    "다": ["다람쥐", "다리", "다리미", "다이아몬드"],
    "라": ["라디오", "라면", "라이터", "라일락"],
    "마": ["마술", "마을", "마이크", "마라톤"],
    "바": ["바다", "바나나", "바람", "바구니"],
    "사": ["사과", "사자", "사진", "사탕"],
    "아": ["아침", "안경", "아기", "악기"],
    "차": ["차표", "차가운", "차선"],
    "카": ["카메라", "카페", "카레"],
    "타": ["타이어", "타악기", "타월"],
    "파": ["파도", "파이프", "파란색"],
    "하": ["하늘", "하모니카", "하천"]
}

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

CONSONANT_KILLER_DICTIONARY = {
    "ㄱ": [("가돌리늄", "원소번호 64번 / 대표적인 '늄' 한방 단어"), ("갈륨", "원소번호 31번 / 강력한 '륨' 한방 단어"), ("기슭", "끝말잇기 최강 공격 단어 ('슭')"), ("곬", "물길이 한쪽으로 트인 줄기 ('곬')")],
    "ㄴ": [("나트륨", "원소번호 11번 / 대표적인 '륨' 공격"), ("나이오븀", "원소번호 41번 / '븀' 공격 단어"), ("녘", "해질녘/동녘 등에 쓰이는 강력한 한방 단어"), ("늧", "앞날의 징조를 뜻하는 단어 ('늧')")],
    "ㄷ": [("다름슈타튬", "원소번호 110번 / '튬' 공격 단어"), ("디스프로슘", "원소번호 66번 / '슘' 공격 단어"), ("듐", "화학 단위 또는 합성어로 방어 불가"), ("뎄", "어미 활용형 한방 단어")],
    "ㄹ": [("라듐", "원소번호 88번 / '듐' 한방 단어"), ("라돈", "원소번호 86번 / '돈' 공격 단어"), ("란타넘", "원소번호 57번 / '넘' 공격 단어"), ("릇", "그릇의 고어로 사용되는 한방 단어")],
    "ㅁ": [("마그네슘", "원소번호 12번 / 강력한 '슘' 공격"), ("마이트너륨", "원소번호 109번 / '륨' 한방 단어"), ("뮴", "화학 원소 어미 단어")],
    "ㅂ": [("바륨", "원소번호 56번 / '륨' 한방 단어"), ("바나듐", "원소번호 23번 / '듐' 한방 단어"), ("버클륨", "원소번호 97번 / '륨' 한방 단어"), ("븀", "화학 원소 어미 단어")],
    "ㅅ": [("사마륨", "원소번호 62번 / '륨' 한방 단어"), ("산기슭", "산의 밑자락 / 대표 한방 단어"), ("스트론튬", "원소번호 38번 / '튬' 한방 단어"), ("슭", "방어 불가 초강력 한방 끝문자")],
    "ㅇ": [("알루미늄", "원소번호 13번 / 대표 한방 단어"), ("아인슈타이늄", "원소번호 99번 / '늄' 한방 단어"), ("아메리슘", "원소번호 95번 / '슘' 한방 단어"), ("앙증", "어질고 귀여운 느낌 ('증')")],
    "ㅈ": [("지르코늄", "원소번호 40번 / '늄' 한방 단어"), ("저마늄", "원소번호 32번 / '늄' 한방 단어"), ("즙", "과일이나 채소를 짠 즙 ('즙')")],
    "ㅊ": [("차표", "승차권 ('표')"), ("차이코프스키", "인물명 ('키')"), ("츰", "‘즈음’의 옛말 방어 불가 단어")],
    "ㅋ": [("칼륨", "원소번호 19번 / '륨' 한방 단어"), ("칼슘", "원소번호 20번 / '슘' 한방 단어"), ("카드뮴", "원소번호 48번 / '뮴' 한방 단어"), ("캘리포늄", "원소번호 98번 / '늄' 한방 단어")],
    "ㅌ": [("티타늄", "원소번호 22번 / '늄' 한방 단어"), ("테크네튬", "원소번호 43번 / '튬' 한방 단어"), ("텔루륨", "원소번호 52번 / '륨' 한방 단어"), ("테르븀", "원소번호 65번 / '븀' 한방 단어")],
    "ㅍ": [("팔라듐", "원소번호 46번 / '듐' 한방 단어"), ("플루토늄", "원소번호 94번 / '늄' 한방 단어"), ("프랑슘", "원소번호 87번 / '슘' 한방 단어"), ("페르븀", "원소번호 100번 / '븀' 한방 단어")],
    "ㅎ": [("하프늄", "원소번호 72번 / '늄' 한방 단어"), ("하슘", "원소번호 108번 / '슘' 한방 단어"), ("해질녘", "노을 지는 시간 / 강력한 '녘' 한방 단어"), ("홀뮴", "원소번호 67번 / '뮴' 한방 단어")]
}

ALL_KILLER_WORDS = [item[0] for words in CONSONANT_KILLER_DICTIONARY.values() for item in words]

# ==========================================
# 🎮 게임 로직 함수
# ==========================================
STARTING_WORDS = ["바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "무지개", "사과", "바나나", "태양", "우주"]

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
    
    # 1. 네이버 API 검색
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

    # 2. API 실패/응답 없음 대비 백업 사적 단어 추가
    for sc in start_chars:
        if sc in BACKUP_DICTIONARY:
            for w in BACKUP_DICTIONARY[sc]:
                if w not in clean_used:
                    candidates.append(w)

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
        {"role": "bot", "text": f"안녕 {st.session_state.user_name}! 나랑 끝말잇기 한판 하자! 🎈\n첫 단어는 **'{first_word}'**이야! **'{first_word[-1]}'**(으)로 시작해줘!"}
    ]
    st.session_state.last_word = first_word
    st.session_state.used_words = [first_word]
    st.session_state.game_over = False
    st.session_state.turn_start_time = time.time()

if "chat_history" not in st.session_state:
    reset_game()

# ==========================================
# 📌 대형 사이드바
# ==========================================
st.sidebar.markdown(f"""
<div class="point-badge">
    💰 {st.session_state.points} P
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("메뉴 이동", [
    "💬 끝말잇기 톡", 
    "👤 내 프로필",
    "🛒 고급 상점",
    "🧪 원소 주기율표",
    "📖 초성 한방단어 대사전"
])

# ==========================================
# 1. 💬 끝말잇기 톡
# ==========================================
if menu == "💬 끝말잇기 톡":
    st.title(f"💬 {st.session_state.user_name} ({st.session_state.equipped_title}) 의 끝말잇기")

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
    
    # 닉네임 입력/수정 영역
    st.subheader("✍️ 닉네임 설정")
    new_name = st.text_input("사용할 닉네임을 입력하세요:", value=st.session_state.user_name)
    if new_name != st.session_state.user_name:
        st.session_state.user_name = new_name.strip() if new_name.strip() else "플레이어"
        save_user_data()
        st.success(f"닉네임이 **'{st.session_state.user_name}'**(으)로 변경되었습니다!")

    st.divider()

    stats = st.session_state.stats
    total, wins, losses = stats["total_games"], stats["wins"], stats["losses"]
    win_rate = (wins / total * 100) if total > 0 else 0.0
    percentile = calculate_percentile()

    frame_style = "border: 2px solid #555; background: #1e1e1e;"
    if "불타는" in st.session_state.equipped_frame:
        frame_style = "border: 3px solid #ff4500; box-shadow: 0 0 20px #ff4500; background: linear-gradient(135deg, #1f0d08, #3a150d);"
    elif "다이아몬드" in st.session_state.equipped_frame:
        frame_style = "border: 3px solid #00ffff; box-shadow: 0 0 20px #00ffff; background: linear-gradient(135deg, #091f2c, #0a334a);"
    elif "은하수" in st.session_state.equipped_frame:
        frame_style = "border: 3px solid #a855f7; box-shadow: 0 0 20px #a855f7; background: linear-gradient(135deg, #1e0b36, #3b0764);"
    elif "황금" in st.session_state.equipped_frame:
        frame_style = "border: 3px solid #facc15; box-shadow: 0 0 25px #facc15; background: linear-gradient(135deg, #2a2004, #423207);"

    st.markdown(f"""
    <div style="padding: 30px; border-radius: 20px; {frame_style} text-align: center; margin-bottom: 25px;">
        <div style="font-size: 65px; margin-bottom: 5px;">{st.session_state.equipped_avatar.split()[0]}</div>
        <div style="font-size: 16px; font-weight: bold; color: #ffd700; background: rgba(255,215,0,0.15); display: inline-block; padding: 6px 16px; border-radius: 12px; margin-bottom: 10px;">
            {st.session_state.equipped_title}
        </div>
        <h1 style="margin: 5px 0; color: #ffffff;">{st.session_state.user_name}</h1>
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
# 3. 🛒 대규모 고급 상점
# ==========================================
elif menu == "🛒 고급 상점":
    st.title("🛒 고급 프리미엄 상점")
    st.write(f"보유 포인트: **{st.session_state.points} P**")

    shop_categories = {
        "👥 아바타": [
            ("⚡ 뇌섹남", 100, "지적인 포스의 명쾌한 두뇌파 아바타"),
            ("👑 단어의 제왕", 200, "모든 단어를 섭렵한 마스터 아바타"),
            ("🐉 골드 드래곤", 300, "압도적인 위엄을 자랑하는 드래곤"),
            ("🤖 하이테크 사이보그", 150, "오차 없는 계산 능력의 로봇"),
            ("🧙‍♂️ 대마법사", 250, "단어를 자유자재로 다루는 아바타"),
            ("🥷 섀도우 닌자", 180, "바람처럼 빠른 한방 단어의 달인")
        ],
        "🏷️ 칭호": [
            ("⚡ 뇌섹남", 100, "언어 감각이 뛰어난 천재 플레이어"),
            ("⚔️ 끝말잇기 패왕", 150, "상대를 단번에 무너뜨리는 기세"),
            ("🧠 걸어다니는 국어사전", 200, "단어 고갈을 모르는 보물창고"),
            ("🔥 불패의 마스터", 250, "연승 행진을 이어가는 최고의 칭호"),
            ("🧪 원소의 연금술사", 180, "화학 원소 공격 전문 플레이어")
        ],
        "🖼️ 테두리 프레임": [
            ("🔥 불타는 아우라 프레임", 200, "붉게 타오르는 정열적인 프로필"),
            ("💎 다이아몬드 프레임", 250, "영롱하고 반짝이는 시안빛 테두리"),
            ("🌌 은하수 아우라 프레임", 300, "신비로운 보라색 네온 프레임"),
            ("👑 황금 왕관 프레임", 400, "황금빛 화려함이 폭발하는 VIP 프레임")
        ]
    }

    tabs = st.tabs(list(shop_categories.keys()))

    for tab_idx, (cat_name, items) in enumerate(shop_categories.items()):
        with tabs[tab_idx]:
            cols = st.columns(2)
            for idx, (item_name, price, desc) in enumerate(items):
                with cols[idx % 2]:
                    st.markdown(f"### {item_name}")
                    st.caption(f"가격: **{price} P**")
                    st.write(desc)
                    
                    is_owned = item_name in st.session_state.inventory
                    if is_owned:
                        st.info("✓ 이미 보유중")
                        if "아바타" in cat_name and st.session_state.equipped_avatar != item_name:
                            if st.button(f"착용하기", key=f"eq_av_{item_name}"):
                                st.session_state.equipped_avatar = item_name
                                save_user_data()
                                st.rerun()
                        elif "칭호" in cat_name and st.session_state.equipped_title != item_name:
                            if st.button(f"착용하기", key=f"eq_ti_{item_name}"):
                                st.session_state.equipped_title = item_name
                                save_user_data()
                                st.rerun()
                        elif "프레임" in cat_name and st.session_state.equipped_frame != item_name:
                            if st.button(f"착용하기", key=f"eq_fr_{item_name}"):
                                st.session_state.equipped_frame = item_name
                                save_user_data()
                                st.rerun()
                    else:
                        if st.button(f"구매 ({price} P)", key=f"buy_{item_name}"):
                            if st.session_state.points >= price:
                                st.session_state.points -= price
                                st.session_state.inventory.append(item_name)
                                save_user_data()
                                st.success("구매 성공!")
                                st.rerun()
                            else:
                                st.error("포인트가 부족합니다!")
                    st.divider()

# ==========================================
# 4. 🧪 원소 주기율표
# ==========================================
elif menu == "🧪 원소 주기율표":
    st.title("🧪 원소 주기율표 (Periodic Table)")
    st.caption("1번 수소부터 118번 오가네손까지 전체 원소 데이터입니다.")

    search_q = st.text_input("🔍 원소 검색 (예: 나트륨, Na, 헬륨)", "")

    filtered_elements = [
        e for e in ELEMENTS_DATA 
        if search_q.lower() in e[1].lower() or search_q in e[2] or search_q == str(e[0])
    ]

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
# 5. 📖 초성 한방단어 대사전 (ㄱ~ㅎ)
# ==========================================
elif menu == "📖 초성 한방단어 대사전":
    st.title("📖 ㄱ~ㅎ 초성 기반 실전 한방단어 대사전")
    st.caption("모든 자음별 필살 단어 모음집입니다.")

    consonants = list(CONSONANT_KILLER_DICTIONARY.keys())
    tabs = st.tabs(consonants)

    for idx, con in enumerate(consonants):
        with tabs[idx]:
            st.subheader(f"📌 '{con}' 초성으로 검색되는 한방 공격 단어")
            words_list = CONSONANT_KILLER_DICTIONARY[con]
            
            for word, desc in words_list:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"💥 **{word}**")
                with col2:
                    st.caption(desc)
                st.divider()
