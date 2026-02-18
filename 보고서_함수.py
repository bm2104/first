# 주간업무일지 함수 1
def process_data(df, df2):
    """데이터 처리 함수"""
    # 첫 행(단가 합계) 삭제 
    df = df.drop(index=0)
    df2 = df2.drop(index=0)

    # 저장소품목별단가 정리
    # 단가열 삭제
    df = df.drop(['단가'], axis=1)

    # 필터링 
    filters = {
        '품목번호' : r'^[AMXE]',
        '창고' : r'렌탈'
    }

    for column, pattern in filters.items():
        df = df[~df[column].str.contains(pattern, regex=True, na=False)]

    # 구매입고 리스트 정리
    # 원하는 열만 가지고 오기
    df2 = df2[['입고일자', '거래처명', '품목', '품목명', '규격', '입고수량', '원화단가', '원화금액']] 
    df2 = df2.rename(columns={'품목':'품목번호'})

    # 재고단가 0 인 행 업데이트 하기 
    #df.loc[df['재고단가'] == 0, '재고단가'] = df.loc[df['재고단가'] == 0, '품목번호'].map(df2.set_index('품목번호')['원화단가'])
    # 중복코드값이 있어 에러 발생 

    # 중복코드값이 있어도 실행 - 공부할것!!! 
    mask = df['재고단가'] == 0
    df_temp = df[mask][['품목번호']].copy()

    # df2와 merge (중복이 있어도 작동)
    #df_temp = df_temp.merge(df2[['품목번호', '원화단가']], on='품목번호', how='left')
    df_temp = df_temp.merge(
    df2[['품목번호', '원화단가']].drop_duplicates(subset='품목번호', keep='last'),
    on='품목번호',
    how='left')
    
    # 원래 데이터프레임에 업데이트
    df.loc[mask, '재고단가'] = df_temp['원화단가'].values
    df['금액'] = df['재고단가'] * df['창고재고']

    return df, df2

# 주간업무일지 함수 2
def calculate_summary(df):
    """창고별 금액 합계""" 
    summary = {
        '총액': df['금액'].sum(),
        '마을방송': df[df['품목번호'].str.startswith('B', na=False)]['금액'].sum(),
        '쉴더스': df[df['규격'].str.contains('리퍼', na=False)]['금액'].sum(),
        '교육청': df[df['규격'].str.contains('교육청', na=False)]['금액'].sum(),
        '전자단말': df[df['품목번호'].str.startswith('C', na=False)]['금액'].sum(),
    }
    summary['dp'] = summary['총액'] - sum([summary[k] for k in ['마을방송', '쉴더스', '교육청', '전자단말']])    

    return summary

# 주간업무일지 함수 3
def week_buy_price(df2, toDay, lastweek):
    """주간 구매 금액 합계"""
    week_price = df2[(df2['입고일자'] < toDay) & (df2['입고일자'] >= lastweek)]['원화금액'].sum()

    return week_price





# 회전률 함수 1
def data_process(df, df2):
    """ 회전률 데이터 처리 함수"""
    # 첫 행 삭제
    df = df.drop(index=0)

    # 조건 정의 
    delete_conditions = [
        ('품목번호', 'startswith', 'X'),
        ('품목번호', 'startswith', 'B'),
        ('창고', 'contains', '영업'),
        ('창고', 'contains', '전자'),
        ('창고', 'contains', '자재'),
        ('창고', 'contains', '상주'),
        ('창고', 'contains', '인천'),
        ('규격', 'contains', 'AFWM'),
        ('규격', 'contains', 'APD3'),
        ('규격', 'contains', '교육청'),
        ('규격', 'contains', '전자칠판'),
        ('규격', 'contains', '건강보험'),
        ('규격', 'contains', '연금공단'),
    ]

    # 반복문으로 처리
    for column, method, value in delete_conditions:
        if method == 'startswith':
            df = df[~df[column].str.startswith(value)]
        elif method == 'contains':
            df = df[~df[column].str.contains(value)]

    # 
    df2 = df2[['이동일자', '품목', '품목명', '규격', '단위', '이동수량', '출고창고', '입고창고', '담당부서', '담당자']]


    delete_conditions2 = [
        ('품목', 'startswith', 'X'),
        ('입고창고', 'contains', '자재'),
        ('입고창고', 'contains', '영업'),
        ('출고창고', 'contains', '자재'),
        ('규격', 'contains', 'AFWM'),
        ('규격', 'contains', 'APD3'),
        ('규격', 'contains', '교육청'),
        ('규격', 'contains', '전자칠판'),
        ('규격', 'contains', '건강보험'),
        ('규격', 'contains', '연금공단'),
    ]

    for column, method, value in delete_conditions2:
        if method == 'startswith':
            df2 = df2[~df2[column].str.startswith(value)]
        elif  column == '입고창고' and value == '자재':
            df2 = df2[df2[column].str.contains(value)]
        else:
            df2 = df2[~df2[column].str.contains(value)]

    return df, df2







