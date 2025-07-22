import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import geopy.distance

# ฟังก์ชันสำหรับโหลดข้อมูลจาก Excel
def load_data(file_path):
    try:
        # อ่านข้อมูลจากไฟล์ Excel
        data = pd.read_excel('DATA.xls')
        
        # แสดงข้อมูลตัวอย่าง
        print(data.head())  # แสดง 5 แถวแรกของข้อมูล
        
        return data
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return None

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

# แอปพลิเคชันหลัก
def main():
    st.title("🌊 โปรแกรมทำนายระดับน้ำและเส้นทางอพยพ")
    st.write("ป้อนค่าปัจจัยทางสภาพอากาศเพื่อทำนายระดับน้ำและดูเส้นทางอพยพที่ใกล้ที่สุด")

    # ระบุไฟล์ Excel ที่ต้องการโหลด
    file_path = "path/to/your/data.xlsx"  # ระบุที่อยู่ของไฟล์ Excel

    # โหลดข้อมูลจากไฟล์ Excel
    data = load_data(file_path)
    
    if data is not None:
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
    else:
        st.error("ไม่สามารถโหลดข้อมูลจากไฟล์ได้")

if __name__ == "__main__":
    main()