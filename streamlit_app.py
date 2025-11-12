import streamlit as st
import pandas as pd
import plotly.express as px  # Plotly 라이브러리
import re  # 정규식(Regex) 라이브러리 임포트

# ----------------------------------------------------------------------
# 1. 앱 기본 설정
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="미래 주거 키워드 대시보드",
    page_icon="🏠",
    layout="wide"
)

# ----------------------------------------------------------------------
# 2. 축 정의 (수정 완료된 버전)
# ----------------------------------------------------------------------
# 'key'는 '키워드 점수 표.xlsx'의 컬럼명과 정확히 일치해야 합니다.
AXIS_DEFINITIONS = {
    "개인 경험 vs 집단 경험": {
        "key": "개인 경험 vs 집단 경험",
        "name": "개인 경험 vs 집단 경험",
        "min_label": "집단 경험 (Collective)", # 수정됨: 점수 기준에 따라 의미 반전
        "max_label": "개인 경험 (Personal)"     # 수정됨: 점수 기준에 따라 의미 반전
    },
    "대중화 vs 프리미엄화": {
        "key": "대중화 vs 프리미엄화",
        "name": "대중화 vs 프리미엄화",
        "min_label": "프리미엄화 (Premium)", # 수정됨: 점수 기준에 따라 의미 반전
        "max_label": "대중화 (Mass)"        # 수정됨: 점수 기준에 따라 의미 반전
    },
    "단기 수익 vs 장기 지속 가능성": {
        "key": "단기 수익 vs 장기 지속 가능성",
        "name": "단기 수익 vs 장기 지속 가능성",
        "min_label": "장기 지속 (Long-term)",  # 수정됨: 점수 기준에 따라 의미 반전
        "max_label": "단기 수익 (Short-term)" # 수정됨: 점수 기준에 따라 의미 반전
    },
    "자동화 vs 인간 개입": {
        "key": "자동화 vs 인간 개입",
        "name": "자동화 vs 인간 개입",
        "min_label": "인간 개입 (Human)",    # 수정됨: 점수 기준에 따라 의미 반전
        "max_label": "자동화 (Automation)"  # 수정됨: 점수 기준에 따라 의미 반전
    },
    "자연 친화 vs 인공/도시 중심": {
        "key": "자연 친화 vs 인공/도시 중심",
        "name": "자연 친화 vs 인공/도시 중심",
        "min_label": "인공/도시 (Urban)",  # 수정됨: 점수 기준에 따라 의미 반전
        "max_label": "자연 친화 (Nature)"   # 수정됨: 점수 기준에 따라 의미 반전
    },
    "프라이버시/보안 vs 개방/공유": {
        "key": "프라이버시/보안 vs 개방/공유",
        "name": "프라이버시/보안 vs 개방/공유",
        "min_label": "개방/공유 (Sharing)",  # 수정됨: 점수 기준에 따라 의미 반전
        "max_label": "프라이버시 (Privacy)" # 수정됨: 점수 기준에 따라 의미 반전
    },
    "기능 중심 vs 감성 중심": {
        "key": "기능 중심 vs 감성 중심",
        "name": "기능 중심 vs 감성 중심",
        "min_label": "감성 중심 (Emotional)",  # 수정됨: 점수 기준에 따라 의미 반전
        "max_label": "기능 중심 (Functional)" # 수정됨: 점수 기준에 따라 의미 반전
    }
}


# ----------------------------------------------------------------------
# 3. 데이터 로딩 (Excel 파일) - 점수/근거 파싱
# ----------------------------------------------------------------------
# [수정] 엑셀 파일과 시트 이름을 사용하도록 복원
EXCEL_FILE_NAME = "키워드 점수 표.xlsx"
SHEET_NAME = "키워드_중복제거"
SCENARIO_SHEET_NAME = "아이디어"

# [수정] 정규식 패턴: '+' 부호를 인식하도록 [+-]?로 변경
SCORE_RATIONALE_PATTERN = re.compile(r"^\s*([+-]?\d+\.?\d*)\s*\((.*)\)\s*$")

def parse_score_rationale(text):
    """
    "점수 (근거...)" 형식의 문자열을 (점수, 근거) 튜플로 분리합니다.
    """
    if not isinstance(text, str):
        return (None, None)
    
    match = SCORE_RATIONALE_PATTERN.match(text)
    if match:
        try:
            score = float(match.group(1))
            rationale = match.group(2).strip()
            return (score, rationale)
        except (ValueError, TypeError):
            return (None, None) # 파싱 실패
    return (None, None) # 매치 실패

@st.cache_data
def load_data(file_name, sheet_name): # '키워드_중복제거' 시트 로드용
    """
    미리 계산된 점수 엑셀 파일을 로드하고,
    7개 축 컬럼을 파싱하여 새 컬럼을 생성합니다.
    """
    try:
        # [수정] pd.read_excel을 사용하도록 복원
        df = pd.read_excel(file_name, sheet_name=sheet_name, header=0)
        
        # 1-67번 키워드 누락 문제 해결
        df['번호'] = pd.to_numeric(df['번호'], errors='coerce')
        df = df.dropna(subset=['번호', '트렌드 키워드', '핵심 정의'])
        df['번호'] = df['번호'].astype(int)
        df = df.drop_duplicates(subset=['번호'], keep='first')
        
        # --- [핵심] 점수 및 근거 파싱 (수정된 7개 축 기준) ---
        for axis_info in AXIS_DEFINITIONS.values():
            axis_key = axis_info['key'] # 예: "개인 경험 vs 집단 경험"
            
            # 파싱된 결과를 저장할 새 컬럼 이름
            score_col_name = f"score_{axis_key}"
            rationale_col_name = f"rationale_{axis_key}"
            
            if axis_key in df.columns:
                # parse_score_rationale 함수를 적용하여 두 개의 새 컬럼 생성
                parsed_data = df[axis_key].apply(parse_score_rationale)
                df[score_col_name] = parsed_data.apply(lambda x: x[0])
                df[rationale_col_name] = parsed_data.apply(lambda x: x[1])
            else:
                st.error(f"오류: 엑셀에서 '{axis_key}' 컬럼을 찾을 수 없습니다.")
        
        return df
    
    except FileNotFoundError:
        st.error(f"오류: '{file_name}' 파일을 찾을 수 없습니다. 파일 이름이 정확한지 확인하세요.")
        return None
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}. 'openpyxl' 라이브러리가 설치되었는지 확인하세요.")
        return None

# [수정] 시나리오(아이디어) 데이터 로드 함수 (Excel에서 직접 로드 및 파싱)
@st.cache_data
def load_scenario_data(file_name, sheet_name):
    """
    시나리오(아이디어) 엑셀 시트를 로드하고
    병합된 셀처럼 보이는 '전략' 컬럼을 정리합니다.
    또한 점수(근거) 컬럼을 파싱합니다.
    """
    try:
        # [수정] pd.read_excel을 사용하도록 복원
        df = pd.read_excel(file_name, sheet_name=sheet_name)
        
        # 컬럼 이름이 'Unnamed: 1', 'Unnamed: 3' 등으로 읽힐 것을 대비
        df = df.rename(columns={'Unnamed: 1': '전략명', 'Unnamed: 3': '아이디어명'})

        # [수정] .fillna(method='ffill') -> .ffill()로 변경 (경고 제거)
        df['전략'] = df['전략'].ffill()
        df['전략명'] = df['전략명'].ffill()

        # '전략_대분류' 컬럼 생성
        df['전략_대분류'] = df['전략'].astype(float).astype(int).astype(str) + ". " + df['전략명']
        
        # '아이디어_명' 컬럼 생성
        df['아이디어_명'] = df['아이디어'] + ". " + df['아이디어명']
        
        # --- 점수/근거 파싱 ---
        criteria_cols = ['기술 실현 가능성', '법제도 허용성', '기술 수용성']
        score_cols_to_check = []
        parsed_score_cols = [] # [신규] 합산 점수 계산용
        
        for col_name in criteria_cols:
            if col_name in df.columns:
                score_col = f"score_{col_name}"
                rationale_col = f"rationale_{col_name}"
                score_cols_to_check.append(score_col)
                parsed_score_cols.append(score_col) # [신규]
                
                # parse_score_rationale 함수를 적용하여 두 개의 새 컬럼 생성
                parsed_data = df[col_name].apply(parse_score_rationale)
                df[score_col] = parsed_data.apply(lambda x: x[0])
                df[rationale_col] = parsed_data.apply(lambda x: x[1])
            else:
                st.error(f"오류: 아이디어 시트에서 '{col_name}' 컬럼을 찾을 수 없습니다.")

        # 파싱된 점수 컬럼 기준으로 NaN이 아닌 행만 선택
        df_clean = df.dropna(subset=score_cols_to_check).copy()
        
        # [신규] '전체점수' 컬럼 계산
        df_clean['score_전체점수'] = df_clean[parsed_score_cols].sum(axis=1)
        
        return df_clean

    except FileNotFoundError:
        st.error(f"오류: '{file_name}' 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        st.error(f"시나리오 데이터 로딩 중 오류: {e}")
        return None

# ----------------------------------------------------------------------
# 4. 시각화 함수 (2x2 매트릭스용)
# ----------------------------------------------------------------------
def display_visualizations(df, x_axis, y_axis, show_text, color_map): # [수정] color_map 인수 추가
    """
    미리 파싱된 데이터를 바탕으로 2D 사분면 차트와 테이블을 표시합니다.
    show_text (bool): 차트에 텍스트 레이블을 표시할지 여부
    """
    if df.empty:
        st.warning("선택한 필터 조건에 맞는 키워드가 없습니다.")
        return
        
    # --- 1. 동적 컬럼명 및 호버 데이터 생성 ---
    x_score_col = f"score_{x_axis['key']}"
    y_score_col = f"score_{y_axis['key']}"
    x_rationale_col = f"rationale_{x_axis['key']}"
    y_rationale_col = f"rationale_{y_axis['key']}"
    
    # [수정] .copy()를 추가하여 SettingWithCopyWarning 해결
    df_display = df.dropna(subset=[x_score_col, y_score_col]).copy()
    
    if df_display.empty:
        st.warning(f"선택된 '{x_axis['name']}' 또는 '{y_axis['name']}' 축에 대한 점수 데이터가 없습니다.")
        return
        
    # [수정] 툴팁 서식 지정을 위한 새 컬럼 생성 (.loc 사용)
    df_display.loc[:, 'X축 점수_str'] = df_display[x_score_col].map('{:+.1f}'.format)
    df_display.loc[:, 'X축 근거'] = df_display[x_rationale_col].fillna('N/A')
    df_display.loc[:, 'Y축 점수_str'] = df_display[y_score_col].map('{:+.1f}'.format)
    df_display.loc[:, 'Y축 근거'] = df_display[y_rationale_col].fillna('N/A')

    # [수정] 툴팁 'nan' 및 dtype 경고 방지를 위해 텍스트 컬럼 처리
    df_display.loc[:, '트렌드 키워드'] = df_display['트렌드 키워드'].fillna('키워드 없음')
    # [수정] '번호_str'이라는 새 컬럼을 만들어 dtype 충돌 경고(FutureWarning) 해결
    df_display['번호_str'] = df_display['번호'].astype(str).fillna('N/A')
    df_display.loc[:, '대분류'] = df_display['대분류'].fillna('분류 없음')
    df_display.loc[:, '중분류 (접근방식 기준)'] = df_display['중분류 (접근방식 기준)'].fillna('분류 없음')


    text_labels = df_display["트렌드 키워드"] if show_text else None

    # 2. 2D 키워드 매트릭스 (Plotly Scatter Plot)
    st.subheader("📊 2x2 키워드 매트릭스")
    try:
        fig = px.scatter(
            df_display,
            x=x_score_col, 
            y=y_score_col, 
            hover_name="트렌드 키워드", 
            custom_data=[ 
                '번호_str', 
                '대분류', 
                '중분류 (접근방식 기준)',
                'X축 점수_str', 
                'X축 근거', 
                'Y축 점수_str', 
                'Y축 근거'
            ],
            color="대분류",
            color_discrete_map=color_map, # [신규] 파스텔 색상 적용
            title="키워드 사분면 분석",
            text=text_labels
        )

        # [수정] 툴팁 템플릿 (<font> 태그 제거)
        hovertemplate = (
            "<b>%{hovertext}</b> (번호: %{customdata[0]})" # 1) 키워드명
            "<br><br>" # 간격
            "대분류: %{customdata[1]}<br>" # 2) 대분류, 중분류
            "중분류: %{customdata[2]}"
            "<br><br>" # 간격
            "X축 점수: %{customdata[3]}<br>" # 3) X축
            "X축 근거: %{customdata[4]}<br>"
            "Y축 점수: %{customdata[5]}<br>" # 3) Y축
            "Y축 근거: %{customdata[6]}"
            "<extra></extra>" # 우측의 회색 박스 제거
        )

        if show_text:
            fig.update_traces(
                textposition='top center', 
                textfont=dict(size=15), # [수정] 글씨 크기 12 -> 15
                hovertemplate=hovertemplate 
            )
        else:
            fig.update_traces(
                hovertemplate=hovertemplate
            )


        fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="grey")
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="grey")
        
        # --- [수정] X, Y 축 범위 및 눈금 간격 조정 ---
        tick_values = list(range(-100, 101, 25)) # -100, -75, -50, ... 100
        tick_text = [str(v) for v in tick_values]

        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(
                range=[-110, 110], # [수정] 범위를 줄여서 줌인 (키워드 간격 확보)
                zeroline=False,
                showgrid=True,
                tickvals=tick_values, # [수정] 25 단위 눈금
                ticktext=tick_text  # [수정] 25 단위 텍스트
            ),
            yaxis=dict(
                range=[-110, 110], # [수정] 범위를 줄여서 줌인 (키워드 간격 확보)
                zeroline=False,
                showgrid=True,
                tickvals=tick_values, # [수정] 25 단위 눈금
                ticktext=tick_text  # [수정] 25 단위 텍스트
            ),
            height=1200, # [수정] 차트 크기 800 -> 1200
            margin=dict(l=150, r=150, t=100, b=100),
            dragmode='pan',
            hoverlabel=dict(font_size=16), # [신규] 툴팁 글씨 크기 16
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        # ---------------------------------------------------

        # X축 최소 레이블
        fig.add_annotation(
            text=f"<b>{x_axis['min_label']}</b>", 
            align='center', 
            showarrow=False,
            xref='paper', yref='paper', 
            x=0.01, y=-0.08,
            font=dict(size=14),
            xanchor='left'
        )
        # X축 최대 레이블
        fig.add_annotation(
            text=f"<b>{x_axis['max_label']}</b>", 
            align='center', 
            showarrow=False,
            xref='paper', yref='paper', 
            x=0.99, y=-0.08,
            font=dict(size=14),
            xanchor='right'
        )
        # Y축 최소 레이블
        fig.add_annotation(
            text=f"<b>{y_axis['min_label']}</b>", 
            align='center', 
            showarrow=False,
            xref='paper', yref='paper', 
            x=-0.08, y=0.01,
            font=dict(size=14), 
            textangle=-90,
            yanchor='bottom'
        )
        # Y축 최대 레이블
        fig.add_annotation(
            text=f"<b>{y_axis['max_label']}</b>", 
            align='center', 
            showarrow=False,
            xref='paper', yref='paper', 
            x=-0.08, y=0.99,
            font=dict(size=14), 
            textangle=-90,
            yanchor='top'
        )
        
        st.plotly_chart(
            fig, 
            use_container_width=True, 
            config={'scrollZoom': True}
        )
        
        st.caption("점에 마우스를 올리면 키워드와 상세 근거를 볼 수 있습니다. (사이드바에서 텍스트 표시 토글 가능)")

    except Exception as e:
        st.error(f"Plotly 차트 생성 중 오류: {e}")

    # 3. 전체 키워드 분석 데이터 (테이블)
    st.subheader("📋 전체 키워드 분석 데이터")
    
    df_display_table = df_display.copy()
    for col in df_display_table.columns:
        if df_display_table[col].dtype == 'object':
            df_display_table[col] = df_display_table[col].astype(str).fillna('N/A')
    
    # [수정] width='stretch' 사용 (경고 제거)
    st.dataframe(df_display_table, width='stretch')

    st.caption("테이블 헤더를 클릭하여 정렬할 수 있습니다.")


# ----------------------------------------------------------------------
# 5. Streamlit 메인 UI 구성 (탭 구조로 변경)
# ----------------------------------------------------------------------

# --- [수정] 데이터 로딩 (엑셀 파일 사용) ---
df_scores = load_data(EXCEL_FILE_NAME, SHEET_NAME)
df_scenario = load_scenario_data(EXCEL_FILE_NAME, SCENARIO_SHEET_NAME) 

# --- [신규] 파스텔 색상 맵 정의 ---
pastel_colors = px.colors.qualitative.Pastel
color_map_keyword = {}
color_map_scenario = {}

if df_scores is not None:
    keyword_categories = df_scores['대분류'].dropna().unique()
    color_map_keyword = {cat: pastel_colors[i % len(pastel_colors)] for i, cat in enumerate(keyword_categories)}

if df_scenario is not None:
    scenario_categories = df_scenario['전략_대분류'].dropna().unique()
    color_map_scenario = {cat: pastel_colors[i % len(pastel_colors)] for i, cat in enumerate(scenario_categories)}
# ---------------------------------


# --- '전체' 옵션 및 세션 상태 정의 (사이드바용) ---
all_cat_option = "--- 전체 (대분류) ---"
all_sub_cat_option = "--- 전체 (중분류) ---"

if 'cat_selection' not in st.session_state:
    st.session_state.cat_selection = [all_cat_option]
if 'sub_cat_selection' not in st.session_state:
    st.session_state.sub_cat_selection = [all_sub_cat_option]
if 'prev_cat_selection' not in st.session_state:
    st.session_state.prev_cat_selection = st.session_state.cat_selection.copy()
if 'prev_sub_cat_selection' not in st.session_state:
    st.session_state.prev_sub_cat_selection = st.session_state.sub_cat_selection.copy()

# 필터 변경 시 호출될 콜백 함수
def update_filters():
    # --- 대분류 로직 ---
    current_cat = st.session_state.cat_selection
    prev_cat = st.session_state.prev_cat_selection
    added_cat = [item for item in current_cat if item not in prev_cat]
    
    if added_cat:
        if added_cat[0] == all_cat_option:
            st.session_state.cat_selection = [all_cat_option]
        else:
            if all_cat_option in st.session_state.cat_selection:
                st.session_state.cat_selection.remove(all_cat_option)
    st.session_state.prev_cat_selection = st.session_state.cat_selection.copy()

    # --- 중분류 로직 ---
    current_sub = st.session_state.sub_cat_selection
    prev_sub = st.session_state.prev_sub_cat_selection
    added_sub = [item for item in current_sub if item not in prev_sub]
    
    if added_sub:
        if added_sub[0] == all_sub_cat_option:
            st.session_state.sub_cat_selection = [all_sub_cat_option]
        else:
            if all_sub_cat_option in st.session_state.sub_cat_selection:
                st.session_state.sub_cat_selection.remove(all_sub_cat_option)
    st.session_state.prev_sub_cat_selection = st.session_state.sub_cat_selection.copy()

# --- 사이드바 UI (탭과 무관하게 항상 표시) ---
# 사이드바는 df_scores 데이터가 있어야 옵션을 만들 수 있습니다.
if df_scores is not None:
    with st.sidebar:
        st.header("⚙️ 2x2 매트릭스 설정") 
        
        axis_options = list(AXIS_DEFINITIONS.keys())
        
        selected_x_axis_name = st.selectbox(
            "X축 기준을 선택하세요:",
            options=axis_options,
            index=0 
        )
        
        selected_y_axis_name = st.selectbox(
            "Y축 기준을 선택하세요:",
            options=axis_options,
            index=1
        )
        
        x_axis = AXIS_DEFINITIONS[selected_x_axis_name]
        y_axis = AXIS_DEFINITIONS[selected_y_axis_name]

        st.divider()

        show_text = st.checkbox("✅ 차트에 키워드 텍스트 표시", value=True) 
        st.caption("텍스트가 많아 겹칠 수 있습니다.")

        st.divider()

        # '대분류' 필터
        try:
            all_categories_list = list(df_scores['대분류'].dropna().unique())
            options_cat = [all_cat_option] + all_categories_list
            
            st.multiselect(
                "표시할 대분류를 선택하세요:",
                options=options_cat,
                key='cat_selection',
                on_change=update_filters
            )
        except KeyError:
            st.warning("'대분류' 컬럼을 찾을 수 없습니다.")
        
        # '중분류(접근방식 기준)' 필터
        try:
            all_sub_categories_list = list(df_scores['중분류 (접근방식 기준)'].dropna().unique())
            options_sub_cat = [all_sub_cat_option] + all_sub_categories_list
            
            st.multiselect(
                "표시할 중분류(접근방식 기준)를 선택하세요:",
                options=options_sub_cat,
                key='sub_cat_selection',
                on_change=update_filters
            )
        except KeyError:
            st.warning("'중분류 (접근방식 기준)' 컬럼을 찾을 수 없습니다.")
else:
    st.sidebar.error("키워드 엑셀 파일을 로드하지 못했습니다. 사이드바 옵션을 표시할 수 없습니다.")


# --- 메인 페이지 타이틀 ---
st.title("🏠 미래 주거 키워드 대시보드")

# --- 탭 생성 ---
tab_keyword, tab_scenario = st.tabs(["📊 2x2 키워드 매트릭스", "💡 시나리오 평가"])

# --- 탭 1: 2x2 키워드 매트릭스 ---
with tab_keyword:
    st.markdown("2x2 매트릭스(사분면)에 키워드를 배치하고 시각화합니다.")
    
    if df_scores is not None:
        # 필터 로직 (사이드바 값 기반)
        if 'cat_selection' not in st.session_state or all_cat_option in st.session_state.cat_selection:
            selected_categories = list(df_scores['대분류'].dropna().unique())
        else:
            selected_categories = st.session_state.cat_selection

        if 'sub_cat_selection' not in st.session_state or all_sub_cat_option in st.session_state.sub_cat_selection:
            selected_sub_categories = list(df_scores['중분류 (접근방식 기준)'].dropna().unique())
        else:
            selected_sub_categories = st.session_state.sub_cat_selection

        # 데이터 필터링 적용
        df_filtered = df_scores.copy() 
        if '대분류' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['대분류'].isin(selected_categories)]
        if '중분류 (접근방식 기준)' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['중분류 (접근방식 기준)'].isin(selected_sub_categories)]
        
        st.markdown(f"**{len(df_filtered)}**개 키워드를 **'{x_axis['name']}'** (X축) 및 **'{y_axis['name']}'** (Y축) 기준으로 표시합니다.")

        if selected_x_axis_name == selected_y_axis_name:
            st.error("X축과 Y축은 서로 다른 기준을 선택해야 합니다.")
        else:
            # [수정] color_map_keyword 전달
            display_visualizations(df_filtered, x_axis, y_axis, show_text, color_map_keyword)
    else:
        st.error(f"'{EXCEL_FILE_NAME}' ({SHEET_NAME}) 파일을 찾을 수 없습니다. 2x2 매트릭스를 표시할 수 없습니다.")

# --- 탭 2: 시나리오 평가 ---
with tab_scenario:
    st.subheader("💡 10대 아이디어 시나리오 평가")
    
    if df_scenario is not None:
        st.markdown("기술 실현 가능성, 법제도 허용성, 기술 수용성을 기준으로 10개 아이디어를 평가합니다.")

        # --- [신규] 1. '전체점수' 차트 (먼저 표시) ---
        st.subheader("시나리오별 '전체점수' (3대 기준 합산)")
        
        fig_total_score = px.bar(
            df_scenario,
            x='아이디어_명',
            y='score_전체점수',
            color='전략_대분류',
            color_discrete_map=color_map_scenario, # [신규] 파스텔 색상 적용
            title="시나리오별 '전체점수' (3대 기준 합산)",
            hover_data={ # 호버에는 원본(근거포함) 컬럼과 합산 점수 표시
                '전략_대분류': True,
                '아이디어_명': False,
                'score_전체점수': True,
                '기술 실현 가능성': True, 
                '법제도 허용성': True,
                '기술 수용성': True
            },
            labels={
                '아이디어_명': '아이디어', 
                'score_전체점수': '전체점수 (최대 30)',
                '전략_대분류': '전략',
                '기술 실현 가능성': '기술 실현 가능성',
                '법제도 허용성': '법제도 허용성',
                '기술 수용성': '기술 수용성'
            }
        )
        
        # [수정] 높이 및 눈금 간격 수정
        tick_values_30 = list(range(0, 31, 5)) # 0, 5, 10, ... 30
        
        fig_total_score.update_layout(
            height=1000, # [수정] 차트 높이 800 -> 1000
            xaxis_title=None,
            xaxis_tickangle=-45,
            yaxis=dict(
                range=[0, 30.5], # Y축 범위 (최대 30점)
                tickvals=tick_values_30, # [수정] 눈금 간격 5
                ticktext=[str(v) for v in tick_values_30]
            ), 
            hoverlabel=dict(font_size=16), # [신규] 툴팁 글씨 크기 16
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_total_score, use_container_width=True)
        
        st.divider() # --- 구분선 ---
        
        # --- 2. '개별 기준' 차트 (아래에 표시) ---
        st.subheader("시나리오별 '개별 기준' 점수 및 근거")
        
        # 평가 기준 선택자
        criteria_options = ['기술 실현 가능성', '법제도 허용성', '기술 수용성']
        selected_criterion = st.selectbox(
            "확인할 평가 기준을 선택하세요:",
            options=criteria_options,
            index=0 # 기본값: 첫 번째 기준
        )

        # 파싱된 컬럼명 정의
        score_col = f"score_{selected_criterion}"
        rationale_col = f"rationale_{selected_criterion}"

        # 선택된 기준으로 막대 차트 생성 (파싱된 점수 컬럼 사용)
        fig_scenario = px.bar(
            df_scenario,
            x='아이디어_명',
            y=score_col,    # Y축을 파싱된 'score_' 컬럼으로 변경
            color='전략_대분류',
            color_discrete_map=color_map_scenario, # [신규] 파스텔 색상 적용
            title=f'시나리오별 "{selected_criterion}" 점수',
            hover_data={
                '전략_대분류': True,
                '아이디어_명': False,
                '기술 실현 가능성': True, 
                '법제도 허용성': True,
                '기술 수용성': True,
                score_col: False
            },
            labels={
                '아이디어_명': '아이디어', 
                score_col: '점수 (1-10)',
                '전략_대분류': '전략',
                '기술 실현 가능성': '기술 실현 가능성',
                '법제도 허용성': '법제도 허용성',
                '기술 수용성': '기술 수용성'
            }
        )
        
        # [수정] 높이 및 눈금 간격 수정
        tick_values_10 = list(range(0, 11)) # 0, 1, 2, ... 10
        
        fig_scenario.update_layout(
            height=1000, # [수정] 차트 높이 800 -> 1000
            xaxis_title=None,
            xaxis_tickangle=-45,
            yaxis=dict(
                range=[0, 10.1], # Y축 범위 (최대 10점)
                tickvals=tick_values_10, # [수정] 눈금 간격 1
                ticktext=[str(v) for v in tick_values_10]
            ), 
            hoverlabel=dict(font_size=16), # [신규] 툴팁 글씨 크기 16
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_scenario, use_container_width=True)
        
        # --- 평가 근거 테이블 ---
        st.subheader(f"📋 '{selected_criterion}' 평가 근거")
        df_rationale = df_scenario[['아이디어_명', rationale_col]].copy()
        df_rationale.rename(
            columns={'아이디어_명': '아이디어', rationale_col: '근거'}, 
            inplace=True
        )
        st.dataframe(df_rationale.set_index('아이디어'), width='stretch')
        
        st.divider() # --- 구분선 ---

        # --- [수정] 3. 원본 데이터를 Expander 안에 넣기 ---
        with st.expander("📋 시나리오 평가 원본 데이터 (전체 보기)"):
            display_cols = ['전략_대분류', '기술 실현 가능성', '법제도 허용성', '기술 수용성']
            st.dataframe(
                df_scenario.set_index('아이디어_명')[display_cols], 
                width='stretch'
            )
        
    else:
        st.error(f"'{EXCEL_FILE_NAME}' ({SCENARIO_SHEET_NAME}) 파일을 찾을 수 없습니다. 시나리오 평가 탭을 표시할 수 없습니다.")