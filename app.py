import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Vietnam Macroeconomic Dashboard", layout="wide", page_icon="📈")

col1, col2 = st.columns([1, 15])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/State_Bank_of_Vietnam_logo.svg/512px-State_Bank_of_Vietnam_logo.svg.png")
with col2:
    st.title("Bảng Điều Khiển: Kinh Tế Vĩ Mô Việt Nam (2010 - 2024)")

st.markdown("Dữ liệu được lấy trực tiếp từ **Ngân hàng Thế giới (World Bank)** phục vụ mục đích phân tích.")

@st.cache_data
def load_data():
    try:
        indicators = {
            'NY.GDP.MKTP.KD.ZG': 'GDP',
            'FM.LBL.BMNY.GD.ZS': 'M2',
            'FP.CPI.TOTL.ZG': 'INF',
            'FR.INR.RINR': 'R',
            'NE.TRD.GNFS.ZS': 'TRADE'
        }
        data_frames = []
        for ind, name in indicators.items():
            url = f"http://api.worldbank.org/v2/country/VNM/indicator/{ind}?date=2010:2024&format=json"
            res = requests.get(url).json()
            if len(res) == 2 and res[1]:
                df_temp = pd.DataFrame(res[1])
                df_temp = df_temp[['date', 'value']].rename(columns={'date': 'date', 'value': name})
                df_temp['date'] = df_temp['date'].astype(int)
                data_frames.append(df_temp)
        
        if data_frames:
            df = data_frames[0]
            for df_t in data_frames[1:]:
                df = pd.merge(df, df_t, on='date', how='outer')
            df = df.rename(columns={'date': 'year'}).sort_values('year').reset_index(drop=True)
            for col in ['GDP', 'M2', 'INF', 'R', 'TRADE']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu từ World Bank: {e}")
        return pd.DataFrame()

with st.spinner("⏳ Đang tải dữ liệu từ World Bank..."):
    df = load_data()

if not df.empty:
    st.subheader("Vùng xem tổng quan dữ liệu gốc")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Trực Quan Hóa (Visualizations)")

    # Ánh xạ tên chỉ số cho đẹp
    name_map = {
        'GDP': 'Tăng trưởng GDP (%)',
        'M2': 'Cung tiền M2 / GDP (%)',
        'INF': 'Lạm phát (%)',
        'R': 'Lãi suất thực (%)',
        'TRADE': 'Thương mại / GDP (%)'
    }

    # =================
    # Biểu đồ tuỳ chọn
    # =================
    indicator = st.selectbox("📌 Chọn Chỉ Số Để Xem Biểu Đồ Chi Tiết (Động):", ['GDP', 'INF', 'M2', 'R', 'TRADE'])

    fig_main = px.area(df, x='year', y=indicator, markers=True, 
                  title=f"Xu Hướng {name_map[indicator]} từ 2010-2024",
                  labels={"year": "Năm", indicator: name_map[indicator]},
                  color_discrete_sequence=['#005b9f']) # Màu xanh biển đặc trưng của SBV
    fig_main.update_layout(
        xaxis=dict(tick0=2010, dtick=1),
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig_main, use_container_width=True)


    st.markdown("---")
    # Hai cột để xem nhiều biểu đồ cùng lúc
    col1, col2 = st.columns(2)

    with col1:
        st.write("##### 1. Tăng trưởng GDP các năm")
        # Thay đổi màu để hấp dẫn thị giác
        fig_gdp = px.bar(df, x='year', y='GDP', 
                         color='GDP', color_continuous_scale="Blues",
                         text_auto='.2s')
        fig_gdp.update_layout(
            xaxis=dict(tick0=2010, dtick=2),
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_gdp, use_container_width=True)

    with col2:
        st.write("##### 2. Lạm Phát (INF) so với Lãi Suất Thực (R)")
        fig_inf_r = go.Figure()
        fig_inf_r.add_trace(go.Scatter(x=df['year'], y=df['INF'], mode='lines+markers', line=dict(color='#d62728', width=3), name='Lạm Phát (INF)'))
        fig_inf_r.add_trace(go.Scatter(x=df['year'], y=df['R'], mode='lines+markers', line=dict(color='#ff7f0e', width=3), name='Lãi Suất Thực (R)'))
        fig_inf_r.update_layout(
            xaxis=dict(tick0=2010, dtick=2),
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_inf_r, use_container_width=True)

else:
    st.warning("Không có dữ liệu để hiển thị.")
