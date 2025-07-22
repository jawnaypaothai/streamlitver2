import streamlit as st
import numpy as np
from sklearn.linear_model import LinearRegression

# ตั้งค่าธีมและโลโก้
st.set_page_config(
    page_title="Water Level Predictor",
    page_icon="🌊",
    layout="centered"
)

# CSS สำหรับตกแต่ง
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .title {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric {
        font-weight: bold;
        font-size: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ส่วนหัวของแอป
st.markdown('<div class="title">🌧️ Water Level Predictor</div>', unsafe_allow_html=True)
st.subheader("ระบุปัจจัยทางสภาพอากาศเพื่อทำนายระดับน้ำในแม่น้ำ")

# การสร้างฟอร์มรับข้อมูล
with st.form(key="water_level_form"):
    st.markdown('<div class="main">', unsafe_allow_html=True)

    # อินพุต
    rainfall = st.number_input("ปริมาณน้ำฝน (มม.)", min_value=0.0, step=0.1)
    humidity = st.number_input("ความชื้นสัมพัทธ์ (%)", min_value=0.0, max_value=100.0, step=0.1)
    temperature = st.number_input("อุณหภูมิ (°C)", step=0.1)
    wind_speed = st.number_input("ความเร็วลม (กม./ชม.)", min_value=0.0, step=0.1)

    # ปุ่ม
    submitted = st.form_submit_button("ทำนาย")

# การคำนวณผลลัพธ์เมื่อผู้ใช้ส่งแบบฟอร์ม
if submitted:
    # โมเดลจำลองง่ายๆ
    model = LinearRegression()
    X_train = np.array([[100, 85, 30, 10], [200, 75, 28, 15], [150, 80, 29, 12]])
    y_train = np.array([2.5, 4.0, 3.0])
    model.fit(X_train, y_train)

    # การทำนาย
    input_data = np.array([[rainfall, humidity, temperature, wind_speed]])
    prediction = model.predict(input_data)[0]

    # การแสดงผล
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    st.metric("ระดับน้ำที่คาดการณ์", f"{prediction:.2f} เมตร")

    # แจ้งเตือนน้ำท่วม
    if prediction > 3.5:
        st.error("🚨 แจ้งเตือน: ระดับน้ำสูง! ควรเตรียมพร้อมอพยพ")
        st.info("""
        **คำแนะนำ:**
        - ติดต่อเจ้าหน้าที่ในพื้นที่
        - เตรียมสิ่งของจำเป็น
        - อพยพไปยังที่สูง
        """)
    else:
        st.success("✅ ระดับน้ำอยู่ในเกณฑ์ปกติ")

