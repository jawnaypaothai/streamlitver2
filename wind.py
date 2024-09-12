import streamlit as st
import pandas as pd
import numpy as np
import scipy
from scipy import interpolate
from PIL import Image

st.set_page_config(page_title='แรงลม มยผ',layout='wide',page_icon="🏗️")

def img_show(name, caption='', width=True):
   image = Image.open(name)
   return st.image(image, use_column_width=width, caption=caption, )

st.write('# การคำนวณแรงลมสำหรับอาคารเตี้ย')
st.write('# ตามมาตรฐาน มยผ.1311-50 ด้วยวิธีอย่างง่าย')

inputs = st.container()
with inputs:
    st.write('### มิติอาคาร')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        H_roof = st.number_input(label='ความสูงจั่วหลังคา, $H_\mathrm{roof} \mathrm{~[m]}$', min_value=0.0, max_value=23.0, value=8.65, step=0.1)
        H = st.number_input(label='ความสูงอาคาร (ชายคา), $H \mathrm{~[m]}$', min_value=0.0, max_value=23.0, value=6.0, step=0.1)
        
        
    with col2:
        B = st.number_input(label='ความกว้างในแนวตั้งฉากสันหลังคา, $B \mathrm{~[m]}$', min_value=0.0, value=60.0, step=0.1)
        W = st.number_input(label='ความกว้างในแนวขนานสันหลังคา, $W \mathrm{~[m]}$', min_value=0.0, value=60.0, step=0.1)
        Ds = min(B,W)
        st.write(r'ความกว้างด้านแคบที่สุด, $D_s = %.2f \mathrm{~m}$'%(Ds))
        
    with col1:
        slope = np.arctan((H_roof-H)/(0.5*B))*180.0/np.pi
        st.markdown(r'Roof slope, $\theta = %.2f \mathrm{~deg}$'%(slope))
        round(slope,2)
        
        
df_important = pd.DataFrame({
    'ประเภทความสำคัญ': ['น้อย', 'ปกติ', 'มาก', 'สูงมาก'],
    'สภาวะจำกัดด้านกำลัง': [0.8, 1.0, 1.15, 1.15],
    'สภาวะจำกัดด้านการใช้งาน': [0.75, 0.75, 0.75, 0.75],
})
        

df_wind_speed = pd.DataFrame({
    'กลุ่ม': ['1', '2', '3', '4A', '4B'],
    'V50 [m/s]': [25, 27, 29, 25, 25],
    'T_F': [1.0, 1.0, 1.0, 1.2, 1.08],
})

col1, col2 = st.columns(2)
with col1:
    st.write('### ค่าประกอบความสำคัญของแรงลม, $I$')
    col1x, col2x, col3x = st.columns(3)
    with col1x:
        important_type = st.selectbox(label='ประเภทความสำคัญ', options=df_important['ประเภทความสำคัญ'])
    with col2x:
        cal_type = st.selectbox(label='ประเภทการออกแบบ', options=['สภาวะจำกัดด้านกำลัง', 'สภาวะจำกัดด้านการใช้งาน'])
    with col3x:
        I = df_important.loc[df_important['ประเภทความสำคัญ'] == important_type, cal_type]
        st.markdown('')
        st.markdown('')
        st.markdown(r'$I = %.2f$'%(I))

    with st.expander("See table"):
        st.dataframe(df_important, hide_index=True)
        
col1, col2 = st.columns(2)
with col1:
    st.write('### ความเร็วลมอ้างอิง, $\overline{V}$')
    col1x, col2x = st.columns(2)
    with col1x:
        area_group = st.selectbox(label='กลุ่มพื้นที่', options=df_wind_speed['กลุ่ม'])
    with col2x:  
        V50 = df_wind_speed.loc[df_wind_speed['กลุ่ม'] == area_group, 'V50 [m/s]']
        T_F = df_wind_speed.loc[df_wind_speed['กลุ่ม'] == area_group, 'T_F']
        
        if cal_type == 'สภาวะจำกัดด้านกำลัง':
            v = V50*T_F
            st.markdown(r'$v_{50} = %.2f \mathrm{~m/s,} \quad T_F = %.2f$'%(V50, T_F))
            st.markdown(r'$\overline{V} = V_{50} T_F = %.2f \times %.2f = %.2f \mathrm{~m/s}$'%(V50, T_F, v))
        else:
            v = V50
            st.markdown(r'$V_{50} = %.2f \mathrm{~m/s}$'%(V50))
            st.markdown(r'$\overline{V} = V_{50} T_F = %.2f \mathrm{~m/s}$'%(v))
            
            
    
    with st.expander("See table"):
        st.dataframe(df_wind_speed, hide_index=True)
        
col1, col2 = st.columns(2)
with col1:
    st.write('### หน่วยแรงลมอ้างอิง, $q$')
    rho = 1.25
    g = 9.81
    q = 0.5*rho*g*(v**2)
    st.write(q)
    st.markdown(r'ความหนาแน่นของมวลอากาศ, $\rho \approx 1.25 \mathrm{~kg/m^3}$')
    st.markdown(r'อัตราเร่งเนื่องจากแรงโน้มถ่วงของโลก, $g = 9.81 \mathrm{~m/s^2}$')
    st.markdown(r'$q = \frac{1}{2} \left( \frac{\rho}{g} \right) \overline{V}^{2} = \frac{1}{2} \left( \frac{%.2f \mathrm{~kg/m^3}}{%.2f \mathrm{~m/s^2}} \right) \left( %.2f \mathrm{~m/s} \right)^{2} = %.2f \mathrm{~kg/m^2}$'%(rho,g,v,q))

st.markdown(r'### ค่าประกอบเนื่องจากสภาพภูมิประเทศ, $C_e$')

# z = st.number_input(label='ความสูงจากพื้นดิน, $z \mathrm{~[m]}$', min_value=0.0, max_value=80.0, value=5.0, step=0.5)

if slope < 7:
    st.markdown(r'สำหรับหลังคาที่มีความชัน**น้อยกว่า 7 องศา**, ความสูงอ้างอิง, $h$, สามารถใช้ความสูงชายคา, $H$, แทนได้ แต่ต้องมีค่าไม่น้อยกว่า 6 เมตร')
    h_ = H
    h = max(h_,6.0)
    st.markdown(r'$\qquad$ ความสูงอ้างอิง, $\quad h = \max \left( H, 6.0 \mathrm{~m}  \right) = \max \left(%.2f \mathrm{~m}, 6.0 \mathrm{~m} \right) = %.2f \mathrm{~m}$'%(h_,h))
    
    z = h
    st.markdown(r'ความสูงตำแหน่งคำนวณแรงลมจากพื้นดิน, $z = h = %.2f \mathrm{~m}$'%(z))
    
else:
    st.markdown(r'สำหรับหลังคาที่มีความชัน**มากกว่า 7 องศา**, ความสูงอ้างอิง, $h$, ให้ใช้ความสูงเฉลี่ยของหลังคา แต่ต้องมีค่าไม่น้อยกว่า 6 เมตร')
    h_ = 0.5*(H_roof+H)
    h = max(h_,6.0)
    st.markdown(r'$\qquad$ ความสูงเฉลี่ยของหลังคา, $\quad H_\mathrm{avg} = 0.5 \left( H_\mathrm{roof} + H \right) = 0.5 \left( %.2f \mathrm{~m} + %.2f \mathrm{~m} \right) = %.2f \mathrm{~m}$'%(H_roof,H,h_))
    st.markdown(r'$\qquad$ ความสูงอ้างอิง, $\quad h = \max \left( H_\mathrm{avg}, 6.0 \mathrm{~m}  \right) = \max \left(%.2f \mathrm{~m}, 6.0 \mathrm{~m} \right) = %.2f \mathrm{~m}$'%(h_,h))
    
    z = h
    st.markdown(r'ความสูงตำแหน่งคำนวณแรงลมจากพื้นดิน, $z = h = %.2f \mathrm{~m}$'%(z))
    
    
    
col1, buff, buff, buff, buff = st.columns(5)
with col1:
    land_type = st.selectbox(label='สภาพภูมิประเทศ', options=['แบบ A', 'แบบ B'])
    
if land_type == 'แบบ A':
    Ce = (z/10)**0.2
    st.markdown(r'$C_e = \left( \frac{z}{10} \right) ^{0.2} \ge 0.9$')
    st.markdown(r'$\quad\>\> = \left( \frac{%.2f}{10} \right) ^{0.2}$'%(z))
    st.markdown(r'$\quad\>\> = %.2f \ge 0.9$'%(Ce))
    Ce = max(Ce, 0.9)
    st.markdown(r'$\quad\>\> = %.2f$'%(Ce))
    
else:
    Ce_ = 0.7*(z/12)**0.3
    Ce = max(Ce_, 0.7)
    st.markdown(r'''$
                \begin{aligned}
                C_e &= 0.7 \left( \frac{z}{12} \right) ^{0.3} \ge 0.7 \\
                &= 0.7 \left( \frac{%.2f}{12} \right) ^{0.3} \\
                &= %.2f \ge 0.7 \\
                &= %.2f  \\
                \end{aligned}
                $'''%(z,Ce_,Ce))


st.markdown(r'### ค่าสัมประสิทธิ์ของหน่วยแรงลมภายนอก, $C_p C_g$')


df_case1 = pd.DataFrame({
    'Slope min [deg]': [0, 20, 30, 90],
    'Slope max [deg]': [5, 20, 45, 90],
    '1': [0.75, 1.0, 1.05, 1.05],
    '1E': [1.15, 1.5, 1.3, 1.3],
    '2': [-1.3, -1.3, 0.4, 1.05],
    '2E': [-2.0, -2.0, 0.5, 1.3],
    '3': [-0.7, -0.9, -0.8, -0.7],
    '3E': [-1.0, -1.3, -1.0, -0.9],
    '4': [-0.55, -0.8, -0.7, -0.7],
    '4E': [-0.8, -1.2, -0.9, -0.9],
})

df_case2 = pd.DataFrame({
    'Slope min [deg]': [0],
    'Slope max [deg]': [90],
    '1': [-0.85],
    '1E': [-0.9],
    '2': [-1.3],
    '2E': [-2.0],
    '3': [-0.7],
    '3E': [-1.0],
    '4': [-0.85],
    '4E': [-0.9],
    '5': [0.75],
    '5E': [1.15],
    '6': [-0.55],
    '6E': [-0.8],
})






zone_list = df_case1.columns
zone_list = ['Slope [deg]'] + zone_list[2:].to_list()

def interpolate_y(index):
    x_data = [float(df_case1['Slope max [deg]'][index]), float(df_case1['Slope min [deg]'][index+1])]
    aa = df_case1.iloc[index,2:].to_list()
    bb = df_case1.iloc[index+1,2:].to_list()
    y_all = zip(aa, bb)
    
    y_interpolate = []
    for y_data in y_all:
        f = interpolate.interp1d(x_data, y_data)
        y_interpolate.append(round(f([slope])[0],2))

    df = pd.DataFrame(data=[round(slope,2)] + y_interpolate)
    df = df.T
    df.columns = zone_list
    
    return df

if slope > 5.0 and slope < 20.0:
    df_CpCg = interpolate_y(0)
elif slope > 20.0 and slope < 30.0:
    df_CpCg = interpolate_y(1)
elif slope > 45.0 and slope < 90.0:
    df_CpCg = interpolate_y(2)
elif slope >= 0.0 and slope <= 5.0:
    df_CpCg = pd.DataFrame(data=[round(slope,2)] + df_case1.iloc[0,2:].to_list())
    df_CpCg = df_CpCg.T
    df_CpCg.columns = zone_list
elif slope == 20.0:
    df_CpCg = pd.DataFrame(data=[round(slope,2)] + df_case1.iloc[1,2:].to_list())
    df_CpCg = df_CpCg.T
    df_CpCg.columns = zone_list
elif slope >= 30.0 and slope <= 45.0:
    df_CpCg = pd.DataFrame(data=[round(slope,2)] + df_case1.iloc[2,2:].to_list())
    df_CpCg = df_CpCg.T
    df_CpCg.columns = zone_list
elif slope == 90.0:
    df_CpCg = pd.DataFrame(data=[round(slope,2)] + df_case1.iloc[3,2:].to_list())
    df_CpCg = df_CpCg.T
    df_CpCg.columns = zone_list


col1, col2 = st.columns([0.6,0.4])
with col1:
    st.markdown('**กรณีที่ 1:** ทิศทางการพัดของลมโดยทั่วไปอยู่ในแนว**ตั้งฉาก**กับสันหลังคา')
    col1x, buff = st.columns([0.5,0.5])
    with col1x:
        img_show('CpCg_case1.png')
        
    st.dataframe(df_CpCg, hide_index=True, use_container_width=True)
    with st.expander('See table'):
        st.dataframe(df_case1, hide_index=True, use_container_width=True)
    
col1, col2 = st.columns([0.6,0.4])
with col1:
    st.markdown('**กรณีที่ 2:** ทิศทางการพัดของลมโดยทั่วไปอยู่ในแนว**ขนาน**กับสันหลังคา')
    col1x, buff = st.columns([0.5,0.5])
    with col1x:
        img_show('CpCg_case2.png')
    with st.expander('See table'):
        st.dataframe(df_case2, hide_index=True, use_container_width=True)
    
st.markdown(r'### การคำนวณแรงลม')
with st.expander('information'):
    I= st.number_input(label='I',min_value=0.75,max_value=1.15, step=0.1)
    g = st.number_input(label='q',min_value=0.0,max_value=1000000.00,step=0.1)
    Cpi1 = st.number_input(label='cpi+',min_value=-2.0,max_value=5.0, step=0.1)
    Cpi2= st.number_input(label='cpi-',min_value=-2.0,max_value=5.0, step=0.1)
st.markdown(r' **คำนวณแรงลมภายนอกอาคาร**')

col1, col2 = st.columns([0.5,0.5])
with col1:
    st.markdown('calculation case1')
with col2:
    with st.expander('### แรงกระทำตั้งฉาก'):
        st.markdown('### case1 ตั้งฉาก')
      
      
        P =   float(I) * float(q) * df_CpCg.loc[[0],['1','1E','2','2E','3','3E','4','4E',]] * Ce
        st.write('pnet','=',P)
     
        
    df_Pw = pd.DataFrame() 
col1, col2 = st.columns([0.5,0.5])
with col1:  
        st.markdown('calculation case2')
with col2:
    with st.expander('### แรงกระทำขนาน'):
        st.markdown('### case2 ขนาน')
   
      
        P1 = float(I) *float(q) * df_case2.loc[[0],['1','1E','2','2E','3','3E','4','4E','5','5E','6','6E']] * Ce
        st.write('pNet','=',P1)
    df_Pw = pd.DataFrame() 


st.markdown(r'**คำนวณแรงลมภายในอาคาร**')
col1, col2 = st.columns([0.5,0.5])
with col1:
    st.markdown('calculation แนวตั้งฉาก')
with col2:
    with st.expander('แรงลมกระทำเป็นบวก'):
        st.markdown('### case1 เป็นบวก')
        P2 = float(I) *float(q) *(df_CpCg.loc[[0],['1','1E','2','2E','3','3E','4','4E',]]-(2*Cpi1)) * Ce
        st.write('pNet','=',P2)
    with st.expander('แรงลมกระทำค่าเป็นลบ'):
        st.markdown('### case1 เป็นลบ')
        P6 = float(I) * float(q)*(df_CpCg.loc[[0],['1','1E','2','2E','3','3E','4','4E']]-(2*Cpi2)) * Ce
        st.write('Pnet','=',P6)   
    df_Pw = pd.DataFrame() 

col1, col2 = st.columns([0.5,0.5])
with col1:
    st.markdown('calculation แนวขนาน')
with col2:
    with st.expander('แรงลมกระทำค่าเป็นบวก'):
        st.markdown('### case2 เป็นบวก')
        
        
    
        P3 = float(I)* float(q)* (df_case2.loc[[0],['1','1E','2','2E','3','3E','4','4E','5','5E','6','6E',]]-(2*Cpi1))  * Ce
        st.write('pNet','=',P3)
    
    with st.expander('แรงลมกระทำค่าเป็นลบ'):
        st.markdown('### case2 เป็นลบ')
       
        P5 = float(I) *   float(q)*(df_case2.loc[[0],['1','1E','2','2E','3','3E','4','4E','5','5E','6','6E']]-(2*Cpi2)) * Ce
        st.write('pNet','=',P5)
        df_Pw = pd.DataFrame() 
