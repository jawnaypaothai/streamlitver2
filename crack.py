import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import math

# เพิ่มความแม่นยำโดยกำจัด noise เบื้องต้นก่อน threshold
def preprocess_image(image_np):
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    filtered = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    return filtered

# ค่ามาตรฐานเริ่มต้น (กรณีไม่มีการคำนวณ scale)
PIXEL_TO_MM = 0.2

# แผนที่ทิศทางของรอยร้าว
orientation_map = {
    "Vertical": "แนวตั้ง",
    "Horizontal": "แนวนอน",
    "Diagonal": "เฉียง"
}

# แผนที่ระดับความรุนแรงของรอยร้าว
severity_map = {
    "Light": "เบา",
    "Moderate": "ปานกลาง",
    "Severe": "รุนแรง"
}

# แผนที่คำแนะนำในการซ่อมแซม
repair_recommendation = {
    "Light": "ทำความสะอาดและอุดรอยร้าวด้วยวัสดุทั่วไป เช่น ซีเมนต์ขาวหรือโป๊วผนัง แล้วทาสีทับ",
    "Moderate": "ใช้วัสดุอุดรอยร้าวประเภทอีพ็อกซี่หรือมอร์ต้าซ่อมแซม ตรวจสอบโครงสร้างโดยวิศวกร",
    "Severe": "หยุดใช้งานส่วนที่เสียหายทันที ติดต่อวิศวกรโครงสร้าง ตรวจสอบและซ่อมแซมโดยวิธีทางวิศวกรรม เช่น FRP หรือฉีดอีพ็อกซี่"
}

# แผนที่สีของระดับความรุนแรง
severity_color = {
    "Light": "🟢",
    "Moderate": "🟠",
    "Severe": "🔴"
}

# ฟังก์ชันในการจัดประเภททิศทางของรอยร้าว
def classify_crack_orientation(contour):
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / h if h != 0 else 0
    if aspect_ratio < 0.5:
        return "Vertical"
    elif aspect_ratio > 2.0:
        return "Horizontal"
    else:
        return "Diagonal"

# ฟังก์ชันในการวิเคราะห์รอยร้าว
def analyze_crack(image_np, min_crack_area=20, reference_length_mm=None, reference_box=None, contour_thickness=2, min_crack_length_mm=10):
    filtered = preprocess_image(image_np)

    # หากผู้ใช้ใส่ reference object (เช่น เหรียญ/ไม้บรรทัด)
    global PIXEL_TO_MM
    if reference_length_mm and reference_box:
        ref_x, ref_y, ref_w, ref_h = reference_box
        ref_px = max(ref_w, ref_h)  # ความยาวพิกเซลของ reference
        PIXEL_TO_MM = reference_length_mm / ref_px

    # ใช้ adaptive threshold แทน Canny เพื่อจับรอยแตกละเอียดขึ้น
    adaptive = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, 11, 2)

    # Morphological operation เพื่อปิดช่องว่าง
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    result = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
    orientations = []
    crack_lengths_mm = []
    intensities = []

    total_crack_area = 0
    total_crack_length = 0
    for cnt in contours:
        # คำนวณความยาวของรอยร้าวจาก bounding box
        x, y, w, h = cv2.boundingRect(cnt)
        crack_length_px = math.sqrt(w**2 + h**2)  # คำนวณความยาวในพิกเซล
        crack_length_mm = crack_length_px * PIXEL_TO_MM  # แปลงเป็นมิลลิเมตร

        # กรองรอยร้าวที่ยาวพอสมควร
        if crack_length_mm >= min_crack_length_mm:
            # คำนวณค่าความเข้มเฉลี่ยของรอยร้าว
            mask = np.zeros_like(filtered)
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            mean_intensity = cv2.mean(filtered, mask=mask)[0]
            intensities.append(mean_intensity)

            # เพิ่มการวาดรอยร้าวในภาพ
            orientation = classify_crack_orientation(cnt)
            orientations.append(orientation)

            # วาด contour และ bounding box
            cv2.drawContours(result, [cnt], -1, (0, 0, 255), contour_thickness)
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), contour_thickness)
            cv2.putText(result, f"{crack_length_mm:.1f}mm", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,0), 1)

            crack_lengths_mm.append(crack_length_mm)
            total_crack_length += crack_length_mm
            total_crack_area += cv2.contourArea(cnt) * (PIXEL_TO_MM ** 2)

    avg_intensity = np.mean(intensities) if intensities else 0
    num_cracks = len(crack_lengths_mm)

    # กำหนดระดับความรุนแรงตามเกณฑ์ใหม่
    if total_crack_length >= 50 or total_crack_area >= 200:
        severity = "Severe"
    elif total_crack_length >= 30 or total_crack_area >= 100:
        severity = "Moderate"
    else:
        severity = "Light"

    return result, len(crack_lengths_mm), total_crack_area, severity, orientations, avg_intensity, num_cracks, crack_lengths_mm, total_crack_length

# ส่วนของ Streamlit
st.set_page_config(page_title="Crack Detector App", layout="wide")
st.title("🧱 ระบบตรวจจับรอยร้าวด้วยภาพถ่าย")

uploaded_files = st.file_uploader("📷 อัปโหลดภาพ (รองรับหลายภาพ)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ให้ผู้ใช้เลือกระดับความหนาของเส้น
contour_thickness = st.slider("เลือกระดับความหนาของเส้นรอยร้าว", 1, 10, 2)
min_crack_length_mm = st.slider("เลือกระยะความยาวขั้นต่ำของรอยร้าว (มม)", 1, 50, 10)

if uploaded_files:
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        image = Image.open(uploaded_file).convert("RGB")
        image_np = np.array(image)

        processed, crack_pixel_count, total_area_mm2, severity, orientations, avg_intensity, num_cracks, crack_lengths_mm, total_length_mm = analyze_crack(image_np, contour_thickness=contour_thickness, min_crack_length_mm=min_crack_length_mm)

        col1, col2 = st.columns(2)
        with col1:
            st.image(image_np, caption=f"Original - {filename}", use_column_width=True)
        with col2:
            st.image(processed, caption=f"Detected Cracks - {filename}", use_column_width=True, clamp=True)

        severity_th = severity_map.get(severity, severity)
        translated_orientations = [orientation_map.get(o, o) for o in set(orientations)]
        st.markdown(f"**{severity_color[severity]} ระดับ:** {severity_th}  ")
        st.markdown(f"**จำนวนพิกเซลรอยร้าว:** {crack_pixel_count} px | **พื้นที่รวม:** {total_area_mm2:.2f} มม² | **ทิศทาง:** {', '.join(translated_orientations)}")
        st.markdown(f"**จำนวนรอยร้าวที่ตรวจพบ:** {num_cracks} | **ค่าความเข้มเฉลี่ยของรอยร้าว:** {avg_intensity:.2f}")
        st.markdown(f"**ความยาวรวมของรอยร้าว:** {total_length_mm:.1f} มม")
        st.markdown(f"**คำแนะนำในการซ่อมแซม:** {repair_recommendation[severity]}")
        st.markdown("""
        💡 **ความหมายของข้อมูล:**  
        - **จำนวนพิกเซลรอยร้าว:** จุดในภาพที่ตรวจพบว่าเป็นรอยร้าว (ยิ่งมาก รอยร้าวยิ่งใหญ่หรือหลายจุด)  
        - **พื้นที่:** พื้นที่จริงของรอยร้าว (เมื่อแปลงจากพิกเซลเป็นมิลลิเมตร²)  
        - **ทิศทาง:** แนวของรอยร้าวที่พบ เช่น แนวตั้ง แนวนอน หรือเฉียง  
        - **จำนวนรอยร้าว:** จำนวนกลุ่มรอยแยกที่ตรวจพบ (ไม่ใช่พิกเซลรวม)  
        - **ค่าความเข้มเฉลี่ย:** ความมืด-สว่างของรอยร้าว (ยิ่งต่ำ → รอยร้าวเข้ม/ลึก)
        """)

        st.divider()
