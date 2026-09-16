import streamlit as st
import requests
import random
import json
import os

st.set_page_config(page_title="끝말잇기 PRO", page_icon="⚔️", layout="wide")

# ==========================================
# 💾 데이터 영구 저장 로직
# ==========================================
SAVE_FILE = "user_tactical_data.json"

def load_user_data():
    default_data = {
        "user_name": "요원_01",
        "points": 5000,
        "inventory": ["🎖️ 초보 끝말러", "👤 기본 요원", "기본 프레임", "🔴 다크 레드 테마"],
        "equipped_theme": "🔴 다크 레드 테마",
        "equipped_avatar": "👤 기본 요원",
        "equipped_frame": "기본 프레임",
        "equipped_title": "🎖️ 초보 끝말러",
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
# 🎨 테마 및 프레임 디자인
# ==========================================
THEME_CONFIGS = {
    "🔴 다크 레드 테마": {
        "bg_css": "linear-gradient(135deg, #1f070a 0%, #0a0e17 100%)",
        "card_bg": "#1e293b",
        "accent": "#ff334b",
        "glow": "rgba(255, 51, 75, 0.4)"
    },
    "⚡ 사이버펑크 네온": {
        "bg_css": "linear-gradient(135deg, #022c22 0%, #020617 100%)",
        "card_bg": "#0f172a",
        "accent": "#00ffcc",
        "glow": "rgba(0, 255, 204, 0.5)"
    },
    "👑 로열 골드 레전드": {
        "bg_css": "linear-gradient(135deg, #281d07 0%, #0d0a03 100%)",
        "card_bg": "#1c1917",
        "accent": "#fbbf24",
        "glow": "rgba(251, 191, 36, 0.5)"
    },
    "🔮 심연의 갤럭시": {
        "bg_css": "linear-gradient(135deg, #1e0b36 0%, #080312 100%)",
        "card_bg": "#180e29",
        "accent": "#c084fc",
        "glow": "rgba(192, 132, 252, 0.5)"
    },
    "🌸 사쿠라 블로섬": {
        "bg_css": "linear-gradient(135deg, #2d0c1e 0%, #12030b 100%)",
        "card_bg": "#24101b",
        "accent": "#f472b6",
        "glow": "rgba(244, 114, 182, 0.5)"
    },
    "🌊 심해의 아틀란티스": {
        "bg_css": "linear-gradient(135deg, #032b45 0%, #020b14 100%)",
        "card_bg": "#0b1e2e",
        "accent": "#38bdf8",
        "glow": "rgba(56, 189, 248, 0.5)"
    }
}

FRAME_STYLES = {
    "기본 프레임": "2px solid #64748b",
    "🔴 네온 레드 펄스": "3px solid #ff334b",
    "⚡ 네온 사이버 글레이어": "3px solid #00ffcc",
    "👑 황금 왕관 프레임": "4px solid #fbbf24",
    "🔮 공허의 은하수 프레임": "4px solid #c084fc",
    "💎 영롱한 다이아몬드": "4px solid #38bdf8",
    "🔥 불꽃 네온 오라": "4px solid #f97316"
}

cur_theme = THEME_CONFIGS.get(st.session_state.equipped_theme, THEME_CONFIGS["🔴 다크 레드 테마"])
cur_frame = FRAME_STYLES.get(st.session_state.equipped_frame, FRAME_STYLES["기본 프레임"])

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800;900&display=swap');

    * {{ font-family: 'Pretendard', sans-serif; }}

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background: {cur_theme['bg_css']} !important;
        color: #ffffff !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: #070a12 !important;
        border-right: 2px solid {cur_theme['accent']}55;
    }}
    
    p, span, label, div, .stMarkdown {{ color: #f8fafc !important; }}
    h1, h2, h3, h4 {{ color: #ffffff !important; font-weight: 800 !important; }}

    .stChatMessage {{
        background-color: {cur_theme['card_bg']} !important;
        border-radius: 12px !important;
        border: 1px solid {cur_theme['accent']}aa !important;
        box-shadow: 0 4px 15px {cur_theme['glow']};
    }}
    .stChatMessage p {{ color: #ffffff !important; font-size: 16px !important; }}

    [data-testid="stChatInput"] textarea, 
    [data-testid="stChatInput"] input,
    div[data-baseweb="input"] input {{
        color: #ffffff !important;
        background-color: #0f172a !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #ffffff !important;
    }}
    
    [data-testid="stChatInput"] {{
        background-color: #0f172a !important;
        border: 2px solid {cur_theme['accent']} !important;
        border-radius: 12px !important;
        box-shadow: 0 0 12px {cur_theme['glow']};
    }}

    .stButton>button {{
        background: {cur_theme['accent']} !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease-in-out;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px {cur_theme['glow']};
    }}
    
    .point-badge {{
        background: #0f172a;
        border: 2px solid {cur_theme['accent']};
        color: {cur_theme['accent']} !important;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-size: 22px;
        font-weight: 900;
        box-shadow: 0 0 10px {cur_theme['glow']};
        margin-bottom: 15px;
    }}

    .killer-card {{
        background: #0f172a !important;
        border-left: 4px solid #ef4444 !important;
        border: 1px solid #334155;
        padding: 10px 14px;
        margin: 4px 0;
        font-weight: bold;
        color: #ffffff !important;
        border-radius: 6px;
    }}

    .shop-card {{
        background: #0f172a;
        border: 1px solid {cur_theme['accent']}aa;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }}
    
    .elem-card {{
        border: 1px solid {cur_theme['accent']}aa;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        background: #0f172a !important;
        margin-bottom: 10px;
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
# 📕 방대한 오프라인 사전 DB (어휘 폭 대폭 확대!)
# ==========================================
MEGA_FALLBACK_DICTIONARY = {
    "가": ["가방", "가수", "가구", "가을", "가족", "가시", "가면", "가자미", "가라오케", "가장복", "가로수", "가공품", "가위"],
    "나": ["나비", "나무", "나팔", "나침반", "나이테", "나물", "나그네", "나방", "나들이", "나이프"],
    "다": ["다람쥐", "다리", "다리미", "다이아몬드", "다이빙", "다짐", "다큐멘터리", "다시마", "다문화", "다용도"],
    "라": ["라면", "라디오", "라일락", "라쿤", "라떼", "라인업", "라이터", "라켓", "라벨"],
    "마": ["마술", "마을", "마스크", "마우스", "마늘", "마라톤", "마분지", "마이크", "마라탕"],
    "바": ["바다", "바나나", "바구니", "바람", "바위", "바질", "바코드", "바퀴벌레", "바비큐"],
    "사": ["사자", "사과", "사슴", "사탕", "사이다", "사막", "사람", "사다리", "사무실", "사파이어"],
    "아": ["아기", "아이스크림", "아카시아", "아버지", "아침", "아파트", "아령", "아보카도", "아나운서"],
    "자": ["자전거", "자두", "자동차", "자석", "자라", "자존심", "자연", "자몽", "자유"],
    "차": ["차표", "차창", "차나무", "차고지", "차선", "차돌", "차량", "차고", "차지", "차도"],
    "카": ["카메라", "카레", "카펫", "카누", "카드", "카라멜", "카운터", "카리스마", "카트"],
    "타": ["타이어", "타자기", "타월", "타조", "타이머", "타워", "타코", "타격", "타자"],
    "파": ["파도", "파이프", "파인애플", "파리", "파랑새", "파스타", "파도타기", "파자마"],
    "하": ["하늘", "하마", "하모니카", "하트", "하수구", "하얀색", "하와이", "하키"],
    "면": ["면발", "면도기", "면장갑", "면화", "면접", "면제", "면적", "면류관", "면목", "면수", "면실유", "면포"],
    "연": ["연필", "연극", "연못", "연기", "연꽃", "연쇄", "연료", "연습", "연속", "연말", "연어"],
    "표": ["표정", "표지판", "표범", "표준", "표적", "표류", "표면", "표현", "표제어"],
    "리": ["리본", "리듬", "리코더", "리모컨", "리조트", "리갈", "리액션", "리필"],
    "이": ["이야기", "이발소", "이유", "이불", "이웃", "이메일", "이탈리아", "이동", "이발기"],
    "기": ["기차", "기린", "기타", "기와", "기구", "기사", "기름", "기적", "기업", "기계"],
    "구": ["구름", "구두", "구슬", "구경", "구조대", "구역", "구경꾼", "구식", "구급차"],
    "음": ["음악", "음식", "음료수", "음성", "음향", "음자리표", "음반", "음원"],
    "호": ["호랑이", "호수", "호두", "호박", "호루라기", "호텔", "호기심", "호아유"],
    "림": ["림보", "림프구", "림프절", "림프관"],
    "님": ["님프", "님카", "님프화"],
    "스": ["스케이트", "스노보드", "스피커", "스파게티", "스폰지", "스마트폰", "스웨터"],
    "키": ["키보드", "키위", "키노트", "키홀더", "키다리", "키스탄"],
    "비": ["비행기", "비누", "비빔밥", "비밀", "비둘기", "비디오", "비버", "비닐공"],
    "지": ["지우개", "지도", "지구", "지하철", "지렁이", "지붕", "지갑"],
    "초": ["초초", "초콜릿", "초초생", "초소", "초록색", "초등학생", "초가집"],
    "풍": ["풍선", "풍차", "풍경", "풍류", "풍물놀이", "풍선껌"],
    "창": ["창문", "창고", "창공", "창작", "창술"],
    "상": ["상자", "상어", "상추", "상점", "상상력", "상태"],
    "문": ["문구점", "문학", "문어", "문살", "문풍지"]
}

MASSIVE_KILLER_DICTIONARY = {
    "륨 계열 💥": [
        "나트륨", "칼륨", "헬륨", "베릴륨", "바륨", "라듐", "루비듐", "세슘", "이테르븀", "페르븀",
        "노벨륨", "플레로븀", "리버모륨", "마이트너륨", "다름슈타튬", "카드뮴", "오스뮴", "로듐", "이리듐"
    ],
    "늄 계열 💥": [
        "플루토늄", "우라늄", "악티늄", "넵튜늄", "알루미늄", "지르코늄", "더브늄", "시보귬", "보륨", "하슘",
        "뢴트게늄", "코페르니슘", "니호늄", "모스코븀", "라돈", "게르마늄", "저마늄", "티타늄"
    ],
    "특수 끝말 💥": [
        "해질녘", "새벽녘", "들녘", "동녘", "서녘", "남녘", "북녘", "저녁녘",
        "모더니즘", "리얼리즘", "메커니즘", "알고리즘", "유턴", "패턴"
    ]
}

ALL_KILLER_WORDS = list(set([w for group in MASSIVE_KILLER_DICTIONARY.values() for w in group]))

# ==========================================
# 🧪 원소 주기율표 데이터 (1~118)
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

ELEMENT_NAMES = [e[2] for e in ELEMENTS_DATA]

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

# ==========================================
# 💥 엄격한 단어 검수 로직
# ==========================================
def is_valid_korean_word(word):
    if len(word) < 2 or not word.isalpha():
        return False

    if word in ELEMENT_NAMES or word in ALL_KILLER_WORDS:
        return True
        
    first_char = word[0]
    if first_char in MEGA_FALLBACK_DICTIONARY and word in MEGA_FALLBACK_DICTIONARY[first_char]:
        return True

    res_json = safe_naver_search(word)
    if res_json:
        for group in res_json.get("items", []):
            for item in group:
                dict_word = item[0][0].strip()
                if dict_word == word:
                    return True

    return False

# ==========================================
# 🤖 AI 탐색 로직 (어휘 폭 대폭 확장)
# ==========================================
def get_bot_response_word(start_chars, used_words, difficulty):
    clean_used = [w.strip() for w in used_words]
    candidates = []

    # 1. API 기반 단어 탐색
    for sc in start_chars:
        res_json = safe_naver_search(sc)
        if res_json:
            for group in res_json.get("items", []):
                for item in group:
                    w = item[0][0].strip()
                    if len(w) >= 2 and w.isalpha() and w[0] in start_chars and w not in clean_used:
                        candidates.append(w)

    # 2. 내장 백업 사전 단어 추가 (풍부한 어휘 보장)
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

# 시작 단어 풀 (50개 이상으로 대폭 확장!)
STARTING_WORDS = [
    "라면", "바다", "하늘", "구름", "기차", "자전거", "호랑이", "비행기", "사과", "기름",
    "나비", "다람쥐", "라디오", "마술", "바나나", "사자", "아카시아", "자두", "차표", "카메라",
    "타이어", "파도", "하마", "이야기", "구슬", "스케이트", "지우개", "초콜릿", "풍선", "상자",
    "가방", "나무", "다리미", "마스크", "바람", "설탕", "아침", "자석", "차창", "카드",
    "타조", "파인애플", "하모니카", "이발소", "연필", "음악", "호수", "비누", "지도", "창문"
]

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
# 📌 네비게이션
# ==========================================
st.sidebar.markdown(f"""
<div class="point-badge">
    💰 {st.session_state.points} P
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("메뉴 선택", [
    "⚔️ 끝말잇기 매치", 
    "🛒 상점",
    "🧪 원소 주기율표 (1~118)",
    "📕 한방 단어 대사전",
    "👤 내 프로필"
])

# ==========================================
# 1. ⚔️ 끝말잇기 매치
# ==========================================
if menu == "⚔️ 끝말잇기 매치":
    st.title("⚔️ 끝말잇기 매치")
    
    col_diff, col_reset = st.columns([3, 1])
    with col_diff:
        difficulty = st.select_slider("⚙️ AI 난이도:", options=["쉬움", "보통", "어려움", "매우 어려움"], value="보통")
    with col_reset:
        st.write(" ")
        if st.button("🔄 게임 재시작"):
            reset_game()
            st.rerun()

    for msg in st.session_state.chat_history:
        avatar = st.session_state.equipped_avatar.split()[0] if msg["role"] == "user" else "🤖"
        st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar).write(msg["text"])

    last_char = st.session_state.last_word[-1]
    allowed_chars = get_allowed_initials(last_char)
    allowed_str = '/'.join(allowed_chars)

    if not st.session_state.game_over:
        user_input = st.chat_input(f"'{allowed_str}' (으)로 시작하는 단어를 입력하세요...")
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
                st.session_state.chat_history.append({"role": "bot", "text": f"❌ **'{user_clean}'** (은)는 사전에 존재하지 않는 지어낸 단어입니다!"})
                st.session_state.game_over = True
            else:
                st.session_state.used_words.append(user_clean)
                st.session_state.last_word = user_clean

                bot_next_chars = get_allowed_initials(user_clean[-1])
                bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, difficulty)

                if bot_word is None:
                    st.session_state.chat_history.append({"role": "bot", "text": f"💥 **'{user_clean}'** 승리! 봇이 대응할 단어를 찾지 못했습니다! (+200P)"})
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
                    st.session_state.chat_history.append({"role": "bot", "text": f"⚡ AI 수비: **'{bot_word}'**! 다음 시작어: **'{next_allowed}'**"})
            st.rerun()

# ==========================================
# 2. 🛒 상점
# ==========================================
elif menu == "🛒 상점":
    st.title("🛒 프리미엄 아이템 상점")
    st.caption("등급별 칭호, 테마, 테두리, 특수 아바타를 구매하고 장착해보세요!")

    HIGH_QUALITY_SHOP = {
        "🏷️ 프리미엄 칭호": [
            ("🎖️ 초보 끝말러", 0, "일반", "기본으로 지급되는 깔끔한 칭호입니다."),
            ("🔥 끝말잇기 제왕", 300, "희귀", "상대를 압도하는 열정의 불꽃 칭호"),
            ("⚡ 광속의 두뇌", 500, "희귀", "빠른 타핑과 두뇌 회전을 상징하는 칭호"),
            ("🎓 국어 국문학 박사", 800, "전설", "모든 단어를 통달한 학자의 칭호"),
            ("👑 신화 속 끝말신", 1500, "신화", "끝말잇기 세계관의 단 하나뿐인 전설")
        ],
        "🎨 고급 테마 배경": [
            ("🔴 다크 레드 테마", 0, "일반", "깔끔한 고대비 다크 레드 디자인"),
            ("⚡ 사이버펑크 네온", 400, "희귀", "네온 그린빛이 도는 미래형 테마"),
            ("🌊 심해의 아틀란티스", 600, "희귀", "깊은 바닷속 고요함을 담은 딥블루 테마"),
            ("🌸 사쿠라 블로섬", 800, "전설", "화사한 핑크빛 오라를 뿜는 감성 테마"),
            ("🔮 심연의 갤럭시", 1000, "전설", "신비로운 보랏빛 우주 디자인"),
            ("👑 로열 골드 레전드", 1500, "신화", "최고급 골드 글로우가 적용된 상위 1% 테마")
        ],
        "🖼️ 테두리 프레임": [
            ("기본 프레임", 0, "일반", "기본 사각 프레임"),
            ("🔴 네온 레드 펄스", 300, "희귀", "선명한 레드 라이닝"),
            ("⚡ 네온 사이버 글레이어", 500, "희귀", "사이언 네온 불빛 효과"),
            ("🔮 공허의 은하수 프레임", 800, "전설", "보랏빛 공허 오라 테두리"),
            ("🔥 불꽃 네온 오라", 1000, "전설", "뜨겁게 타오르는 주황빛 프레임"),
            ("💎 영롱한 다이아몬드", 1200, "신화", "반짝이는 블루 다이아몬드 아우라"),
            ("👑 황금 왕관 프레임", 1500, "신화", "챔피언만을 위한 4px 굵은 골드 레이어")
        ],
        "👤 캐릭터 아바타": [
            ("👤 기본 요원", 0, "일반", "기본 아바타"),
            ("🐱 닌자 고양이", 300, "희귀", "재빠른 신속의 닌자 캣"),
            ("🦊 은둔 사막여우", 500, "희귀", "지혜로운 사막여우 요원"),
            ("👾 사이버 픽셀", 800, "전설", "레트로 감성의 사이버 아바타"),
            ("🐉 전설의 드래곤", 1200, "신화", "강력한 화염을 뿜는 용의 기운"),
            ("👑 황제 펭귄", 1500, "신화", "귀여움과 존엄함을 겸비한 왕")
        ]
    }

    slot_keys = {
        "🏷️ 프리미엄 칭호": "equipped_title",
        "🎨 고급 테마 배경": "equipped_theme",
        "🖼️ 테두리 프레임": "equipped_frame",
        "👤 캐릭터 아바타": "equipped_avatar"
    }

    rarity_colors = {
        "일반": "#94a3b8",
        "희귀": "#38bdf8",
        "전설": "#c084fc",
        "신화": "#fbbf24"
    }

    tabs = st.tabs(list(HIGH_QUALITY_SHOP.keys()))
    for idx, (cat_name, item_list) in enumerate(HIGH_QUALITY_SHOP.items()):
        slot_key = slot_keys[cat_name]
        with tabs[idx]:
            for item_name, price, rarity, desc in item_list:
                r_color = rarity_colors.get(rarity, "#ffffff")
                
                st.markdown(f"""
                <div class="shop-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="background:{r_color}22; color:{r_color}; border:1px solid {r_color}; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:bold;">[{rarity}]</span>
                            <span style="font-size:18px; font-weight:bold; color:#ffffff; margin-left:8px;">{item_name}</span>
                            <p style="margin:6px 0 0 0; font-size:13px; color:#cbd5e1;">{desc}</p>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:#fbbf24; font-weight:bold; font-size:16px;">{price} P</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_space, col_btn = st.columns([4, 1])
                with col_btn:
                    if item_name in st.session_state.inventory:
                        if st.session_state[slot_key] == item_name:
                            st.info("장착 중")
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
                                st.session_state[slot_key] = item_name
                                save_user_data()
                                st.rerun()
                            else:
                                st.error("포인트 부족!")

# ==========================================
# 3. 🧪 원소 주기율표 (1~118)
# ==========================================
elif menu == "🧪 원소 주기율표 (1~118)":
    st.title("🧪 원소 주기율표 (1~118)")
    st.caption("화학 원소 검색 및 끝말잇기 한방 단어 사전 연결")

    search_elem = st.text_input("🔍 원소 이름 또는 기호 검색 (예: H, 수소, Na):", "")
    filtered = [e for e in ELEMENTS_DATA if search_elem in e[2] or search_elem.lower() in e[1].lower()]
    cols = st.columns(4)
    for idx, (num, sym, name, state) in enumerate(filtered):
        with cols[idx % 4]:
            is_k = name.endswith(("륨", "늄", "튬", "슘", "뮴"))
            st.markdown(f"""
            <div class="elem-card">
                <span style="font-size: 12px; color: #94a3b8; font-weight: bold;">No.{num} [{state}]</span>
                <h2 style="margin: 4px 0; color: {cur_theme['accent']}; font-size: 26px;">{sym}</h2>
                <span style="font-size: 17px; font-weight: bold; color: #ffffff;">{name}</span>
                {('<br/><span style="color:#ef4444; font-weight:bold; font-size:12px;">💥 한방단어</span>' if is_k else '')}
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 4. 📕 한방 단어 대사전
# ==========================================
elif menu == "📕 한방 단어 대사전":
    st.title("📕 한방 필살기 단어 사전")
    search_k = st.text_input("🔍 단어 검색:", "")
    if search_k:
        results = [w for w in ALL_KILLER_WORDS if search_k in w]
        cols = st.columns(4)
        for idx, word in enumerate(results):
            with cols[idx % 4]:
                st.markdown(f"<div class='killer-card'>{word}</div>", unsafe_allow_html=True)
    else:
        tabs = st.tabs(list(MASSIVE_KILLER_DICTIONARY.keys()))
        for idx, (cat_name, words) in enumerate(MASSIVE_KILLER_DICTIONARY.items()):
            with tabs[idx]:
                cols = st.columns(4)
                for w_idx, word in enumerate(words):
                    with cols[w_idx % 4]:
                        st.markdown(f"<div class='killer-card'>{word}</div>", unsafe_allow_html=True)

# ==========================================
# 5. 👤 내 프로필
# ==========================================
elif menu == "👤 내 프로필":
    st.title("👤 마이 프로필")
    avatar_icon = st.session_state.equipped_avatar.split()[0]
    st.markdown(f"""
    <div style="padding: 24px; border-radius: 12px; border: {cur_frame}; text-align: center; background: #0f172a; margin-top: 15px; box-shadow: 0 0 20px {cur_theme['glow']};">
        <div style="font-size: 70px;">{avatar_icon}</div>
        <div style="font-size: 18px; font-weight: bold; color: {cur_theme['accent']}; margin-top: 8px;">[{st.session_state.equipped_title}]</div>
        <h2 style="margin: 8px 0; color: #ffffff;">{st.session_state.user_name}</h2>
        <p style="font-size: 15px; color: #ffffff;">🎨 장착 테마: <b>{st.session_state.equipped_theme}</b></p>
        <p style="font-size: 15px; color: #ffffff;">🖼️ 장착 테두리: <b>{st.session_state.equipped_frame}</b></p>
        <p style="font-size: 20px; font-weight: bold; color: #fbbf24;">💰 보유 포인트: {st.session_state.points} P</p>
    </div>
    """, unsafe_allow_html=True)

    new_name = st.text_input("닉네임 변경:", value=st.session_state.user_name)
    if st.button("닉네임 저장"):
        st.session_state.user_name = new_name
        save_user_data()
        st.success("닉네임이 변경되었습니다!")
        st.rerun()
