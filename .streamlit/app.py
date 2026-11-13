import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import base64
import requests
from datetime import datetime

# ==============================================================================
# 🎨 [UI 및 기본 설정 영역] - 나중에 디자인이나 문구를 바꾸고 싶을 때 여기만 수정하세요!
# ==============================================================================
SITE_TITLE = "제주시 월평동 4·3 기억 아카이브"
SITE_SUBTITLE = "제주 4·3 당시 월평마을의 잃어버린 터와 주민들의 기억을 기록하고 보존하는 공간입니다."

# 색상 설정 (원하는 색상 코드로 변경 가능)
COLOR_PRIMARY_NAVY = "#141E30"   # 상단 배너 및 포인트 네이비 색상
COLOR_ACCENT_RED = "#D94848"     # 동백꽃 포인트 레드 색상
COLOR_BG_IVORY = "#FBF9F5"       # 배경 웜 아이보리 색상

# ==============================================================================
# 1. 페이지 기본 설정 및 커스텀 CSS 적용
# ==============================================================================
st.set_page_config(
    page_title=SITE_TITLE,
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(f"""
<style>
    /* 전체 배경 및 폰트 여백 다듬기 */
    .stApp {{
        background-color: {COLOR_BG_IVORY};
    }}
    /* 상단 히어로 배너 스타일 */
    .hero-banner {{
        background: linear-gradient(135deg, {COLOR_PRIMARY_NAVY} 0%, #243B55 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(20, 30, 48, 0.15);
    }}
    .hero-badge {{
        display: inline-block;
        background-color: rgba(217, 72, 72, 0.2);
        border: 1px solid {COLOR_ACCENT_RED};
        color: #FF8A8A;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }}
    .hero-title {{
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
    }}
    .hero-desc {{
        font-size: 1.05rem;
        color: #CBD5E1;
        margin: 0;
    }}
    /* 자료 카드 디자인 */
    .archive-card {{
        background-color: white;
        border: 1px solid #E5E0D8;
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .cat-badge {{
        background-color: #F1F5F9;
        color: {COLOR_PRIMARY_NAVY};
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
    }}
    .meta-text {{
        color: #64748B;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. 깃허브(GitHub) 연동 데이터 영구 저장 및 불러오기 함수
# ==============================================================================
# 기본 샘플 데이터 (깃허브에 아직 데이터가 없을 때 자동으로 보여줄 초기 기록)
DEFAULT_RECORDS = [
    {
        "id": "rec_001",
        "title": "1948년 11월 월평마을 소개령과 잃어버린 웃동네 터 조사",
        "category": "문서/사료",
        "location": "월평 웃동네 옛터",
        "year": "1948",
        "author": "월평동 4·3 조사팀",
        "source": "제주4·3사건진상조사보고서 및 마을 원로 구술 채록",
        "summary": "중산간 지역 소개령 당시 월평마을 상단부(웃동네) 가옥 전소 경위와 주민 피난 경로를 정리한 기초 조사 자료입니다.",
        "content": "1948년 11월 중순, 해안선으로부터 5km 이상 떨어진 중산간 마을에 대한 강경 진압 작전과 소개령이 내려지면서 월평동 웃동네 일대 40여 가구가 전소되었습니다.\n\n당시 주민들은 아라동과 영평동 방면, 또는 해안가 친척 집으로 흩어져 피난 생활을 이어갔으며, 현재도 대나무 숲과 팽나무 주변으로 옛 집터의 올레길과 돌담 흔적이 남아 있습니다.",
        "image_url": "",
        "published": True,
        "created_at": "2026-11-10"
    },
    {
        "id": "rec_002",
        "title": "월평 본동 옛 성담(방어벽) 축조 및 주민 동원 기록",
        "category": "현장 사진",
        "location": "월평마을 본동 옛터",
        "year": "1949",
        "author": "현장기록반",
        "source": "제주시 월평동 향토지 및 현장 답사 기록",
        "summary": "1949년 초 마을 외곽을 둘러싸고 쌓았던 전략촌 성담의 잔존 구간과 당시 주민들의 보초 동원 실태를 기록했습니다.",
        "content": "소개령 이후 남아 있던 본동 주민들은 마을 외곽에 높이 약 2~3m 규모의 돌담(성담)을 쌓도록 동원되었습니다.\n\n현재 마을 안길 일부 구간에는 당시 쌓았던 겹담 형태의 성담 하단부가 보존되어 있어, 당시 마을의 긴박했던 상황을 증언하고 있습니다.",
        "image_url": "",
        "published": True,
        "created_at": "2026-11-11"
    },
    {
        "id": "rec_003",
        "title": "[구술채록] '불탄 집터에 다시 돌담을 쌓기까지' - 월평동 어르신 증언",
        "category": "구술 증언",
        "location": "월평동 마을회관 일대",
        "year": "1950",
        "author": "구술기록단",
        "source": "2025년 월평동 4·3 생애사 구술 프로젝트",
        "summary": "유년 시절 4·3을 겪은 월평동 원로 주민의 피난 기억과 1950년대 마을 재건 과정에 대한 생생한 증언입니다.",
        "content": "\"그때는 밤마다 총소리가 들려서 밭담 밑에 숨어 지냈지. 나중에 마을이 다시 복구될 때도 터만 남아 있어서 처음부터 돌을 하나씩 날라 집을 다시 지었어.\"\n\n본 기록은 구술자의 동의를 얻어 원문의 제주어 어휘를 최대한 살려 채록하였습니다.",
        "image_url": "",
        "published": True,
        "created_at": "2026-11-12"
    }
]

def github_api_available():
    return all(k in st.secrets for k in ["GITHUB_TOKEN", "GITHUB_REPO"])

def load_records():
    """깃허브 저장소의 data/records.json에서 데이터를 불러옵니다."""
    if not github_api_available():
        if "local_records" not in st.session_state:
            st.session_state.local_records = DEFAULT_RECORDS.copy()
        return st.session_state.local_records

    token = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    url = f"https://api.github.com/repos/{repo}/contents/data/records.json"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        content = base64.b64decode(res.json()["content"]).decode("utf-8")
        return json.loads(content)
    else:
        return DEFAULT_RECORDS.copy()

def save_records(records, commit_msg="Update archive records"):
    """수정된 데이터 목록을 깃허브 저장소 data/records.json에 영구 저장합니다."""
    if not github_api_available():
        st.session_state.local_records = records
        return True

    token = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    url = f"https://api.github.com/repos/{repo}/contents/data/records.json"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    # 기존 파일 SHA 확인
    get_res = requests.get(url, headers=headers)
    sha = get_res.json().get("sha") if get_res.status_code == 200 else None

    encoded = base64.b64encode(json.dumps(records, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    payload = {"message": commit_msg, "content": encoded}
    if sha:
        payload["sha"] = sha

    put_res = requests.put(url, headers=headers, json=payload)
    return put_res.status_code in [200, 201]

def upload_image_to_github(uploaded_file):
    """관계자가 올린 이미지 파일을 깃허브 저장소에 저장하고 이미지 URL을 반환합니다."""
    if not github_api_available() or uploaded_file is None:
        return ""

    token = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"images/{timestamp}_{uploaded_file.name}"
    url = f"https://api.github.com/repos/{repo}/contents/{safe_name}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    encoded = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    payload = {"message": f"Upload image {safe_name}", "content": encoded}
    res = requests.put(url, headers=headers, json=payload)

    if res.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{repo}/main/{safe_name}"
    return ""

# ==============================================================================
# 3. 세션 상태 및 권한(관리자 로그인) 관리
# ==============================================================================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

records = load_records()
visible_records = records if st.session_state.is_admin else [r for r in records if r.get("published", True)]

# ==============================================================================
# 4. 상단 헤더 & 관계자 로그인 바
# ==============================================================================
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.caption("🌺 JEJU 4·3 REGIONAL ARCHIVE | 제주시 월평동 지역사 기록보관소")
with top_col2:
    if st.session_state.is_admin:
        if st.button("🔓 관계자 로그아웃", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()
    else:
        with st.popover("🔐 관계자 로그인", use_container_width=True):
            st.markdown("**관계자 전용 로그인**")
            st.caption("일반 시청자는 로그인 없이 모든 공개 자료를 열람할 수 있습니다.")
            input_id = st.text_input("아이디", key="login_id")
            input_pw = st.text_input("비밀번호", type="password", key="login_pw")
            if st.button("로그인", type="primary", use_container_width=True):
                admin_id = st.secrets.get("ADMIN_ID", "admin_wolpyeong")
                admin_pw = st.secrets.get("ADMIN_PW", "43jeju1948")
                if input_id == admin_id and input_pw == admin_pw:
                    st.session_state.is_admin = True
                    st.success("관계자 모드로 전환되었습니다.")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

# 상단 히어로 배너
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">제주시 월평동 4·3 기록 아카이브</div>
    <h1 class="hero-title">{SITE_TITLE}</h1>
    <p class="hero-desc">{SITE_SUBTITLE}</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. 메인 탭 메뉴 구성 (관계자 로그인 시 '자료 업로드/관리' 탭 자동 추가)
# ==============================================================================
tab_names = ["🏠 아카이브 홈", "📚 자료 목록 및 열람", "🗺️ 월평동 유적지 지도", "⏳ 사건 연표"]
if st.session_state.is_admin:
    tab_names.append("✍️ 관계자 자료 등록·관리")

tabs = st.tabs(tab_names)

# ------------------------------------------------------------------------------
# [탭 1] 아카이브 홈
# ------------------------------------------------------------------------------
with tabs[0]:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 등록 사료", f"{len(visible_records)}건")
    m2.metric("조사 권역", "5개 주요 터")
    m3.metric("기록 시기", "1947 ~ 현재")
    m4.metric("열람 권한", "관계자 편집 모드" if st.session_state.is_admin else "누구나 무료 열람")

    st.markdown("---")
    st.subheader("📌 최근 등록된 월평동 4·3 기록")
    for rec in visible_records[:3]:
        status_tag = "" if rec.get("published", True) else " 🔒 [비공개 임시저장]"
        st.markdown(f"""
        <div class="archive-card">
            <span class="cat-badge">{rec['category']}</span> <span style="color:#D94848; font-weight:700; font-size:0.85rem;">{status_tag}</span>
            <h4 style="margin: 8px 0 6px 0; color:#141E30;">{rec['title']}</h4>
            <p style="margin: 0; color:#334155; font-size:0.95rem;">{rec['summary']}</p>
            <div class="meta-text">📍 {rec['location']} &nbsp;|&nbsp; 📅 시기: {rec['year']}년 &nbsp;|&nbsp; ✍️ {rec['author']}</div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# [탭 2] 자료 목록 및 상세 열람
# ------------------------------------------------------------------------------
with tabs[1]:
    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        selected_cat = st.selectbox("자료 유형 필터", ["전체", "문서/사료", "현장 사진", "구술 증언", "논문/기사"])
    with f_col2:
        search_kw = st.text_input("키워드 검색 (제목, 장소, 내용 검색)", placeholder="예: 웃동네, 성담, 소개령...")

    filtered = visible_records
    if selected_cat != "전체":
        filtered = [r for r in filtered if r["category"] == selected_cat]
    if search_kw:
        kw = search_kw.lower()
        filtered = [r for r in filtered if kw in r["title"].lower() or kw in r["content"].lower() or kw in r["location"].lower()]

    st.caption(f"총 **{len(filtered)}건**의 기록이 검색되었습니다. 각 항목을 클릭하면 전체 본문과 이미지를 볼 수 있습니다.")

    for rec in filtered:
        badge = "" if rec.get("published", True) else "🔒 [임시저장] "
        with st.expander(f"{badge}[{rec['category']}] {rec['title']}  ({rec['year']}년 · {rec['location']})"):
            st.markdown(f"**요약:** {rec['summary']}")
            st.markdown("---")
            if rec.get("image_url"):
                st.image(rec["image_url"], caption=rec["title"], use_container_width=True)
            st.write(rec["content"])
            st.info(f"📌 **자료 출처:** {rec['source']}  |  **조사/작성:** {rec['author']}  |  **등록일:** {rec['created_at']}")

# ------------------------------------------------------------------------------
# [탭 3] 월평동 유적지 지도
# ------------------------------------------------------------------------------
with tabs[2]:
    st.subheader("🗺️ 제주시 월평동 4·3 주요 조사 지점")
    st.caption("지도 위의 핀을 클릭하면 해당 지점의 역사적 배경을 확인할 수 있습니다.")

    # 제주시 월평동 일대 주요 조사 좌표
    locations_data = [
        {"name": "월평마을 본동 옛터", "lat": 33.4735, "lon": 126.5592, "desc": "4·3 당시 마을 중심지로, 1949년 전략촌 성담 축조의 중심 구역입니다."},
        {"name": "월평 웃동네 잃어버린 마을 터", "lat": 33.4678, "lon": 126.5615, "desc": "1948년 11월 중산간 소개령 당시 전소되어 복구되지 못한 옛 집터 일대입니다."},
        {"name": "월평 옛 성담(방어벽) 잔존 구간", "lat": 33.4748, "lon": 126.5570, "desc": "주민들이 동원되어 쌓았던 마을 외곽 방어용 돌담 흔적이 남아 있는 곳입니다."},
        {"name": "월평동 마을회관 및 구술 채록 거점", "lat": 33.4729, "lon": 126.5585, "desc": "월평동 원로 주민들의 4·3 기억과 생애사 구술 기록이 모이는 공간입니다."}
    ]

    m = folium.Map(location=[33.4718, 126.5595], zoom_start=15)
    for loc in locations_data:
        folium.Marker(
            [loc["lat"], loc["lon"]],
            popup=folium.Popup(f"<b>{loc['name']}</b><br>{loc['desc']}", max_width=250),
            tooltip=loc["name"],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    st_folium(m, width="100%", height=450)

# ------------------------------------------------------------------------------
# [탭 4] 사건 연표
# ------------------------------------------------------------------------------
with tabs[3]:
    st.subheader("⏳ 제주시 월평동 4·3 주요 연표")
    timeline_items = [
        ("1947년 3월", "3·1절 발포 사건 이후 제주 전역 긴장 고조 및 월평마을 내 청년 활동 전개"),
        ("1948년 11월", "중산간 지역 강경 진압 작전 및 소개령 발령 — 월평 웃동네 일대 가옥 전소 및 주민 피난"),
        ("1949년 초", "해안·중간 지대 전략촌화 정책에 따라 월평 본동 외곽 성담 축조 및 보초 동원"),
        ("1950년대 중반", "한라산 금족령 해제 이후 월평마을 본동 중심의 주민 귀환 및 마을 재건"),
        ("2020년대 ~ 현재", "월평동 4·3 유적지 기초 조사, 잃어버린 마을 터 기록화 및 주민 구술 채록 사업 진행")
    ]
    for period, event in timeline_items:
        st.markdown(f"""
        <div class="archive-card" style="border-left: 5px solid {COLOR_ACCENT_RED}; padding: 1rem 1.4rem;">
            <strong style="color:{COLOR_ACCENT_RED}; font-size:1.05rem;">{period}</strong>
            <p style="margin: 4px 0 0 0; color:#1F2937;">{event}</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# [탭 5] 관계자 전용 자료 등록 및 수정/삭제 (로그인 시에만 표시)
# ------------------------------------------------------------------------------
if st.session_state.is_admin:
    with tabs[4]:
        st.subheader("✍️ 새 조사 자료 업로드")
        with st.form("upload_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            new_title = c1.text_input("자료 제목 *", placeholder="예: 월평동 냇가 일대 유적 현장 답사 보고")
            new_cat = c2.selectbox("자료 유형 *", ["문서/사료", "현장 사진", "구술 증언", "논문/기사"])

            c3, c4, c5 = st.columns(3)
            new_loc = c3.text_input("관련 장소", value="제주시 월평동")
            new_year = c4.text_input("사건/자료 연도", value="1948")
            new_author = c5.text_input("작성자/조사팀", value="월평동 4·3 조사팀")

            new_source = st.text_input("자료 출처 / 참고문헌", placeholder="예: 제주4·3평화재단 아카이브, 현장 직접 촬영 등")
            new_summary = st.text_input("한 줄 요약 *", placeholder="목록 카드에 표시될 핵심 요약 문장을 적어주세요.")
            new_content = st.text_area("상세 본문 내용 *", height=180, placeholder="조사한 상세 기록이나 구술 내용을 입력하세요.")
            new_image = st.file_uploader("현장 사진 또는 문서 스캔본 첨부 (선택)", type=["png", "jpg", "jpeg"])
            is_published = st.checkbox("즉시 시청자에게 공개하기 (체크 해제 시 관계자만 보는 임시저장으로 등록)", value=True)

            submitted = st.form_submit_button("📥 아카이브에 저장하기", type="primary")
            if submitted:
                if not new_title or not new_summary or not new_content:
                    st.warning("제목, 한 줄 요약, 상세 본문 내용은 필수 입력 항목입니다.")
                else:
                    with st.spinner("자료를 저장하는 중입니다..."):
                        img_url = upload_image_to_github(new_image)
                        new_item = {
                            "id": f"rec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "title": new_title,
                            "category": new_cat,
                            "location": new_loc,
                            "year": new_year,
                            "author": new_author,
                            "source": new_source if new_source else "자체 조사 기록",
                            "summary": new_summary,
                            "content": new_content,
                            "image_url": img_url,
                            "published": is_published,
                            "created_at": datetime.now().strftime("%Y-%m-%d")
                        }
                        records.insert(0, new_item)
                        if save_records(records, f"Add record: {new_title}"):
                            st.success("새 자료가 성공적으로 저장되었습니다!")
                            st.rerun()
                        else:
                            st.error("저장 중 오류가 발생했습니다. Secrets 설정을 확인해 주세요.")

        st.markdown("---")
        st.subheader("🗂️ 기존 등록 자료 수정 / 삭제 관리")
        for idx, rec in enumerate(records):
            with st.expander(f"관리: {rec['title']} ({'공개중' if rec.get('published', True) else '비공개'})"):
                edit_title = st.text_input("제목 수정", value=rec["title"], key=f"t_{rec['id']}")
                edit_summary = st.text_input("요약 수정", value=rec["summary"], key=f"s_{rec['id']}")
                edit_content = st.text_area("본문 수정", value=rec["content"], key=f"c_{rec['id']}")
                edit_pub = st.checkbox("공개 상태 유지", value=rec.get("published", True), key=f"p_{rec['id']}")

                b1, b2 = st.columns([1, 5])
                if b1.button("💾 수정 저장", key=f"save_{rec['id']}"):
                    records[idx]["title"] = edit_title
                    records[idx]["summary"] = edit_summary
                    records[idx]["content"] = edit_content
                    records[idx]["published"] = edit_pub
                    save_records(records, f"Edit record: {edit_title}")
                    st.success("수정되었습니다.")
                    st.rerun()
                if b2.button("🗑️ 삭제", key=f"del_{rec['id']}"):
                    records.pop(idx)
                    save_records(records, f"Delete record: {rec['title']}")
                    st.warning("삭제되었습니다.")
                    st.rerun()
