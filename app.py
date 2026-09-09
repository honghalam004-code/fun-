import streamlit as st
import requests
import time
import random

st.set_page_config(page_title="친한친구 끝말잇기 톡", page_icon="💬", layout="centered")

# ==========================================
# 💥 두음법칙 검증완료 한방단어 DB
# ==========================================
KILLER_WORDS_BY_SYLLABLE = {
    "가": ["가돌리늄", "갈륨", "가녘", "가재무릇", "가쪽녘"],
    "개": ["개울녘", "개녘"], "게": ["게르마늄"],
    "구": ["구연산나트륨", "구연산칼륨", "구연산칼슘"],
    "귀": ["귀신녘", "귀때그릇"], "기": ["기슭"],
    "과": ["과산화나트륨", "과산화바륨", "과망간산칼륨"],
    "꽃": ["꽃그릇"], "나": ["나트륨", "나이오븀", "나치즘"],
    "남": ["남녘"], "네": ["네오디뮴", "네프튜늄"], "노": ["노벨륨"],
    "놋": ["놋그릇"], "다": ["다우늄", "다이크로뮴산나트륨", "다이디뮴"],
    "더": ["더블륨", "더브늄"], "도": ["도기그릇"], "동": ["동녘"], "들": ["들녘"],
    "디": ["디스프로슘", "디디뮴"], "라": ["라듐", "란타늄"], "러": ["러더포듐"],
    "로": ["로듐", "로렌슘"], "루": ["루비듐", "루테늄", "루테튬"],
    "리": ["리튬", "류머티즘", "리버모륨", "리얼리즘"], "마": ["마그네슘", "마이트너륨"],
    "메": ["멘델레븀", "메커니즘"], "모": ["모스코븀"], "몰": ["몰리브덴산암모늄"],
    "바": ["바륨", "바나듐"], "밥": ["밥그릇"], "방": ["방사성스트론튬"],
    "버": ["버클륨", "버릇"], "베": ["베릴륨", "베클레륨"], "보": ["보륨", "보라녘"],
    "북": ["북녘"], "사": ["사기그릇", "사마륨", "산기슭"],
    "새": ["새벽녘"], "서": ["서녘"], "세": ["세륨", "세슘"], "소": ["소듐"],
    "수": ["수탉", "수산화나트륨", "수산화칼륨", "수산화칼슘", "수산화바륨"],
    "스": ["스트론튬", "스칸듐", "시보륨"], "씨": ["씨암탉"],
    "아": ["아메리슘", "아인슈타이늄", "아세트산칼슘"], "악": ["악티늄"],
    "알": ["알루미늄", "알고리즘"], "암": ["암탉", "암모늄"], "오": ["오스뮴"],
    "우": ["우라늄"], "유": ["유로퓸", "유머니즘"],
    "이": ["이리듐", "이터륨", "이트륨", "아이오딘산칼륨"], "인": ["인듐", "인산나트륨"],
    "자": ["자연질그릇"], "제": ["제라늄"], "지": ["지르코늄", "질산나트륨", "질산칼슘"],
    "차": ["차랑녘", "차아인산바륨"], "처": ["처마기슭"], "초": ["초산나트륨"],
    "카": ["카드뮴", "칼리포늄"], "칼": ["칼슘", "칼륨"], "코": ["코페르니슘"],
    "쿠": ["쿠비즘"], "퀴": ["퀴륨"], "크": ["크로뮴"], "타": ["타타르산칼륨나트륨"],
    "탄": ["탄산수소나트륨", "탄산나트륨", "탄산칼슘"], "탈": ["탈륨"],
    "테": ["테르븀", "테크네튬", "텔루륨"], "토": ["토륨"], "티": ["티타늄"],
    "트": ["트리튬"], "파": ["파라듐", "파시즘"], "페": ["페르뮴"],
    "포": ["포타슘", "포풀리즘"], "프": ["프랑슘", "프로메튬", "프리즘"],
    "플": ["플루토늄", "플레로븀"], "하": ["하프늄"], "해": ["해질녘"],
    "헬": ["헬륨"], "호": ["홀뮴"], "황": ["황산나트륨", "황산칼륨", "황산마그네슘"]
}

ALL_KILLER_WORDS = [word for words in KILLER_WORDS_BY_SYLLABLE.values() for word in words]

# 🔍 네이버 사전 실시간 연동 API
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

# 네이버 사전에 있는 단어로 봇의 답장 단어 찾기
def get_bot_response_word(start_char):
    url = f"https://dict.naver.com/api/search/autocomplete?query={start_char}&st=11111"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            candidates = []
            for item_group in items:
                for item in item_group:
                    w = item[0][0]
                    # 2글자 이상, 허용 시작글자, 일반 단어 위주 선택
                    if len(w) >= 2 and w[0] == start_char and w not in ALL_KILLER_WORDS:
                        candidates.append(w)
            if candidates:
                return random.choice(candidates[:10])
    except Exception:
        pass
    
    # 예비 고정 단어 사전
    backup_dict = {
        "다": "다리", "리": "리본", "본": "본보기", "기": "기차", "차": "차표", "표": "표범",
        "범": "범래", "자": "자전거", "거": "거미", "미": "미소", "소": "소나무", "무": "무지개",
        "개": "개구리", "구": "구름", "름": "름름", "나무": "무용", "용": "용기", "기": "기상"
    }
    return backup_dict.get(start_char, f"{start_char}생선")

# 두음법칙 적용
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

# ==========================================
# 세션 상태 초기화
# ==========================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "text": "안녕! 나랑 끝말잇기 한판 하자 ㅋㅋㅋ 내가 먼저 시작할게! 첫 단어는 **'바다'**야! **'다'**로 받아봐! 😜", "word": "바다"}
    ]
if "last_word" not in st.session_state:
    st.session_state.last_word = "바다"
if "used_words" not in st.session_state:
    st.session_state.used_words = ["바다"]
if "score" not in st.session_state:
    st.session_state.score = 0
if "points" not in st.session_state:
    st.session_state.points = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "equipped_theme" not in st.session_state:
    st.session_state.equipped_theme = "기본"

def reset_game():
    st.session_state.chat_history = [
        {"role": "bot", "text": "다시 한판 더? ㅋㅋ 좋아! 내가 선공이다. 첫 단어는 **'바다'**! **'다'**로 시작해봐!", "word": "바다"}
    ]
    st.session_state.last_word = "바다"
    st.session_state.used_words = ["바다"]
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.start_time = time.time()

# 테마 적용
if st.session_state.equipped_theme == "🔥 지옥불 테마":
    st.markdown("""<style>.stApp {background-color: #2b0000; color: #ffcccc;}</style>""", unsafe_allow_html=True)
elif st.session_state.equipped_theme == "🌌 심연의 우주 테마":
    st.markdown("""<style>.stApp {background-color: #0b0c10; color: #66fcf1;}</style>""", unsafe_allow_html=True)
elif st.session_state.equipped_theme == "🌸 벚꽃 테마":
    st.markdown("""<style>.stApp {background-color: #fff0f5; color: #d1495b;}</style>""", unsafe_allow_html=True)

# 사이드바
st.sidebar.title("📌 메뉴")
st.sidebar.write(f"💰 내 포인트: **{st.session_state.points} P**")
st.sidebar.write(f"🏆 점수: **{st.session_state.score}점**")
menu = st.sidebar.radio("페이지 이동:", [
    "💬 친구랑 톡 끝말잇기", 
    "🧪 원소 주기율표 (화학무기)", 
    "🔍 네이버 사전 검색기", 
    "📖 한방단어 대사전", 
    "🛒 상점 (꾸미기)"
])

# ==========================================
# 1. 💬 친구랑 톡 끝말잇기 (대화형 봇)
# ==========================================
if menu == "💬 친구랑 톡 끝말잇기":
    title_emoji = "👑" if "👑 왕관 칭호" in st.session_state.inventory else "💬"
    st.title(f"{title_emoji} 끝말잇기 짱친 AI 봇")

    difficulty = st.sidebar.selectbox("난이도 (타임어택)", ["🟢 쉬움 (15초, 2글자)", "🟡 보통 (10초, 2글자)", "🔴 어려움 (5초, 3글자)"])
    time_limit = 15 if "쉬움" in difficulty else 10 if "보통" in difficulty else 5
    min_length = 3 if "어려움" in difficulty else 2

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, int(time_limit - elapsed_time))

    if not st.session_state.game_over:
        st.progress(remaining_time / time_limit, text=f"⏱️ 답장 남은 시간: {remaining_time}초")
        if remaining_time <= 0:
            st.session_state.game_over = True
            st.session_state.chat_history.append({"role": "bot", "text": "⏰ 야 너 왜 대답이 없어?! 시간 초과다! ㅋㅋㅋ 내가 이겼지? 😜"})

    # 대화 기록 출력
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["text"])
        else:
            st.chat_message("assistant", avatar="🤖").write(msg["text"])

    # 입력창
    last_char = st.session_state.last_word[-1]
    allowed_chars = get_allowed_initials(last_char)

    if not st.session_state.game_over:
        user_input = st.chat_input(f"'{'/'.join(allowed_chars)}'(으)로 시작하는 {min_length}글자 이상 단어 입력...")
        if user_input:
            user_input = user_input.strip()
            
            # 사용자 메시지 채팅창 표시
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            
            # 검증 로직
            if len(user_input) < min_length:
                st.session_state.chat_history.append({"role": "bot", "text": f"야~ 최소 {min_length}글자는 써야지! ㅋㅋ 땡! ❌"})
                st.session_state.game_over = True
            elif user_input[0] not in allowed_chars:
                st.session_state.chat_history.append({"role": "bot", "text": f"ㅋㅋ 글자 틀렸잖아! **'{'/'.join(allowed_chars)}'**로 시작해야지! 내가 이겼당 😜"})
                st.session_state.game_over = True
            elif user_input in st.session_state.used_words:
                st.session_state.chat_history.append({"role": "bot", "text": f"**'{user_input}'**은(는) 아까 썼던 단어잖아! 중복 단어라 너 패배! ㅋㅋㅋ"})
                st.session_state.game_over = True
            elif not is_valid_korean_word(user_input):
                st.session_state.chat_history.append({"role": "bot", "text": f"에이~ **'{user_input}'**이(가) 어디 있어? 네이버 사전에 안 나온다구! 😜"})
                st.session_state.game_over = True
            else:
                st.session_state.used_words.append(user_input)
                st.session_state.last_word = user_input
                
                # 🔥 한방단어 사용 시
                if user_input in ALL_KILLER_WORDS:
                    st.session_state.chat_history.append({"role": "bot", "text": f"헐... **'{user_input}'** (끝글자: {user_input[-1]})?! 😱 사기야!! 받아칠 수가 없잖아!! 으악 전사함... 니가 이겼다 ㅠㅠ (+100P)"})
                    st.session_state.score += 50
                    st.session_state.points += 100
                    st.session_state.game_over = True
                    st.balloons()
                else:
                    # 정상 진행 -> 봇의 답장
                    bot_next_char = user_input[-1]
                    bot_allowed = get_allowed_initials(bot_next_char)
                    bot_word = get_bot_response_word(random.choice(bot_allowed))

                    st.session_state.used_words.append(bot_word)
                    st.session_state.last_word = bot_word
                    st.session_state.score += 10
                    st.session_state.points += 5
                    st.session_state.start_time = time.time()

                    bot_reactions = [
                        f"올~ **'{user_input}'** 좀 치는데? 그럼 난 **'{bot_word}'**! 다음은 **'{bot_word[-1]}'**이다!",
                        f"ㅋㅋㅋ 나 안 졌지! 난 **'{bot_word}'** 받아친다! **'{bot_word[-1]}'**(으)로 계속해봐!",
                        f"오 케이! **'{user_input}'** 받아서 **'{bot_word}'**! 자, **'{bot_word[-1]}'** 모디 준비해!"
                    ]
                    st.session_state.chat_history.append({"role": "bot", "text": random.choice(bot_reactions), "word": bot_word})
            st.rerun()

    if st.session_state.game_over:
        st.button("🔄 한판 더 하기", on_click=reset_game)

# ==========================================
# 2. 🧪 원소 주기율표 (실제 주기율표 격자 그래픽)
# ==========================================
elif menu == "🧪 원소 주기율표 (화학무기)":
    st.title("🧪 원소 주기율표 (화학 무기 백과)")
    st.caption("주기율표 속 🔥빨간 테두리 원소들은 상대방을 즉사시키는 절대 한방단어(륨, 늄, 슘, 듐, 튬 등)입니다!")

    # CSS 주기율표 스타일 정의
    st.markdown("""
    <style>
    .periodic-table {
        display: grid;
        grid-template-columns: repeat(18, 1fr);
        gap: 2px;
        background-color: #222;
        padding: 10px;
        border-radius: 8px;
        overflow-x: auto;
    }
    .element-box {
        border: 1px solid #444;
        background-color: #1e1e1e;
        color: white;
        text-align: center;
        padding: 4px 1px;
        font-size: 10px;
        border-radius: 3px;
        min-height: 48px;
    }
    .killer-box {
        border: 2px solid #ff4d4d !important;
        background-color: #4a0000 !important;
        color: #ffcccc !important;
        font-weight: bold;
        box-shadow: 0 0 5px #ff4d4d;
    }
    .elem-num { font-size: 8px; color: #888; }
    .elem-sym { font-size: 13px; font-weight: bold; }
    .elem-name { font-size: 9px; }
    </style>
    """, unsafe_allow_html=True)

    # 주요 118개 원소 데이터 (번호, 기호, 이름, 한방 여부, 행, 열)
    elements_data = [
        (1, "H", "수소", False, 1, 1), (2, "He", "헬륨", True, 1, 18),
        (3, "Li", "리튬", True, 2, 1), (4, "Be", "베릴륨", True, 2, 2), (5, "B", "붕소", False, 2, 13), (6, "C", "탄소", False, 2, 14), (7, "N", "질소", False, 2, 15), (8, "O", "산소", False, 2, 16), (9, "F", "플루오린", False, 2, 17), (10, "Ne", "네온", False, 2, 18),
        (11, "Na", "나트륨", True, 3, 1), (12, "Mg", "마그네슘", True, 3, 2), (13, "Al", "알루미늄", True, 3, 13), (14, "Si", "규소", False, 3, 14), (15, "P", "인", False, 3, 15), (16, "S", "황", False, 3, 16), (17, "Cl", "염소", False, 3, 17), (18, "Ar", "아르곤", False, 3, 18),
        (19, "K", "칼륨", True, 4, 1), (20, "Ca", "칼슘", True, 4, 2), (21, "Sc", "스칸듐", True, 4, 3), (22, "Ti", "티타늄", True, 4, 4), (23, "V", "바나듐", True, 4, 5), (24, "Cr", "크로뮴", True, 4, 6), (25, "Mn", "망가니즈", False, 4, 7), (26, "Fe", "철", False, 4, 8), (27, "Co", "코발트", False, 4, 9), (28, "Ni", "니켈", False, 4, 10), (29, "Cu", "구리", False, 4, 11), (30, "Zn", "아연", False, 4, 12), (31, "Ga", "갈륨", True, 4, 13), (32, "Ge", "저머니엄", True, 4, 14), (33, "As", "비소", False, 4, 15), (34, "Se", "셀레늄", True, 4, 16), (35, "Br", "브로민", False, 4, 17), (36, "Kr", "크립톤", False, 4, 18),
        (37, "Rb", "루비듐", True, 5, 1), (38, "Sr", "스트론튬", True, 5, 2), (39, "Y", "이트륨", True, 5, 3), (40, "Zr", "지르코늄", True, 5, 4), (41, "Nb", "나이오븀", True, 5, 5), (42, "Mo", "몰리브데넘", False, 5, 6), (43, "Tc", "테크네튬", True, 5, 7), (44, "Ru", "루테늄", True, 5, 8), (45, "Rh", "로듐", True, 5, 9), (46, "Pd", "파라듐", True, 5, 10), (47, "Ag", "은", False, 5, 11), (48, "Cd", "카드뮴", True, 5, 12), (49, "In", "인듐", True, 5, 13), (50, "Sn", "주석", False, 5, 14), (51, "Sb", "안티모니", False, 5, 15), (52, "Te", "텔루륨", True, 5, 16), (53, "I", "아이오딘", False, 5, 17), (54, "Xe", "제논", False, 5, 18),
        (55, "Cs", "세슘", True, 6, 1), (56, "Ba", "바륨", True, 6, 2), (72, "Hf", "하프늄", True, 6, 4), (73, "Ta", "탄탈럼", False, 6, 5), (74, "W", "텅스텐", False, 6, 6), (75, "Re", "레늄", True, 6, 7), (76, "Os", "오스뮴", True, 6, 8), (77, "Ir", "이리듐", True, 6, 9), (78, "Pt", "백금", False, 6, 10), (79, "Au", "금", False, 6, 11), (80, "Hg", "수은", False, 6, 12), (81, "Tl", "탈륨", True, 6, 13), (82, "Pb", "납", False, 6, 14), (83, "Bi", "비스무트", False, 6, 15), (84, "Po", "폴로늄", True, 6, 16), (85, "At", "아스타틴", False, 6, 17), (86, "Rn", "라돈", False, 6, 18),
        (87, "Fr", "프랑슘", True, 7, 1), (88, "Ra", "라듐", True, 7, 2), (104, "Rf", "러더포듐", True, 7, 4), (105, "Db", "더브늄", True, 7, 5), (106, "Sg", "시보륨", True, 7, 6), (107, "Bh", "보륨", True, 7, 7), (108, "Hs", "하슘", True, 7, 8), (109, "Mt", "마이트너륨", True, 7, 9), (110, "Ds", "다름슈타튬", True, 7, 10), (111, "Rg", "뢴트게늄", True, 7, 11), (112, "Cn", "코페르니슘", True, 7, 12), (113, "Nh", "니호늄", True, 7, 13), (114, "Fl", "플레로븀", True, 7, 14), (115, "Mc", "모스코븀", True, 7, 15), (116, "Lv", "리버모륨", True, 7, 16), (117, "Ts", "테네신", False, 7, 17), (118, "Og", "오가네손", False, 7, 18)
    ]

    # HTML 주기율표 생성
    grid_html = "<div class='periodic-table'>"
    # 7행 18열 격자 채우기
    grid_map = {(row, col): None for row in range(1, 8) for col in range(1, 19)}
    for elem in elements_data:
        grid_map[(elem[3 if len(elem)==5 else 4], elem[4 if len(elem)==5 else 5])] = elem

    for row in range(1, 8):
        for col in range(1, 19):
            elem = grid_map.get((row, col))
            if elem:
                num, sym, name, is_killer = elem[0], elem[1], elem[2], elem[3]
                box_class = "element-box killer-box" if is_killer else "element-box"
                fire = "🔥" if is_killer else ""
                grid_html += f"""
                <div class='{box_class}'>
                    <div class='elem-num'>{num}</div>
                    <div class='elem-sym'>{sym}</div>
                    <div class='elem-name'>{name}{fire}</div>
                </div>
                """
            else:
                grid_html += "<div style='background-color: transparent;'></div>"
    grid_html += "</div>"

    st.markdown(grid_html, unsafe_allow_html=True)
    st.info("💡 Tip: 원소명에 **🔥 표시가 붙어있는 원소**는 상대방이 절대로 받아칠 수 없는 완벽한 필승 한방단어입니다!")

# ==========================================
# 3. 🔍 네이버 사전 실시간 검색기
# ==========================================
elif menu == "🔍 네이버 사전 검색기":
    st.title("🔍 네이버 사전 실시간 검증 검색기")
    st.caption("네이버 표준국어대사전에 실제 등재되어 있는지, 한방단어인지 실시간 연동되어 검색됩니다.")
    
    search_query = st.text_input("검색할 단어를 입력해보세요:")
    if search_query:
        search_query = search_query.strip()
        is_dict_valid = is_valid_korean_word(search_query)
        is_killer = search_query in ALL_KILLER_WORDS

        st.subheader(f"검색 결과: '{search_query}'")
        col1, col2 = st.columns(2)
        
        with col1:
            if is_dict_valid:
                st.success("✅ 네이버 표준국어대사전 등재 단어")
            else:
                st.error("❌ 사전에 없는 단어 (게임에서 사용 불가)")

        with col2:
            if is_killer:
                st.error("💥 절대 한방단어 (사용 시 봇 즉사 및 승리!)")
            else:
                st.info("🔵 일반 단어 (주고받기 가능)")

# ==========================================
# 4. 📖 한방단어 대사전
# ==========================================
elif menu == "📖 한방단어 대사전":
    st.title("📖 두음법칙 검증완료 절대 한방단어 사전")
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
                        st.subheader(f"📌 '{syllable}' 시작 한방단어")
                        for word in words:
                            st.markdown(f"- **{word[:-1]}<span style='color:red; font-weight:bold;'>{word[-1]}</span>**", unsafe_allow_html=True)
            if not found:
                st.info("등록된 한방단어가 없습니다.")

# ==========================================
# 5. 🛒 상점 (포인트 꾸미기)
# ==========================================
elif menu == "🛒 상점 (꾸미기)":
    st.title("🛒 포인트 꾸미기 상점")
    st.write(f"보유 포인트: **{st.session_state.points} P**")
    st.divider()

    items = {
        "👑 왕관 칭호": {"price": 100, "type": "칭호", "desc": "채팅창 제목에 👑 왕관 아이콘 표시"},
        "🌸 벚꽃 테마": {"price": 150, "type": "테마", "desc": "화사한 분홍빛 배경 테마"},
        "🌌 심연의 우주 테마": {"price": 250, "type": "테마", "desc": "다크 모드 우주 배경 테마"},
        "🔥 지옥불 테마": {"price": 300, "type": "테마", "desc": "강렬한 붉은색 지옥불 테마"}
    }

    for item_name, info in items.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{item_name} ({info['price']} P)")
            st.write(info['desc'])
        with col2:
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

    if st.button("테마 기본으로 되돌리기"):
        st.session_state.equipped_theme = "기본"
        st.rerun()
