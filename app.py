import streamlit as st
import requests
import random
import json
import os

st.set_page_config(page_title="TACTICAL WORD CHAIN", page_icon="⚔️", layout="wide")

# ==========================================
# 💾 데이터 영구 저장 및 불러오기
# ==========================================
SAVE_FILE = "user_tactical_data.json"

def load_user_data():
    default_data = {
        "user_name": "요원_01",
        "points": 1500,
        "score": 0,
        "inventory": ["🎖️ 신병 요원", "👤 요원 아바타", "기본 프레임", "🔴 발로란트 레드"],
        "equipped_theme": "🔴 발로란트 레드",
        "equipped_avatar": "👤 요원 아바타",
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
# 🔤 두음법칙 규칙 매핑
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
# 🌐 안정화된 네이버 사전 API
# ==========================================
def safe_naver_search(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = f"https://dict.naver.com/api/search/autocomplete?query={query}&st=11111"
    try:
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

# ==========================================
# 🎨 발로란트 / 롤 택티컬 게이밍 스타일 CSS
# ==========================================
theme_styles = {
    "🔴 발로란트 레드": "background-color: #0f1923; color: #ece8e1; primary-color: #ff4655;",
    "🟢 래디언트 시안": "background-color: #081619; color: #dbf8ff; primary-color: #00f5d4;",
    "🟡 챌린저 골드": "background-color: #12100b; color: #f7e7c4; primary-color: #f59e0b;",
    "🟣 공허의 아칼리": "background-color: #140b24; color: #e9d8a6; primary-color: #a855f7;",
    "⚔️ 밀리터리 카키": "background-color: #191c14; color: #e2e8f0; primary-color: #84cc16;"
}

frame_styles = {
    "기본 프레임": "2px solid #334155",
    "🔴 발로란트 레드 테두리": "3px solid #ff4655",
    "🟢 래디언트 네온 테두리": "3px solid #00f5d4",
    "🟡 챌린저 테두리": "3px solid #f59e0b",
    "🟣 공허 테두리": "3px solid #a855f7",
    "⚔️ 특수부대 테두리": "3px solid #84cc16"
}

active_theme = theme_styles.get(st.session_state.equipped_theme, theme_styles["🔴 발로란트 레드"])
active_frame = frame_styles.get(st.session_state.equipped_frame, frame_styles["기본 프레임"])

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Malgun Gothic', 'Noto Sans KR', sans-serif; }}
    .main {{ {active_theme} }}
    
    .stChatMessage {{ background-color: rgba(255, 255, 255, 0.03) !important; border-radius: 8px !important; margin-bottom: 8px !important; border: 1px solid rgba(255,255,255,0.08); }}
    .stChatMessage p {{ font-size: 19px !important; line-height: 1.5 !important; }}
    
    .stButton>button {{
        background: linear-gradient(135deg, #ff4655 0%, #bd3944 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 900 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        border-radius: 4px !important;
        padding: 10px 24px !important;
        box-shadow: 0 0 15px rgba(255, 70, 85, 0.4);
    }}
    
    .tactical-badge {{
        background: rgba(15, 25, 35, 0.85);
        border: 2px solid #ff4655;
        color: #ff4655;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 10px rgba(255, 70, 85, 0.2);
    }}
    
    .killer-card {{
        background: #1e293b;
        border-left: 4px solid #ef4444;
        padding: 10px;
        margin: 4px 0;
        font-weight: bold;
        color: #f8fafc;
        font-size: 16px;
    }}
    
    .dict-card {{
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #3b82f6;
        border-radius: 6px;
        padding: 12px;
        margin: 8px 0;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧪 원소 주기율표 데이터 (1~118)
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
# 💥 한방 단어 사전 (진짜 표준 명사만)
# ==========================================
MASSIVE_KILLER_DICTIONARY = {
    "륨 계열 (25개) 💥": [
        "나트륨", "칼륨", "헬륨", "베릴륨", "바륨", "라듐", "루비듐", "세슘", "이테르븀", "페르븀",
        "노벨륨", "플레로븀", "리버모륨", "마이트너륨", "다름슈타튬", "카드뮴", "오스뮴", "로듐", "이리듐",
        "탈륨", "세륨", "테르븀", "에르븀", "툴륨", "하프늄"
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
    "특수 끝말 (녘/즘/븀) (25개) 💥": [
        "해질녘", "새벽녘", "들녘", "어스름녘", "동녘", "서녘", "남녘", "북녘", "밤녘", "날녘",
        "아침녘", "저녁녘", "모더니즘", "리얼리즘", "메커니즘", "알고리즘", "네오디뮴", "퀴륨", "버클륨",
        "홀뮴", "콜롬븀", "테네신", "오가네손", "아스타틴", "크립톤"
    ]
}

ALL_KILLER_WORDS = list(set([w for group in MASSIVE_KILLER_DICTIONARY.values() for w in group]))

# ==========================================
# 📚 백업 실사용 사전 ('표', '리', '기' 등 모든 어휘 포함)
# ==========================================
MEGA_FALLBACK_DICTIONARY = {
    "표": ["표정", "표지판", "표범", "표준", "표적", "표류", "표면", "표현", "표제어", "표인"],
    "리": ["리본", "리듬", "리코더", "리모컨", "리조트", "리갈", "리액션", "리필", "리얼리티", "리허설"],
    "이": ["이야기", "이발소", "이유", "이불", "이웃", "이메일", "이탈리아", "이동", "이구아나", "이발사"],
    "기": ["기차", "기린", "기타", "기와", "기구", "기사", "기름", "기적", "기업", "기계"],
    "차": ["차표", "차창", "차나무", "차고지", "차선", "차돌", "차량", "차고", "차지"],
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
# 🎮 랜덤 시작 단어 풀 (50개 이상)
# ==========================================
STARTING_WORDS = [
    "바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "무지개", 
    "사과", "바나나", "표지판", "스마트폰", "태양이", "자동차", "우주선", "카메라", "도서관", "선풍기",
    "아이스크림", "초콜릿", "피자", "햄버거", "고양이", "강아지", "돌고래", "독수리", "해바라기", "장미꽃",
    "축구공", "농구공", "야구방망이", "체육관", "운동장", "수영장", "박물관", "미술관", "영화관", "백화점",
    "편의점", "지하철", "고속버스", "오토바이", "헬리콥터", "잠수함", "망원경", "현미경", "계산기", "시계"
]

# ==========================================
# 🤖 봇 인공지능 로직 (난이도 완전 적용)
# ==========================================
def is_valid_korean_word(word):
    res_json = safe_naver_search(word)
    if res_json:
        for group in res_json.get("items", []):
            for item in group:
                if item[0][0] == word: return True
    return len(word) >= 2 and word.isalpha()

def get_bot_response_word(start_chars, used_words, difficulty="보통"):
    clean_used = [w.strip() for w in used_words]
    candidates = []

    # 1. 온라인 사전 검색
    for sc in start_chars:
        res_json = safe_naver_search(sc)
        if res_json:
            for group in res_json.get("items", []):
                for item in group:
                    w = item[0][0].strip()
                    if len(w) >= 2 and w.isalpha() and w[0] in start_chars and w not in clean_used:
                        candidates.append(w)

    # 2. 오프라인 백업 단어장 검색
    for sc in start_chars:
        if sc in MEGA_FALLBACK_DICTIONARY:
            for fw in MEGA_FALLBACK_DICTIONARY[sc]:
                if fw not in clean_used:
                    candidates.append(fw)

    candidates = list(set(candidates))
    
    # 단어가 없으면 지어내지 않고 패배 인정
    if not candidates:
        return None

    killer_endings = ("륨", "늄", "튬", "슘", "뮴", "븀", "녘", "즘")
    safe_candidates = [w for w in candidates if w not in ALL_KILLER_WORDS and not w.endswith(killer_endings)]
    killer_candidates = [w for w in candidates if w in ALL_KILLER_WORDS or w.endswith(killer_endings)]

    # 난이도 제어 로직
    if difficulty == "쉬움":
        # 안전한 짧은 단어 우선 선택
        if safe_candidates:
            return random.choice(safe_candidates)
        return random.choice(candidates)
        
    elif difficulty == "보통":
        # 기본 공격 확률 (10% 확률로 한방 단어)
        if killer_candidates and random.random() < 0.1:
            return random.choice(killer_candidates)
        return random.choice(safe_candidates) if safe_candidates else random.choice(candidates)
        
    elif difficulty == "어려움":
        # 공격적 (50% 확률로 한방 단어)
        if killer_candidates and random.random() < 0.5:
            return random.choice(killer_candidates)
        return random.choice(safe_candidates) if safe_candidates else random.choice(candidates)
        
    elif difficulty == "매우 어려움":
        # 무조건 한방 단어 최우선 공격
        if killer_candidates:
            return random.choice(killer_candidates)
        return random.choice(safe_candidates) if safe_candidates else random.choice(candidates)

    return random.choice(candidates)

def reset_game():
    first_word = random.choice(STARTING_WORDS)
    st.session_state.chat_history = [
        {"role": "bot", "text": f"🎯 **[TACTICAL MATCH MATCH]** 첫 단어는 **'{first_word}'**! 다음 단어를 입력하라. (**'{first_word[-1]}'** 시작)"}
    ]
    st.session_state.last_word = first_word
    st.session_state.used_words = [first_word]
    st.session_state.game_over = False
    st.session_state.game_turn = 0

if "chat_history" not in st.session_state: reset_game()

# ==========================================
# 📌 사이드바 (포인트 & 메인 메뉴)
# ==========================================
st.sidebar.markdown(f"""
<div class="tactical-badge">
    CREDITS: {st.session_state.points} P
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("COMMAND CENTER", [
    "⚔️ 끝말잇기 매치", 
    "📕 한방 단어 대사전",
    "🔍 네이버 사전 정밀 검색",
    "🛒 택티컬 상점 (40종)",
    "👤 요원 프로필 & 테마 설정",
    "🧪 원소 주기율표 (1~118)"
])

# ==========================================
# 1. ⚔️ 끝말잇기 매치
# ==========================================
if menu == "⚔️ 끝말잇기 매치":
    st.title("⚔️ TACTICAL WORD CHAIN MATCH")
    
    col_diff, col_reset = st.columns([3, 1])
    with col_diff:
        difficulty = st.select_slider("⚙️ 봇 인공지능 난이도 설정:", options=["쉬움", "보통", "어려움", "매우 어려움"], value="보통")
    with col_reset:
        st.write(" ")
        if st.button("🔄 매치 리셋"):
            reset_game()
            st.rerun()

    st.caption(f"턴 진행: {st.session_state.game_turn} | 선택 난이도: {difficulty} | 두음법칙 자동 적용 중")

    for msg in st.session_state.chat_history:
        avatar = st.session_state.equipped_avatar.split()[0] if msg["role"] == "user" else "🤖"
        st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar).write(msg["text"])

    last_char = st.session_state.last_word[-1]
    allowed_chars = get_allowed_initials(last_char)
    allowed_str = '/'.join(allowed_chars)

    if not st.session_state.game_over:
        user_input = st.chat_input(f"'{allowed_str}' (으)로 시작하는 단어 입력...")
        if user_input:
            user_input_clean = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "text": user_input_clean})

            if len(user_input_clean) < 2:
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 최소 2글자 이상이어야 합니다!"})
                st.session_state.game_over = True
            elif user_input_clean[0] not in allowed_chars:
                st.session_state.chat_history.append({"role": "bot", "text": f"❌ 단어가 일치하지 않습니다! **'{allowed_str}'** 로 시작해야 합니다."})
                st.session_state.game_over = True
            elif user_input_clean in st.session_state.used_words:
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 이미 사용된 중복 단어입니다!"})
                st.session_state.game_over = True
            elif not is_valid_korean_word(user_input_clean):
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 국어사전에 등재되지 않은 단어입니다!"})
                st.session_state.game_over = True
            else:
                st.session_state.used_words.append(user_input_clean)
                st.session_state.last_word = user_input_clean
                st.session_state.game_turn += 1

                bot_next_chars = get_allowed_initials(user_input_clean[-1])
                bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, difficulty)

                if bot_word is None:
                    st.session_state.chat_history.append({"role": "bot", "text": f"💥 **'{user_input_clean}'** 공격 성공! 봇이 단어를 찾지 못했습니다. 매치 승리! 🎉 (+150P)"})
                    st.session_state.points += 150
                    st.session_state.game_over = True
                    save_user_data()
                    st.balloons()
                else:
                    st.session_state.used_words.append(bot_word)
                    st.session_state.last_word = bot_word
                    st.session_state.points += 10
                    save_user_data()
                    next_allowed = '/'.join(get_allowed_initials(bot_word[-1]))
                    st.session_state.chat_history.append({"role": "bot", "text": f"⚡ **'{user_input_clean}'** ➔ 봇의 수비: **'{bot_word}'**! 다음 목표: **'{next_allowed}'**"})
            st.rerun()

# ==========================================
# 2. 📕 한방 단어 대사전
# ==========================================
elif menu == "📕 한방 단어 대사전":
    st.title("📕 한방 단어 대사전")
    st.write("상대를 제압할 수 있는 검증된 끝말잇기 필살기 데이터베이스입니다.")
    
    search_k = st.text_input("🔍 대사전 내 필살기 검색:", "")
    
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
# 3. 🔍 네이버 사전 정밀 검색
# ==========================================
elif menu == "🔍 네이버 사전 정밀 검색":
    st.title("🔍 네이버 사전 실시간 검증 시스템")
    st.write("단어가 국어사전에 실제 등재되어 있는지 즉시 검색합니다.")
    
    search_q = st.text_input("검색 단어 입력:", "")
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
                st.success(f"검색 성공 ({len(found_words)}건 검색됨)")
                for w in found_words:
                    is_killer = " 💥 [한방 단어]" if w in ALL_KILLER_WORDS or w.endswith(("륨", "늄", "튬", "슘", "뮴", "븀", "녘", "즘")) else ""
                    st.markdown(f"""
                    <div class="dict-card">
                        <h3 style="margin:0; color:#00f5d4;">{w} {is_killer}</h3>
                        <p style="margin:4px 0 0 0; color:#94a3b8;">네이버 국어사전 검증 완료 명사</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("사전에 존재하지 않는 단어입니다.")
        else:
            st.warning("네이버 사전 통신 네트워크 상태를 확인하세요.")

# ==========================================
# 4. 🛒 택티컬 상점 (40종 아이템)
# ==========================================
elif menu == "🛒 택티컬 상점 (40종)":
    st.title("🛒 TACTICAL ITEM SHOP")
    st.write("아이템을 구매하고 장착하면 앱 테마, 테두리, 아바타, 칭호가 즉시 변경됩니다.")

    shop_items_data = {
        "🏷️ 칭호 (10종)": [
            ("🎖️ 신병 요원", 0), ("⚡ 래디언트 게이머", 150), ("⚔️ 불멸의 듀얼리스트", 300),
            ("🧪 원소 연금술사", 450), ("👑 국어 챌린저", 600), ("🎯 100% 한방 사수", 750),
            ("🔥 티키타카 마스터", 900), ("🛡️ 철벽 수비대장", 1000), ("🚀 우주 전설", 1200), ("🏆 바론 베이더", 1500)
        ],
        "👤 요원 아바타 (10종)": [
            ("👤 요원 아바타", 0), ("⚡ 네온 아바타", 150), ("🦁 제드 아바타", 300),
            ("🤖 로봇 요원", 450), ("🐉 드래곤 요원", 600), ("🐱 시커먼 냥이", 750),
            ("🐶 늑대 요원", 750), ("🦊 미라지 요원", 900), ("🐯 뱅가드 타이거", 1000), ("👑 암살자", 1500)
        ],
        "🖼️ 테두리 프레임 (10종)": [
            ("기본 프레임", 0), ("🔴 발로란트 레드 테두리", 150), ("🟢 래디언트 네온 테두리", 300),
            ("🟡 챌린저 테두리", 450), ("🟣 공허 테두리", 600), ("⚔️ 특수부대 테두리", 750),
            ("❄️ 얼음 테두리", 900), ("⚡ 번개 테두리", 1000), ("🌿 카모 테두리", 1200), ("🔮 흑마법 테두리", 1500)
        ],
        "🎨 UI 테마 (10종)": [
            ("🔴 발로란트 레드", 0), ("🟢 래디언트 시안", 200), ("🟡 챌린저 골드", 400),
            ("🟣 공허의 아칼리", 600), ("⚔️ 밀리터리 카키", 800)
        ]
    }

    slot_keys = {
        "🏷️ 칭호 (10종)": "equipped_title",
        "👤 요원 아바타 (10종)": "equipped_avatar",
        "🖼️ 테두리 프레임 (10종)": "equipped_frame",
        "🎨 UI 테마 (10종)": "equipped_theme"
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
                            st.success("장착 완료")
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
# 5. 👤 요원 프로필 & 테마 설정
# ==========================================
elif menu == "👤 요원 프로필 & 테마 설정":
    st.title("👤 AGENT PROFILE")
    
    st.subheader("✏️ 요원 코드네임 변경")
    new_username = st.text_input("새 코드네임:", value=st.session_state.user_name)
    if st.button("💾 코드네임 저장"):
        if new_username.strip():
            st.session_state.user_name = new_username.strip()
            save_user_data()
            st.success("코드네임 업데이트 완료!")
            st.rerun()

    st.markdown("---")
    avatar_icon = st.session_state.equipped_avatar.split()[0]
    st.markdown(f"""
    <div style="padding: 25px; border-radius: 8px; border: {active_frame}; text-align: center; margin-top: 15px; background: rgba(0,0,0,0.4);">
        <div style="font-size: 75px;">{avatar_icon}</div>
        <div style="font-size: 18px; font-weight: bold; color: #ff4655; margin-top: 10px;">[{st.session_state.equipped_title}]</div>
        <h1 style="margin: 10px 0; font-family: 'Orbitron';">{st.session_state.user_name}</h1>
        <p style="font-size: 18px;">🎨 장착 테마: <b>{st.session_state.equipped_theme}</b></p>
        <p style="font-size: 18px;">🖼️ 장착 테두리: <b>{st.session_state.equipped_frame}</b></p>
        <p style="font-size: 22px; font-weight: bold; color: #f59e0b;">💰 CREDITS: {st.session_state.points} P</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. 🧪 원소 주기율표 (1~118)
# ==========================================
elif menu == "🧪 원소 주기율표 (1~118)":
    st.title("🧪 원소 주기율표 (1~118 DATABASE)")
    search_elem = st.text_input("원소 명칭 또는 기호 검색 (예: H, 수소, Na):", "")
    
    filtered = [e for e in ELEMENTS_DATA if search_elem in e[2] or search_elem.lower() in e[1].lower()]
    cols = st.columns(3)
    for idx, (num, sym, name, state, cat) in enumerate(filtered):
        with cols[idx % 3]:
            is_k = name.endswith(("륨", "늄", "튬", "슘", "뮴"))
            st.markdown(f"""
            <div style="border: 2px solid {'#ef4444' if is_k else '#475569'}; border-radius: 6px; padding: 12px; margin-bottom: 10px; text-align: center; background: rgba(0,0,0,0.3);">
                <span style="font-size: 13px; color: #94a3b8;">No.{num} [{cat}]</span>
                <h2 style="margin: 4px 0; color: #00f5d4; font-family: 'Orbitron';">{sym}</h2>
                <span style="font-size: 20px; font-weight: bold; color: #f8fafc;">{name}</span>
                {('<br/><span style="color:#ef4444; font-weight:bold; font-size:14px;">💥 한방 단어</span>' if is_k else '')}
            </div>
            """, unsafe_allow_html=True)
