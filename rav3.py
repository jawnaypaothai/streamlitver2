import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import geopy.distance
import streamlit.components.v1 as components

# ฟังก์ชันสำหรับโหลดข้อมูล
def load_data():
    data = {
        "rainfall": [50, 100, 200, 150, 80, 30, 10, 5],
        "humidity": [70, 80, 90, 85, 75, 65, 60, 55],
        "temperature": [25, 28, 30, 27, 26, 24, 23, 22],
        "air_pressure": [1015, 1012, 1010, 1013, 1011, 1014, 1016, 1017],
        "wind_speed": [36, 43.2, 54, 36, 28.8, 18, 10.8, 7.2],
        "water_level": [2.5, 3.0, 4.5, 4.0, 3.2, 1.8, 1.2, 0.8],
    }
    return pd.DataFrame(data)

# ฟังก์ชันสำหรับสร้างและฝึกโมเดล
def train_model(data):
    X = data[["rainfall", "humidity", "temperature", "air_pressure", "wind_speed"]]
    y = data["water_level"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    return model, rmse

# ฟังก์ชันคำนวณระยะทาง
def calculate_distance(coord1, coord2):
    return geopy.distance.distance(coord1, coord2).km

# จุดอพยพ (ตัวอย่าง)
evacuation_points = [
    {"name": "ศูนย์อพยพ A", "latitude": 13.7563, "longitude": 100.5018},
    {"name": "ศูนย์อพยพ B", "latitude": 13.8496, "longitude": 100.6000},
    {"name": "ศูนย์อพยพ C", "latitude": 13.9200, "longitude": 100.5400},
]

# ฟังก์ชันค้นหาจุดอพยพที่ใกล้ที่สุด
def find_nearest_evacuation(user_location):
    nearest = None
    shortest_distance = float('inf')

    for point in evacuation_points:
        distance = calculate_distance(user_location, (point["latitude"], point["longitude"]))
        if distance < shortest_distance:
            nearest = point
            shortest_distance = distance

    return nearest, shortest_distance

# แอปพลิเคชันหลัก
def main():
    st.title("🌊 โปรแกรมทำนายระดับน้ำและเส้นทางอพยพ")
    st.write("ป้อนค่าปัจจัยทางสภาพอากาศเพื่อทำนายระดับน้ำและดูเส้นทางอพยพที่ใกล้ที่สุด")

    # โหลดข้อมูลและสร้างโมเดล
    data = load_data()
    model, rmse = train_model(data)

    # แสดงค่า RMSE ของโมเดล
    st.sidebar.write("**ความแม่นยำของโมเดล (RMSE):**")
    st.sidebar.write(f"{rmse:.2f} เมตร")

    # รับอินพุตจากผู้ใช้ในรูปแบบกรอกข้อความ
    try:
        rainfall = float(st.text_input("ปริมาณน้ำฝน (มม.)", value="50"))
        humidity = float(st.text_input("ความชื้น (%)", value="70"))
        temperature = float(st.text_input("อุณหภูมิ (°C)", value="25"))
        air_pressure = float(st.text_input("ความกดอากาศ (mb)", value="1015"))
        wind_speed_kmh = float(st.text_input("ความเร็วลม (km/h)", value="36"))

        # ทำนายผลลัพธ์
        input_data = pd.DataFrame([[rainfall, humidity, temperature, air_pressure, wind_speed_kmh / 3.6]],
                                  columns=["rainfall", "humidity", "temperature", "air_pressure", "wind_speed"])
        prediction = model.predict(input_data)

        # แสดงการทำนายระดับน้ำ
        st.success(f"ระดับน้ำในแม่น้ำที่คาดการณ์: {prediction[0]:.2f} เมตร")

        # แจ้งเตือนน้ำท่วมและคำแนะนำการอพยพ
        if prediction[0] > 2.75:  # เกณฑ์น้ำท่วม
            st.error("⚠️ แจ้งเตือน: ระดับน้ำเกินเกณฑ์ ปริมาณน้ำอาจท่วม!")
            st.warning("📌 **คำแนะนำการอพยพ:** ตรวจสอบเส้นทางอพยพด้านล่าง")

            # รับตำแหน่งจากผู้ใช้
            lat = float(st.text_input("ตำแหน่งปัจจุบันของคุณ (ละติจูด)", value="13.7563"))
            lon = float(st.text_input("ตำแหน่งปัจจุบันของคุณ (ลองจิจูด)", value="100.5018"))
            user_location = (lat, lon)

            # ค้นหาจุดอพยพที่ใกล้ที่สุด
            nearest_point, distance = find_nearest_evacuation(user_location)

            if nearest_point:
                st.info(f"📍 จุดอพยพที่ใกล้ที่สุด: **{nearest_point['name']}**\n"
                        f"ระยะทางประมาณ: **{distance:.2f} กิโลเมตร**")

                # แสดงแผนที่พร้อมเส้นทาง
                m = folium.Map(location=user_location, zoom_start=12)
                folium.Marker(user_location, popup="ตำแหน่งปัจจุบัน", icon=folium.Icon(color="blue")).add_to(m)
                folium.Marker([nearest_point["latitude"], nearest_point["longitude"]],
                              popup=f"{nearest_point['name']} (ระยะทาง: {distance:.2f} กม.)",
                              icon=folium.Icon(color="red")).add_to(m)
                folium.PolyLine([user_location, 
                                 (nearest_point["latitude"], nearest_point["longitude"])],
                                color="green", weight=2.5, opacity=1).add_to(m)
                st_folium(m, width=700, height=500)
        else:
            st.info("✅ ระดับน้ำอยู่ในเกณฑ์ปลอดภัย")
    except ValueError:
        st.error("กรุณากรอกข้อมูลที่ถูกต้อง")

    # แสดงข้อมูลตัวอย่าง
    st.write("### ข้อมูลตัวอย่าง")
    st.dataframe(data)

if __name__ == "__main__":
    main()
