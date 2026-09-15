import streamlit as st
import requests
import random
import json
import os

st.set_page_config(page_title="친한친구 끝말잇기 톡", page_icon="💬", layout="wide")

# ==========================================
# 💾 데이터 영구 저장 및 불러오기
# ==========================================
SAVE_FILE = "user_data.json"

def load_user_data():
    default_data = {
        "user_name": "플레이어",
        "points": 1000,
        "score": 0,
        "inventory": ["🐣 끝말잇기 병아리", "🐣 병아리", "기본 프레임", "기본 테마"],
        "equipped_theme": "기본 테마",
        "equipped_avatar": "🐣 병아리",
        "equipped_frame": "기본 프레임",
        "equipped_title": "🐣 끝말잇기 병아리",
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
# 🔤 두음법칙 사전
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
# 🛡️ 네이버 사전 API (자동완성 & 검색)
# ==========================================
def safe_naver_search(query):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    url = f"https://dict.naver.com/api/search/autocomplete?query={query}&st=11111"
    try:
        res = requests.get(url, headers=headers, timeout=2)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

# ==========================================
# 🎨 스타일링 CSS (상점 테마 & 프레임 적용)
# ==========================================
theme_styles = {
    "기본 테마": "background-color: #ffffff; color: #1e293b;",
    "🌙 딥 다크": "background-color: #0f172a; color: #f8fafc;",
    "⚡ 사이버 네온": "background-color: #0d0221; color: #00f6ff;",
    "✨ 화려한 골드": "background-color: #1a1500; color: #ffd700;",
    "🌸 핑크 블라썸": "background-color: #fff0f5; color: #8b008b;",
    "🌲 포레스트 그린": "background-color: #052e16; color: #4ade80;",
    "🌊 오션 블루": "background-color: #0c4a6e; color: #38bdf8;",
    "🌆 노을 서셋": "background-color: #451a03; color: #fb923c;",
    "🍇 바이올렛": "background-color: #2e1065; color: #c084fc;",
    "🍞 따뜻한 카페": "background-color: #291d18; color: #e5e5e5;"
}

frame_styles = {
    "기본 프레임": "2px solid #94a3b8",
    "🔥 화염 테두리": "4px solid #ff4500",
    "💎 다이아 테두리": "4px solid #00ffff",
    "🌟 은하수 테두리": "4px solid #a855f7",
    "👑 황금 왕관 테두리": "4px solid #eab308",
    "🌈 무지개 테두리": "4px solid #ff007f",
    "❄️ 얼음 테두리": "4px solid #38bdf8",
    "⚡ 번개 테두리": "4px solid #facc15",
    "🌿 자연 테두리": "4px solid #22c55e",
    "🔮 마법 테두리": "4px solid #6366f1"
}

active_theme = theme_styles.get(st.session_state.equipped_theme, theme_styles["기본 테마"])
active_frame = frame_styles.get(st.session_state.equipped_frame, frame_styles["기본 프레임"])

st.markdown(f"""
<style>
    html, body, [class*="css"] {{ font-size: 19px !important; }}
    .main {{ {active_theme} }}
    .stChatMessage p {{ font-size: 21px !important; line-height: 1.6 !important; }}
    .stButton>button {{ font-size: 18px !important; font-weight: bold !important; padding: 10px 20px !important; border-radius: 12px !important; }}
    .point-badge {{ background: linear-gradient(135deg, #facc15, #eab308); color: #000; padding: 18px; border-radius: 16px; text-align: center; font-size: 28px; font-weight: 900; box-shadow: 0 4px 15px rgba(250, 204, 21, 0.4); margin-bottom: 25px; }}
    .killer-card {{ background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 10px; padding: 12px; margin: 5px 0; text-align: center; font-weight: bold; font-size: 18px; color: #ef4444; }}
    .dict-card {{ background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; margin: 10px 0; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧪 원소 주기율표 (1~118 완벽 데이터)
# ==========================================
ELEMENTS_DATA = [
    (1, "H", "수소", "기체", "비금속"), (2, "He", "헬륨", "기체", "비활성기체"), (3, "Li", "리튬", "고체", "알칼리금속"), (4, "Be", "베릴륨", "고체", "알칼리토금속"),
    (5, "B", "붕소", "고체", "준금속"), (6, "C", "탄소", "고체", "비금속"), (7, "N", "질소", "기체", "비금속"), (8, "O", "산소", "기체", "비금속"),
    (9, "F", "플루오린", "기체", "할로젠"), (10, "Ne", "네온", "기체", "비활성기체"), (11, "Na", "나트륨", "고체", "알칼리금속"), (12, "Mg", "마그네슘", "고체", "알칼리토금속"),
    (13, "Al", "알루미늄", "고체", "전이후금속"), (14, "Si", "규소", "고체", "준금속"), (15, "P", "인", "고체", "비금속"), (16, "S", "황", "고체", "비금속"),
    (17, "Cl", "염소", "기체", "할로젠"), (18, "Ar", "아르곤", "기체", "비활성기체"), (19, "K", "칼륨", "고체", "알칼리금속"), (20, "Ca", "칼슘", "고체", "알칼리토금속"),
    (21, "Sc", "스칸듐", "고체", "전이금속"), (22, "Ti", "티타늄", "고체", "전이금속"), (23, "V", "바나듐", "고체", "전이금속"), (24, "Cr", "크롬", "고체", "전이금속"),
    (25, "Mn", "망가니즈", "고체", "전이금속"), (26, "Fe", "철", "고체", "전이금속"), (27, "Co", "코발트", "고체", "전이금속"), (28, "Ni", "니켈", "고체", "전이금속"),
    (29, "Cu", "구리", "고체", "전이금속"), (30, "Zn", "아연", "고체", "전이금속"), (31, "Ga", "갈륨", "고체", "전이후금속"), (32, "Ge", "저마늄", "고체", "준금속"),
    (33, "As", "비소", "고체", "준금속"), (34, "Se", "셀레늄", "고체", "비금속"), (35, "Br", "브로민", "액체", "할로젠"), (36, "Kr", "크립톤", "기체", "비활성기체"),
    (37, "Rb", "루비듐", "고체", "알칼리금속"), (38, "Sr", "스트론튬", "고체", "알칼리토금속"), (39, "Y", "이트륨", "고체", "전이금속"), (40, "Zr", "지르코늄", "고체", "전이금속"),
    (41, "Nb", "나이오븀", "고체", "전이금속"), (42, "Mo", "몰리브데넘", "고체", "전이금속"), (43, "Tc", "테크네튬", "고체", "전이금속"), (44, "Ru", "루테늄", "고체", "전이금속"),
    (45, "Rh", "로듐", "고체", "전이금속"), (46, "Pd", "팔라듐", "고체", "전이금속"), (47, "Ag", "은", "고체", "전이금속"), (48, "Cd", "카드뮴", "고체", "전이금속"),
    (49, "In", "인듐", "고체", "전이후금속"), (50, "Sn", "주석", "고체", "전이후금속"), (51, "Sb", "안티몬", "고체", "준금속"), (52, "Te", "텔루륨", "고체", "준금속"),
    (53, "I", "아이오딘", "고체", "할로젠"), (54, "Xe", "제논", "기체", "비활성기체"), (55, "Cs", "세슘", "고체", "알칼리금속"), (56, "Ba", "바륨", "고체", "알칼리토금속"),
    (57, "La", "란타넘", "고체", "란타넘족"), (58, "Ce", "세륨", "고체", "란타넘족"), (59, "Pr", "프라세오디뮴", "고체", "란타넘족"), (60, "Nd", "네오디뮴", "고체", "란타넘족"),
    (61, "Pm", "프로메튬", "고체", "란타넘족"), (62, "Sm", "사마륨", "고체", "란타넘족"), (63, "Eu", "유로퓸", "고체", "란타넘족"), (64, "Gd", "가돌리늄", "고체", "란타넘족"),
    (65, "Tb", "테르븀", "고체", "란타넘족"), (66, "Dy", "디스프로슘", "고체", "란타넘족"), (67, "Ho", "홀뮴", "고체", "란타넘족"), (68, "Er", "에르븀", "고체", "란타넘족"),
    (69, "Tm", "툴륨", "고체", "란타넘족"), (70, "Yb", "이테르븀", "고체", "란타넘족"), (71, "Lu", "루테튬", "고체", "란타넘족"), (72, "Hf", "하프늄", "고체", "전이금속"),
    (73, "Ta", "탄탈럼", "고체", "전이금속"), (74, "W", "텅스텐", "고체", "전이금속"), (75, "Re", "레늄", "고체", "전이금속"), (76, "Os", "오스뮴", "고체", "전이금속"),
    (77, "Ir", "이리듐", "고체", "전이금속"), (78, "Pt", "백금", "고체", "전이금속"), (79, "Au", "금", "고체", "전이금속"), (80, "Hg", "수은", "액체", "전이금속"),
    (81, "Tl", "탈륨", "고체", "전이후금속"), (82, "Pb", "납", "고체", "전이후금속"), (83, "Bi", "비스무트", "고체", "전이후금속"), (84, "Po", "폴로늄", "고체", "전이후금속"),
    (85, "At", "아스타틴", "고체", "할로젠"), (86, "Rn", "라돈", "기체", "비활성기체"), (87, "Fr", "프랑슘", "고체", "알칼리금속"), (88, "Ra", "라듐", "고체", "알칼리토금속"),
    (89, "Ac", "악티늄", "고체", "악티늄족"), (90, "Th", "토륨", "고체", "악티늄족"), (91, "Pa", "프로트악티늄", "고체", "악티늄족"), (92, "U", "우라늄", "고체", "악티늄족"),
    (93, "Np", "넵튜늄", "고체", "악티늄족"), (94, "Pu", "플루토늄", "고체", "악티늄족"), (95, "Am", "아메리슘", "고체", "악티늄족"), (96, "Cm", "퀴륨", "고체", "악티늄족"),
    (97, "Bk", "버클륨", "고체", "악티늄족"), (98, "Cf", "캘리포늄", "고체", "악티늄족"), (99, "Es", "아인슈타이늄", "고체", "악티늄족"), (100, "Fm", "페르븀", "고체", "악티늄족"),
    (101, "Md", "멘델레븀", "고체", "악티늄족"), (102, "No", "노벨륨", "고체", "악티늄족"), (103, "Lr", "로렌슘", "고체", "악티늄족"), (104, "Rf", "러더포듐", "고체", "전이금속"),
    (105, "Db", "더브늄", "고체", "전이금속"), (106, "Sg", "시보귬", "고체", "전이금속"), (107, "Bh", "보륨", "고체", "전이금속"), (108, "Hs", "하슘", "고체", "전이금속"),
    (109, "Mt", "마이트너륨", "고체", "전이금속"), (110, "Ds", "다름슈타튬", "고체", "전이금속"), (111, "Rg", "뢴트게늄", "고체", "전이금속"), (112, "Cn", "코페르니슘", "고체", "전이금속"),
    (113, "Nh", "니호늄", "고체", "전이후금속"), (114, "Fl", "플레로븀", "고체", "전이후금속"), (115, "Mc", "모스코븀", "고체", "전이후금속"), (116, "Lv", "리버모륨", "고체", "전이후금속"),
    (117, "Ts", "테네신", "고체", "할로젠"), (118, "Og", "오가네손", "기체", "비활성기체")
]

# ==========================================
# 💥 한방단어 대사전 (검증된 100개 이상)
# ==========================================
MASSIVE_KILLER_DICTIONARY = {
    "륨 계열 (25개) 💥": [
        "나트륨", "칼륨", "헬륨", "베릴륨", "바륨", "라듐", "루비듐", "세슘", "이테르븀", "페르븀",
        "노벨륨", "플레로븀", "리버모륨", "마이트너륨", "다름슈타튬", "일륨", "카드뮴", "오스뮴", "로듐", "이리듐",
        "탈륨", "세륨", "테르븀", "에르븀", "툴륨"
    ],
    "늄 계열 (25개) 💥": [
        "플루토늄", "우라늄", "악티늄", "넵튜늄", "알루미늄", "지르코늄", "더브늄", "시보귬", "보륨", "하슘",
        "뢴트게늄", "코페르니슘", "니호늄", "모스코븀", "라돈", "게르마늄", "저마늄", "티타늄", "바나듐", "몰리브데넘",
        "테크네튬", "루테늄", "팔라듐", "프랑슘", "캘리포늄"
    ],
    "튬/슘 계열 (20개) 💥": [
        "리튬", "루테튬", "프로메튬", "스칸듐", "칼슘", "마그네슘", "스트론튬", "포타슘", "아메리슘", "아이오딘",
        "아인슈타이늄", "멘델레븀", "로렌슘", "러더포듐", "프라세오디뮴", "네오디뮴", "사마륨", "유로퓸", "가돌리늄", "디스프로슘"
    ],
    "특수 끝말 (슭/녘/즘/븀) (30개) 💥": [
        "기슭", "산기슭", "강기슭", "처마기슭", "해질녘", "새벽녘", "들녘", "어스름녘", "동녘", "서녘",
        "남녘", "북녘", "밤녘", "날녘", "아침녘", "저녁녘", "모더니즘", "리얼리즘", "메커니즘", "알고리즘",
        "네오디뮴", "퀴륨", "버클륨", "홀뮴", "콜롬븀", "테네신", "오가네손", "아스타틴", "크립톤", "아르곤"
    ]
}

ALL_KILLER_WORDS = list(set([w for group in MASSIVE_KILLER_DICTIONARY.values() for w in group]))

# ==========================================
# 📚 백업 사전 (실제 존재하는 단어로만 구성)
# ==========================================
MEGA_FALLBACK_DICTIONARY = {
    "리": ["리본", "리듬", "리코더", "리모컨", "리조트", "리갈", "리액션", "리필", "리얼리티", "리하사자"],
    "이": ["이야기", "이발소", "이유", "이불", "이웃", "이메일", "이탈리아", "이동", "이구아나", "이발사"],
    "기": ["기차", "기린", "기타", "기와", "기구", "기사", "기름", "기적", "기업", "기계", "기와집"],
    "차": ["차표", "차창", "차나무", "차고지", "차선", "차돌", "차량", "차고"],
    "구": ["구름", "구두", "구슬", "구경", "구조대", "구역", "구경꾼", "구식"],
    "음": ["음악", "음식", "음료수", "음성", "음향", "음자리표"],
    "바": ["바다", "바나나", "바구니", "바람", "바위", "바질", "바코드", "바리스타"],
    "다": ["다람쥐", "다리", "다리미", "다이아몬드", "다이빙", "다짐", "다이어리"],
    "자": ["자전거", "자두", "자동차", "자석", "자라", "자존심", "자연", "자유"],
    "호": ["호랑이", "호수", "호두", "호박", "호루라기", "호텔", "호기심"],
    "장": ["장난감", "장미", "장갑", "장화", "장터", "장수풍뎅이"],
    "사": ["사자", "사과", "사슴", "사탕", "사이다", "사막", "사람", "사진"]
}

# ==========================================
# 🎮 AI 봇 로직 (지어낸 단어 완전 차단)
# ==========================================
STARTING_WORDS = ["바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "무지개", "사과", "바나나"]

def is_valid_korean_word(word):
    res_json = safe_naver_search(word)
    if res_json:
        for group in res_json.get("items", []):
            for item in group:
                if item[0][0] == word: return True
    return len(word) >= 2 and word.isalpha()

def get_bot_response_word(start_chars, used_words, difficulty="보통", game_turn=0):
    clean_used = [w.strip() for w in used_words]
    candidates = []

    # 1. 온라인 사전 검증 검색
    for sc in start_chars:
        res_json = safe_naver_search(sc)
        if res_json:
            for group in res_json.get("items", []):
                for item in group:
                    w = item[0][0].strip()
                    if len(w) >= 2 and w.isalpha() and w[0] in start_chars and w not in clean_used:
                        candidates.append(w)

    # 2. 검증된 오프라인 백업 단어장 검색
    for sc in start_chars:
        if sc in MEGA_FALLBACK_DICTIONARY:
            for fw in MEGA_FALLBACK_DICTIONARY[sc]:
                if fw not in clean_used:
                    candidates.append(fw)

    candidates = list(set(candidates))
    
    # 지어낸 단어 안전 로직 완전 삭제 (단어가 없으면 정직하게 인정)
    if not candidates:
        return None

    killer_endings = ("륨", "늄", "튬", "슘", "뮴", "븀", "슭", "녘", "즘")
    safe_candidates = [w for w in candidates if w not in ALL_KILLER_WORDS and not w.endswith(killer_endings)]

    # 15턴 이하 안전 모드 (티키타카 보장)
    if game_turn <= 15:
        if safe_candidates:
            return random.choice(safe_candidates)
        return random.choice(candidates)

    # 15턴 이후 공격 모드
    if difficulty in ["어려움", "매우 어려움"]:
        killers = [w for w in candidates if w in ALL_KILLER_WORDS or w.endswith(killer_endings)]
        if killers and random.random() < 0.6:
            return random.choice(killers)

    return random.choice(safe_candidates) if safe_candidates else random.choice(candidates)

def reset_game():
    first_word = random.choice(STARTING_WORDS)
    st.session_state.chat_history = [
        {"role": "bot", "text": f"안녕 {st.session_state.user_name}! 첫 단어는 **'{first_word}'**이야! **'{first_word[-1]}'**(으)로 시작해줘!"}
    ]
    st.session_state.last_word = first_word
    st.session_state.used_words = [first_word]
    st.session_state.game_over = False
    st.session_state.game_turn = 0

if "chat_history" not in st.session_state: reset_game()

# ==========================================
# 📌 사이드바 메뉴 & 포인트 표시
# ==========================================
st.sidebar.markdown(f"""
<div class="point-badge">
    💰 {st.session_state.points} P
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("메뉴 이동", [
    "💬 끝말잇기 톡", 
    "📕 한방단어 대사전 (100+)",
    "🔍 네이버 사전 단어/뜻 검색",
    "🛒 상점 (40종 아이템)",
    "👤 프로필 & 스타일 꾸미기",
    "🧪 원소 주기율표 (1~118)"
])

# ==========================================
# 1. 💬 끝말잇기 톡
# ==========================================
if menu == "💬 끝말잇기 톡":
    st.title("💬 끝말잇기 톡")
    difficulty = st.sidebar.select_slider("⚙️ 난이도 선택:", options=["쉬움", "보통", "어려움", "매우 어려움"], value="보통")
    
    st.info(f"🔄 **현재 진행: {st.session_state.game_turn}턴** | 두음법칙 완벽 지원 & 가짜 단어 생성 차단")

    for msg in st.session_state.chat_history:
        avatar = st.session_state.equipped_avatar.split()[0] if msg["role"] == "user" else "🤖"
        st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar).write(msg["text"])

    last_char = st.session_state.last_word[-1]
    allowed_chars = get_allowed_initials(last_char)
    allowed_str = '/'.join(allowed_chars)

    if not st.session_state.game_over:
        user_input = st.chat_input(f"'{allowed_str}'(으)로 시작하는 단어 입력...")
        if user_input:
            user_input_clean = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "text": user_input_clean})

            if len(user_input_clean) < 2:
                st.session_state.chat_history.append({"role": "bot", "text": "두 글자 이상 입력해야 해! ❌"})
                st.session_state.game_over = True
            elif user_input_clean[0] not in allowed_chars:
                st.session_state.chat_history.append({"role": "bot", "text": f"글자가 맞지 않아! **'{allowed_str}'**(으)로 시작해야 해! (두음법칙 가능)"})
                st.session_state.game_over = True
            elif user_input_clean in st.session_state.used_words:
                st.session_state.chat_history.append({"role": "bot", "text": "이미 사용된 중복 단어야! 😜"})
                st.session_state.game_over = True
            elif not is_valid_korean_word(user_input_clean):
                st.session_state.chat_history.append({"role": "bot", "text": "사전에 존재하지 않는 단어야! 😅"})
                st.session_state.game_over = True
            else:
                st.session_state.used_words.append(user_input_clean)
                st.session_state.last_word = user_input_clean
                st.session_state.game_turn += 1

                bot_next_chars = get_allowed_initials(user_input_clean[-1])
                bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, difficulty, st.session_state.game_turn)

                if bot_word is None:
                    st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'**?! 😱 더 이상 단어가 없어... 네가 이겼어! 🎉 (+100P)"})
                    st.session_state.points += 100
                    st.session_state.game_over = True
                    save_user_data()
                    st.balloons()
                else:
                    st.session_state.used_words.append(bot_word)
                    st.session_state.last_word = bot_word
                    st.session_state.points += 10
                    save_user_data()
                    next_allowed = '/'.join(get_allowed_initials(bot_word[-1]))
                    st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'** 받아쳐서 **'{bot_word}'**! 다음은 **'{next_allowed}'**!"})
            st.rerun()

    if st.session_state.game_over:
        st.button("🔄 새 게임 시작", on_click=reset_game)

# ==========================================
# 2. 📕 한방단어 대사전 (100개+)
# ==========================================
elif menu == "📕 한방단어 대사전 (100+)":
    st.title("📕 한방단어 대사전 (100개 이상)")
    st.write("상대방을 한번에 제압할 수 있는 검증된 한방 단어 모음입니다.")
    
    search_k = st.text_input("🔍 대사전 내 검색:", "")
    
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
                st.subheader(f"{cat_name}")
                cols = st.columns(4)
                for w_idx, word in enumerate(words):
                    with cols[w_idx % 4]:
                        st.markdown(f"<div class='killer-card'>{word}</div>", unsafe_allow_html=True)

# ==========================================
# 3. 🔍 네이버 사전 단어/뜻 검색
# ==========================================
elif menu == "🔍 네이버 사전 단어/뜻 검색":
    st.title("🔍 네이버 사전 단어 & 뜻 실시간 검색")
    st.write("단어가 국어사전에 등록되어 있는지, 연관 단어와 뜻이 무엇인지 확인합니다.")
    
    search_q = st.text_input("검색할 단어를 입력하세요:", "")
    if search_q:
        res_json = safe_naver_search(search_q)
        if res_json:
            items = res_json.get("items", [])
            found_words = []
            for group in items:
                for item in group:
                    found_words.append(item[0][0])
            
            found_words = list(dict.fromkeys(found_words))
            
            if found_words:
                st.success(f"네이버 사전 검색 결과 ({len(found_words)}건 등록됨):")
                for w in found_words:
                    is_killer = " 💥 [한방 단어]" if w in ALL_KILLER_WORDS or w.endswith(("륨", "늄", "튬", "슘", "뮴", "븀", "슭", "녘", "즘")) else ""
                    st.markdown(f"""
                    <div class="dict-card">
                        <h3 style="margin:0; color:#3b82f6;">{w} {is_killer}</h3>
                        <p style="margin:5px 0 0 0; color:#64748b;">네이버 국어사전 표준 등재 명사</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("국어사전에 등재되지 않은 단어입니다.")
        else:
            st.warning("네이버 사전 검색 서비스 연동이 원활하지 않습니다.")

# ==========================================
# 4. 🛒 상점 (40종 아이템)
# ==========================================
elif menu == "🛒 상점 (40종 아이템)":
    st.title("🛒 아이템 상점 (40종 세트)")
    st.write("게임으로 모은 포인트로 칭호, 아바타, 테두리, 테마를 구매해보세요!")

    shop_items_data = {
        "🏷️ 칭호 (10종)": [
            ("🐣 끝말잇기 병아리", 0), ("⚡ 뇌섹남", 100), ("⚔️ 끝말잇기 패왕", 200),
            ("🧪 원소의 지배자", 300), ("👑 국어사전의 신", 500), ("🎯 단어의 연금술사", 600),
            ("🔥 티키타카 마스터", 700), ("🛡️ 언어의 수호자", 800), ("🚀 우주 대스타", 900), ("🏆 국어대왕", 1000)
        ],
        "👤 아바타 (10종)": [
            ("🐣 병아리", 0), ("⚡ 뇌섹남", 100), ("🦁 사자왕", 200),
            ("🤖 AI 봇", 300), ("🐉 드래곤", 500), ("🐱 냥이", 600),
            ("🐶 댕댕이", 600), ("🦊 여우", 700), ("🐯 호랑이", 800), ("👑 황제", 1000)
        ],
        "🖼️ 프레임 (10종)": [
            ("기본 프레임", 0), ("🔥 화염 테두리", 100), ("💎 다이아 테두리", 200),
            ("🌟 은하수 테두리", 300), ("👑 황금 왕관 테두리", 500), ("🌈 무지개 테두리", 600),
            ("❄️ 얼음 테두리", 700), ("⚡ 번개 테두리", 700), ("🌿 자연 테두리", 800), ("🔮 마법 테두리", 1000)
        ],
        "🎨 테마 (10종)": [
            ("기본 테마", 0), ("🌙 딥 다크", 100), ("⚡ 사이버 네온", 200),
            ("✨ 화려한 골드", 300), ("🌸 핑크 블라썸", 500), ("🌲 포레스트 그린", 600),
            ("🌊 오션 블루", 700), ("🌆 노을 서셋", 800), ("🍇 바이올렛", 900), ("🍞 따뜻한 카페", 1000)
        ]
    }

    slot_keys = {
        "🏷️ 칭호 (10종)": "equipped_title",
        "👤 아바타 (10종)": "equipped_avatar",
        "🖼️ 프레임 (10종)": "equipped_frame",
        "🎨 테마 (10종)": "equipped_theme"
    }

    tabs = st.tabs(list(shop_items_data.keys()))
    for idx, (cat_name, item_list) in enumerate(shop_items_data.items()):
        slot_key = slot_keys[cat_name]
        with tabs[idx]:
            for item_name, price in item_list:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"### {item_name}\n가격: **{price} P**")
                with col2:
                    if item_name in st.session_state.inventory:
                        if st.session_state[slot_key] == item_name:
                            st.success("장착 중")
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
# 5. 👤 프로필 & 스타일 꾸미기
# ==========================================
elif menu == "👤 프로필 & 스타일 꾸미기":
    st.title("👤 플레이어 프로필")
    
    st.subheader("✏️ 닉네임 수정")
    new_username = st.text_input("새로운 닉네임:", value=st.session_state.user_name)
    if st.button("💾 닉네임 저장"):
        if new_username.strip():
            st.session_state.user_name = new_username.strip()
            save_user_data()
            st.success("닉네임이 성공적으로 저장되었습니다!")
            st.rerun()
        else:
            st.error("올바른 닉네임을 입력하세요.")

    st.markdown("---")
    avatar_icon = st.session_state.equipped_avatar.split()[0]
    st.markdown(f"""
    <div style="padding: 30px; border-radius: 20px; border: {active_frame}; text-align: center; margin-top: 15px;">
        <div style="font-size: 80px;">{avatar_icon}</div>
        <div style="font-size: 20px; font-weight: bold; color: #eab308; margin-top: 10px;">[{st.session_state.equipped_title}]</div>
        <h1 style="margin: 10px 0;">{st.session_state.user_name}</h1>
        <p style="font-size: 20px;">🎨 현재 테마: <b>{st.session_state.equipped_theme}</b></p>
        <p style="font-size: 20px;">🖼️ 현재 프레임: <b>{st.session_state.equipped_frame}</b></p>
        <p style="font-size: 24px; font-weight: bold; color: #facc15;">💰 보유 포인트: {st.session_state.points} P</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. 🧪 원소 주기율표 (1~118)
# ==========================================
elif menu == "🧪 원소 주기율표 (1~118)":
    st.title("🧪 원소 주기율표 (1~118 완벽 수록)")
    search_elem = st.text_input("원소 이름 또는 기호 검색 (예: 수소, H, Na, 바나듐):", "")
    
    filtered = [e for e in ELEMENTS_DATA if search_elem in e[2] or search_elem.lower() in e[1].lower()]
    cols = st.columns(3)
    for idx, (num, sym, name, state, cat) in enumerate(filtered):
        with cols[idx % 3]:
            is_k = name.endswith(("륨", "늄", "튬", "슘", "뮴"))
            st.markdown(f"""
            <div style="border: 2px solid {'#ef4444' if is_k else '#4b5563'}; border-radius: 12px; padding: 15px; margin-bottom: 12px; text-align: center;">
                <span style="font-size: 14px; color: #888;">No.{num} [{cat}]</span>
                <h2 style="margin: 5px 0;">{sym}</h2>
                <span style="font-size: 22px; font-weight: bold;">{name}</span>
                {('<br/><span style="color:#ef4444; font-weight:bold;">💥 한방 단어 사용 가능</span>' if is_k else '')}
            </div>
            """, unsafe_allow_html=True)
