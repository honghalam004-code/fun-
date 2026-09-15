import streamlit as st
import requests
import random
import json
import os

st.set_page_config(page_title="TACTICAL WORD CHAIN", page_icon="⚔️", layout="wide")

# ==========================================
# 💾 데이터 저장 및 불러오기
# ==========================================
SAVE_FILE = "user_tactical_data.json"

def load_user_data():
    default_data = {
        "user_name": "요원_01",
        "points": 2000,
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
# 🎨 다이나믹 테마 & 배경 스타일 정의
# ==========================================
THEME_PALETTES = {
    "🔴 발로란트 레드": {
        "bg": "#0f1923", "card": "#1e293b", "accent": "#ff4655", "text": "#ece8e1", "border": "#ff4655"
    },
    "🟢 래디언트 시안": {
        "bg": "#061417", "card": "#0c2429", "accent": "#00f5d4", "text": "#dbf8ff", "border": "#00f5d4"
    },
    "🟡 챌린저 골드": {
        "bg": "#120e07", "card": "#241c0e", "accent": "#f59e0b", "text": "#f7e7c4", "border": "#f59e0b"
    },
    "🟣 공허의 아칼리": {
        "bg": "#0f081c", "card": "#1e1038", "accent": "#a855f7", "text": "#e9d8a6", "border": "#a855f7"
    },
    "⚔️ 밀리터리 카키": {
        "bg": "#141710", "card": "#22261b", "accent": "#84cc16", "text": "#e2e8f0", "border": "#84cc16"
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

cur_palette = THEME_PALETTES.get(st.session_state.equipped_theme, THEME_PALETTES["🔴 발로란트 레드"])
cur_frame = FRAME_STYLES.get(st.session_state.equipped_frame, FRAME_STYLES["기본 프레임"])

# 전체 배경 및 요소 스타일 강제 적용
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {cur_palette['bg']} !important;
        color: {cur_palette['text']} !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.4) !important;
        border-right: 1px solid {cur_palette['accent']}33;
    }}
    
    .stChatMessage {{
        background-color: {cur_palette['card']} !important;
        border-radius: 8px !important;
        border: 1px solid {cur_palette['accent']}44 !important;
        color: {cur_palette['text']} !important;
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, {cur_palette['accent']} 0%, #000000 150%) !important;
        color: #ffffff !important;
        border: 1px solid {cur_palette['accent']} !important;
        font-weight: 800 !important;
        border-radius: 4px !important;
        box-shadow: 0 0 10px {cur_palette['accent']}44;
    }}
    
    .tactical-badge {{
        background: {cur_palette['card']};
        border: 2px solid {cur_palette['accent']};
        color: {cur_palette['accent']};
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 15px;
    }}

    .shop-card {{
        background: {cur_palette['card']};
        border: 1px solid {cur_palette['accent']}66;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔤 두음법칙 매핑
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
# 📚 방대해진 내장 사전 (네이버 오류 방어용)
# ==========================================
MEGA_FALLBACK_DICTIONARY = {
    "표": ["표정", "표지판", "표범", "표준", "표적", "표류", "표면", "표현", "표제어", "표상", "표의자", "표목"],
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

# 네트워크 에러가 나도 절대 안내창 안 띄우고 내부 사전으로 처리
def safe_naver_search(query):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    url = f"https://dict.naver.com/api/search/autocomplete?query={query}&st=11111"
    try:
        res = requests.get(url, headers=headers, timeout=1.5)
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
    # 네트워크 실패 시 오프라인 데이터 또는 한국어 규격 검증
    first_char = word[0]
    if first_char in MEGA_FALLBACK_DICTIONARY and word in MEGA_FALLBACK_DICTIONARY[first_char]:
        return True
    return len(word) >= 2 and word.isalpha()

# ==========================================
# 🤖 AI 봇 단어 탐색 (난이도 완전 제어)
# ==========================================
ALL_KILLER_WORDS = ["나트륨", "헬륨", "칼륨", "플루토늄", "우라늄", "해질녘", "리얼리즘", "알고리즘", "네오디뮴"]

def get_bot_response_word(start_chars, used_words, difficulty):
    clean_used = [w.strip() for w in used_words]
    candidates = []

    # 1. 네이버 사전 조율
    for sc in start_chars:
        res_json = safe_naver_search(sc)
        if res_json:
            for group in res_json.get("items", []):
                for item in group:
                    w = item[0][0].strip()
                    if len(w) >= 2 and w.isalpha() and w[0] in start_chars and w not in clean_used:
                        candidates.append(w)

    # 2. 오프라인 백업 사전 자동 연동 (네이버 실패 시 무조건 보장)
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

    # 난이도 반영
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

STARTING_WORDS = ["바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "사과", "차표", "표지판"]

def reset_game():
    first_word = random.choice(STARTING_WORDS)
    st.session_state.chat_history = [
        {"role": "bot", "text": f"🎯 첫 단어: **'{first_word}'**! 다음 단어를 입력하세요. (**'{first_word[-1]}'** 로 시작)"}
    ]
    st.session_state.last_word = first_word
    st.session_state.used_words = [first_word]
    st.session_state.game_over = False

if "chat_history" not in st.session_state: reset_game()

# ==========================================
# 📌 사이드바 메뉴
# ==========================================
st.sidebar.markdown(f"""
<div class="tactical-badge">
    CREDITS: {st.session_state.points} P
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("COMMAND CENTER", [
    "⚔️ 끝말잇기 매치", 
    "🛒 택티컬 상점 (실시간 반영)",
    "👤 프로필 & 스타일 설정"
])

# ==========================================
# 1. ⚔️ 끝말잇기 매치
# ==========================================
if menu == "⚔️ 끝말잇기 매치":
    st.title("⚔️ TACTICAL WORD CHAIN MATCH")
    
    col_diff, col_reset = st.columns([3, 1])
    with col_diff:
        difficulty = st.select_slider("⚙️ 봇 난이도 조절:", options=["쉬움", "보통", "어려움", "매우 어려움"], value="보통")
    with col_reset:
        st.write(" ")
        if st.button("🔄 게임 리셋"):
            reset_game()
            st.rerun()

    for msg in st.session_state.chat_history:
        avatar = st.session_state.equipped_avatar.split()[0] if msg["role"] == "user" else "🤖"
        st.chat_message("user" if msg["role"] == "user" else "assistant", avatar=avatar).write(msg["text"])

    last_char = st.session_state.last_word[-1]
    allowed_chars = get_allowed_initials(last_char)
    allowed_str = '/'.join(allowed_chars)

    if not st.session_state.game_over:
        user_input = st.chat_input(f"'{allowed_str}' (으)로 시작하는 단어...")
        if user_input:
            user_clean = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "text": user_clean})

            if len(user_clean) < 2:
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 2글자 이상 입력하세요!"})
                st.session_state.game_over = True
            elif user_clean[0] not in allowed_chars:
                st.session_state.chat_history.append({"role": "bot", "text": f"❌ 단어 불일치! **'{allowed_str}'** 로 시작해야 합니다."})
                st.session_state.game_over = True
            elif user_clean in st.session_state.used_words:
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 중복 단어입니다!"})
                st.session_state.game_over = True
            elif not is_valid_korean_word(user_clean):
                st.session_state.chat_history.append({"role": "bot", "text": "❌ 사전 미등재 단어입니다!"})
                st.session_state.game_over = True
            else:
                st.session_state.used_words.append(user_clean)
                st.session_state.last_word = user_clean

                bot_next_chars = get_allowed_initials(user_clean[-1])
                bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, difficulty)

                if bot_word is None:
                    st.session_state.chat_history.append({"role": "bot", "text": f"💥 **'{user_clean}'** 성공! 봇이 단어를 찾지 못했습니다. 승리! (+200P)"})
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
                    st.session_state.chat_history.append({"role": "bot", "text": f"⚡ 봇: **'{bot_word}'**! 다음: **'{next_allowed}'**"})
            st.rerun()

# ==========================================
# 2. 🛒 택티컬 상점 (실시간 배경 반영)
# ==========================================
elif menu == "🛒 택티컬 상점 (실시간 반영)":
    st.title("🛒 TACTICAL ITEM SHOP")
    st.caption("아이템을 구매하고 장착하면 전체 UI 색상과 배경 테마가 즉시 바뀝니다.")

    shop_data = {
        "🎨 전체 UI 배경 테마": [
            ("🔴 발로란트 레드", 0), ("🟢 래디언트 시안", 300), 
            ("🟡 챌린저 골드", 500), ("🟣 공허의 아칼리", 700), ("⚔️ 밀리터리 카키", 900)
        ],
        "🖼️ 요원 테두리": [
            ("기본 프레임", 0), ("🔴 발로란트 레드 테두리", 200), ("🟢 래디언트 네온 테두리", 400),
            ("🟡 챌린저 테두리", 600), ("🟣 공허 테두리", 800), ("⚔️ 특수부대 테두리", 1000)
        ],
        "👤 아바타": [
            ("👤 요원 아바타", 0), ("⚡ 네온 아바타", 200), ("🦁 제드 아바타", 400),
            ("🤖 로봇 요원", 600), ("👑 암살자", 1000)
        ]
    }

    slot_keys = {
        "🎨 전체 UI 배경 테마": "equipped_theme",
        "🖼️ 요원 테두리": "equipped_frame",
        "👤 아바타": "equipped_avatar"
    }

    tabs = st.tabs(list(shop_data.keys()))
    for idx, (cat_name, item_list) in enumerate(shop_data.items()):
        slot_key = slot_keys[cat_name]
        with tabs[idx]:
            for item_name, price in item_list:
                st.markdown(f"""
                <div class="shop-card">
                    <h3 style="margin:0;">{item_name}</h3>
                    <p style="margin:5px 0;">가격: <b>{price} P</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 4])
                with c1:
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
                                save_user_data()
                                st.rerun()
                            else:
                                st.error("포인트가 부족합니다!")

# ==========================================
# 3. 👤 프로필 설정
# ==========================================
elif menu == "👤 프로필 & 스타일 설정":
    st.title("👤 요원 프로필")
    
    avatar_icon = st.session_state.equipped_avatar.split()[0]
    st.markdown(f"""
    <div style="padding: 30px; border-radius: 12px; border: {cur_frame}; text-align: center; background: {cur_palette['card']};">
        <div style="font-size: 80px;">{avatar_icon}</div>
        <div style="font-size: 20px; font-weight: bold; color: {cur_palette['accent']}; margin-top: 10px;">[{st.session_state.equipped_title}]</div>
        <h1 style="margin: 10px 0; font-family: 'Orbitron';">{st.session_state.user_name}</h1>
        <p style="font-size: 18px;">🎨 적용 테마: <b>{st.session_state.equipped_theme}</b></p>
        <p style="font-size: 22px; font-weight: bold; color: #f59e0b;">💰 보유 포인트: {st.session_state.points} P</p>
    </div>
    """, unsafe_allow_html=True)
