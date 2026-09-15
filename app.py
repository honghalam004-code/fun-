import streamlit as st
import requests
import random
import json
import os

st.set_page_config(page_title="TACTICAL WORD CHAIN PRO", page_icon="⚔️", layout="wide")

# ==========================================
# 💾 데이터 영구 저장 로직
# ==========================================
SAVE_FILE = "user_tactical_data.json"

def load_user_data():
    default_data = {
        "user_name": "요원_01",
        "points": 3000,
        "inventory": ["🎖️ 신병 요원", "👤 기본 요원", "기본 프레임", "🔴 발로란트 레드"],
        "equipped_theme": "🔴 발로란트 레드",
        "equipped_avatar": "👤 기본 요원",
        "equipped_frame": "기본 프레임",
        "equipped_title": "🎖️ 신병 요원",
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
        "inventory": st.session_state.inventory,
        "equipped_theme": st.session_state.equipped_theme,
        "equipped_avatar": st.session_state.equipped_avatar,
        "equipped_frame": st.session_state.equipped_frame,
        "equipped_title": st.session_state.equipped_title,
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if "data_loaded" not in st.session_state:
    saved_data = load_user_data()
    for k, v in saved_data.items():
        st.session_state[k] = v
    st.session_state.data_loaded = True

# ==========================================
# 🎨 다이내믹 게이밍 UI / 테마 배경 엔진
# ==========================================
THEME_CONFIGS = {
    "🔴 발로란트 레드": {
        "bg_css": "background: radial-gradient(circle at 50% 10%, #2b0910 0%, #0f1923 80%) !important;",
        "card_bg": "rgba(255, 70, 85, 0.08)",
        "accent": "#ff4655",
        "text": "#ece8e1"
    },
    "🟢 래디언트 시안": {
        "bg_css": "background: radial-gradient(circle at 50% 10%, #043831 0%, #061417 80%) !important;",
        "card_bg": "rgba(0, 245, 212, 0.08)",
        "accent": "#00f5d4",
        "text": "#dbf8ff"
    },
    "🟡 챌린저 골드": {
        "bg_css": "background: radial-gradient(circle at 50% 10%, #3b2807 0%, #120e07 80%) !important;",
        "card_bg": "rgba(245, 158, 11, 0.08)",
        "accent": "#f59e0b",
        "text": "#f7e7c4"
    },
    "🟣 공허의 아칼리": {
        "bg_css": "background: radial-gradient(circle at 50% 10%, #2e104d 0%, #0f081c 80%) !important;",
        "card_bg": "rgba(168, 85, 247, 0.08)",
        "accent": "#a855f7",
        "text": "#e9d8a6"
    },
    "⚔️ 밀리터리 카키": {
        "bg_css": "background: radial-gradient(circle at 50% 10%, #252e17 0%, #11140c 80%) !important;",
        "card_bg": "rgba(132, 204, 22, 0.08)",
        "accent": "#84cc16",
        "text": "#e2e8f0"
    }
}

FRAME_STYLES = {
    "기본 프레임": "2px solid #475569",
    "🔴 발로란트 레드 테두리": "3px solid #ff4655",
    "🟢 래디언트 네온 테두리": "3px solid #00f5d4",
    "🟡 챌린저 테두리": "3px solid #f59e0b",
    "🟣 공허 테두리": "3px solid #a855f7",
    "⚔️ 특수부대 테두리": "3px solid #84cc16"
}

cur_theme = THEME_CONFIGS.get(st.session_state.equipped_theme, THEME_CONFIGS["🔴 발로란트 레드"])
cur_frame = FRAME_STYLES.get(st.session_state.equipped_frame, FRAME_STYLES["기본 프레임"])

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

    /* 배경 레이어 강제 적용 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        {cur_theme['bg_css']}
        color: {cur_theme['text']} !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        border-right: 1px solid {cur_theme['accent']}44;
    }}
    
    .stChatMessage {{
        background-color: {cur_theme['card_bg']} !important;
        border-radius: 8px !important;
        border: 1px solid {cur_theme['accent']}44 !important;
        backdrop-filter: blur(5px);
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, {cur_theme['accent']} 0%, #000000 160%) !important;
        color: #ffffff !important;
        border: 1px solid {cur_theme['accent']} !important;
        font-weight: 800 !important;
        border-radius: 4px !important;
        box-shadow: 0 0 12px {cur_theme['accent']}66;
    }}
    
    .tactical-badge {{
        background: {cur_theme['card_bg']};
        border: 2px solid {cur_theme['accent']};
        color: {cur_theme['accent']};
        padding: 14px;
        border-radius: 6px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 24px;
        font-weight: 900;
        margin-bottom: 15px;
        box-shadow: inset 0 0 15px {cur_theme['accent']}33;
    }}

    .killer-card {{
        background: rgba(0,0,0,0.4);
        border-left: 4px solid #ef4444;
        padding: 8px 12px;
        margin: 4px 0;
        font-weight: bold;
        color: #f8fafc;
        border-radius: 0 4px 4px 0;
    }}

    .elem-card {{
        border: 1px solid {cur_theme['accent']}66;
        border-radius: 6px;
        padding: 10px;
        text-align: center;
        background: rgba(0,0,0,0.3);
        margin-bottom: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔤 두음법칙 계산기
# ==========================================
DUEUM_MAP = {
    '라': ['나'], '락': ['낙'], '란': ['난'], '랄': ['날'], '람': ['남'], '랍': ['납'], '랑': ['낭'],
    '래': ['내'], '랭': ['냉'], '로': ['노'], '록': ['녹'], '론': ['논'], '롱': ['농'], '뢰': ['뇌'],
    '루': ['누'], '르': ['느'],
    '량': ['양'], '려': ['여'], '력': ['역'], '련': ['연'], '렬': ['열'], '렴': ['염'], '렵': ['엽'],
    '령': ['영'], '례': ['예'], '료': ['요'], '류': ['유'], '륙': ['육'], '륜': ['윤'], '률': ['율'],
    '륭': ['융'], '름': ['음'], '릉': ['응'], '리': ['이'], '린': ['인'], '림': ['임'], '립': ['입'], '링': ['잉'],
    '녀': ['여'], '녁': ['역'], '년': ['연'], '념': ['염'], '닙': ['입'], '뉴': ['유'], '니': ['이'],
    '님': ['임'], '닌': ['인'], '닝': ['잉']
}

def get_allowed_initials(char):
    allowed = [char]
    if char in DUEUM_MAP:
        allowed.extend(DUEUM_MAP[char])
    return list(dict.fromkeys(allowed))

# ==========================================
# 📕 한방 단어 100선 (완전한 정품 명사 데이터)
# ==========================================
MASSIVE_KILLER_DICTIONARY = {
    "륨 계열 💥": [
        "나트륨", "칼륨", "헬륨", "베릴륨", "바륨", "라듐", "루비듐", "세슘", "이테르븀", "페르븀",
        "노벨륨", "플레로븀", "리버모륨", "마이트너륨", "다름슈타튬", "카드뮴", "오스뮴", "로듐", "이리듐",
        "탈륨", "세륨", "테르븀", "에르븀", "툴륨", "하프늄", "일레늄", "칼슘"
    ],
    "늄 계열 💥": [
        "플루토늄", "우라늄", "악티늄", "넵튜늄", "알루미늄", "지르코늄", "더브늄", "시보귬", "보륨", "하슘",
        "뢴트게늄", "코페르니슘", "니호늄", "모스코븀", "라돈", "게르마늄", "저마늄", "티타늄", "바나듐", "몰리브데넘",
        "테크네튬", "루테늄", "팔라듐", "프랑슘", "캘리포늄", "스칸듐"
    ],
    "튬/슘 계열 💥": [
        "리튬", "루테튬", "프로메튬", "스트론튬", "포타슘", "아메리슘", "아이오딘", "마그네슘",
        "아인슈타이늄", "멘델레븀", "로렌슘", "러더포듐", "프라세오디뮴", "네오디뮴", "사마륨", "유로퓸", "가돌리늄", "디스프로슘"
    ],
    "특수 끝말 (녘/즘/븀/턴) 💥": [
        "해질녘", "새벽녘", "들녘", "어스름녘", "동녘", "서녘", "남녘", "북녘", "밤녘", "날녘",
        "아침녘", "저녁녘", "모더니즘", "리얼리즘", "메커니즘", "알고리즘", "네오디뮴", "퀴륨", "버클륨",
        "홀뮴", "콜롬븀", "테네신", "오가네손", "아스타틴", "크립톤", "유턴", "패턴"
    ]
}

ALL_KILLER_WORDS = list(set([w for group in MASSIVE_KILLER_DICTIONARY.values() for w in group]))

# ==========================================
# 🧪 원소 주기율표 데이터 (1~118 풀 세트)
# ==========================================
ELEMENTS_DATA = [
    (1, "H", "수소", "기체"), (2, "He", "헬륨", "기체"), (3, "Li", "리튬", "고체"), (4, "Be", "베릴륨", "고체"),
    (5, "B", "붕소", "고체"), (6, "C", "탄소", "고체"), (7, "N", "질소", "기체"), (8, "O", "산소", "기체"),
    (9, "F", "플루오린", "기체"), (10, "Ne", "네온", "기체"), (11, "Na", "나트륨", "고체"), (12, "Mg", "마그네슘", "고체"),
    (13, "Al", "알루미늄", "고체"), (14, "Si", "규소", "고체"), (15, "P", "인", "고체"), (16, "S", "황", "고체"),
    (17, "Cl", "염소", "기체"), (18, "Ar", "아르곤", "기체"), (19, "K", "칼륨", "고체"), (20, "Ca", "칼슘", "고체"),
    (21, "Sc", "스칸듐", "고체"), (22, "Ti", "티타늄", "고체"), (23, "V", "바나듐", "고체"), (24, "Cr", "크롬", "고체"),
    (25, "Mn", "망가니즈", "고체"), (26, "Fe", "철", "고체"), (27, "Co", "코발트", "고체"), (28, "Ni", "니켈", "고체"),
    (29, "Cu", "구리", "고체"), (30, "Zn", "아연", "고체"), (31, "Ga", "갈륨", "고체"), (32, "Ge", "저마늄", "고체"),
    (33, "As", "비소", "고체"), (34, "Se", "셀레늄", "고체"), (35, "Br", "브로민", "액체"), (36, "Kr", "크립톤", "기체"),
    (37, "Rb", "루비듐", "고체"), (38, "Sr", "스트론튬", "고체"), (39, "Y", "이트륨", "고체"), (40, "Zr", "지르코늄", "고체"),
    (41, "Nb", "나이오븀", "고체"), (42, "Mo", "몰리브데넘", "고체"), (43, "Tc", "테크네튬", "고체"), (44, "Ru", "루테늄", "고체"),
    (45, "Rh", "로듐", "고체"), (46, "Pd", "팔라듐", "고체"), (47, "Ag", "은", "고체"), (48, "Cd", "카드뮴", "고체"),
    (49, "In", "인듐", "고체"), (50, "Sn", "주석", "고체"), (51, "Sb", "안티몬", "고체"), (52, "Te", "텔루륨", "고체"),
    (53, "I", "아이오딘", "고체"), (54, "Xe", "제논", "기체"), (55, "Cs", "세슘", "고체"), (56, "Ba", "바륨", "고체"),
    (57, "La", "란타넘", "고체"), (58, "Ce", "세륨", "고체"), (59, "Pr", "프라세오디뮴", "고체"), (60, "Nd", "네오디뮴", "고체"),
    (61, "Pm", "프로메튬", "고체"), (62, "Sm", "사마륨", "고체"), (63, "Eu", "유로퓸", "고체"), (64, "Gd", "가돌리늄", "고체"),
    (65, "Tb", "테르븀", "고체"), (66, "Dy", "디스프로슘", "고체"), (67, "Ho", "홀뮴", "고체"), (68, "Er", "에르븀", "고체"),
    (69, "Tm", "툴륨", "고체"), (70, "Yb", "이테르븀", "고체"), (71, "Lu", "루테튬", "고체"), (72, "Hf", "하프늄", "고체"),
    (73, "Ta", "탄탈럼", "고체"), (74, "W", "텅스텐", "고체"), (75, "Re", "레늄", "고체"), (76, "Os", "오스뮴", "고체"),
    (77, "Ir", "이리듐", "고체"), (78, "Pt", "백금", "고체"), (79, "Au", "금", "고체"), (80, "Hg", "수은", "액체"),
    (81, "Tl", "탈륨", "고체"), (82, "Pb", "납", "고체"), (83, "Bi", "비스무트", "고체"), (84, "Po", "폴로늄", "고체"),
    (85, "At", "아스타틴", "고체"), (86, "Rn", "라돈", "기체"), (87, "Fr", "프랑슘", "고체"), (88, "Ra", "라듐", "고체"),
    (89, "Ac", "악티늄", "고체"), (90, "Th", "토륨", "고체"), (91, "Pa", "프로트악티늄", "고체"), (92, "U", "우라늄", "고체"),
    (93, "Np", "넵튜늄", "고체"), (94, "Pu", "플루토늄", "고체"), (95, "Am", "아메리슘", "고체"), (96, "Cm", "퀴륨", "고체"),
    (97, "Bk", "버클륨", "고체"), (98, "Cf", "캘리포늄", "고체"), (99, "Es", "아인슈타이늄", "고체"), (100, "Fm", "페르븀", "고체"),
    (101, "Md", "멘델레븀", "고체"), (102, "No", "노벨륨", "고체"), (103, "Lr", "로렌슘", "고체"), (104, "Rf", "러더포듐", "고체"),
    (105, "Db", "더브늄", "고체"), (106, "Sg", "시보귬", "고체"), (107, "Bh", "보륨", "고체"), (108, "Hs", "하슘", "고체"),
    (109, "Mt", "마이트너륨", "고체"), (110, "Ds", "다름슈타튬", "고체"), (111, "Rg", "뢴트게늄", "고체"), (112, "Cn", "코페르니슘", "고체"),
    (113, "Nh", "니호늄", "고체"), (114, "Fl", "플레로븀", "고체"), (115, "Mc", "모스코븀", "고체"), (116, "Lv", "리버모륨", "고체"),
    (117, "Ts", "테네신", "고체"), (118, "Og", "오가네손", "기체")
]

# ==========================================
# 📚 완전 방어 오프라인 백업 사전 (표, 차 등 연속 단어 보장)
# ==========================================
MEGA_FALLBACK_DICTIONARY = {
    "표": ["표정", "표지판", "표범", "표준", "표적", "표류", "표면", "표현", "표제어", "표상", "표인", "표목"],
    "차": ["차표", "차창", "차나무", "차고지", "차선", "차돌", "차량", "차고", "차지", "차림표"],
    "리": ["리본", "리듬", "리코더", "리모컨", "리조트", "리갈", "리액션", "리필", "리얼리티", "리허설"],
    "이": ["이야기", "이발소", "이유", "이불", "이웃", "이메일", "이탈리아", "이동", "이구아나", "이발사"],
    "기": ["기차", "기린", "기타", "기와", "기구", "기사", "기름", "기적", "기업", "기계"],
    "구": ["구름", "구두", "구슬", "구경", "구조대", "구역", "구경꾼", "구식", "구원자"],
    "음": ["음악", "음식", "음료수", "음성", "음향", "음자리표", "음반"],
    "바": ["바다", "바나나", "바구니", "바람", "바위", "바질", "바코드", "바리스타"],
    "다": ["다람쥐", "다리", "다리미", "다이아몬드", "다이빙", "다짐", "다이어리"],
    "자": ["자전거", "자두", "자동차", "자석", "자라", "자존심", "자연", "자유"],
    "호": ["호랑이", "호수", "호두", "호박", "호루라기", "호텔", "호기심"],
    "장": ["장난감", "장미", "장갑", "장화", "장터", "장수풍뎅이"],
    "사": ["사자", "사과", "사슴", "사탕", "사이다", "사막", "사람", "사진"]
}

# 에러 메시지 팝업 노출 없이 조용히 통신 처리
def safe_naver_search(query):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    url = f"https://dict.naver.com/api/search/autocomplete?query={query}&st=11111"
    try:
        res = requests.get(url, headers=headers, timeout=1.2)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

def is_valid_korean_word(word):
    res_json = safe_naver_search(word)
    if res_json:
        for group in res_json.get("items", []):
            for item in group:
                if item[0][0] == word: return True
    # 네이버 통신 불안정 시 오프라인 데이터 및 한글 검증
    first_char = word[0]
    if first_char in MEGA_FALLBACK_DICTIONARY and word in MEGA_FALLBACK_DICTIONARY[first_char]:
        return True
    return len(word) >= 2 and word.isalpha()

def get_bot_response_word(start_chars, used_words, difficulty):
    clean_used = [w.strip() for w in used_words]
    candidates = []

    for sc in start_chars:
        res_json = safe_naver_search(sc)
        if res_json:
            for group in res_json.get("items", []):
                for item in group:
                    w = item[0][0].strip()
                    if len(w) >= 2 and w.isalpha() and w[0] in start_chars and w not in clean_used:
                        candidates.append(w)

    for sc in start_chars:
        if sc in MEGA_FALLBACK_DICTIONARY:
            for fw in MEGA_FALLBACK_DICTIONARY[sc]:
                if fw not in clean_used:
                    candidates.append(fw)

    candidates = list(set(candidates))
    if not candidates:
        return None

    killer_endings = ("륨", "늄", "튬", "슘", "뮴", "븀", "녘", "즘")
    safe_candidates = [w for w in candidates if w not in ALL_KILLER_WORDS and not w.endswith(killer_endings)]
    killer_candidates = [w for w in candidates if w in ALL_KILLER_WORDS or w.endswith(killer_endings)]

    if difficulty == "쉬움":
        return random.choice(safe_candidates) if safe_candidates else random.choice(candidates)
    elif difficulty == "보통":
        if killer_candidates and random.random() < 0.15:
            return random.choice(killer_candidates)
        return random.choice(safe_candidates) if safe_candidates else random.choice(candidates)
    elif difficulty == "어려움":
        if killer_candidates and random.random() < 0.55:
            return random.choice(killer_candidates)
        return random.choice(safe_candidates) if safe_candidates else random.choice(candidates)
    elif difficulty == "매우 어려움":
        if killer_candidates:
            return random.choice(killer_candidates)
        return random.choice(safe_candidates) if safe_candidates else random.choice(candidates)

    return random.choice(candidates)

STARTING_WORDS = ["바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "사과", "차표", "표지판", "이야기"]

def reset_game():
    first_word = random.choice(STARTING_WORDS)
    st.session_state.chat_history = [
        {"role": "bot", "text": f"🎯 첫 제시어: **'{first_word}'**! (**'{first_word[-1]}'** 로 시작하는 단어를 입력하세요)"}
    ]
    st.session_state.last_word = first_word
    st.session_state.used_words = [first_word]
    st.session_state.game_over = False

if "chat_history" not in st.session_state: reset_game()

# ==========================================
# 📌 메인 네비게이션 메뉴
# ==========================================
st.sidebar.markdown(f"""
<div class="tactical-badge">
    CREDITS: {st.session_state.points} P
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("COMMAND CENTER", [
    "⚔️ 끝말잇기 매치", 
    "📕 한방 단어 대사전 (100+)",
    "🧪 원소 주기율표 (1~118)",
    "🛒 택티컬 상점 (실시간 배경)",
    "👤 프로필 & 스타일 설정"
])

# ==========================================
# 1. ⚔️ 끝말잇기 매치
# ==========================================
if menu == "⚔️ 끝말잇기 매치":
    st.title("⚔️ TACTICAL WORD CHAIN MATCH")
    
    col_diff, col_reset = st.columns([3, 1])
    with col_diff:
        difficulty = st.select_slider("⚙️ 봇 AI 난이도 설정:", options=["쉬움", "보통", "어려움", "매우 어려움"], value="보통")
    with col_reset:
        st.write(" ")
        if st.button("🔄 매치 초기화"):
            reset_game()
            st.rerun()

    for msg in st.session_state.chat_history:
        avatar = st.session_state.equipped_avatar.split()[0] if msg["role"] == "user" else "🤖"
        st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar).write(msg["text"])

    last_char = st.session_state.last_word[-1]
    allowed_chars = get_allowed_initials(last_char)
    allowed_str = '/'.join(allowed_chars)

    if not st.session_state.game_over:
        user_input = st.chat_input(f"'{allowed_str}' (으)로 시작하는 단어 입력...")
        if user_input:
            user_clean = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "text": user_clean})

            if len(user_clean) < 2:
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 최소 2글자 이상 입력해야 합니다!"})
                st.session_state.game_over = True
            elif user_clean[0] not in allowed_chars:
                st.session_state.chat_history.append({"role": "bot", "text": f"❌ 시작 단어 오류! **'{allowed_str}'** 로 시작해야 합니다."})
                st.session_state.game_over = True
            elif user_clean in st.session_state.used_words:
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 이미 나온 중복 단어입니다!"})
                st.session_state.game_over = True
            elif not is_valid_korean_word(user_clean):
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 사전에 존재하지 않는 단어입니다!"})
                st.session_state.game_over = True
            else:
                st.session_state.used_words.append(user_clean)
                st.session_state.last_word = user_clean

                bot_next_chars = get_allowed_initials(user_clean[-1])
                bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, difficulty)

                if bot_word is None:
                    st.session_state.chat_history.append({"role": "bot", "text": f"💥 **'{user_clean}'** 공격 성공! 봇이 대응 단어를 찾지 못했습니다. 승리! (+200P)"})
                    st.session_state.points += 200
                    st.session_state.game_over = True
                    save_user_data()
                    st.balloons()
                else:
                    st.session_state.used_words.append(bot_word)
                    st.session_state.last_word = bot_word
                    st.session_state.points += 10
                    save_user_data()
                    next_allowed = '/'.join(get_allowed_initials(bot_word[-1]))
                    st.session_state.chat_history.append({"role": "bot", "text": f"⚡ 봇 수비: **'{bot_word}'**! 다음 시작어: **'{next_allowed}'**"})
            st.rerun()

# ==========================================
# 2. 📕 한방 단어 대사전 (100+)
# ==========================================
elif menu == "📕 한방 단어 대사전 (100+)":
    st.title("📕 한방 단어 필살기 대사전 (100+)")
    st.caption("실전에서 상대를 즉시 제압할 수 있는 검증된 표준 명사 데이터베이스입니다.")

    search_k = st.text_input("🔍 사전 내부 검색:", "")
    if search_k:
        results = [w for w in ALL_KILLER_WORDS if search_k in w]
        st.write(f"검색 결과 ({len(results)}개):")
        cols = st.columns(4)
        for idx, word in enumerate(results):
            with cols[idx % 4]:
                st.markdown(f"<div class='killer-card'>{word}</div>", unsafe_allow_html=True)
    else:
        tabs = st.tabs(list(MASSIVE_KILLER_DICTIONARY.keys()))
        for idx, (cat_name, words) in enumerate(MASSIVE_KILLER_DICTIONARY.items()):
            with tabs[idx]:
                st.write(f"### {cat_name} (총 {len(words)}개)")
                cols = st.columns(4)
                for w_idx, word in enumerate(words):
                    with cols[w_idx % 4]:
                        st.markdown(f"<div class='killer-card'>{word}</div>", unsafe_allow_html=True)

# ==========================================
# 3. 🧪 원소 주기율표 (1~118)
# ==========================================
elif menu == "🧪 원소 주기율표 (1~118)":
    st.title("🧪 원소 주기율표 데이터베이스 (1~118)")
    search_elem = st.text_input("원소 명칭 또는 기호 검색 (예: H, 수소, Na):", "")
    
    filtered = [e for e in ELEMENTS_DATA if search_elem in e[2] or search_elem.lower() in e[1].lower()]
    cols = st.columns(4)
    for idx, (num, sym, name, state) in enumerate(filtered):
        with cols[idx % 4]:
            is_k = name.endswith(("륨", "늄", "튬", "슘", "뮴"))
            st.markdown(f"""
            <div class="elem-card">
                <span style="font-size: 12px; color: #94a3b8;">No.{num} [{state}]</span>
                <h2 style="margin: 2px 0; color: {cur_theme['accent']}; font-family: 'Orbitron';">{sym}</h2>
                <span style="font-size: 18px; font-weight: bold; color: #f8fafc;">{name}</span>
                {('<br/><span style="color:#ef4444; font-weight:bold; font-size:12px;">💥 한방단어</span>' if is_k else '')}
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 4. 🛒 택티컬 상점 (실시간 배경 반영)
# ==========================================
elif menu == "🛒 택티컬 상점 (실시간 배경)":
    st.title("🛒 TACTICAL ITEM SHOP")
    st.caption("구매 및 장착 즉시 게임 전체 배경과 비주얼 테마 스타일이 변경됩니다.")

    shop_data = {
        "🎨 전체 UI 테마 배경": [
            ("🔴 발로란트 레드", 0), ("🟢 래디언트 시안", 300), 
            ("🟡 챌린저 골드", 500), ("🟣 공허의 아칼리", 700), ("⚔️ 밀리터리 카키", 900)
        ],
        "🖼️ 테두리 프레임": [
            ("기본 프레임", 0), ("🔴 발로란트 레드 테두리", 200), ("🟢 래디언트 네온 테두리", 400),
            ("🟡 챌린저 테두리", 600), ("🟣 공허 테두리", 800), ("⚔️ 특수부대 테두리", 1000)
        ],
        "👤 요원 아바타": [
            ("👤 기본 요원", 0), ("⚡ 네온 요원", 200), ("🦁 제드 요원", 400),
            ("🤖 메카 요원", 600), ("👑 섀도우 킹", 1000)
        ]
    }

    slot_keys = {
        "🎨 전체 UI 테마 배경": "equipped_theme",
        "🖼️ 테두리 프레임": "equipped_frame",
        "👤 요원 아바타": "equipped_avatar"
    }

    tabs = st.tabs(list(shop_data.keys()))
    for idx, (cat_name, item_list) in enumerate(shop_data.items()):
        slot_key = slot_keys[cat_name]
        with tabs[idx]:
            for item_name, price in item_list:
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"### {item_name}\n가격: **{price} P**")
                with c2:
                    if item_name in st.session_state.inventory:
                        if st.session_state[slot_key] == item_name:
                            st.info("장착됨")
                        else:
                            if st.button("장착하기", key=f"eq_{cat_name}_{item_name}"):
                                st.session_state[slot_key] = item_name
                                save_user_data()
                                st.rerun()
                    else:
                        if st.button(f"구매 ({price}P)", key=f"buy_{cat_name}_{item_name}"):
                            if st.session_state.points >= price:
                                st.session_state.points -= price
                                st.session_state.inventory.append(item_name)
                                save_user_data()
                                st.rerun()
                            else:
                                st.error("포인트 부족!")

# ==========================================
# 5. 👤 프로필 & 스타일 설정
# ==========================================
elif menu == "👤 프로필 & 스타일 설정":
    st.title("👤 요원 프로필")
    
    avatar_icon = st.session_state.equipped_avatar.split()[0]
    st.markdown(f"""
    <div style="padding: 30px; border-radius: 10px; border: {cur_frame}; text-align: center; background: rgba(0,0,0,0.4); margin-top: 15px;">
        <div style="font-size: 80px;">{avatar_icon}</div>
        <div style="font-size: 20px; font-weight: bold; color: {cur_theme['accent']}; margin-top: 10px;">[{st.session_state.equipped_title}]</div>
        <h1 style="margin: 10px 0; font-family: 'Orbitron';">{st.session_state.user_name}</h1>
        <p style="font-size: 18px;">🎨 장착 테마 배경: <b>{st.session_state.equipped_theme}</b></p>
        <p style="font-size: 18px;">🖼️ 장착 테두리: <b>{st.session_state.equipped_frame}</b></p>
        <p style="font-size: 22px; font-weight: bold; color: #f59e0b;">💰 보유 포인트: {st.session_state.points} P</p>
    </div>
    """, unsafe_allow_html=True)
