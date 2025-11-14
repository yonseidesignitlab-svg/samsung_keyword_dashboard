import streamlit as st
import pandas as pd
import plotly.express as px  # Plotly 라이브러리
import plotly.graph_objects as go # [신규] 아이디어 레이어(Trace) 추가용
import re  # 정규식(Regex) 라이브D러리 임포트

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
# 'key'는 'keyword_score.xlsx'의 컬럼명과 정확히 일치해야 합니다.
AXIS_DEFINITIONS = {
    "개인 경험 vs 집단 경험": {
        "key": "개인 경험 vs 집단 경험",
        "name": "개인 경험 vs 집단 경험",
        "min_label": "개인 경험 (Personal)",
        "max_label": "집단 경험 (Collective)"
    },
    "대중화 vs 프리미엄화": {
        "key": "대중화 vs 프리미엄화",
        "name": "대중화 vs 프리미엄화",
        "min_label": "대중화 (Mass)",
        "max_label": "프리미엄화 (Premium)"
    },
    "단기 수익 vs 장기 지속 가능성": {
        "key": "단기 수익 vs 장기 지속 가능성",
        "name": "단기 수익 vs 장기 지속 가능성",
        "min_label": "단기 수익 (Short-term)",
        "max_label": "장기 지속 가능성 (Long-term)"
    },
    "자동화 vs 인간 개입": {
        "key": "자동화 vs 인간 개입",
        "name": "자동화 vs 인간 개입",
        "min_label": "자동화 (Automation)",
        "max_label": "인간 개입 (Human)"
    },
    "자연 친화 vs 인공/도시 중심": {
        "key": "자연 친화 vs 인공/도시 중심",
        "name": "자연 친화 vs 인공/도시 중심",
        "min_label": "자연 친화 (Nature)",
        "max_label": "인공/도시 중심 (Artificial)"
    },
    "프라이버시/보안 vs 개방/공유": {
        "key": "프라이버시/보안 vs 개방/공유",
        "name": "프라이버시/보안 vs 개방/공유",
        "min_label": "프라이버시/보안 (Privacy)",
        "max_label": "개방/공유 (Openness)"
    },
    "기능 중심 vs 감성 중심": {
        "key": "기능 중심 vs 감성 중심",
        "name": "기능 중심 vs 감성 중심",
        "min_label": "기능 중심 (Function)",
        "max_label": "감성 중심 (Emotion)"
    },
    "낮은 인지도 vs 높은 인지도": {
        "key": "낮은 인지도 vs 높은 인지도",
        "name": "낮은 인지도 vs 높은 인지도",
        "min_label": "낮은 인지도",
        "max_label": "높은 인지도"
    },
    "낮은 미래적 기대 vs 높은 미래적 기대": {
        "key": "낮은 미래적 기대 vs 높은 미래적 기대",
        "name": "낮은 미래적 기대 vs 높은 미래적 기대",
        "min_label": "낮은 미래적 기대",
        "max_label": "높은 미래적 기대"
    },
    "낮은 도입율 vs 높은 도입율": {
        "key": "낮은 도입율 vs 높은 도입율",
        "name": "낮은 도입율 vs 높은 도입율",
        "min_label": "낮은 도입율",
        "max_label": "높은 도입율"
    },
    "소극적 도입 의지 vs 적극적 도입 의지": {
        "key": "소극적 도입 의지 vs 적극적 도입 의지",
        "name": "소극적 도입 의지 vs 적극적 도입 의지",
        "min_label": "소극적 도입 의지",
        "max_label": "적극적 도입 의지"
    },
    "입주민 불만족 vs 입주민 고만족": {
        "key": "입주민 불만족 vs 입주민 고만족",
        "name": "입주민 불만족 vs 입주민 고만족",
        "min_label": "입주민 불만족",
        "max_label": "입주민 고만족"
    },
    "낮은 구현 가능성 vs 높은 구현 가능성": {
        "key": "낮은 구현 가능성 vs 높은 구현 가능성",
        "name": "낮은 구현 가능성 vs 높은 구현 가능성",
        "min_label": "낮은 구현 가능성",
        "max_label": "높은 구현 가능성"
    },
    "초기투자 고비용 vs 초기투자 저비용": {
        "key": "초기투자 고비용 vs 초기투자 저비용",
        "name": "초기투자 고비용 vs 초기투자 저비용",
        "min_label": "초기투자 고비용",
        "max_label": "초기투자 저비용"
    },
    "점진적 개선 vs 파괴적 혁신": {
        "key": "점진적 개선 vs 파괴적 혁신",
        "name": "점진적 개선 vs 파괴적 혁신",
        "min_label": "점진적 개선",
        "max_label": "파괴적 혁신"
    },
    "제한적 확장 가능성(사업성) vs 높은 확장 가능성(사업성)": {
        "key": "제한적 확장 가능성(사업성) vs 높은 확장 가능성(사업성)",
        "name": "제한적 확장 가능성(사업성) vs 높은 확장 가능성(사업성)",
        "min_label": "제한적 확장 가능성(사업성)",
        "max_label": "높은 확장 가능성(사업성)"
    }
}


# ----------------------------------------------------------------------
# 3. 데이터 로딩 (Excel 파일) - 점수/근거 파싱
# ----------------------------------------------------------------------
EXCEL_FILE_NAME = "keyword_score.xlsx"
SHEET_NAME = "Keyword_score"
SCENARIO_SHEET_NAME = "Idea"

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
    [수정]
    미리 계산된 점수 엑셀 파일을 로드하고,
    7개 축 컬럼을 파싱하여 새 컬럼을 생성합니다.
    [신규] 아이디어-키워드 매핑 테이블(df_map)을 함께 반환합니다.
    """
    try:
        df = pd.read_excel(file_name, sheet_name=sheet_name, header=0)
        
        # 1-67번 키워드 누락 문제 해결
        df['번호'] = pd.to_numeric(df['번호'], errors='coerce')
        df = df.dropna(subset=['번호', '트렌드 키워드', '핵심 정의'])
        df['번호'] = df['번호'].astype(int)
        df = df.drop_duplicates(subset=['번호'], keep='first')
        
        # --- [핵심] 점수 및 근거 파싱 (수정된 7개 축 기준) ---
        for axis_info in AXIS_DEFINITIONS.values():
            axis_key = axis_info['key'] # 예: "개인 경험 vs 집단 경험"
            
            score_col_name = f"score_{axis_key}"
            rationale_col_name = f"rationale_{axis_key}"
            
            if axis_key in df.columns:
                parsed_data = df[axis_key].apply(parse_score_rationale)
                df[score_col_name] = parsed_data.apply(lambda x: x[0])
                df[rationale_col_name] = parsed_data.apply(lambda x: x[1])
            else:
                st.error(f"오류: 엑셀에서 '{axis_key}' 컬럼을 찾을 수 없습니다.")
        
        # --- [신규] 아이디어-키워드 맵 생성 ---
        # '아이디어' 컬럼(e.g., "1-1, 1-4")을 파싱하여 매핑 테이블 생성
        if '아이디어' in df.columns and '트렌드 키워드' in df.columns:
            df_map = df[['트렌드 키워드', '아이디어']].copy()
            df_map['아이디어'] = df_map['아이디어'].astype(str).fillna('').apply(
                lambda x: [item.strip() for item in str(x).split(',') if item.strip()]
            )
            df_map = df_map.explode('아이디어')
            df_map = df_map.dropna(subset=['아이디어'])
            df_map = df_map[df_map['아이디어'] != ''] # 공백 제거
        else:
            st.error("오류: '아이디어' 또는 '트렌드 키워드' 컬럼이 없어 아이디어 맵을 생성할 수 없습니다.")
            df_map = pd.DataFrame(columns=['트렌드 키워드', '아이디어']) # 빈 맵
        
        return df, df_map # [수정] df와 df_map을 함께 반환
    
    except FileNotFoundError:
        st.error(f"오류: '{file_name}' 파일을 찾을 수 없습니다. 파일 이름이 정확한지 확인하세요.")
        return None, None # [수정]
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}. 'openpyxl' 라이브러리가 설치되었는지 확인하세요.")
        return None, None # [수정]

@st.cache_data
def load_scenario_data(file_name, sheet_name):
    """
    시나리오(아이디어) 엑셀 시트를 로드하고
    병합된 셀처럼 보이는 '전략' 컬럼을 정리합니다.
    또한 점수(근거) 컬럼을 파싱합니다.
    """
    try:
        df = pd.read_excel(file_name, sheet_name=sheet_name)
        
        df = df.rename(columns={'Unnamed: 1': '전략명', 'Unnamed: 3': '아이디어명'})

        df['전략'] = df['전략'].ffill()
        df['전략명'] = df['전략명'].ffill()

        # '전략_대분류' 컬럼 생성
        df['전략_대분류'] = df['전략'].astype(float).astype(int).astype(str) + ". " + df['전략명']
        
        # '아이디어_명' 컬럼 생성
        df['아이디어_명'] = df['아이디어'] + ". " + df['아이디어명']
        
        # --- 점수/근거 파싱 ---
        criteria_cols = ['기술 실현 가능성', '법제도 허용성', '기술 수용성']
        score_cols_to_check = []
        parsed_score_cols = [] 
        
        for col_name in criteria_cols:
            if col_name in df.columns:
                score_col = f"score_{col_name}"
                rationale_col = f"rationale_{col_name}"
                score_cols_to_check.append(score_col)
                parsed_score_cols.append(score_col) 
                
                parsed_data = df[col_name].apply(parse_score_rationale)
                df[score_col] = parsed_data.apply(lambda x: x[0])
                df[rationale_col] = parsed_data.apply(lambda x: x[1])
            else:
                st.error(f"오류: 아이디어 시트에서 '{col_name}' 컬럼을 찾을 수 없습니다.")

        df_clean = df.dropna(subset=score_cols_to_check).copy()
        
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
def display_visualizations(
    df_keywords,      # [수정] 키워드 데이터
    x_axis, 
    y_axis, 
    show_text, 
    color_map_keyword,  # [수정] 키워드 색상 맵
    color_map_scenario, # [신규] 시나리오 색상 맵
    show_idea_layer,    # [신규] 아이디어 레이어 표시 여부
    df_ideas          # [신규] 아이디어-키워드 마스터 데이터
):
    """
    [수정]
    키워드(필수)와 아이디어(선택)를 2D 사분면 차트에 표시합니다.
    show_idea_layer (bool): 아이디어 레이어(평균 위치, 순위)를 표시할지 여부
    """
    if df_keywords.empty:
        st.warning("선택한 필터 조건에 맞는 키워드가 없습니다.")
        return
        
    # --- 1. 동적 컬럼명 및 호버 데이터 생성 (키워드용) ---
    x_score_col = f"score_{x_axis['key']}"
    y_score_col = f"score_{y_axis['key']}"
    x_rationale_col = f"rationale_{x_axis['key']}"
    y_rationale_col = f"rationale_{y_axis['key']}"
    
    df_display = df_keywords.dropna(subset=[x_score_col, y_score_col]).copy()
    
    if df_display.empty:
        st.warning(f"선택된 '{x_axis['name']}' 또는 '{y_axis['name']}' 축에 대한 키워드 점수 데이터가 없습니다.")
        return
        
    df_display.loc[:, 'X축 점수_str'] = df_display[x_score_col].map('{:+.1f}'.format)
    df_display.loc[:, 'X축 근거'] = df_display[x_rationale_col].fillna('N/A')
    df_display.loc[:, 'Y축 점수_str'] = df_display[y_score_col].map('{:+.1f}'.format)
    df_display.loc[:, 'Y축 근거'] = df_display[y_rationale_col].fillna('N/A')

    df_display.loc[:, '트렌드 키워드'] = df_display['트렌드 키워드'].fillna('키워드 없음')
    df_display['번호_str'] = df_display['번호'].astype(str).fillna('N/A')
    df_display.loc[:, '대분류'] = df_display['대분류'].fillna('분류 없음')
    df_display.loc[:, '중분류 (접근방식 기준)'] = df_display['중분류 (접근방식 기준)'].fillna('분류 없음')


    text_labels = df_display["트렌드 키워드"] if show_text else None

    # 2. 2D 키워드 매트릭스 (Plotly Scatter Plot) - [기반 레이어]
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
            color_discrete_map=color_map_keyword, # 키워드 색상 적용
            title="키워드 사분면 분석",
            text=text_labels
        )

        hovertemplate_keyword = (
            "<b>%{hovertext}</b> (번호: %{customdata[0]})" 
            "<br><br>" 
            "대분류: %{customdata[1]}<br>" 
            "중분류: %{customdata[2]}"
            "<br><br>" 
            "X축 점수: %{customdata[3]}<br>" 
            "X축 근거: %{customdata[4]}<br>"
            "Y축 점수: %{customdata[5]}<br>" 
            "Y축 근거: %{customdata[6]}"
            "<extra></extra>"
        )

        if show_text:
            fig.update_traces(
                textposition='top center', 
                textfont=dict(size=15), 
                hovertemplate=hovertemplate_keyword 
            )
        else:
            fig.update_traces(
                hovertemplate=hovertemplate_keyword
            )

        fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="grey")
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="grey")
        
        tick_values = list(range(-100, 101, 25)) 
        tick_text = [str(v) for v in tick_values]

        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(
                range=[-110, 110], 
                zeroline=False,
                showgrid=True,
                tickvals=tick_values, 
                ticktext=tick_text  
            ),
            yaxis=dict(
                range=[-110, 110], 
                zeroline=False,
                showgrid=True,
                tickvals=tick_values, 
                ticktext=tick_text  
            ),
            height=1000, 
            margin=dict(l=150, r=150, t=100, b=100),
            dragmode='pan',
            hoverlabel=dict(font_size=16), 
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # X축 레이블
        fig.add_annotation(text=f"<b>{x_axis['min_label']}</b>", align='center', showarrow=False, xref='paper', yref='paper', x=0.01, y=-0.08, font=dict(size=14), xanchor='left')
        fig.add_annotation(text=f"<b>{x_axis['max_label']}</b>", align='center', showarrow=False, xref='paper', yref='paper', x=0.99, y=-0.08, font=dict(size=14), xanchor='right')
        # Y축 레이블
        fig.add_annotation(text=f"<b>{y_axis['min_label']}</b>", align='center', showarrow=False, xref='paper', yref='paper', x=-0.08, y=0.01, font=dict(size=14), textangle=-90, yanchor='bottom')
        fig.add_annotation(text=f"<b>{y_axis['max_label']}</b>", align='center', showarrow=False, xref='paper', yref='paper', x=-0.08, y=0.99, font=dict(size=14), textangle=-90, yanchor='top')
        

        # --- [신규] 3. 아이디어 레이어 추가 (show_idea_layer == True 인 경우) ---
        if show_idea_layer:
            if df_ideas.empty:
                st.info("💡 아이디어 레이어: 필터링된 키워드와 연결된 아이디어가 없습니다.")
            else:
                # 3-1. 아이디어 평균 위치(무게중심) 계산
                df_ideas_valid = df_ideas.dropna(subset=[x_score_col, y_score_col]).copy()
                
                if df_ideas_valid.empty:
                    st.warning("💡 아이디어 레이어: 연결된 키워드 중 현재 축에 대한 점수 데이터가 없습니다.")
                else:
                    df_centroids = df_ideas_valid.groupby(['아이디어', '아이디어_명', '전략_대분류']).agg(
                        x_mean=(x_score_col, 'mean'),
                        y_mean=(y_score_col, 'mean'),
                        keyword_count=('트렌드 키워드', 'nunique'),
                        # 툴팁에 표시할 키워드 목록 (최대 5개)
                        keyword_list=('트렌드 키워드', lambda x: ', '.join(list(x.unique())[:5]) + ('...' if x.nunique() > 5 else ''))
                    ).reset_index()

                    # 3-2. 아이디어 툴팁 텍스트 생성
                    df_centroids['hover_text'] = df_centroids.apply(
                        lambda r: f"<b>{r['아이디어_명']} ({r['아이디어']})</b><br>" +
                                  f"전략: {r['전략_대분류']}<br>" +
                                  f"포함된 키워드 수: {r['keyword_count']}<br>" +
                                  f"평균 X ({x_axis['name']}): {r['x_mean']:.1f}<br>" +
                                  f"평균 Y ({y_axis['name']}): {r['y_mean']:.1f}<br>" +
                                  f"포함 키워드 (일부): {r['keyword_list']}",
                        axis=1
                    )

                    # 3-3. Plotly 차트에 아이디어 레이어(Trace) 추가
                    fig.add_trace(go.Scatter(
                        x=df_centroids['x_mean'],
                        y=df_centroids['y_mean'],
                        mode='markers+text',
                        name='아이디어 (평균 위치)',
                        text=df_centroids['아이디어'], # 아이디어 번호 (e.g., "1-1")
                        textposition='top center',
                        textfont=dict(size=14, color='red', family="Arial, sans-serif"),
                        marker=dict(
                            size=df_centroids['keyword_count'] * 2 + 10, # 키워드 수에 따라 크기 조절
                            color='rgba(255, 0, 0, 0.4)', # 반투명 빨강
                            symbol='star', # 별 모양
                            line=dict(width=1, color='DarkRed')
                        ),
                        hoverinfo='text',
                        hovertext=df_centroids['hover_text'], # 위에서 생성한 상세 툴팁
                        legendgroup='ideas',
                        showlegend=True
                    ))
        
        # --- 4. 차트 표시 ---
        st.plotly_chart(
            fig, 
            use_container_width=True, 
            config={'scrollZoom': True}
        )
        
        st.caption("점에 마우스를 올리면 키워드와 상세 근거를 볼 수 있습니다. (사이드바에서 텍스트/아이디어 표시 토글 가능)")

# --- [신규] 5. 아이디어 사분면 순위 테이블 ---
        if show_idea_layer and not df_ideas.empty:
            st.divider()
            
            df_ideas_valid = df_ideas.dropna(subset=[x_score_col, y_score_col]).copy()

            if not df_ideas_valid.empty:
                # 사분면 정의 함수
                def get_quadrant(x, y):
                    if x > 0 and y > 0: return '1사분면 (X+, Y+)'
                    elif x <= 0 and y > 0: return '2사분면 (X-, Y+)'
                    elif x <= 0 and y <= 0: return '3사분면 (X-, Y-)'
                    elif x > 0 and y <= 0: return '4사분면 (X+, Y-)'
                    return 'N/A'
                
                df_ideas_valid['quadrant'] = df_ideas_valid.apply(
                    lambda r: get_quadrant(r[x_score_col], r[y_score_col]), axis=1
                )
                
                # [수정] 키워드 중복 제거 (점수 포함)
                df_ideas_unique_scored = df_ideas_valid.drop_duplicates(subset=['아이디어', '트렌드 키워드'])

                # --- [수정] '개수'가 아닌 'X축 점수 총합'으로 피벗 테이블 생성 ---
                df_pivot = pd.pivot_table(
                    df_ideas_unique_scored,
                    values=x_score_col,     # 합산할 값: X축 점수
                    index=['아이디어', '아이디어_명'], # 행
                    columns=['quadrant'],   # 열
                    aggfunc='sum',          # 집계방식: 총합
                    fill_value=0            # 0으로 채우기
                )
                # ----------------------------------------------------

                # 모든 사분면 컬럼 보장
                all_quadrants = ['1사분면 (X+, Y+)', '2사분면 (X-, Y+)', '3사분면 (X-, Y-)', '4사분면 (X+, Y-)']
                for q in all_quadrants:
                    if q not in df_pivot:
                        df_pivot[q] = 0
                
                # 아이디어명 정리
                df_display_table = df_pivot.reset_index()
                df_display_table['아이디어_명'] = df_display_table['아이디어_명'].apply(
                    lambda x: x.split('. ', 1)[-1] if '. ' in x else x
                )
                df_display_table = df_display_table.set_index(['아이디어', '아이디어_명'])

                # 축 레이블 (괄호 제거)
                y_max_label = y_axis['max_label'].split(' (', 1)[0]
                y_min_label = y_axis['min_label'].split(' (', 1)[0]
                x_max_label = x_axis['max_label'].split(' (', 1)[0]
                
                # --- [수정] 테이블 2개 분리 (점수 총합 기준) ---

                # 1. Q1 (X+, Y+) 테이블
                st.subheader(f"💡 {y_max_label} (Y+) | {x_max_label} (X+)")
                st.caption(f"Y축 '{y_axis['name']}'의 '{y_max_label}' 특성과 X축 '{x_axis['name']}'의 '{x_max_label}' 특성을 가진 키워드들의 **X축 점수 총합**")
                
                df_q1_table = df_display_table[['1사분면 (X+, Y+)']].sort_values(by='1사분면 (X+, Y+)', ascending=False)
                
                max_q1 = float(df_q1_table['1사분면 (X+, Y+)'].max())
                if max_q1 <= 0: # 0이거나 음수일 경우(가능성 낮음)
                    max_q1 = 1.0 # 0이 아닌 값으로 보정
                    
                st.dataframe(
                    df_q1_table,
                    width='stretch',
                    column_config={
                        "1사분면 (X+, Y+)": st.column_config.ProgressColumn(
                            label=f"{y_max_label} | {x_max_label} (X축 점수 총합)", 
                            min_value=0, 
                            max_value=max_q1, 
                            format="%.1f점" # [수정] '개' -> '점'
                        )
                    }
                )

                st.divider() # 테이블 구분선

                # 2. Q4 (X+, Y-) 테이블
                st.subheader(f"💡 {y_min_label} (Y-) | {x_max_label} (X+)")
                st.caption(f"Y축 '{y_axis['name']}'의 '{y_min_label}' 특성과 X축 '{x_axis['name']}'의 '{x_max_label}' 특성을 가진 키워드들의 **X축 점수 총합**")
                
                df_q4_table = df_display_table[['4사분면 (X+, Y-)']].sort_values(by='4사분면 (X+, Y-)', ascending=False)

                max_q4 = float(df_q4_table['4사분면 (X+, Y-)'].max())
                if max_q4 <= 0:
                    max_q4 = 1.0

                st.dataframe(
                    df_q4_table,
                    width='stretch',
                    column_config={
                        "4사분면 (X+, Y-)": st.column_config.ProgressColumn(
                            label=f"{y_min_label} | {x_max_label} (X축 점수 총합)", 
                            min_value=0, 
                            max_value=max_q4, 
                            format="%.1f점" # [수정] '개' -> '점'
                        )
                    }
                )
                st.caption("테이블 헤더를 클릭하여 순위를 정렬할 수 있습니다.")

    except Exception as e:
        st.error(f"Plotly 차트 생성 중 오류: {e}")

    # 3. 전체 키워드 분석 데이터 (테이블) - [수정] df_display -> df_keywords
    st.subheader("📋 전체 키워드 분석 데이터")
    
    # 원본 df_keywords (필터링됨)에서 필요한 컬럼만 표시 (파싱된 컬럼 제외)
    display_cols = [
        '번호', '트렌드 키워드', '핵심 정의', '대분류', '중분류 (접근방식 기준)', '아이디어',
        x_axis['key'], y_axis['key'] # 원본 점수(근거) 컬럼
    ]
    # 실제 존재하는 컬럼만 선택
    display_cols_exist = [col for col in display_cols if col in df_keywords.columns]
    
    df_display_table = df_keywords[display_cols_exist].copy()
    
    for col in df_display_table.columns:
        if df_display_table[col].dtype == 'object':
            df_display_table[col] = df_display_table[col].astype(str).fillna('N/A')
    
    st.dataframe(df_display_table, width='stretch')

    st.caption("테이블 헤더를 클릭하여 정렬할 수 있습니다.")


# ----------------------------------------------------------------------
# 5. Streamlit 메인 UI 구성 (탭 구조로 변경)
# ----------------------------------------------------------------------

# --- [수정] 데이터 로딩 (키워드, 키워드-아이디어맵, 시나리오) ---
df_scores, df_keyword_idea_map = load_data(EXCEL_FILE_NAME, SHEET_NAME)
df_scenario = load_scenario_data(EXCEL_FILE_NAME, SCENARIO_SHEET_NAME) 

# --- [신규] 아이디어-키워드 마스터 데이터 생성 ---
df_master_idea = None
if df_scores is not None and df_keyword_idea_map is not None and df_scenario is not None:
    try:
        # 시나리오(아이디어) 시트에서 아이디어 번호, 이름, 전략(색상용) 정보 가져오기
        df_idea_names = df_scenario[['아이디어', '아이디어_명', '전략_대분류']].drop_duplicates()
        
        # 1. 키워드-아이디어맵 + 아이디어 이름/전략 병합
        df_master_idea = pd.merge(df_keyword_idea_map, df_idea_names, on='아이디어', how='left')
        
        # 2. (1)결과 + 키워드 상세 정보(점수 등) 병합
        # df_scores에서 '아이디어' 컬럼은 제외하고 merge (중복 방지)
        df_scores_base = df_scores.drop(columns=['아이디어'], errors='ignore')
        df_master_idea = pd.merge(df_master_idea, df_scores_base, on='트렌드 키워드', how='left')
        
    except Exception as e:
        st.error(f"아이디어-키워드 마스터 데이터 생성 중 오류: {e}")
        df_master_idea = pd.DataFrame() # 오류 시 빈 데이터프레임
else:
    st.error("키워드 또는 시나리오 데이터 로딩에 실패하여 아이디어-키워드 매핑을 생성할 수 없습니다.")
    df_master_idea = pd.DataFrame() # 로딩 실패 시 빈 데이터프레임
# -------------------------------------------------


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
with st.sidebar:
    st.header("⚙️ 2x2 매트릭스 설정") 
    
    if df_scores is not None:
        
        # --- [신규] X축 전용 옵션 리스트 (평가 기준) ---
        x_axis_options = [
            "낮은 인지도 vs 높은 인지도",
            "낮은 미래적 기대 vs 높은 미래적 기대",
            "낮은 도입율 vs 높은 도입율",
            "소극적 도입 의지 vs 적극적 도입 의지",
            "입주민 불만족 vs 입주민 고만족",
            "낮은 구현 가능성 vs 높은 구현 가능성",
            "초기투자 고비용 vs 초기투자 저비용",
            "제한적 확장 가능성(사업성) vs 높은 확장 가능성(사업성)"
        ]
        
        # --- [신규] Y축 전용 옵션 리스트 (선호 기준) ---
        y_axis_options = [
            "개인 경험 vs 집단 경험",
            "대중화 vs 프리미엄화",
            "단기 수익 vs 장기 지속 가능성",
            "자동화 vs 인간 개입",
            "자연 친화 vs 인공/도시 중심",
            "프라이버시/보안 vs 개방/공유",
            "기능 중심 vs 감성 중심",
            "점진적 개선 vs 파괴적 혁신"
        ]
        # ----------------------------------------------

        selected_x_axis_name = st.selectbox(
            "X축 기준을 선택하세요 (평가 기준):", # [수정] 레이블 변경
            options=x_axis_options,           # [수정] X축 리스트 사용
            index=0 
        )
        
        selected_y_axis_name = st.selectbox(
            "Y축 기준을 선택하세요 (선호 기준):", # [수정] 레이블 변경
            options=y_axis_options,           # [수정] Y축 리스트 사용
            index=0                           # [수정] 기본값을 0번째로 변경
        )
        
        x_axis = AXIS_DEFINITIONS[selected_x_axis_name]
        y_axis = AXIS_DEFINITIONS[selected_y_axis_name]

        st.divider()

        show_text = st.checkbox("✅ 차트에 키워드 텍스트 표시", value=True) 
        st.caption("텍스트가 많아 겹칠 수 있습니다.")

        st.divider()

        # '대분류' 필터
        try:
            all_categories_list = sorted(list(df_scores['대분류'].dropna().unique()))
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
            all_sub_categories_list = sorted(list(df_scores['중분류 (접근방식 기준)'].dropna().unique()))
            options_sub_cat = [all_sub_cat_option] + all_sub_categories_list
            
            st.multiselect(
                "표시할 중분류(접근방식 기준)를 선택하세요:",
                options=options_sub_cat,
                key='sub_cat_selection',
                on_change=update_filters
            )
        except KeyError:
            st.warning("'중분류 (접근방식 기준)' 컬럼을 찾을 수 없습니다.")
            
        # --- [신규] 아이디어 레이어 토글 ---
        st.divider()
        st.header("💡 아이디어 레이어")
        # [수정] value=True로 변경하여 기본값으로 켜지도록 설정
        show_idea_layer = st.checkbox("✅ 아이디어 레이어 표시", value=True)
        st.caption("2x2 매트릭스에 아이디어의 평균 위치와 사분면 순위를 표시합니다.")
        # ---------------------------------
            
    else:
        st.sidebar.error("키워드 엑셀 파일을 로드하지 못했습니다. 사이드바 옵션을 표시할 수 없습니다.")


# --- 메인 페이지 타이틀 ---
st.title("🏠 미래 주거 키워드 대시보드")

# --- 탭 생성 ---
tab_keyword, tab_scenario = st.tabs(["📊 2x2 키워드 매트릭스", "💡 시나리오 평가"])

# --- 탭 1: 2x2 키워드 매트릭스 ---
with tab_keyword:
    st.markdown("2x2 매트릭스(사분면)에 키워드를 배치하고 시각화합니다.")
    
    if df_scores is not None and df_master_idea is not None:
        # 필터 로직 (사이드바 값 기반)
        if 'cat_selection' not in st.session_state or all_cat_option in st.session_state.cat_selection:
            selected_categories = list(df_scores['대분류'].dropna().unique())
        else:
            selected_categories = st.session_state.cat_selection

        if 'sub_cat_selection' not in st.session_state or all_sub_cat_option in st.session_state.sub_cat_selection:
            selected_sub_categories = list(df_scores['중분류 (접근방식 기준)'].dropna().unique())
        else:
            selected_sub_categories = st.session_state.sub_cat_selection

        # [수정] 키워드 데이터 필터링 적용
        df_filtered = df_scores.copy() 
        if '대분류' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['대분류'].isin(selected_categories)]
        if '중분류 (접근방식 기준)' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['중분류 (접근방식 기준)'].isin(selected_sub_categories)]
        
        # [신규] 아이디어 마스터 데이터도 동일하게 필터링
        df_master_idea_filtered = df_master_idea.copy()
        if '대분류' in df_master_idea_filtered.columns:
            df_master_idea_filtered = df_master_idea_filtered[df_master_idea_filtered['대분류'].isin(selected_categories)]
        if '중분류 (접근방식 기준)' in df_master_idea_filtered.columns:
            df_master_idea_filtered = df_master_idea_filtered[df_master_idea_filtered['중분류 (접근방식 기준)'].isin(selected_sub_categories)]
        
        
        st.markdown(f"**{len(df_filtered)}**개 키워드를 **'{x_axis['name']}'** (X축) 및 **'{y_axis['name']}'** (Y축) 기준으로 표시합니다.")

        if selected_x_axis_name == selected_y_axis_name:
            st.error("X축과 Y축은 서로 다른 기준을 선택해야 합니다.")
        else:
            # [수정] color_map_scenario, show_idea_layer, df_master_idea_filtered 전달
            display_visualizations(
                df_filtered, 
                x_axis, 
                y_axis, 
                show_text, 
                color_map_keyword,
                color_map_scenario,
                show_idea_layer,
                df_master_idea_filtered
            )
    else:
        st.error(f"'{EXCEL_FILE_NAME}' ({SHEET_NAME}) 파일을 찾을 수 없습니다. 2x2 매트릭스를 표시할 수 없습니다.")

# --- 탭 2: 시나리오 평가 ---
with tab_scenario:
    st.subheader("💡 10대 아이디어 시나리오 평가")
    
    if df_scenario is not None:
        st.markdown("기술 실현 가능성, 법제도 허용성, 기술 수용성을 기준으로 10개 아이디어를 평가합니다.")

        # --- 1. '전체점수' 차트 ---
        st.subheader("시나리오별 '전체점수' (3대 기준 합산)")
        
        fig_total_score = px.bar(
            df_scenario.sort_values(by='score_전체점수', ascending=False), # [수정] 점수 순 정렬
            x='아이디어_명',
            y='score_전체점수',
            color='전략_대분류',
            color_discrete_map=color_map_scenario, 
            title="시나리오별 '전체점수' (3대 기준 합산)",
            hover_data={ 
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
        
        tick_values_30 = list(range(0, 31, 5)) 
        
        fig_total_score.update_layout(
            height=1000, 
            xaxis_title=None,
            xaxis_tickangle=-45,
            yaxis=dict(
                range=[0, 30.5], 
                tickvals=tick_values_30, 
                ticktext=[str(v) for v in tick_values_30]
            ), 
            hoverlabel=dict(font_size=16), 
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_total_score, use_container_width=True)
        
        st.divider() 
        
        # --- 2. '개별 기준' 차트 ---
        st.subheader("시나리오별 '개별 기준' 점수 및 근거")
        
        criteria_options = ['기술 실현 가능성', '법제도 허용성', '기술 수용성']
        selected_criterion = st.selectbox(
            "확인할 평가 기준을 선택하세요:",
            options=criteria_options,
            index=0 
        )

        score_col = f"score_{selected_criterion}"
        rationale_col = f"rationale_{selected_criterion}"

        fig_scenario = px.bar(
            df_scenario.sort_values(by=score_col, ascending=False), # [수정] 점수 순 정렬
            x='아이디어_명',
            y=score_col,    
            color='전략_대분류',
            color_discrete_map=color_map_scenario, 
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
        
        tick_values_10 = list(range(0, 11)) 
        
        fig_scenario.update_layout(
            height=1000, 
            xaxis_title=None,
            xaxis_tickangle=-45,
            yaxis=dict(
                range=[0, 10.1], 
                tickvals=tick_values_10, 
                ticktext=[str(v) for v in tick_values_10]
            ), 
            hoverlabel=dict(font_size=16), 
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
        
        st.divider() 

        # --- 3. 원본 데이터 ---
        with st.expander("📋 시나리오 평가 원본 데이터 (전체 보기)"):
            display_cols = ['전략_대분류', '기술 실현 가능성', '법제도 허용성', '기술 수용성']
            st.dataframe(
                df_scenario.set_index('아이디어_명')[display_cols], 
                width='stretch'
            )
        
    else:
        st.error(f"'{EXCEL_FILE_NAME}' ({SCENARIO_SHEET_NAME}) 파일을 찾을 수 없습니다. 시나리오 평가 탭을 표시할 수 없습니다.")
