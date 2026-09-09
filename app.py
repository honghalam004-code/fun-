import streamlit as st
import requests
import time
import random
import json
import os
from datetime import datetime

st.set_page_config(page_title="친한친구 끝말잇기 톡", page_icon="💬", layout="centered")

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

# 세션 상태 초기화
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
    
    if rating >= 1000:
        return "상위 0.1% (천상계) 👑"
    elif rating >= 600:
        return "상위 1.0% (랭커) 💎"
    elif rating >= 350:
        return "상위 5.0% (마스터) 🔥"
    elif rating >= 200:
        return "상위 15.0% (다이아) ✨"
    elif rating >= 100:
        return "상위 30.0% (골드) 🥇"
    elif rating >= 40:
        return "상위 50.0% (실버) 🥈"
    else:
        return "상위 85.0% (브론즈) 🥉"

# ==========================================
# 🎨 테마별 채팅 UI Custom CSS 적용
# ==========================================
equipped_theme = st.session_state.equipped_theme

if equipped_theme == "💛 카톡 노랑 테마":
    st.markdown("""
    <style>
        .stApp { background-color: #b2c7da !important; }
        div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #ffffff !important; color: #000 !important; border-radius: 15px 15px 15px 0px !important; }
        div[data-testid="stChatMessage"]:nth-child(even) { background-color: #ffe812 !important; color: #000 !important; border-radius: 15px 15px 0px 15px !important; }
    </style>
    """, unsafe_allow_html=True)

elif equipped_theme == "🌸 핑크 로맨스 테마":
    st.markdown("""
    <style>
        .stApp { background-color: #fff0f3 !important; }
        div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #ffffff !important; border: 1px solid #ffccd5 !important; border-radius: 18px !important; }
        div[data-testid="stChatMessage"]:nth-child(even) { background-color: #ffb3c1 !important; color: #590d22 !important; border-radius: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

elif equipped_theme == "🌌 딥 다크 테마":
    st.markdown("""
    <style>
        .stApp { background-color: #121212 !important; color: #ffffff !important; }
        div[data-testid="stChatMessage"] { background-color: #1e1e1e !important; color: #e0e0e0 !important; border: 1px solid #333333 !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

elif equipped_theme == "🎖️ 밀리터리 테마":
    st.markdown("""
    <style>
        .stApp { background-color: #2b3323 !important; color: #d0e0c0 !important; }
        div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #1c2417 !important; color: #d8e6ce !important; border: 1px solid #4a5d3b !important; border-radius: 8px !important; }
        div[data-testid="stChatMessage"]:nth-child(even) { background-color: #4b5e38 !important; color: #ffffff !important; border: 1px solid #6b8252 !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

elif equipped_theme == "🎯 발로란트 테마":
    st.markdown("""
    <style>
        .stApp { background-color: #0f1923 !important; color: #ece8e1 !important; }
        div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #1f2b36 !important; color: #ece8e1 !important; border-left: 4px solid #ff4655 !important; border-radius: 4px !important; }
        div[data-testid="stChatMessage"]:nth-child(even) { background-color: #ff4655 !important; color: #ffffff !important; font-weight: bold; border-radius: 4px !important; }
    </style>
    """, unsafe_allow_html=True)

elif equipped_theme == "⚔️ 롤 (LoL) 테마":
    st.markdown("""
    <style>
        .stApp { background-color: #091428 !important; color: #cdbe91 !important; }
        div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #1e2328 !important; color: #cdbe91 !important; border: 1px solid #c8aa6e !important; border-radius: 10px !important; }
        div[data-testid="stChatMessage"]:nth-child(even) { background-color: #c8aa6e !important; color: #091428 !important; font-weight: bold; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🎲 사전 단어 데이터 및 핵심 게임 기능
# ==========================================
STARTING_WORDS = ["바다", "하늘", "구름", "기차", "자전거", "호랑이", "사자", "비행기", "컴퓨터", "무지개", "사과", "바나나", "강아지", "고양이", "태양"]

REAL_KOREAN_WORDS = {
    "가": ["가방", "가수", "가구", "가을", "가족", "가면"],
    "나": ["나비", "나무", "나이", "나팔", "나라"],
    "다": ["다리", "다람쥐", "다리미", "다이아몬드"],
    "라": ["라디오", "라면", "라일락", "라이터"],
    "마": ["마을", "마술", "마스크", "마라톤"],
    "바": ["바람", "바위", "바구니", "바베큐", "바다"],
    "사": ["사람", "사자", "사과", "사탕", "사막"],
    "아": ["아침", "아기", "아이스크림", "아파트"],
    "자": ["자전거", "자동차", "자연", "자유"],
    "차": ["차표", "차고", "차선", "차림"],
    "하": ["하늘", "하마", "하모니카", "하트"],
    "선": ["선풍기", "선물", "선생님", "선박", "선수"],
    "생": ["생일", "생각", "생물", "생명", "생수"],
    "성": ["성곽", "성공", "성장", "성당"],
    "장": ["장난감", "장미", "장갑", "장소"],
    "지": ["지구", "지우개", "지도", "지하철"],
    "기": ["기차", "기린", "기타", "기쁨"]
}

KILLER_WORDS_BY_SYLLABLE = {
    "가": ["가돌리늄", "갈륨", "가녘"], "구": ["구연산나트륨", "구연산칼륨"],
    "기": ["기슭"], "나": ["나트륨", "나이오븀"], "라": ["라듐", "란타늄"],
    "리": ["리튬", "리버모륨"], "마": ["마그네슘"], "바": ["바륨", "바나듐"],
    "사": ["사마륨", "산기슭"], "수": ["수산화나트륨", "수산화칼륨"],
    "알": ["알루미늄"], "우": ["우라늄"], "칼": ["칼슘", "칼륨"], "헬": ["헬륨"]
}
ALL_KILLER_WORDS = [word for words in KILLER_WORDS_BY_SYLLABLE.values() for word in words]

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

    for sc in start_chars:
        if sc in REAL_KOREAN_WORDS:
            for w in REAL_KOREAN_WORDS[sc]:
                w_clean = w.strip()
                if w_clean not in clean_used:
                    candidates.append(w_clean)

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
    if is_win:
        st.session_state.stats["wins"] += 1
    else:
        st.session_state.stats["losses"] += 1

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
# 📌 사이드바
# ==========================================
st.sidebar.title("📌 메뉴")
st.sidebar.write(f"👤 플레이어: **{st.session_state.equipped_avatar}**")
st.sidebar.write(f"🏷️ 칭호: **{st.session_state.equipped_title}**")
st.sidebar.write(f"💰 보유 포인트: **{st.session_state.points} P**")

menu = st.sidebar.radio("페이지 이동:", [
    "💬 친구랑 톡 끝말잇기", 
    "👤 내 프로필",
    "🛒 상점 (꾸미기)",
    "📖 한방단어 대사전"
])

# ==========================================
# 1. 💬 친구랑 톡 끝말잇기
# ==========================================
if menu == "💬 친구랑 톡 끝말잇기":
    st.title(f"{st.session_state.equipped_title} 의 끝말잇기 톡")

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
                st.session_state.chat_history.append({"role": "bot", "text": "⏰ 시간 초과! 입력 시간이 지나서 내가 이겼어! 😜"})
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

            chat_keywords = ["두 번", "두번", "중복", "또", "아까", "썼잖아", "말했어", "반칙", "이상해"]
            is_conversation = (" " in user_input_clean) or any(kw in user_input_clean for kw in chat_keywords)

            if is_conversation and len(user_input_clean) > 3:
                used_list = st.session_state.used_words
                has_bot_duplicated = len(used_list) != len(set(used_list))

                if any(kw in user_input_clean for kw in ["두 번", "두번", "중복", "또", "아까"]):
                    if has_bot_duplicated:
                        st.session_state.chat_history.append({"role": "bot", "text": "헐... 진짜 내가 두 번 말했었네?! 😭 내가 깜빡했다 미안해!! 네 날카로운 지적 승리! 🎉 (+50P)"})
                        st.session_state.score += 30
                        st.session_state.points += 50
                        st.session_state.game_over = True
                        record_game_result(True, "상대 봇 중복 적발 승리", st.session_state.score)
                    else:
                        st.session_state.chat_history.append({"role": "bot", "text": f"어?? 나 중복 안 썼는데?! 😜 우리 지금까지 중복 없어!\n자자, **'{allowed_str}'**(으)로 이어서 입력해줘!"})
                else:
                    st.session_state.chat_history.append({"role": "bot", "text": f"ㅋㅋㅋ 게임 계속하자!\n지금 차례는 **'{allowed_str}'**(으)로 시작하는 단어야!"})
            
            else:
                if len(user_input_clean) < 2:
                    st.session_state.chat_history.append({"role": "bot", "text": "두 글자 이상의 단어만 쓸 수 있어! ❌"})
                    st.session_state.game_over = True
                    record_game_result(False, "한 글자 입력 실수", st.session_state.score)
                elif user_input_clean[0] not in allowed_chars:
                    st.session_state.chat_history.append({"role": "bot", "text": f"글자가 맞지 않아! **'{allowed_str}'**(으)로 시작해야지! 내가 이겼당 😜"})
                    st.session_state.game_over = True
                    record_game_result(False, "첫 글자 불일치", st.session_state.score)
                elif user_input_clean in st.session_state.used_words:
                    st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'**은(는) 이미 쓴 단어야! 중복이라 패배! ㅋㅋㅋ"})
                    st.session_state.game_over = True
                    record_game_result(False, "중복 단어 사용", st.session_state.score)
                elif not is_valid_korean_word(user_input_clean):
                    st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input_clean}'**은(는) 사전에 없는 단어야! 진짜 있는 단어만 쓰자~ 😅"})
                    st.session_state.game_over = True
                    record_game_result(False, "존재하지 않는 단어 사용", st.session_state.score)
                else:
                    st.session_state.used_words.append(user_input_clean)
                    st.session_state.last_word = user_input_clean

                    if user_input_clean in ALL_KILLER_WORDS:
                        st.session_state.chat_history.append({"role": "bot", "text": f"와... **'{user_input_clean}'**?! 😱 단어가 **'{user_input_clean[-1]}'**(으)로 끝나서 받아칠 수 없어! 네 승리야! 🎉 (+100P)"})
                        st.session_state.score += 50
                        st.session_state.points += 100
                        st.session_state.game_over = True
                        record_game_result(True, f"한방단어('{user_input_clean}') 성공", st.session_state.score)
                        st.balloons()
                    else:
                        bot_next_chars = get_allowed_initials(user_input_clean[-1])
                        bot_word = get_bot_response_word(bot_next_chars, st.session_state.used_words, normal_difficulty)

                        if bot_word is None:
                            st.session_state.chat_history.append({"role": "bot", "text": f"아... **'{user_input_clean[-1]}'**(으)로 시작하는 단어가 안 떠올라. 네가 이겼어! 👏 (+50P)"})
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

                            reactions = [
                                f"좋아! **'{user_input_clean}'** 받아서 난 **'{bot_word}'**! 다음은 **'{bot_word[-1]}'**!",
                                f"**'{user_input_clean}'** 이라니! 난 **'{bot_word}'**(으)로 받아친다! **'{bot_word[-1]}'** 순서야!",
                                f"올~ 난 **'{bot_word}'**! **'{bot_word[-1]}'**(으)로 계속 이어봐! 😃"
                            ]
                            st.session_state.chat_history.append({"role": "bot", "text": random.choice(reactions)})
            st.rerun()

    if st.session_state.game_over:
        st.button("🔄 새로운 단어로 다시 시작!", on_click=reset_game)

# ==========================================
# 2. 👤 내 프로필 페이지 (커스텀 인게임 카드 UI)
# ==========================================
elif menu == "👤 내 프로필":
    st.title("👤 플레이어 프로필 카드")
    st.caption("상점에서 구매한 아이템으로 프로필 카드를 꾸밀 수 있습니다!")

    stats = st.session_state.stats
    total = stats["total_games"]
    wins = stats["wins"]
    losses = stats["losses"]
    win_rate = (wins / total * 100) if total > 0 else 0.0
    percentile = calculate_percentile()

    # 프로필 카드 CSS 아우라 테두리 스타일 지정
    frame_style = "border: 2px solid #ccc;"
    if st.session_state.equipped_frame == "🔥 불타는 아우라 프레임":
        frame_style = "border: 3px solid #ff4500; box-shadow: 0 0 15px #ff4500; background: linear-gradient(135deg, #1f0d08, #3a150d);"
    elif st.session_state.equipped_frame == "💎 다이아몬드 프레임":
        frame_style = "border: 3px solid #00ffff; box-shadow: 0 0 15px #00ffff; background: linear-gradient(135deg, #091f2c, #0a334a);"
    elif st.session_state.equipped_frame == "🌌 은하수 아우라 프레임":
        frame_style = "border: 3px solid #a855f7; box-shadow: 0 0 15px #a855f7; background: linear-gradient(135deg, #1e0b36, #3b0764);"
    else:
        frame_style = "border: 2px solid #555; background: #1e1e1e;"

    # 🎴 프로필 카드 렌더링
    st.markdown(f"""
    <div style="padding: 25px; border-radius: 20px; {frame_style} text-align: center; margin-bottom: 25px;">
        <div style="font-size: 55px; margin-bottom: 5px;">{st.session_state.equipped_avatar.split()[0]}</div>
        <div style="font-size: 14px; font-weight: bold; color: #ffd700; background: rgba(255,215,0,0.1); display: inline-block; padding: 4px 12px; border-radius: 12px; margin-bottom: 8px;">
            {st.session_state.equipped_title}
        </div>
        <h2 style="margin: 5px 0; color: #ffffff;">{st.session_state.equipped_avatar.split()[1] if len(st.session_state.equipped_avatar.split()) > 1 else '플레이어'}</h2>
        <div style="font-size: 16px; color: #38bdf8; font-weight: bold; margin-bottom: 15px;">
            📈 랭킹 평가: {percentile}
        </div>
        <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 15px 0;">
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
                <div style="font-size: 12px; color: #aaa;">전적</div>
                <div style="font-size: 18px; font-weight: bold; color: #fff;">{total}전 {wins}승 {losses}패</div>
            </div>
            <div>
                <div style="font-size: 12px; color: #aaa;">승률</div>
                <div style="font-size: 18px; font-weight: bold; color: #4ade80;">{win_rate:.1f}%</div>
            </div>
            <div>
                <div style="font-size: 12px; color: #aaa;">최고 점수</div>
                <div style="font-size: 18px; font-weight: bold; color: #facc15;">{st.session_state.high_score}점</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📜 상세 경기 기록")
    if not st.session_state.history:
        st.info("아직 플레이 기록이 없습니다.")
    else:
        for item in st.session_state.history[:5]:
            st.write(f"• **[{item['time']}]** {item['result']} | {item['reason']} ({item['score']}점)")

# ==========================================
# 3. 🛒 상점 (프로필 아바타, 프레임, 칭호, 테마)
# ==========================================
elif menu == "🛒 상점 (꾸미기)":
    st.title("🛒 포인트 상점 & 인벤토리")
    st.write(f"현재 보유 포인트: **{st.session_state.points} P**")
    st.caption("아이템을 구매하고 바로 장착하여 나만의 멋진 프로필을 만들어보세요!")
    st.divider()

    shop_items = {
        # 👤 아바타
        "🤖 메카 로봇": {"price": 100, "type": "아바타", "desc": "강력한 분위기의 AI 로봇 아바타"},
        "🥷 전설의 닌자": {"price": 150, "type": "아바타", "desc": "어둠 속에서 빠르게 단어를 치는 닌자"},
        "🐉 골드 드래곤": {"price": 250, "type": "아바타", "desc": "황금빛 아우라를 내뿜는 드래곤"},
        "👑 국왕 펭귄": {"price": 300, "type": "아바타", "desc": "귀엽지만 무서운 귀족 펭귄 아바타"},

        # ✨ 프레임
        "🔥 불타는 아우라 프레임": {"price": 200, "type": "프레임", "desc": "프로필 카드를 붉게 불태우는 아우라"},
        "💎 다이아몬드 프레임": {"price": 250, "type": "프레임", "desc": "영롱한 시안빛 다이아몬드 아우라"},
        "🌌 은하수 아우라 프레임": {"price": 300, "type": "프레임", "desc": "신비로운 보랏빛 우주 아우라"},

        # 🏷️ 칭호
        "⚔️ 끝말잇기 패왕": {"price": 150, "type": "칭호", "desc": "상대를 순식간에 제압하는 자의 칭호"},
        "🧠 두뇌 풀가동": {"price": 150, "type": "칭호", "desc": "모든 단어를 기억해내는 천재의 칭호"},

        # 🎨 채팅 UI 테마
        "💛 카톡 노랑 테마": {"price": 100, "type": "테마", "desc": "노란색 카톡 스타일 채팅창"},
        "🎯 발로란트 테마": {"price": 200, "type": "테마", "desc": "시그니처 레드 다크 택티컬 UI"},
        "⚔️ 롤 (LoL) 테마": {"price": 200, "type": "테마", "desc": "소환사의 골드 & 딥 블루 UI"}
    }

    tab1, tab2, tab3, tab4 = st.tabs(["👤 아바타", "✨ 카드 프레임", "🏷️ 칭호", "🎨 채팅 테마"])

    def render_shop_category(category_name):
        for item_name, info in shop_items.items():
            if info["type"] == category_name:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{item_name} ({info['price']} P)")
                    st.write(info['desc'])
                with col2:
                    is_owned = item_name in st.session_state.inventory
                    
                    # 장착 여부 확인
                    is_equipped = (
                        (info["type"] == "아바타" and st.session_state.equipped_avatar == item_name) or
                        (info["type"] == "프레임" and st.session_state.equipped_frame == item_name) or
                        (info["type"] == "칭호" and st.session_state.equipped_title == item_name) or
                        (info["type"] == "테마" and st.session_state.equipped_theme == item_name)
                    )

                    if is_owned:
                        if is_equipped:
                            st.button("✅ 장착 중", key=f"active_{item_name}", disabled=True)
                        else:
                            if st.button("장착하기", key=f"equip_{item_name}"):
                                if info["type"] == "아바타": st.session_state.equipped_avatar = item_name
                                elif info["type"] == "프레임": st.session_state.equipped_frame = item_name
                                elif info["type"] == "칭호": st.session_state.equipped_title = item_name
                                elif info["type"] == "테마": st.session_state.equipped_theme = item_name
                                save_user_data()
                                st.success(f"'{item_name}' 장착 완료!")
                                time.sleep(0.4)
                                st.rerun()
                    else:
                        if st.button("구매하기", key=f"buy_{item_name}"):
                            if st.session_state.points >= info["price"]:
                                st.session_state.points -= info["price"]
                                st.session_state.inventory.append(item_name)
                                save_user_data()
                                st.success(f"'{item_name}' 구매 완료!")
                                time.sleep(0.4)
                                st.rerun()
                            else:
                                st.error("포인트가 부족합니다!")
                st.divider()

    with tab1: render_shop_category("아바타")
    with tab2: render_shop_category("프레임")
    with tab3: render_shop_category("칭호")
    with tab4: render_shop_category("테마")

# ==========================================
# 4. 📖 한방단어 대사전
# ==========================================
elif menu == "📖 한방단어 대사전":
    st.title("📖 한방단어 대사전")
    consonants = ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    tabs = st.tabs(consonants)

    for i, con in enumerate(consonants):
        with tabs[i]:
            found = False
            for syllable, words in KILLER_WORDS_BY_SYLLABLE.items():
                code = ord(syllable[0]) - 0xAC00
                if 0 <= code <= 11172:
                    initial_idx = code // (21 * 28)
                    initial_char = consonants[initial_idx] if initial_idx < len(consonants) else ""
                    if initial_char == con:
                        found = True
                        st.subheader(f"📌 '{syllable}' 시작 단어")
                        for word in words:
                            st.markdown(f"• **{word}**")
            if not found:
                st.info("등록된 단어가 없습니다.")
