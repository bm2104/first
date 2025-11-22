import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from 보고서_함수 import calculate_summary, process_data, week_buy_price, data_process 
from io import BytesIO

# 날짜 확인 및 지정
today = datetime.today()
to_day = today.strftime('%Y%m%d')
days = today.strftime('%m월 %d일')
days_from_wed = (today.weekday() - 2) % 7 + 7
days_from_fri = (today.weekday() - 4) % 7 
days_from_yester = (today.weekday() - 1) % 7
toDay = (today - timedelta(days=days_from_yester)).strftime('%Y/%m/%d')
td = (today - timedelta(days=days_from_yester)).strftime('%Y-%m-%d')
lastweek = (today - timedelta(days=days_from_wed)).strftime('%Y/%m/%d')
lw = (today - timedelta(days=days_from_wed)).strftime('%Y-%m-%d')
month = today.month
week_of_month = (today.day - 1) // 7 
lastweek_fri = (today - timedelta(days=days_from_fri)).strftime('%Y년 %m 월 %d일')




_, col, _ = st.columns([2, 7, 1])
col.title('자재센터 보고서 자동화')

''
''
# 3개의 텝으로 분리
tab1, tab2, tab3 = st.tabs(['주간업무일지', '회전률', '월마감'])


# 탭1 - 주간업무일지
with tab1:
    st.subheader(f'{lw} ~ {td} 주간보고')
    ''
    st.write(f'{td} 기준 저장소품목별단가 파일 필요 ')
    ''
    
    buffer = BytesIO()

    df = ''
    df2 = ''

    # 파일 로드 
    file_path = st.file_uploader('저장소품목별단가 Excel 파일을 선택하세요.', type=['xlsx', 'xls'])
    out1 = st.empty()

    if file_path:
        out1.write('저장소품목별단가를 성공적으로 올렸습니다~')
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except:
            df = pd.read_excel(file_path, engine='xlrd')
    '---'
    file_path2 = st.file_uploader('구매입고리스트 Excel 파일을 선택하세요.', type=['xlsx', 'xls'])
    out2 = st.empty()

    if file_path2:
        out2.write('구매입고리스트를 성공적으로 올렸습니다~')
        try:
            df2 = pd.read_excel(file_path2, engine='openpyxl')
        except:
            df2 = pd.read_excel(file_path2, engine='xlrd')

    '---'
    file_path3 = st.file_uploader('저번주데이터 Excel 파일을 선택하세요.', type=['xlsx', 'xls'])
    out3 = st.empty()

    if file_path3:
        out3.write('저번주데이터를 성공적으로 올렸습니다~')
        try:
            df_lastweek = pd.read_excel(file_path3, engine='openpyxl', sheet_name='금액비교')
        except:
            df_lastweek = pd.read_excel(file_path3, engine='xlrd', sheet_name='금액비교')

    ''
    ''

    if file_path and file_path2 and file_path3:
        # 데이터 처리 
        df, df2 = process_data(df, df2)

        # 금액 합계
        summary = calculate_summary(df)

        df3 = pd.DataFrame({
            '-': list(summary.keys()),
            '금주': list(summary.values())
        })

        if '금주' in df_lastweek.columns:
            df3['전주'] = df_lastweek['금주'].values[:len(df3)]
            df3['차액'] = df3['금주'] - df3['전주']
            df3 = df3[['-', '전주', '금주', '차액']]

        df3 = df3.round()

        # dp 금액 증감 확인
        hr = '증가' if df3["차액"][5] >0 else '김소'

        # 주간금액 불러오기
        wp = week_buy_price(df2, toDay, lastweek)

        week_work_list ={
            '1':f'{days}(화) 전사 재고 총 금액 {int(df3["금주"][0]):,}원 / DP {int(df3["금주"][5]):,}백 ({int(df3["차액"][5]):,}원 {hr})\n' 
                f'- SK쉴더스 {int(df3["금주"][2]):,}백 / 교육청 {int(df3["금주"][3]):,}백 / 전자단말기 {int(df3["금주"][4]):,}백 / 스마트케어 {int(df3["금주"][1]):,}백',

            '2':f'주간 구매 금액 : {wp:,}원 \n'    
                '- DP 서비스 자재 : ECS Q670 메인보드 외 ??? 백 \n'
                '- 교육청 자재 : 인천시교육청 판매용 마우스 외 ??? 백 \n'
                '- 유상수리 : 기가바이트 H310M 메인보드 외 ???백',

            '3':'기타\n'
                '- 롯데렌탈 회수장비 반납 : PC, 모니터 등 총 ??EA'
                '\n- 11월 ?주차 자재회전률 ???% (목표 50%)'
        }
    
        df4 = pd.DataFrame(week_work_list.items(), columns=['구분', '내용'])
    
        
        # 엑셀 저장
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='RAW', index=False)
            df2.to_excel(writer, sheet_name='구매', index=False)
            df3.to_excel(writer, sheet_name='금액비교', index=False)
            df4.to_excel(writer, sheet_name='주간업무내용', index=False)


    else:
        st.write('모든 파일을 업로드해주세요.')
  
    # 버퍼의 내용 가져오기
    excel_data = buffer.getvalue()        
    
    if st.download_button(label='파일 다운로드', data=excel_data, file_name=f'{to_day}raw.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):

        st.write ('다운로드 되었습니다.')





# 탭2 - 회전률
with tab2:
    # 날짜 구하기

    st.subheader(f'{month}월 {week_of_month}주차 회전률 RAW')
    ''
    st.write(f'{lastweek_fri} 파일')
    buffer = BytesIO()
    ''
    # 파일 로드 
    # 저번주 금요일 저장소 불러오기 
    file_path = st.file_uploader('회전률 저장소품목별단가 Excel 파일을 선택하세요.')
    out1 = st.empty()

    if file_path:
        out1.write('회전률 저장소품목별단가를 성공적으로 올렸습니다~')
        df = pd.read_excel(file_path)
    '---'
    file_path2 = st.file_uploader('S/L 간 이동처리 리스트 Excel 파일을 선택하세요.')
    out2 = st.empty()

    if file_path2:
        out2.write('S/L 간 이동처리 리스트를 성공적으로 올렸습니다~')
        df2 = pd.read_excel(file_path2)

    ''
    ''
    if file_path and file_path2:
        df, df2 = data_process(df, df2)

        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='재고', index=False)
                df2.to_excel(writer, sheet_name='반납금액', index=False)

        # 버퍼의 내용 가져오기
        excel_data = buffer.getvalue()

        st.download_button(label='파일 내려 받기', data=excel_data, file_name='회전률raw.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        st.write ('다운로드 되었습니다.')

    else:
        st.write('파일을 불러와주세요.')

