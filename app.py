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
# 🎨 UI 스타일 설정
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
    "임": ["임금님", "임산부", "임계점", "임무", "임시계정", "임상시험"],
    "남": ["나무", "남극", "남대문", "남쪽", "남성"],
    "이": ["이발소", "이집트", "이야기", "이불", "이용권", "이사회"],
    "가": ["가방", "가수", "가구", "가을", "가면", "가족", "가위"],
    "나": ["나비", "나무", "나눔", "나라", "나침반"],
    "다": ["다람쥐", "다리", "다리미", "다이아몬드"],
    "라": ["라디오", "라면", "라이터", "라일락"],
    "마": ["마술", "마을", "마이크", "마라톤"],
    "바": ["바다", "바나나", "바람", "바구니"],
    "사": ["사과", "사자", "사진", "사탕"],
    "아": ["아침", "안경", "아기", "악기"],
    "차": ["차표", "차가운", "차선"],
    "하": ["하늘", "하모니카", "하천"]
}

# ==========================================
# 📖 대폭 확장된 초성 필살 한방단어 대사전 (4배 확장)
# ==========================================
CONSONANT_KILLER_DICTIONARY = {
    "ㄱ": [
        ("가돌리늄", "원소번호 64번 ('늄')"), ("갈륨", "원소번호 31번 ('륨')"), 
        ("기슭", "끝말잇기 최강 공격 ('슭')"), ("곬", "물길이 트인 줄기 ('곬')"),
        ("경뎄", "어미 활용형 한방 단어"), ("광시곡", "클래식 곡 형태 ('곡')"),
        ("구름다리", "장애물 방어용"), ("금구슬", "고유 명사 한방 단어")
    ],
    "ㄴ": [
        ("나트륨", "원소번호 11번 ('륨')"), ("나이오븀", "원소번호 41번 ('븀')"), 
        ("녘", "해질녘/동녘 등의 '녘'"), ("늧", "앞날의 징조 ('늧')"),
        ("네오디뮴", "원소번호 60번 ('뮴')"), ("네온", "비활성 기체 ('온')"),
        ("노을빛", "컬러 단어 ('빛')"), ("눈썰매", "겨울 스포츠 ('매')")
    ],
    "ㄷ": [
        ("다름슈타튬", "원소번호 110번 ('튬')"), ("디스프로슘", "원소번호 66번 ('슘')"), 
        ("듐", "화학 단위 한방어"), ("뎄", "어미 활용 한방어"),
        ("도깨비방망이", "전래동화 한방어"), ("단풍잎", "자연 단어 ('잎')"),
        ("들국화", "꽃 종류 ('화')"), ("달빛", "야간 자연 현상 ('빛')")
    ],
    "ㄹ": [
        ("라듐", "원소번호 88번 ('듐')"), ("라돈", "원소번호 86번 ('돈')"), 
        ("란타넘", "원소번호 57번 ('넘')"), ("릇", "그릇의 옛말 ('릇')"),
        ("루테늄", "원소번호 44번 ('늄')"), ("로듐", "원소번호 45번 ('듐')"),
        ("루테튬", "원소번호 71번 ('튬')"), ("뢴트게늄", "원소번호 111번 ('늄')")
    ],
    "ㅁ": [
        ("마그네슘", "원소번호 12번 ('슘')"), ("마이트너륨", "원소번호 109번 ('륨')"), 
        ("뮴", "원소 어미 한방어"), ("망가니즈", "원소번호 25번 ('즈')"),
        ("모스코븀", "원소번호 115번 ('븀')"), ("무지개빛", "색상 단어 ('빛')"),
        ("마하", "속도 단위 ('하')"), ("물안개", "자연 현상 ('개')")
    ],
    "ㅂ": [
        ("바륨", "원소번호 56번 ('륨')"), ("바나듐", "원소번호 23번 ('듐')"), 
        ("버클륨", "원소번호 97번 ('륨')"), ("븀", "원소 어미 한방어"),
        ("베릴륨", "원소번호 4번 ('륨')"), ("보륨", "원소번호 107번 ('륨')"),
        ("비스무트", "원소번호 83번 ('트')"), ("브로민", "원소번호 35번 ('민')")
    ],
    "ㅅ": [
        ("사마륨", "원소번호 62번 ('륨')"), ("산기슭", "최강의 한방 단어 ('슭')"), 
        ("스트론튬", "원소번호 38번 ('튬')"), ("슭", "방어 불가 끝문자"),
        ("세슘", "원소번호 55번 ('슘')"), ("세륨", "원소번호 58번 ('륨')"),
        ("시보귬", "원소번호 106번 ('귬')"), ("수소", "원소번호 1번 ('소')")
    ],
    "ㅇ": [
        ("알루미늄", "원소번호 13번 ('늄')"), ("아인슈타이늄", "원소번호 99번 ('늄')"), 
        ("아메리슘", "원소번호 95번 ('슘')"), ("앙증", "특수 한방 단어 ('증')"),
        ("아이오딘", "원소번호 53번 ('딘')"), ("이트륨", "원소번호 39번 ('륨')"),
        ("이테르븀", "원소번호 70번 ('븀')"), ("오가네손", "원소번호 118번 ('손')")
    ],
    "ㅈ": [
        ("지르코늄", "원소번호 40번 ('늄')"), ("저마늄", "원소번호 32번 ('늄')"), 
        ("즙", "짜낸 즙 ('즙')"), ("제논", "원소번호 54번 ('논')"),
        ("자물쇠", "생활 용품 ('쇠')"), ("장미꽃", "식물 ('꽃')"),
        ("전등빛", "조명 단어 ('빛')"), ("주석", "원소번호 50번 ('석')")
    ],
    "ㅊ": [
        ("차표", "승차권 ('표')"), ("차이코프스키", "인물명 ('키')"), 
        ("츰", "‘즈음’의 옛말 ('츰')"), ("청개구리", "동물 ('리')"),
        ("초승달", "천체 ('달')"), ("촛불빛", "조명 ('빛')")
    ],
    "ㅋ": [
        ("칼륨", "원소번호 19번 ('륨')"), ("칼슘", "원소번호 20번 ('슘')"), 
        ("카드뮴", "원소번호 48번 ('뮴')"), ("캘리포늄", "원소번호 98번 ('늄')"),
        ("크립톤", "원소번호 36번 ('톤')"), ("퀴륨", "원소번호 96번 ('륨')"),
        ("코페르니슘", "원소번호 112번 ('슘')"), ("크롬", "원소번호 24번 ('롬')")
    ],
    "ㅌ": [
        ("티타늄", "원소번호 22번 ('늄')"), ("테크네튬", "원소번호 43번 ('튬')"), 
        ("텔루륨", "원소번호 52번 ('륨')"), ("테르븀", "원소번호 65번 ('븀')"),
        ("테네신", "원소번호 117번 ('신')"), ("토륨", "원소번호 90번 ('륨')"),
        ("툴륨", "원소번호 69번 ('륨')"), ("태양빛", "자연 빛 ('빛')")
    ],
    "ㅍ": [
        ("팔라듐", "원소번호 46번 ('듐')"), ("플루토늄", "원소번호 94번 ('늄')"), 
        ("프랑슘", "원소번호 87번 ('슘')"), ("페르븀", "원소번호 100번 ('븀')"),
        ("플레로븀", "원소번호 114번 ('븀')"), ("플루오린", "원소번호 9번 ('린')"),
        ("파란빛", "색상 단어 ('빛')"), ("피아노선율", "음악 단어 ('율')")
    ],
    "ㅎ": [
        ("하프늄", "원소번호 72번 ('늄')"), ("하슘", "원소번호 108번 ('슘')"), 
        ("해질녘", "노을 시간 ('녘')"), ("홀뮴", "원소번호 67번 ('뮴')"),
        ("헬륨", "원소번호 2번 ('륨')"), ("화물선", "선박 ('선')"),
        ("황금빛", "색상 단어 ('빛')"), ("휘기장", "특수 단어 ('장')")
    ]
}

ALL_KILLER_WORDS = [item[0] for words in CONSONANT_KILLER_DICTIONARY.values() for item in words]

# ==========================================
# 🎮 게임 로직 & 완벽 두음법칙 알고리즘
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
    """표준 두음법칙 완벽 적용 로직 (님->임, 녀->여, 량->양, 라->나 등)"""
    allowed = [char]
    
    # 1. 수동 예외 및 자주 쓰이는 두음법칙 맵
    dueum_dict = {
        "님": "임", "닢": "잎", "녀": "여", "녀석": "여석", "뇨": "요", "뉴": "유", "니": "이",
        "라": "나", "락": "낙", "란": "난", "람": "남", "랍": "납", "랑": "낭",
        "래": "내", "랭": "냉", "로": "노", "록": "녹", "론": "논", "롱": "농",
        "뢰": "뇌", "루": "누", "류": "유", "륙": "육", "륜": "윤", "률": "율",
        "륭": "융", "르": "느", "리": "이", "린": "인", "림": "임", "립": "입",
        "량": "양", "려": "여", "력": "역", "련": "연", "렬": "열", "렴": "염", "령": "영"
    }
    if char in dueum_dict and dueum_dict[char] not in allowed:
        allowed.append(dueum_dict[char])
        
    # 2. 유니코드 공식 연산 기반 두음법칙
    code = ord(char) - 0xAC00
    if 0 <= code <= 11172:
        initial = code // (21 * 28)
        medial = (code % (21 * 28)) // 28
        final = code % 28
        
        # ㄴ -> ㅇ (녀, 뇨, 뉴, 니 등)
        if initial == 2 and medial in [2, 6, 8, 12, 18, 20]:
            alt = chr(0xAC00 + (11 * 21 * 28) + (medial * 28) + final)
            if alt not in allowed: allowed.append(alt)
        # ㄹ -> ㄴ 또는 ㄹ -> ㅇ
        elif initial == 5:
            if medial in [0, 1, 4, 7, 9, 14, 15, 16, 17, 21]:
                alt = chr(0xAC00 + (2 * 21 * 28) + (medial * 28) + final)
                if alt not in allowed: allowed.append(alt)
            else:
                alt = chr(0xAC00 + (11 * 21 * 28) + (medial * 28) + final)
                if alt not in allowed: allowed.append(alt)
                
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

    # 2. 백업 단어 탑재
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
    "📖 확장 한방단어 대사전"
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
                            st.session_state.chat_history.append({"role": "bot", "text": f"아... **'{'/'.join(bot_next_chars)}'**(으)로 시작하는 단어가 없어! 네가 이겼어! 👏 (+50P)"})
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

                            st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'** 받아서 난 **'{bot_word}'**! 다음은 **'{'/'.join(get_allowed_initials(bot_word[-1]))}'**!"})
            st.rerun()

    if st.session_state.game_over:
        st.button("🔄 새로운 단어로 다시 시작!", on_click=reset_game)

# ==========================================
# 2. 👤 내 프로필
# ==========================================
elif menu == "👤 내 프로필":
    st.title("👤 내 플레이어 프로필")
    
    st.subheader("✍️ 닉네임 수정")
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

    st.markdown(f"""
    <div style="padding: 25px; border-radius: 20px; border: 2px solid #555; background: #1e1e1e; text-align: center;">
        <div style="font-size: 55px;">{st.session_state.equipped_avatar.split()[0]}</div>
        <div style="font-size: 15px; font-weight: bold; color: #ffd700; background: rgba(255,215,0,0.15); display: inline-block; padding: 4px 12px; border-radius: 10px; margin-top: 5px;">
            {st.session_state.equipped_title}
        </div>
        <h2 style="margin: 10px 0; color: #fff;">{st.session_state.user_name}</h2>
        <div style="color: #38bdf8; font-weight: bold;">{percentile}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 🛒 고급 상점
# ==========================================
elif menu == "🛒 고급 상점":
    st.title("🛒 프리미엄 상점")
    st.write(f"보유 포인트: **{st.session_state.points} P**")

    shop_items = [
        ("🐣 끝말잇기 병아리", 0, "기본 칭호"),
        ("⚡ 뇌섹남", 100, "지적인 포스의 칭호"),
        ("⚔️ 끝말잇기 패왕", 150, "강력한 승리자의 칭호"),
        ("🧠 걸어다니는 국어사전", 200, "언어의 연금술사 칭호"),
        ("🔥 불패의 마스터", 250, "연승의 제왕 칭호")
    ]

    for item_name, price, desc in shop_items:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1: st.write(f"**{item_name}**")
        with col2: st.caption(desc)
        with col3:
            if item_name in st.session_state.inventory:
                if st.session_state.equipped_title == item_name:
                    st.success("착용 중")
                else:
                    if st.button("착용", key=f"eq_{item_name}"):
                        st.session_state.equipped_title = item_name
                        save_user_data()
                        st.rerun()
            else:
                if st.button(f"구매 ({price}P)", key=f"buy_{item_name}"):
                    if st.session_state.points >= price:
                        st.session_state.points -= price
                        st.session_state.inventory.append(item_name)
                        save_user_data()
                        st.rerun()

# ==========================================
# 4. 📖 확장 한방단어 대사전 (ㄱ~ㅎ)
# ==========================================
elif menu == "📖 확장 한방단어 대사전":
    st.title("📖 ㄱ~ㅎ 초성 기반 확장 필살 한방단어 대사전")
    
    consonants = list(CONSONANT_KILLER_DICTIONARY.keys())
    tabs = st.tabs(consonants)

    for idx, con in enumerate(consonants):
        with tabs[idx]:
            st.subheader(f"📌 '{con}' 초성 필살 한방 공격 단어 모음")
            words_list = CONSONANT_KILLER_DICTIONARY[con]
            
            for word, desc in words_list:
                c1, c2 = st.columns([1, 2])
                with c1: st.markdown(f"💥 **{word}**")
                with c2: st.caption(desc)
                st.divider()
