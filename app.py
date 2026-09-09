import streamlit as st
import requests
import time

# 페이지 기본 설정
st.set_page_config(page_title="끝말잇기 마스터", page_icon="🎮", layout="centered")

# --- 한방단어 데이터베이스 ---
KILLER_WORDS = {
    "ㄱ": ["그릇", "기쁨", "구름", "기슭"],
    "ㄴ": ["나트륨", "노트북", "나이오븀", "녘"],
    "ㄷ": ["디스크", "들녘", "단백질", "도자기"],
    "ㄹ": ["로봇", "루비듐", "리튬", "라듐", "로듐"],
    "ㅁ": ["마그네슘", "마음", "무릎", "버섯"],
    "ㅂ": ["바깥", "버릇", "부엌", "베릴륨"],
    "ㅅ": ["산기슭", "스트론튬", "수탉", "스칸듐"],
    "ㅇ": ["알루미늄", "우라늄", "이리듐", "오스뮴", "여덟"],
    "ㅈ": ["자물쇠", "징용꾼", "주름", "지르코늄"],
    "ㅊ": ["찰나", "첫눈", "천문학", "철쭉"],
    "ㅋ": ["칼슘", "퀴륨", "크로뮴", "콘크리트"],
    "ㅌ": ["티타늄", "튤립", "트리튬", "탈륨"],
    "ㅍ": ["포타슘", "프랑슘", "플루토늄", "프로메튬"],
    "ㅎ": ["해질녘", "헬륨", "홀뮴", "해돋이"]
}

# 모든 한방단어를 1차원 리스트로 합치기 (검사용)
ALL_KILLER_WORDS = [word for words in KILLER_WORDS.values() for word in words]

# --- 네이버 사전 유효성 검사 ---
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

# --- 세션 상태 초기화 ---
if "words" not in st.session_state:
    st.session_state.words = ["기차"]
if "score" not in st.session_state:
    st.session_state.score = 0
if "points" not in st.session_state:
    st.session_state.points = 0  # 상점 이용 포인트
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "inventory" not in st.session_state:
    st.session_state.inventory = [] # 구매한 아이템 목록
if "equipped_theme" not in st.session_state:
    st.session_state.equipped_theme = "기본"

def reset_game():
    st.session_state.words = ["기차"]
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.start_time = time.time()

# --- 두음법칙 처리 ---
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

# --- 장착된 테마(CSS) 적용 ---
if st.session_state.equipped_theme == "🔥 지옥불 테마":
    st.markdown("""<style>.stApp {background-color: #3b0000; color: #ffcccc;}</style>""", unsafe_allow_html=True)
elif st.session_state.equipped_theme == "🌌 심연의 우주 테마":
    st.markdown("""<style>.stApp {background-color: #0b0c10; color: #66fcf1;}</style>""", unsafe_allow_html=True)
elif st.session_state.equipped_theme == "🌸 벚꽃 테마":
    st.markdown("""<style>.stApp {background-color: #fff0f5; color: #d1495b;}</style>""", unsafe_allow_html=True)

# ==========================================
# 사이드바 메뉴
# ==========================================
st.sidebar.title("📌 메뉴")
st.sidebar.write(f"💰 내 포인트: **{st.session_state.points} P**")
menu = st.sidebar.radio("이동할 페이지:", ["🎮 게임하기", "🛒 상점 (꾸미기)", "📖 한방단어 사전"])

# ==========================================
# 1. 게임 화면
# ==========================================
if menu == "🎮 게임하기":
    title_emoji = "👑" if "👑 왕관 칭호" in st.session_state.inventory else "🎮"
    st.title(f"{title_emoji} 끝말잇기 마스터")
    
    difficulty = st.sidebar.selectbox("난이도 설정", ["🟢 쉬움 (15초, 2글자 이상)", "🟡 보통 (10초, 2글자 이상)", "🔴 어려움 (5초, 3글자 이상)"])
    
    time_limit = 15 if "쉬움" in difficulty else 10 if "보통" in difficulty else 5
    min_length = 3 if "어려움" in difficulty else 2

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, int(time_limit - elapsed_time))

    if not st.session_state.game_over:
        st.warning(f"⏱️ 남은 시간: **{remaining_time}초**")
        if remaining_time <= 0:
            st.session_state.game_over = True
            st.error("⏰ 시간 초과! 게임 오버!")
            st.snow()

    last_word = st.session_state.words[-1]
    last_char = last_word[-1]
    allowed_chars = get_allowed_initials(last_char)

    st.info(f"현재 제시어: **{last_word}** | 시작 글자: **{', '.join(allowed_chars)}**")
    
    col1, col2 = st.columns(2)
    col1.write(f"🏆 현재 점수: **{st.session_state.score}점**")
    col2.write(f"💰 획득 포인트: **{st.session_state.points} P**")

    with st.form(key="game_form", clear_on_submit=True):
        user_input = st.text_input(f"단어를 입력하세요 (최소 {min_length}글자):", disabled=st.session_state.game_over)
        submit = st.form_submit_button("제출", disabled=st.session_state.game_over)

    if submit and user_input and not st.session_state.game_over:
        user_input = user_input.strip()
        
        if len(user_input) < min_length:
            st.error(f"{min_length}글자 이상의 단어만 입력 가능합니다.")
        elif user_input[0] not in allowed_chars:
            st.error(f"실패! '{'/'.join(allowed_chars)}'(으)로 시작해야 합니다.")
            st.session_state.game_over = True
            st.snow()
        elif user_input in st.session_state.words:
            st.error("이미 사용한 단어입니다!")
            st.session_state.game_over = True
            st.snow()
        elif not is_valid_korean_word(user_input):
            st.error(f"'{user_input}'(은)는 사전에 없는 단어입니다!")
            st.session_state.game_over = True
            st.snow()
        else:
            # 성공 처리 로직
            st.session_state.words.append(user_input)
            st.session_state.start_time = time.time()
            
            # [핵심] 한방단어 사용 시 승리 처리
            if user_input in ALL_KILLER_WORDS:
                st.success(f"💥 치명타 작렬! '{user_input}'(은)는 완벽한 한방단어입니다!")
                st.balloons()
                st.session_state.score += 50
                st.session_state.points += 100  # 한방단어 보너스 대박 포인트
                st.session_state.game_over = True # 한방에 끝냈으므로 승리로 게임 종료
                st.info("🎉 상대를 완벽하게 제압했습니다! (보너스 100P 획득)")
            else:
                st.success(f"성공! '{user_input}' (+5 P)")
                st.session_state.score += 10
                st.session_state.points += 5 # 일반 단어 성공 시 포인트 누적
                
                # 50점 돌파 시 추가 보너스
                if st.session_state.score % 50 == 0:
                    st.toast("🎉 연쇄 성공 보너스! (+20 P)")
                    st.session_state.points += 20
            
            st.rerun()

    if st.session_state.game_over:
        st.button("🔄 새로운 게임 시작", on_click=reset_game)

    st.divider()
    st.subheader("📜 플레이 기록")
    st.write(" ➔ ".join(st.session_state.words))


# ==========================================
# 2. 상점 (포인트 사용)
# ==========================================
elif menu == "🛒 상점 (꾸미기)":
    st.title("🛒 포인트 상점")
    st.markdown("게임에서 얻은 포인트를 사용해 특별한 테마나 칭호를 구매하고 장착하세요!")
    
    st.write("---")
    
    # 상점 아이템 리스트
    items = {
        "👑 왕관 칭호": {"price": 100, "type": "칭호", "desc": "게임 제목에 간지나는 왕관(👑)이 추가됩니다."},
        "🌸 벚꽃 테마": {"price": 150, "type": "테마", "desc": "배경을 화사한 핑크빛으로 바꿉니다."},
        "🌌 심연의 우주 테마": {"price": 250, "type": "테마", "desc": "화면을 깊은 다크 모드로 변경합니다."},
        "🔥 지옥불 테마": {"price": 300, "type": "테마", "desc": "어둡고 붉은 카리스마 테마를 적용합니다."}
    }
    
    for item_name, info in items.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{item_name} ({info['price']} P)")
            st.write(info['desc'])
        
        with col2:
            # 이미 구매한 아이템인 경우
            if item_name in st.session_state.inventory:
                if info["type"] == "테마":
                    if st.session_state.equipped_theme == item_name:
                        st.button("✅ 장착 중", key=f"btn_{item_name}", disabled=True)
                    else:
                        if st.button("장착하기", key=f"equip_{item_name}"):
                            st.session_state.equipped_theme = item_name
                            st.rerun()
                else:
                    st.button("✅ 보유 중", key=f"btn_{item_name}", disabled=True)
            
            # 미구매 상태인 경우
            else:
                if st.button("구매하기", key=f"buy_{item_name}"):
                    if st.session_state.points >= info["price"]:
                        st.session_state.points -= info["price"]
                        st.session_state.inventory.append(item_name)
                        st.success(f"{item_name} 구매 완료!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("포인트가 부족합니다!")
        st.divider()

    st.subheader("🎨 현재 장착 중인 테마: " + st.session_state.equipped_theme)
    if st.button("테마 기본으로 되돌리기"):
        st.session_state.equipped_theme = "기본"
        st.rerun()


# ==========================================
# 3. 한방단어 사전
# ==========================================
elif menu == "📖 한방단어 사전":
    st.title("📖 끝말잇기 한방단어 사전")
    st.markdown("여기 있는 단어를 외워서 게임 중 입력하면 **한방에 승리(보너스 100P)**를 거둘 수 있습니다!")

    tabs = st.tabs(list(KILLER_WORDS.keys()))
    for i, (consonant, words) in enumerate(KILLER_WORDS.items()):
        with tabs[i]:
            st.subheader(f"'{consonant}'(으)로 시작하는 한방단어")
            for word in words:
                st.markdown(f"- **{word[:-1]}<span style='color:red'>{word[-1]}</span>**", unsafe_allow_html=True)
