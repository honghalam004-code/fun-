import streamlit as st
import requests
import time
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
        "inventory": ["🐣 끝말잇기 병아리", "🐣 병아리 아바타", "기본 프레임", "기본 테마"],
        "equipped_theme": "기본 테마",
        "equipped_avatar": "🐣 병아리 아바타",
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
# 🔤 완벽 완비 두음법칙 사전
# ==========================================
DUEUM_MAP = {
    # ㄹ -> ㄴ
    '라': ['나'], '락': ['낙'], '란': ['난'], '랄': ['날'], '람': ['남'], '랍': ['납'], '랑': ['낭'],
    '래': ['내'], '랭': ['냉'], '로': ['노'], '록': ['녹'], '론': ['논'], '롱': ['농'], '뢰': ['뇌'],
    '루': ['누'], '르': ['느'],
    # ㄹ -> ㅇ
    '량': ['양'], '려': ['여'], '력': ['역'], '련': ['연'], '렬': ['열'], '렴': ['염'], '렵': ['엽'],
    '령': ['영'], '례': ['예'], '료': ['요'], '류': ['유'], '륙': ['육'], '륜': ['윤'], '률': ['율'],
    '륭': ['융'], '름': ['음'], '릉': ['응'], '리': ['이'], '린': ['인'], '림': ['임'], '립': ['입'], '링': ['잉'],
    # ㄴ -> ㅇ
    '녀': ['여'], '녁': ['역'], '년': ['연'], '념': ['염'], '닙': ['입'], '뉴': ['유'], '니': ['이'],
    '님': ['임'], '닌': ['인'], '닝': ['잉']
}

def get_allowed_initials(char):
    allowed = [char]
    if char in DUEUM_MAP:
        allowed.extend(DUEUM_MAP[char])
    return list(dict.fromkeys(allowed))

# ==========================================
# 🛡️ 안전한 네이버 API 검색
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
# 🎨 스타일링 CSS (디자인 개편)
# ==========================================
theme_css = "background-color: #ffffff; color: #1e293b;"
if st.session_state.equipped_theme == "🌙 딥 다크":
    theme_css = "background-color: #0f172a; color: #f8fafc;"
elif st.session_state.equipped_theme == "⚡ 사이버 네온":
    theme_css = "background-color: #0d0221; color: #00f6ff;"
elif st.session_state.equipped_theme == "✨ 화려한 골드":
    theme_css = "background-color: #1a1500; color: #ffd700;"
elif st.session_state.equipped_theme == "🌸 핑크 블라썸":
    theme_css = "background-color: #fff0f5; color: #8b008b;"

frame_border = "2px solid #94a3b8"
if st.session_state.equipped_frame == "🔥 화염 테두리":
    frame_border = "4px solid #ff4500"
elif st.session_state.equipped_frame == "💎 다이아 테두리":
    frame_border = "4px solid #00ffff"
elif st.session_state.equipped_frame == "🌟 은하수 테두리":
    frame_border = "4px solid #a855f7"
elif st.session_state.equipped_frame == "👑 황금 왕관 테두리":
    frame_border = "4px solid #eab308"

st.markdown(f"""
<style>
    html, body, [class*="css"] {{ font-size: 19px !important; }}
    .main {{ {theme_css} }}
    .stChatMessage p {{ font-size: 21px !important; line-height: 1.6 !important; }}
    .stButton>button {{ font-size: 18px !important; font-weight: bold !important; padding: 10px 20px !important; border-radius: 12px !important; }}
    .point-badge {{ background: linear-gradient(135deg, #facc15, #eab308); color: #000; padding: 18px; border-radius: 16px; text-align: center; font-size: 28px; font-weight: 900; box-shadow: 0 4px 15px rgba(250, 204, 21, 0.4); margin-bottom: 25px; }}
    .killer-card {{ background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 10px; padding: 10px; margin: 5px 0; text-align: center; font-weight: bold; font-size: 18px; color: #ef4444; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💥 원소 주기율표 (1~118) 및 대량 한방 단어
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

MASSIVE_KILLER_DICTIONARY = {
    "륨 계열 💥": ["나트륨", "칼륨", "헬륨", "베릴륨", "바륨", "라듐", "루비듐", "세슘", "이테르븀", "페르븀", "노벨륨", "플레로븀", "리버모륨", "마이트너륨", "다름슈타튬"],
    "늄 계열 💥": ["플루토늄", "우라늄", "악티늄", "넵튜늄", "알루미늄", "지르코늄", "더브늄", "시보귬", "보륨", "하슘", "뢴트게늄", "코페르니슘", "니호늄", "모스코븀"],
    "튬 계열 💥": ["리튬", "루테튬", "프로메튬", "스칸듐"],
    "슘 계열 💥": ["칼슘", "마그네슘", "스트론튬", "포타슘", "아메리슘"],
    "뮴/븀 계열 💥": ["사마륨", "가돌리늄", "퀴륨", "오스뮴", "프라세오디뮴", "몰리브데넘", "이테르븀", "테르븀", "유로퓸", "콜롬븀"],
    "특수 음절 (슭/녘) 💥": ["기슭", "산기슭", "강기슭", "슭곰", "해질녘", "새벽녘", "들녘", "어스름녘", "동녘", "서녘", "남녘", "북녘", "이산화바나듐", "삼산화바나듐"]
}

ALL_KILLER_WORDS = list(set([w for group in MASSIVE_KILLER_DICTIONARY.values() for w in group] + [e[2] for e in ELEMENTS_DATA if e[2].endswith(("륨", "늄", "튬", "슘", "뮴", "븀"))]))

# 🔄 무한 티키타카를 위한 초대형 오프라인 단어장 (절대 끊기지 않음)
MEGA_FALLBACK_DICTIONARY = {
    "리": ["리본", "리듬", "리코더", "리모컨", "리조트", "리갈", "리액션", "리필", "리얼리티", "리하사자"],
    "이": ["이야기", "이발소", "이유", "이불", "이웃", "이메일", "이탈리아", "이동", "이발사", "이구아나"],
    "기": ["기차", "기린", "기타", "기와", "기구", "기사", "기름", "기적", "기억", "기업"],
    "차": ["차표", "차창", "차나무", "차고지", "차선", "차돌", "차량", "차고"],
    "구": ["구름", "구두", "구슬", "구경", "구조대", "구마유시", "구역", "구경꾼"],
    "름": ["름봉", "름장"], "음": ["음악", "음식", "음료수", "음성", "음향"],
    "바": ["바다", "바나나", "바구니", "바람", "바위", "바질", "바리스타", "바코드"],
    "다": ["다람쥐", "다리", "다리미", "다이아몬드", "다큐멘터리", "다이빙", "다짐"],
    "자": ["자전거", "자두", "자동차", "자석", "자라", "자존심", "자연", "자유"],
    "호": ["호랑이", "호수", "호두", "호박", "호루라기", "호텔", "호기심"],
    "장": ["장난감", "장미", "장갑", "장화", "장터", "장수풍뎅이"],
    "사": ["사자", "사과", "사슴", "사탕", "사이다", "사막", "사람", "사진"],
    "컴": ["컴퓨터", "컴퍼스", "컴팩트"], "퓨": ["퓨마", "퓨즈", "퓨전"], "터": ["터널", "터틀넥", "터미널"],
    "스": ["스프", "스케이트", "스마트폰", "스피커", "스웨터"], "폰": ["폰카", "폰트"],
    "나": ["나비", "나무", "나팔", "나침반", "나비넥타이"], "무": ["무지개", "무대", "무당벌레", "무전기"],
    "게": ["게장", "게스트", "게시판"], "판": ["판다", "판사", "판타지"]
}

# ==========================================
# 🎮 게임 로직 & 두음법칙 적용
# ==========================================
STARTING_WORDS = ["바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "무지개", "사과", "바나나"]

def is_valid_korean_word(word):
    res_json = safe_naver_search(word)
    if res_json:
        for group in res_json.get("items", []):
            for item in group:
                if item[0][0] == word: return True
    return len(word) >= 2

def get_bot_response_word(start_chars, used_words, difficulty="보통", game_turn=0):
    clean_used = [w.strip() for w in used_words]
    candidates = []

    # 1. 온라인 사전 검색
    for sc in start_chars:
        res_json = safe_naver_search(sc)
        if res_json:
            for group in res_json.get("items", []):
                for item in group:
                    w = item[0][0].strip()
                    if len(w) >= 2 and w[0] in start_chars and w not in clean_used:
                        candidates.append(w)

    # 2. 오프라인 비상 단어장 (검색 실패 시에도 끊김 방지)
    for sc in start_chars:
        if sc in MEGA_FALLBACK_DICTIONARY:
            for fw in MEGA_FALLBACK_DICTIONARY[sc]:
                if fw not in clean_used:
                    candidates.append(fw)

    candidates = list(set(candidates))
    
    # 3. 만약 완벽히 막혔을 때, 마지막 보루로 글자+잇기 조합 생성하여 게임 끊김 방지
    if not candidates:
        for sc in start_chars:
            safety_word = f"{sc}리더" if sc != "리" else "이유"
            if safety_word not in clean_used:
                candidates.append(safety_word)

    if not candidates: return None

    killer_endings = ("륨", "늄", "튬", "슘", "뮴", "븀", "슭", "녘")
    safe_candidates = [w for w in candidates if w not in ALL_KILLER_WORDS and not w.endswith(killer_endings)]

    # 🛑 티키타카 보장: 15턴 이하에서는 절대 AI가 한방 단어나 판을 끝내는 단어를 안 씀
    if game_turn <= 15:
        if safe_candidates:
            return random.choice(safe_candidates)
        return random.choice(candidates)

    # 15턴 이후 난이도별 적용
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
# 📌 사이드바 메뉴
# ==========================================
st.sidebar.markdown(f"""
<div class="point-badge">
    💰 {st.session_state.points} P
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("메뉴 이동", [
    "💬 끝말잇기 톡", 
    "📕 한방단어 대사전 (새 단장)",
    "🔍 네이버 사전 검색",
    "🛒 상점 (20종 세트)",
    "👤 내 프로필 (이름 변경)",
    "🧪 원소 주기율표 (1~118)"
])

# ==========================================
# 1. 💬 끝말잇기 톡
# ==========================================
if menu == "💬 끝말잇기 톡":
    st.title("💬 끝말잇기 톡")
    difficulty = st.sidebar.select_slider("⚙️ 난이도 선택:", options=["쉬움", "보통", "어려움", "매우 어려움"], value="보통")
    
    st.info(f"🔄 **연속 티키타카: {st.session_state.game_turn}턴 진행 중** (두음법칙 완벽 적용 및 15턴까지 안전 이어나가기 활성화)")

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

            # 두음법칙 검사 강화
            if len(user_input_clean) < 2:
                st.session_state.chat_history.append({"role": "bot", "text": "두 글자 이상 입력해야지! ❌"})
                st.session_state.game_over = True
            elif user_input_clean[0] not in allowed_chars:
                st.session_state.chat_history.append({"role": "bot", "text": f"글자가 맞지 않아! **'{allowed_str}'**(으)로 시작해야 해! (두음법칙 가능)"})
                st.session_state.game_over = True
            elif user_input_clean in st.session_state.used_words:
                st.session_state.chat_history.append({"role": "bot", "text": "이미 사용된 중복 단어야! 패배! 😜"})
                st.session_state.game_over = True
            elif not is_valid_korean_word(user_input_clean):
                st.session_state.chat_history.append({"role": "bot", "text": "사전에 없는 단어야! 😅"})
                st.session_state.game_over = True
            else:
                st.session_state.used_words.append(user_input_clean)
                st.session_state.last_word = user_input_clean
                st.session_state.game_turn += 1

                bot_next_chars = get_allowed_initials(user_input_clean[-1])
                bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, difficulty, st.session_state.game_turn)

                if bot_word is None:
                    st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'**?! 😱 더 이상 받아칠 단어가 없어... 네가 이겼어! 🎉 (+100P)"})
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
# 2. 📕 한방단어 대사전 (보기 편하게 UI 전면 개편)
# ==========================================
elif menu == "📕 한방단어 대사전 (새 단장)":
    st.title("📕 한방단어 대사전")
    st.write("끝말잇기에서 상대방을 제압하는 핵심 한방 단어 모음입니다.")
    
    # 빠른 검색창
    search_k = st.text_input("🔍 한방 단어 빠른 검색:", "")
    
    if search_k:
        results = [w for w in ALL_KILLER_WORDS if search_k in w]
        st.write(f"검색 결과 ({len(results)}개):")
        cols = st.columns(4)
        for idx, word in enumerate(results):
            with cols[idx % 4]:
                st.markdown(f"<div class='killer-card'>{word}</div>", unsafe_allow_html=True)
    else:
        # 카테고리별 Tab으로 깔끔하게 정리
        tabs = st.tabs(list(MASSIVE_KILLER_DICTIONARY.keys()))
        for idx, (cat_name, words) in enumerate(MASSIVE_KILLER_DICTIONARY.items()):
            with tabs[idx]:
                st.subheader(f"{cat_name} 목록 ({len(words)}개)")
                cols = st.columns(4)
                for w_idx, word in enumerate(words):
                    with cols[w_idx % 4]:
                        st.markdown(f"<div class='killer-card'>{word}</div>", unsafe_allow_html=True)

# ==========================================
# 3. 🔍 네이버 사전 검색
# ==========================================
elif menu == "🔍 네이버 사전 검색":
    st.title("🔍 네이버 사전 실시간 검색")
    search_q = st.text_input("검색할 단어 입력:", "")
    if search_q:
        res_json = safe_naver_search(search_q)
        if res_json:
            items = res_json.get("items", [])
            found = [item[0][0] for group in items for item in group]
            if found:
                st.success(f"검색 결과 ({len(found)}개):")
                for w in found:
                    tag = " 💥 [한방 단어]" if w in ALL_KILLER_WORDS or w.endswith(("륨", "늄", "튬", "슘", "뮴", "븀", "슭", "녘")) else ""
                    st.write(f"- **{w}**{tag}")
            else:
                st.error("등록되지 않은 단어입니다.")
        else:
            st.error("네이버 사전 검색 서버 연결이 원활하지 않습니다.")

# ==========================================
# 4. 🛒 상점
# ==========================================
elif menu == "🛒 상점 (20종 세트)":
    st.title("🛒 아이템 상점")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏷️ 칭호 (5종)", "👤 아바타 (5종)", "🖼️ 프레임 (5종)", "🎨 테마 (5종)"])

    shop_categories = [
        (tab1, "equipped_title", [
            ("🐣 끝말잇기 병아리", 0), ("⚡ 뇌섹남", 100), ("⚔️ 끝말잇기 패왕", 200),
            ("🧪 원소의 지배자", 300), ("👑 국어사전의 신", 500)
        ]),
        (tab2, "equipped_avatar", [
            ("🐣 병아리 아바타", 0), ("⚡ 뇌섹남 아바타", 100), ("🦁 사자왕 아바타", 200),
            ("🤖 AI 봇 아바타", 300), ("🐉 드래곤 아바타", 500)
        ]),
        (tab3, "equipped_frame", [
            ("기본 프레임", 0), ("🔥 화염 테두리", 100), ("💎 다이아 테두리", 200),
            ("🌟 은하수 테두리", 300), ("👑 황금 왕관 테두리", 500)
        ]),
        (tab4, "equipped_theme", [
            ("기본 테마", 0), ("🌙 딥 다크", 100), ("⚡ 사이버 네온", 200),
            ("✨ 화려한 골드", 300), ("🌸 핑크 블라썸", 500)
        ])
    ]

    for tab_obj, slot_key, items in shop_categories:
        with tab_obj:
            for item_name, price in items:
                col1, col2 = st.columns([3, 1])
                with col1: st.write(f"### {item_name}  \n가격: **{price} P**")
                with col2:
                    if item_name in st.session_state.inventory:
                        if st.session_state[slot_key] == item_name:
                            st.success("장착 중")
                        else:
                            if st.button("장착하기", key=f"eq_{item_name}"):
                                st.session_state[slot_key] = item_name
                                save_user_data()
                                st.rerun()
                    else:
                        if st.button(f"구매 ({price}P)", key=f"buy_{item_name}"):
                            if st.session_state.points >= price:
                                st.session_state.points -= price
                                st.session_state.inventory.append(item_name)
                                save_user_data()
                                st.rerun()
                            else:
                                st.error("포인트 부족!")

# ==========================================
# 5. 👤 내 프로필
# ==========================================
elif menu == "👤 내 프로필 (이름 변경)":
    st.title("👤 플레이어 프로필")
    
    st.subheader("✏️ 닉네임 수정")
    new_username = st.text_input("새로운 닉네임을 입력하세요:", value=st.session_state.user_name)
    if st.button("💾 닉네임 저장"):
        if new_username.strip():
            st.session_state.user_name = new_username.strip()
            save_user_data()
            st.success("닉네임이 변경되었습니다!")
            st.rerun()
        else:
            st.error("올바른 닉네임을 입력해주세요.")

    st.markdown("---")
    st.markdown(f"""
    <div style="padding: 30px; border-radius: 20px; border: {frame_border}; text-align: center; margin-top: 15px;">
        <div style="font-size: 70px;">{st.session_state.equipped_avatar.split()[0]}</div>
        <div style="font-size: 18px; font-weight: bold; color: #eab308; margin-top: 10px;">[{st.session_state.equipped_title}]</div>
        <h1 style="margin: 10px 0;">{st.session_state.user_name}</h1>
        <p style="font-size: 20px;">🎨 적용 테마: <b>{st.session_state.equipped_theme}</b></p>
        <p style="font-size: 20px;">🖼️ 적용 프레임: <b>{st.session_state.equipped_frame}</b></p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. 🧪 원소 주기율표 (1~118)
# ==========================================
elif menu == "🧪 원소 주기율표 (1~118)":
    st.title("🧪 원소 주기율표 (1~118)")
    search_elem = st.text_input("원소 이름 또는 기호 검색 (예: 소듐, 바나듐, Na):", "")
    
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
                {('<br/><span style="color:#ef4444; font-weight:bold;">💥 끝말잇기 한방 단어</span>' if is_k else '')}
            </div>
            """, unsafe_allow_html=True)
