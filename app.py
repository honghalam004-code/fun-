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
        "inventory": ["🎖️ 신병", "👤 기본 요원", "기본 프레임", "🔴 레드 테마"],
        "equipped_theme": "🔴 레드 테마",
        "equipped_avatar": "👤 기본 요원",
        "equipped_frame": "기본 프레임",
        "equipped_title": "🎖️ 신병",
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
# 🎨 선명한 고대비 UI / 테마 엔진
# ==========================================
THEME_CONFIGS = {
    "🔴 레드 테마": {
        "bg_css": "linear-gradient(135deg, #1a0509 0%, #0f1923 100%)",
        "card_bg": "#1e293b",
        "accent": "#ff4655",
        "text": "#ffffff"
    },
    "🟢 네온 시안": {
        "bg_css": "linear-gradient(135deg, #021a17 0%, #061417 100%)",
        "card_bg": "#1e293b",
        "accent": "#00f5d4",
        "text": "#ffffff"
    },
    "🟡 챌린저 골드": {
        "bg_css": "linear-gradient(135deg, #1c1303 0%, #120e07 100%)",
        "card_bg": "#1e293b",
        "accent": "#fbbf24",
        "text": "#ffffff"
    },
    "🟣 퍼플 보이드": {
        "bg_css": "linear-gradient(135deg, #170829 0%, #0f081c 100%)",
        "card_bg": "#1e293b",
        "accent": "#c084fc",
        "text": "#ffffff"
    },
    "🌸 사쿠라 핑크": {
        "bg_css": "linear-gradient(135deg, #2a0818 0%, #15050f 100%)",
        "card_bg": "#1e293b",
        "accent": "#f472b6",
        "text": "#ffffff"
    },
    "🌊 다크 오션": {
        "bg_css": "linear-gradient(135deg, #031b29 0%, #050f1a 100%)",
        "card_bg": "#1e293b",
        "accent": "#38bdf8",
        "text": "#ffffff"
    }
}

FRAME_STYLES = {
    "기본 프레임": "2px solid #64748b",
    "🔴 강렬한 레드 테두리": "3px solid #ff4655",
    "🟢 빛나는 네온 테두리": "3px solid #00f5d4",
    "🟡 황금 챔피언 테두리": "3px solid #fbbf24",
    "🟣 공허의 아우라 테두리": "3px solid #c084fc",
    "💎 다이아몬드 테두리": "3px solid #38bdf8",
    "🔥 불꽃 네온 테두리": "3px solid #f97316"
}

cur_theme = THEME_CONFIGS.get(st.session_state.equipped_theme, THEME_CONFIGS["🔴 레드 테마"])
cur_frame = FRAME_STYLES.get(st.session_state.equipped_frame, FRAME_STYLES["기본 프레임"])

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');

    * {{
        font-family: 'Pretendard', sans-serif;
    }}

    /* 전체 배경 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background: {cur_theme['bg_css']} !important;
        color: #ffffff !important;
    }}
    
    /* 사이드바 */
    [data-testid="stSidebar"] {{
        background-color: #090d16 !important;
        border-right: 2px solid {cur_theme['accent']}55;
    }}
    
    /* 본문 텍스트 강제 흰색 */
    p, span, label, div, .stMarkdown {{
        color: #f8fafc !important;
    }}
    
    h1, h2, h3, h4 {{
        color: #ffffff !important;
        font-weight: 800 !important;
    }}

    /* 채팅 메시지 패널 */
    .stChatMessage {{
        background-color: #1e293b !important;
        border-radius: 12px !important;
        border: 1px solid {cur_theme['accent']}aa !important;
    }}
    .stChatMessage p {{
        color: #ffffff !important;
        font-size: 16px !important;
    }}

    /* 💥 [핵심] 입력창(st.chat_input & input) 타핑 글씨 선명하게 고정 */
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
        border-radius: 10px !important;
    }}

    /* 일반 버튼 */
    .stButton>button {{
        background: {cur_theme['accent']} !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
    }}
    .stButton>button:hover {{
        filter: brightness(1.2);
    }}
    
    /* 포인트 표시 배지 */
    .point-badge {{
        background: #0f172a;
        border: 2px solid {cur_theme['accent']};
        color: {cur_theme['accent']} !important;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 15px;
    }}

    /* 사전 카드 디자인 */
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

    /* 상점 품목 카드 */
    .shop-item-card {{
        background-color: #1e293b !important;
        border: 1px solid {cur_theme['accent']}66;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
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
# 📕 한방 단어 100선
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

MEGA_FALLBACK_DICTIONARY = {
    "표": ["표정", "표지판", "표범", "표준", "표적", "표류", "표면", "표현", "표제어"],
    "차": ["차표", "차창", "차나무", "차고지", "차선", "차돌", "차량", "차고", "차지"],
    "리": ["리본", "리듬", "리코더", "리모컨", "리조트", "리갈", "리액션", "리필"],
    "이": ["이야기", "이발소", "이유", "이불", "이웃", "이메일", "이탈리아", "이동"],
    "기": ["기차", "기린", "기타", "기와", "기구", "기사", "기름", "기적", "기업"],
    "구": ["구름", "구두", "구슬", "구경", "구조대", "구역", "구경꾼", "구식"],
    "음": ["음악", "음식", "음료수", "음성", "음향", "음자리표", "음반"],
    "바": ["바다", "바나나", "바구니", "바람", "바위", "바질", "바코드"],
    "다": ["다람쥐", "다리", "다리미", "다이아몬드", "다이빙", "다짐"],
    "자": ["자전거", "자두", "자동차", "자석", "자라", "자존심", "자연"],
    "호": ["호랑이", "호수", "호두", "호박", "호루라기", "호텔", "호기심"],
    "사": ["사자", "사과", "사슴", "사탕", "사이다", "사막", "사람"]
}

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

STARTING_WORDS = ["바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "사과", "차표"]

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
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 사전에 존재하지 않는 단어입니다!"})
                st.session_state.game_over = True
            else:
                st.session_state.used_words.append(user_clean)
                st.session_state.last_word = user_clean

                bot_next_chars = get_allowed_initials(user_clean[-1])
                bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, difficulty)

                if bot_word is None:
                    st.session_state.chat_history.append({"role": "bot", "text": f"💥 **'{user_clean}'** 승리! 대응 단어가 없습니다. (+200P)"})
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
# 2. 🛒 상점 (확장된 아이템 라인업)
# ==========================================
elif menu == "🛒 상점":
    st.title("🛒 아이템 상점")
    st.caption("획득한 포인트로 마음에 드는 스타일과 칭호를 구매해 보세요!")

    shop_data = {
        "🏷️ 칭호": [
            ("🎖️ 신병", 0), ("🔥 끝말잇기 제왕", 200), ("⚡ 빛의 속도", 300), 
            ("🎓 국어대학사", 500), ("💎 챌린저 1위", 800), ("👑 전설의 창시자", 1200)
        ],
        "🎨 배경 테마": [
            ("🔴 레드 테마", 0), ("🟢 네온 시안", 300), ("🟡 챌린저 골드", 500), 
            ("🟣 퍼플 보이드", 700), ("🌸 사쿠라 핑크", 900), ("🌊 다크 오션", 1000)
        ],
        "🖼️ 테두리 프레임": [
            ("기본 프레임", 0), ("🔴 강렬한 레드 테두리", 200), ("🟢 빛나는 네온 테두리", 400),
            ("🟡 황금 챔피언 테두리", 600), ("🟣 공허의 아우라 테두리", 800), 
            ("💎 다이아몬드 테두리", 1000), ("🔥 불꽃 네온 테두리", 1200)
        ],
        "👤 아바타": [
            ("👤 기본 요원", 0), ("🐱 닌자 캣", 200), ("🦊 사막여우", 300), 
            ("🐉 드래곤 Master", 500), ("👾 사이버 픽셀", 700), ("👑 국왕 펭귄", 1000)
        ]
    }

    slot_keys = {
        "🏷️ 칭호": "equipped_title",
        "🎨 배경 테마": "equipped_theme",
        "🖼️ 테두리 프레임": "equipped_frame",
        "👤 아바타": "equipped_avatar"
    }

    tabs = st.tabs(list(shop_data.keys()))
    for idx, (cat_name, item_list) in enumerate(shop_data.items()):
        slot_key = slot_keys[cat_name]
        with tabs[idx]:
            for item_name, price in item_list:
                st.markdown(f"""
                <div class="shop-item-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 18px; font-weight: bold; color: #ffffff;">{item_name}</span>
                            <br/><span style="color: #fbbf24; font-size: 14px; font-weight: bold;">가격: {price} P</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([4, 1])
                with c2:
                    if item_name in st.session_state.inventory:
                        if st.session_state[slot_key] == item_name:
                            st.info("장착중")
                        else:
                            if st.button("장착하기", key=f"eq_{cat_name}_{item_name}"):
                                st.session_state[slot_key] = item_name
                                save_user_data()
                                st.rerun()
                    else:
                        if st.button(f"구매하기 ({price}P)", key=f"buy_{cat_name}_{item_name}"):
                            if st.session_state.points >= price:
                                st.session_state.points -= price
                                st.session_state.inventory.append(item_name)
                                st.session_state[slot_key] = item_name
                                save_user_data()
                                st.rerun()
                            else:
                                st.error("포인트 부족!")

# ==========================================
# 3. 📕 한방 단어 대사전
# ==========================================
elif menu == "📕 한방 단어 대사전":
    st.title("📕 한방 단어 대사전")
    search_k = st.text_input("🔍 사전 검색:", "")
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
# 4. 👤 내 프로필
# ==========================================
elif menu == "👤 내 프로필":
    st.title("👤 내 프로필 설정")
    
    avatar_icon = st.session_state.equipped_avatar.split()[0]
    st.markdown(f"""
    <div style="padding: 24px; border-radius: 12px; border: {cur_frame}; text-align: center; background: #0f172a; margin-top: 15px;">
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
        st.success("변경되었습니다!")
        st.rerun()
