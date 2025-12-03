import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------
# 1. 앱 기본 설정
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="미래 주거 키워드 대시보드",
    page_icon="🏠",
    layout="wide"
)

# ----------------------------------------------------------------------
# 2. 축 정의
# ----------------------------------------------------------------------
AXIS_DEFINITIONS = {
    "개인 경험 vs 집단 경험": {"key": "개인 경험 vs 집단 경험", "name": "개인 경험 vs 집단 경험", "min_label": "개인 경험 (Personal)", "max_label": "집단 경험 (Collective)"},
    "대중화 vs 프리미엄화": {"key": "대중화 vs 프리미엄화", "name": "대중화 vs 프리미엄화", "min_label": "대중화 (Mass)", "max_label": "프리미엄화 (Premium)"},
    "단기 수익 vs 장기 지속 가능성": {"key": "단기 수익 vs 장기 지속 가능성", "name": "단기 수익 vs 장기 지속 가능성", "min_label": "단기 수익 (Short-term)", "max_label": "장기 지속 가능성 (Long-term)"},
    "자동화 vs 인간 개입": {"key": "자동화 vs 인간 개입", "name": "자동화 vs 인간 개입", "min_label": "자동화 (Automation)", "max_label": "인간 개입 (Human)"},
    "자연 친화 vs 인공/도시 중심": {"key": "자연 친화 vs 인공/도시 중심", "name": "자연 친화 vs 인공/도시 중심", "min_label": "자연 친화 (Nature)", "max_label": "인공/도시 중심 (Artificial)"},
    "프라이버시/보안 vs 개방/공유": {"key": "프라이버시/보안 vs 개방/공유", "name": "프라이버시/보안 vs 개방/공유", "min_label": "프라이버시/보안 (Privacy)", "max_label": "개방/공유 (Openness)"},
    "기능 중심 vs 감성 중심": {"key": "기능 중심 vs 감성 중심", "name": "기능 중심 vs 감성 중심", "min_label": "기능 중심 (Function)", "max_label": "감성 중심 (Emotion)"},
    "낮은 인지도 vs 높은 인지도": {"key": "낮은 인지도 vs 높은 인지도", "name": "낮은 인지도 vs 높은 인지도", "min_label": "낮은 인지도", "max_label": "높은 인지도"},
    "낮은 미래적 기대 vs 높은 미래적 기대": {"key": "낮은 미래적 기대 vs 높은 미래적 기대", "name": "낮은 미래적 기대 vs 높은 미래적 기대", "min_label": "낮은 미래적 기대", "max_label": "높은 미래적 기대"},
    "낮은 도입율 vs 높은 도입율": {"key": "낮은 도입율 vs 높은 도입율", "name": "낮은 도입율 vs 높은 도입율", "min_label": "낮은 도입율", "max_label": "높은 도입율"},
    "소극적 도입 의지 vs 적극적 도입 의지": {"key": "소극적 도입 의지 vs 적극적 도입 의지", "name": "소극적 도입 의지 vs 적극적 도입 의지", "min_label": "소극적 도입 의지", "max_label": "적극적 도입 의지"},
    "입주민 불만족 vs 입주민 고만족": {"key": "입주민 불만족 vs 입주민 고만족", "name": "입주민 불만족 vs 입주민 고만족", "min_label": "입주민 불만족", "max_label": "입주민 고만족"},
    "낮은 구현 가능성 vs 높은 구현 가능성": {"key": "낮은 구현 가능성 vs 높은 구현 가능성", "name": "낮은 구현 가능성 vs 높은 구현 가능성", "min_label": "낮은 구현 가능성", "max_label": "높은 구현 가능성"},
    "초기투자 고비용 vs 초기투자 저비용": {"key": "초기투자 고비용 vs 초기투자 저비용", "name": "초기투자 고비용 vs 초기투자 저비용", "min_label": "초기투자 고비용", "max_label": "초기투자 저비용"},
    "점진적 개선 vs 파괴적 혁신": {"key": "점진적 개선 vs 파괴적 혁신", "name": "점진적 개선 vs 파괴적 혁신", "min_label": "점진적 개선", "max_label": "파괴적 혁신"},
    "제한적 확장 가능성(사업성) vs 높은 확장 가능성(사업성)": {"key": "제한적 확장 가능성(사업성) vs 높은 확장 가능성(사업성)", "name": "제한적 확장 가능성(사업성) vs 높은 확장 가능성(사업성)", "min_label": "제한적 확장 가능성(사업성)", "max_label": "높은 확장 가능성(사업성)"}
}

# ----------------------------------------------------------------------
# 3. 데이터 로딩 (JSON 파일)
# ----------------------------------------------------------------------
JSON_FILE_NAME = "dashboard_data.json"

@st.cache_data
def load_data_from_json(file_name):
    """
    JSON 파일을 읽어 Pandas DataFrame으로 변환합니다.
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 1. 키워드 데이터프레임
        df_keywords = pd.DataFrame(data['keywords'])
        
        # 2. 시나리오 데이터프레임
        df_scenario = pd.DataFrame(data['scenarios'])

        # 3. 아이디어-키워드 맵 생성 (JSON에 저장된 list 활용)
        if '아이디어_list' in df_keywords.columns:
            df_map = df_keywords[['트렌드 키워드', '아이디어_list']].copy()
            df_map = df_map.explode('아이디어_list')
            df_map = df_map.rename(columns={'아이디어_list': '아이디어'})
            df_map = df_map.dropna(subset=['아이디어'])
            df_map = df_map[df_map['아이디어'] != '']
        else:
            df_map = pd.DataFrame(columns=['트렌드 키워드', '아이디어'])

        return df_keywords, df_scenario, df_map

    except FileNotFoundError:
        st.error(f"오류: '{file_name}' 파일을 찾을 수 없습니다. 데이터 변환 스크립트를 먼저 실행해주세요.")
        return None, None, None
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}")
        return None, None, None


# ----------------------------------------------------------------------
# 4. 시각화 함수 (2x2 매트릭스용)
# ----------------------------------------------------------------------
def display_visualizations(
    df_keywords, x_axis, y_axis, show_text, color_map_keyword, color_map_scenario, show_idea_layer, df_ideas
):
    if df_keywords.empty:
        st.warning("선택한 필터 조건에 맞는 키워드가 없습니다.")
        return
        
    x_score_col = f"score_{x_axis['key']}"
    y_score_col = f"score_{y_axis['key']}"
    x_rationale_col = f"rationale_{x_axis['key']}"
    y_rationale_col = f"rationale_{y_axis['key']}"
    
    # 축 데이터 존재 확인
    if x_score_col not in df_keywords.columns or y_score_col not in df_keywords.columns:
        st.warning(f"데이터에 선택된 축 정보가 없습니다. ({x_axis['name']} 또는 {y_axis['name']})")
        return

    df_display = df_keywords.dropna(subset=[x_score_col, y_score_col]).copy()
    
    if df_display.empty:
        st.warning("선택된 축에 대한 유효한 점수 데이터가 없습니다.")
        return
        
    # 포맷팅
    df_display['X축 점수_str'] = df_display[x_score_col].map('{:+.1f}'.format)
    df_display['X축 근거'] = df_display[x_rationale_col].fillna('N/A')
    df_display['Y축 점수_str'] = df_display[y_score_col].map('{:+.1f}'.format)
    df_display['Y축 근거'] = df_display[y_rationale_col].fillna('N/A')
    
    # 텍스트 라벨
    text_labels = df_display["트렌드 키워드"] if show_text else None
    
    # -------------------------------------------------------
    # 2D 키워드 매트릭스 그리기
    # -------------------------------------------------------
    st.subheader("📊 2x2 키워드 매트릭스")
    
    fig = px.scatter(
        df_display,
        x=x_score_col, y=y_score_col, 
        hover_name="트렌드 키워드", 
        custom_data=['번호', '대분류', '중분류 (접근방식 기준)', 'X축 점수_str', 'X축 근거', 'Y축 점수_str', 'Y축 근거'],
        color="대분류",
        color_discrete_map=color_map_keyword,
        text=text_labels
    )
    
    # 툴팁 설정
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b> (번호: %{customdata[0]})<br><br>" 
            "대분류: %{customdata[1]}<br>중분류: %{customdata[2]}<br><br>" 
            "X축: %{customdata[3]}<br><i>%{customdata[4]}</i><br>"
            "Y축: %{customdata[5]}<br><i>%{customdata[6]}</i><extra></extra>"
        ),
        textposition='top center', textfont=dict(size=15)
    )

    # 차트 레이아웃 (키워드 매트릭스도 높이 1000 고정)
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="grey")
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="grey")
    tick_values = list(range(-100, 101, 25))
    
    fig.update_layout(
        xaxis=dict(range=[-110, 110], zeroline=False, showgrid=True, tickvals=tick_values),
        yaxis=dict(range=[-110, 110], zeroline=False, showgrid=True, tickvals=tick_values),
        height=1000, margin=dict(l=150, r=150, t=50, b=50),
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right")
    )
    
    # 축 라벨
    fig.add_annotation(text=f"<b>{x_axis['min_label']}</b>", x=0.01, y=-0.08, xref='paper', yref='paper', showarrow=False, xanchor='left')
    fig.add_annotation(text=f"<b>{x_axis['max_label']}</b>", x=0.99, y=-0.08, xref='paper', yref='paper', showarrow=False, xanchor='right')
    fig.add_annotation(text=f"<b>{y_axis['min_label']}</b>", x=-0.08, y=0.01, xref='paper', yref='paper', showarrow=False, textangle=-90, yanchor='bottom')
    fig.add_annotation(text=f"<b>{y_axis['max_label']}</b>", x=-0.08, y=0.99, xref='paper', yref='paper', showarrow=False, textangle=-90, yanchor='top')

    # -------------------------------------------------------
    # 아이디어 레이어 추가
    # -------------------------------------------------------
    if show_idea_layer and not df_ideas.empty:
        df_ideas_valid = df_ideas.dropna(subset=[x_score_col, y_score_col])
        if not df_ideas_valid.empty:
            df_centroids = df_ideas_valid.groupby(['아이디어', '아이디어_명', '전략_대분류']).agg(
                x_mean=(x_score_col, 'mean'),
                y_mean=(y_score_col, 'mean'),
                keyword_count=('트렌드 키워드', 'nunique'),
                keyword_list=('트렌드 키워드', lambda x: ', '.join(list(x.unique())[:5]) + ('...' if x.nunique() > 5 else ''))
            ).reset_index()

            fig.add_trace(go.Scatter(
                x=df_centroids['x_mean'], y=df_centroids['y_mean'],
                mode='markers+text', name='아이디어 (평균)',
                text=df_centroids['아이디어'], textposition='top center',
                textfont=dict(size=14, color='red'),
                marker=dict(size=df_centroids['keyword_count'] * 2 + 10, color='rgba(255, 0, 0, 0.4)', symbol='star', line=dict(width=1, color='DarkRed')),
                hoverinfo='text',
                hovertext=df_centroids.apply(lambda r: f"<b>{r['아이디어_명']}</b><br>전략: {r['전략_대분류']}<br>키워드 수: {r['keyword_count']}<br>평균 위치: ({r['x_mean']:.1f}, {r['y_mean']:.1f})<br>키워드: {r['keyword_list']}", axis=1)
            ))

    st.plotly_chart(fig, width="stretch")

    # -------------------------------------------------------
    # 사분면 테이블 (Q1, Q4)
    # -------------------------------------------------------
    if show_idea_layer and not df_ideas.empty:
        st.divider()
        df_valid = df_ideas.dropna(subset=[x_score_col, y_score_col]).copy()
        
        # 사분면 판별
        def get_quad(x, y):
            if x > 0 and y > 0: return 'Q1'
            if x > 0 and y <= 0: return 'Q4'
            return 'Other'
        
        df_valid['quad'] = df_valid.apply(lambda r: get_quad(r[x_score_col], r[y_score_col]), axis=1)
        # 키워드 중복 제거
        df_unique = df_valid.drop_duplicates(subset=['아이디어', '트렌드 키워드'])
        
        # 피벗 테이블
        df_pivot = pd.pivot_table(
            df_unique, values=x_score_col, index=['아이디어', '아이디어_명'], columns=['quad'], aggfunc='sum', fill_value=0
        )
        for q in ['Q1', 'Q4']: 
            if q not in df_pivot.columns: df_pivot[q] = 0
            
        df_display_tbl = df_pivot.reset_index().set_index(['아이디어', '아이디어_명'])

        # Q1 테이블
        st.subheader(f"💡 {y_axis['max_label'].split('(')[0]} (Y+) | {x_axis['max_label'].split('(')[0]} (X+)")
        q1_data = df_display_tbl[['Q1']].sort_values(by='Q1', ascending=False)
        st.dataframe(
            q1_data, 
            column_config={"Q1": st.column_config.ProgressColumn("X축 점수 총합", format="%.1f점", max_value=float(q1_data['Q1'].max()) or 1.0)}, 
            width="stretch"
        )
        
        # Q4 테이블
        st.subheader(f"💡 {y_axis['min_label'].split('(')[0]} (Y-) | {x_axis['max_label'].split('(')[0]} (X+)")
        q4_data = df_display_tbl[['Q4']].sort_values(by='Q4', ascending=False)
        st.dataframe(
            q4_data, 
            column_config={"Q4": st.column_config.ProgressColumn("X축 점수 총합", format="%.1f점", max_value=float(q4_data['Q4'].max()) or 1.0)}, 
            width="stretch"
        )

    # -------------------------------------------------------
    # 전체 데이터 테이블
    # -------------------------------------------------------
    st.subheader("📋 전체 키워드 데이터")
    st.dataframe(
        df_keywords[['번호', '트렌드 키워드', '대분류', x_score_col, x_rationale_col, y_score_col, y_rationale_col]], 
        width="stretch"
    )


# ----------------------------------------------------------------------
# 5. 메인 로직 및 데이터 병합
# ----------------------------------------------------------------------
df_keywords, df_scenario, df_keyword_idea_map = load_data_from_json(JSON_FILE_NAME)

if df_keywords is not None and df_scenario is not None:
    # 1. 아이디어 정보 가져오기
    df_idea_info = df_scenario[['아이디어', '아이디어_명', '전략_대분류']].drop_duplicates()
    
    # 2. [맵] + [아이디어 정보] 병합
    df_master = pd.merge(df_keyword_idea_map, df_idea_info, on='아이디어', how='left')
    
    # 3. [결과] + [키워드 점수] 병합 (중복 방지 처리)
    df_keywords_clean = df_keywords.drop(columns=['아이디어', '아이디어_list'], errors='ignore')
    df_master = pd.merge(df_master, df_keywords_clean, on='트렌드 키워드', how='left')
else:
    df_master = pd.DataFrame()

# 색상 맵 생성
pastel = px.colors.qualitative.Pastel
color_map_kw = {}
color_map_sc = {}

if df_keywords is not None:
    cats = df_keywords['대분류'].dropna().unique()
    color_map_kw = {c: pastel[i % len(pastel)] for i, c in enumerate(cats)}

if df_scenario is not None:
    strats = df_scenario['전략_대분류'].dropna().unique()
    color_map_sc = {s: pastel[i % len(pastel)] for i, s in enumerate(strats)}

# ----------------------------------------------------------------------
# 6. 사이드바 및 UI 구성
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 설정")
    if df_keywords is not None:
        # X축 옵션
        x_eval_list = [
            "낮은 인지도 vs 높은 인지도", "낮은 미래적 기대 vs 높은 미래적 기대", "낮은 도입율 vs 높은 도입율",
            "소극적 도입 의지 vs 적극적 도입 의지", "입주민 불만족 vs 입주민 고만족", "낮은 구현 가능성 vs 높은 구현 가능성",
            "초기투자 고비용 vs 초기투자 저비용", "제한적 확장 가능성(사업성) vs 높은 확장 가능성(사업성)"
        ]
        
        sel_x = st.selectbox("X축 (평가 기준)", x_eval_list, index=0)
        y_opts = [k for k in AXIS_DEFINITIONS.keys() if k not in x_eval_list]
        sel_y = st.selectbox("Y축 (선호 기준)", y_opts, index=0)
        
        show_txt = st.checkbox("텍스트 표시", True)
        show_idea = st.checkbox("아이디어 레이어", True)
        
        st.divider()
        
        # 필터링
        all_cat = "--- 전체 ---"
        if '대분류' in df_keywords.columns:
            cats_list = [all_cat] + sorted(list(df_keywords['대분류'].dropna().unique()))
            sel_cats = st.multiselect("대분류 필터", cats_list, default=[all_cat])
        else:
            sel_cats = [all_cat]
    else:
        st.error("JSON 데이터를 로드할 수 없습니다.")

st.title("🏠 미래 주거 키워드 대시보드")
tab1, tab2 = st.tabs(["📊 키워드 매트릭스", "💡 시나리오 평가"])

# 탭 1: 키워드 매트릭스
with tab1:
    if df_keywords is not None:
        filtered_df = df_keywords.copy()
        filtered_master = df_master.copy()
        
        if sel_cats and all_cat not in sel_cats:
            filtered_df = filtered_df[filtered_df['대분류'].isin(sel_cats)]
            if not filtered_master.empty:
                filtered_master = filtered_master[filtered_master['대분류'].isin(sel_cats)]
            
        display_visualizations(
            filtered_df, AXIS_DEFINITIONS[sel_x], AXIS_DEFINITIONS[sel_y], 
            show_txt, color_map_kw, color_map_sc, show_idea, filtered_master
        )

# 탭 2: 시나리오 평가 (높이 수정됨)
with tab2:
    if df_scenario is not None:
        st.subheader("💡 시나리오 평가")
        
        # 1. 전체 점수 차트
        fig_total = px.bar(
            df_scenario.sort_values('score_전체점수', ascending=False),
            x='아이디어_명', y='score_전체점수', color='전략_대분류',
            color_discrete_map=color_map_sc, title="시나리오 종합 점수 (30점 만점)"
        )
        # [수정] 높이 1000px로 고정
        fig_total.update_layout(height=1000)
        st.plotly_chart(fig_total, width="stretch")
        
        # 2. 개별 기준 차트
        crit = st.selectbox("평가 기준 상세 확인", ['기술 실현 가능성', '법제도 허용성', '기술 수용성'])
        s_col = f"score_{crit}"
        r_col = f"rationale_{crit}"
        
        if s_col in df_scenario.columns:
            fig_sub = px.bar(
                df_scenario.sort_values(s_col, ascending=False),
                x='아이디어_명', y=s_col, color='전략_대분류',
                color_discrete_map=color_map_sc, title=f"'{crit}' 점수 (10점 만점)"
            )
            # [수정] 높이 1000px로 고정
            fig_sub.update_layout(height=1000)
            st.plotly_chart(fig_sub, width="stretch")
            
            st.caption(f"📋 평가 근거: {crit}")
            st.dataframe(
                df_scenario[['아이디어_명', r_col]].set_index('아이디어_명'), 
                width="stretch"
            )
        else:
            st.warning(f"데이터에 '{crit}' 관련 점수가 없습니다.")