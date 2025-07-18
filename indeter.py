import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Eq, solve

st.title("วิเคราะห์คาน Determinate พร้อม SFD และ BMD")

# --- Input Section ---
L = st.number_input("ความยาวคาน (เมตร)", min_value=1.0, value=10.0, step=0.5)

positions = [round(x, 2) for x in np.linspace(0, L, 11)]

st.markdown("### เลือกตำแหน่งจุดรองรับ")
support_pos_A = st.selectbox("ตำแหน่งจุดรองรับ A (m)", positions, key="suppA_pos")
support_A = st.selectbox("ประเภทจุดรองรับ A", ["pinned", "roller", "fixed", "none"], key="suppA")

support_pos_B = st.selectbox("ตำแหน่งจุดรองรับ B (m)", positions, key="suppB_pos")
support_B = st.selectbox("ประเภทจุดรองรับ B", ["roller", "pinned", "fixed", "none"], key="suppB")

st.markdown("""
##### 👉 **คำแนะนำ**: จุดรองรับที่แนะนำ
- หากต้องการวิเคราะห์คานทั่วไป เช่น simple beam: ใช้ `pinned` ที่ A และ `roller` ที่ B
- หากต้องการคานยื่นหรือแบบ fix: ใช้ `fixed` ที่ปลายใดปลายหนึ่ง
""")

st.subheader("แรงกระทำแบบจุด (Point Load)")
point_loads = []
num_point = st.number_input("จำนวนแรงกระทำแบบจุด", min_value=0, value=1, step=1)
for i in range(num_point):
    col1, col2, col3 = st.columns(3)
    with col1:
        pos = st.number_input(f"ตำแหน่งแรงจุด {i+1} (m)", min_value=0.0, max_value=L, key=f"ppos_{i}")
    with col2:
        fx = st.number_input(f"แรงแนว x {i+1} (kN)", key=f"fx_{i}")
    with col3:
        fy = st.number_input(f"แรงแนว y {i+1} (kN)", key=f"fy_{i}")
    point_loads.append((pos, fx, fy))

st.subheader("แรงกระจาย (UDL)")
udls = []
num_udl = st.number_input("จำนวนแรงกระจาย", min_value=0, value=1, step=1)
for i in range(num_udl):
    x1 = st.number_input(f"เริ่มที่ (m) UDL {i+1}", min_value=0.0, max_value=L, key=f"udl_x1_{i}")
    x2 = st.number_input(f"สิ้นสุดที่ (m) UDL {i+1}", min_value=0.0, max_value=L, key=f"udl_x2_{i}")
    w = st.number_input(f"ขนาดแรง (kN/m) UDL {i+1}", key=f"udl_w_{i}")
    if x2 > x1:
        udls.append((x1, x2, w))

st.subheader("โมเมนต์")
moments = []
num_mom = st.number_input("จำนวนโมเมนต์", min_value=0, value=1, step=1)
for i in range(num_mom):
    pos = st.number_input(f"ตำแหน่งโมเมนต์ {i+1} (m)", min_value=0.0, max_value=L, key=f"mpos_{i}")
    mag = st.number_input(f"ขนาดโมเมนต์ {i+1} (kNm)", key=f"mmag_{i}")
    moments.append((pos, mag))

# --- Analysis ---
def beam_analysis(L, point_loads, udls, moments, support_A, support_B, support_pos_A, support_pos_B):
    x_vals = np.linspace(0, L, 500)
    x = symbols('x')
    RAx, RAy, MA, RBx, RBy, MB = symbols('RAx RAy MA RBx RBy MB')

    eqs = []
    unknowns = []

    support_dict = {
        'none': [],
        'roller': ['y'],
        'pinned': ['x', 'y'],
        'fixed': ['x', 'y', 'm']
    }

    pos_dict = {'A': support_pos_A, 'B': support_pos_B}
    for label, support in zip(['A', 'B'], [support_A, support_B]):
        if 'x' in support_dict[support]:
            unknowns.append(symbols(f'R{label}x'))
        if 'y' in support_dict[support]:
            unknowns.append(symbols(f'R{label}y'))
        if 'm' in support_dict[support]:
            unknowns.append(symbols(f'M{label}'))

    fx_eq = 0
    if RAx in unknowns:
        fx_eq += RAx
    if RBx in unknowns:
        fx_eq += RBx
    for _, fx, _ in point_loads:
        fx_eq -= fx
    eqs.append(Eq(fx_eq, 0))

    fy_eq = 0
    if RAy in unknowns:
        fy_eq += RAy
    if RBy in unknowns:
        fy_eq += RBy
    for _, _, fy in point_loads:
        fy_eq -= fy
    for x1, x2, w in udls:
        fy_eq -= w * (x2 - x1)
    eqs.append(Eq(fy_eq, 0))

    moment_eq = 0
    if RAy in unknowns:
        moment_eq += RAy * support_pos_A
    if RBy in unknowns:
        moment_eq += RBy * support_pos_B
    if MA in unknowns:
        moment_eq += MA
    if MB in unknowns:
        moment_eq += MB
    for px, _, fy in point_loads:
        moment_eq -= fy * px
    for x1, x2, w in udls:
        moment_eq -= w * (x2 - x1) * ((x1 + x2)/2)
    for mx, m in moments:
        moment_eq -= m
    eqs.append(Eq(moment_eq, 0))

    sol = solve(eqs, unknowns, dict=True)
    sol = sol[0] if sol else {}

    def safe_eval(sym):
        val = sol.get(sym, 0)
        return float(val.evalf()) if hasattr(val, 'evalf') else 0.0

    RAx_val = safe_eval(symbols('RAx'))
    RAy_val = safe_eval(symbols('RAy'))
    RBx_val = safe_eval(symbols('RBx'))
    RBy_val = safe_eval(symbols('RBy'))
    MA_val = safe_eval(symbols('MA'))
    MB_val = safe_eval(symbols('MB'))

        # คำนวณ SFD และ BMD อย่างง่าย (กรณีจำกัด เฉพาะแรง y และ moment แบบเบื้องต้น)
    V = np.zeros_like(x_vals)
    M = np.zeros_like(x_vals)
    for i, x in enumerate(x_vals):
        V[i] = RAy_val + RBy_val
        for px, _, fy in point_loads:
            if x >= px:
                V[i] -= fy
        for x1, x2, w in udls:
            if x1 <= x <= x2:
                V[i] -= w * (x - x1)
            elif x > x2:
                V[i] -= w * (x2 - x1)

        M[i] = MA_val
        if x >= support_pos_A:
            M[i] += RAy_val * (x - support_pos_A)
        if x >= support_pos_B:
            M[i] += RBy_val * (x - support_pos_B)
        for px, _, fy in point_loads:
            if x >= px:
                M[i] -= fy * (x - px)
        for x1, x2, w in udls:
            if x >= x2:
                M[i] -= w * (x2 - x1) * (x - (x1 + x2) / 2)
            elif x >= x1:
                a = x - x1
                M[i] -= w * a * a / 2
        for mx, m in moments:
            if x >= mx:
                M[i] -= m

    return x_vals, RAx_val, RAy_val, RBx_val, RBy_val, MA_val, MB_val, V, M

if st.button("วิเคราะห์คาน"):
    import matplotlib.pyplot as plt
    x_vals, RAx_val, RAy_val, RBx_val, RBy_val, MA_val, MB_val, V, M = beam_analysis(
        L, point_loads, udls, moments, support_A, support_B, support_pos_A, support_pos_B)

    st.subheader("แรงปฏิกิริยา")
    st.write(f"RAx = {RAx_val:.2f} kN (แนว x → {'ขวา' if RAx_val >= 0 else 'ซ้าย'})")
    st.write(f"RAy = {RAy_val:.2f} kN (แนว y → {'ขึ้น' if RAy_val >= 0 else 'ลง'})")
    st.write(f"RBx = {RBx_val:.2f} kN (แนว x → {'ขวา' if RBx_val >= 0 else 'ซ้าย'})")
    st.write(f"RBy = {RBy_val:.2f} kN (แนว y → {'ขึ้น' if RBy_val >= 0 else 'ลง'})")
    st.write(f"MA = {MA_val:.2f} kNm ({'ทวนเข็ม' if MA_val >= 0 else 'ตามเข็ม'})")
    st.write(f"MB = {MB_val:.2f} kNm ({'ทวนเข็ม' if MB_val >= 0 else 'ตามเข็ม'})")

    # SFD
    st.subheader("Shear Force Diagram (SFD)")
    fig1, ax1 = plt.subplots()
    ax1.plot(x_vals, V, color='green', linewidth=2)
    ax1.fill_between(x_vals, V, color='lightgreen', alpha=0.5)
    for i in range(0, len(x_vals), max(1, int(len(x_vals)/10))):
        ax1.text(x_vals[i], V[i], f"{V[i]:.1f}", fontsize=8, color='black', ha='center')
    ax1.set_xlabel("ตำแหน่ง x (m)")
    ax1.set_ylabel("แรงเฉือน (kN)")
    ax1.grid(True)
    st.pyplot(fig1)

    # BMD
    st.subheader("Bending Moment Diagram (BMD)")
    fig2, ax2 = plt.subplots()
    ax2.plot(x_vals, M, color='blue', linewidth=2)
    ax2.fill_between(x_vals, M, color='lightblue', alpha=0.5)
    for i in range(0, len(x_vals), max(1, int(len(x_vals)/10))):
        ax2.text(x_vals[i], M[i], f"{M[i]:.1f}", fontsize=8, color='black', ha='center')
    ax2.set_xlabel("ตำแหน่ง x (m)")
    ax2.set_ylabel("โมเมนต์ดัด (kNm)")
    ax2.grid(True)
    st.pyplot(fig2)
