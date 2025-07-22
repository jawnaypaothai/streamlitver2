import streamlit as st
import numpy as np
from fpdf import FPDF
from scipy.optimize import newton
import base64
import os
import matplotlib.pyplot as plt

def manning_rectangular(Q, S, n, b):
    def equation(y):
        A = b * y
        P = b + 2 * y
        R = A / P
        return (1 / n) * A * R**(2/3) * S**0.5 - Q

    y_normal = newton(equation, 0.5)
    A = b * y_normal
    P = b + 2 * y_normal
    R = A / P
    v = Q / A
    return y_normal, v, R, A

def manning_semi_circle(Q, S, n):
    def equation(r):
        A = 0.5 * np.pi * r**2
        P = np.pi * r
        R = A / P
        return (1 / n) * A * R**(2/3) * S**0.5 - Q

    r = newton(equation, 0.5)
    y_normal = r
    A = 0.5 * np.pi * r**2
    P = np.pi * r
    R = A / P
    v = Q / A
    return y_normal, v, R, A

def create_pdf(inputs, results):
    class DrainageReport(FPDF):
        def header(self):
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, "Drainage Channel Design Report", ln=True, align="C")
            self.ln(10)

        def add_section(self, title, content):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, title, ln=True)
            self.set_font("Arial", "", 12)
            for line in content:
                self.cell(0, 10, line, ln=True)
            self.ln(5)

    pdf = DrainageReport()
    pdf.add_page()
    pdf.add_section("Input Parameters", inputs)
    pdf.add_section("Calculated Results", results)
    pdf_path = "drainage_report.pdf"
    pdf.output(pdf_path)
    return pdf_path

def file_download_link(filepath):
    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(filepath)}">📥 ดาวน์โหลดรายงาน PDF</a>'

def draw_rectangular_section(b, y):
    fig, ax = plt.subplots()
    ax.plot([0, b, b, 0, 0], [0, 0, y, y, 0], label='Water level')
    ax.set_title("หน้าตัดรางสี่เหลี่ยม")
    ax.set_xlabel("ความกว้าง (m)")
    ax.set_ylabel("ความลึก (m)")
    ax.set_aspect('equal')
    st.pyplot(fig)

def draw_semi_circle_section(r):
    theta = np.linspace(0, np.pi, 100)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    fig, ax = plt.subplots()
    ax.plot(x, y, label='Water level')
    ax.set_title("หน้าตัดรางครึ่งวงกลม")
    ax.set_xlabel("ความกว้าง (m)")
    ax.set_ylabel("ความลึก (m)")
    ax.set_aspect('equal')
    st.pyplot(fig)

st.title("🔧 โปรแกรมออกแบบรางระบายน้ำอัตโนมัติ")

Q = st.number_input("Q: อัตราการไหล (m³/s)", value=0.8)
S = st.number_input("S: ความลาดชัน (ทศนิยม เช่น 0.002)", value=0.002)
n = st.number_input("n: ค่าสัมประสิทธิ์ความหยาบ Manning", value=0.015)

channel_type = st.selectbox("เลือกรูปรางระบายน้ำ", ["รางสี่เหลี่ยมผืนผ้า", "รางครึ่งวงกลม"])

if channel_type == "รางสี่เหลี่ยมผืนผ้า":
    b = st.number_input("ความกว้างราง (m)", value=1.0)
    if st.button("คำนวณ"):
        y, v, R, A = manning_rectangular(Q, S, n, b)
        st.success(f"ระดับน้ำปกติ: {y:.3f} m")
        st.info(f"ความเร็วการไหล: {v:.3f} m/s")
        st.write(f"Hydraulic Radius: {R:.3f} m")
        st.write(f"พื้นที่หน้าตัด: {A:.3f} m²")
        draw_rectangular_section(b, y)

        inputs = [
            f"Q (Flow rate): {Q} m³/s",
            f"S (Slope): {S}",
            f"n (Manning's n): {n}",
            f"Channel type: Rectangular",
            f"Width: {b} m"
        ]
        results = [
            f"Normal depth: {y:.3f} m",
            f"Velocity: {v:.3f} m/s",
            f"Hydraulic radius: {R:.3f} m",
            f"Cross-sectional area: {A:.3f} m²"
        ]
        pdf_file = create_pdf(inputs, results)
        st.markdown(file_download_link(pdf_file), unsafe_allow_html=True)

elif channel_type == "รางครึ่งวงกลม":
    if st.button("คำนวณ"):
        y, v, R, A = manning_semi_circle(Q, S, n)
        st.success(f"รัศมีราง: {y:.3f} m")
        st.info(f"ความเร็วการไหล: {v:.3f} m/s")
        st.write(f"Hydraulic Radius: {R:.3f} m")
        st.write(f"พื้นที่หน้าตัด: {A:.3f} m²")
        draw_semi_circle_section(y)

        inputs = [
            f"Q (Flow rate): {Q} m³/s",
            f"S (Slope): {S}",
            f"n (Manning's n): {n}",
            f"Channel type: Semi-Circle"
        ]
        results = [
            f"Radius: {y:.3f} m",
            f"Velocity: {v:.3f} m/s",
            f"Hydraulic radius: {R:.3f} m",
            f"Cross-sectional area: {A:.3f} m²"
        ]
        pdf_file = create_pdf(inputs, results)
        st.markdown(file_download_link(pdf_file), unsafe_allow_html=True)
