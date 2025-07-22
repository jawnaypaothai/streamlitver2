import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf

# โหลดโมเดล (ต้องมีโมเดล .h5 ที่ฝึกไว้ล่วงหน้า)
@st.cache_resource
def load_model():
    return tf.keras.models.load_model('diabetic_wound_cnn_model.h5')

model = load_model()

# ฟังก์ชันแปลงภาพ
def preprocess_image(image):
    image = image.resize((224, 224))  # ขึ้นกับโมเดล
    image = np.array(image) / 255.0
    return np.expand_dims(image, axis=0)

# UI
st.title("🦶 ระบบวินิจฉัยแผลเบาหวานเบื้องต้นจากภาพ")
uploaded_file = st.file_uploader("📸 อัปโหลดภาพแผล", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="ภาพที่อัปโหลด", use_column_width=True)

    if st.button("วินิจฉัยแผล"):
        processed_image = preprocess_image(image)
        prediction = model.predict(processed_image)[0]

        # สมมุติ label = [เริ่มต้น, ปานกลาง, รุนแรง]
        labels = ['เริ่มต้น', 'ปานกลาง', 'รุนแรง']
        predicted_label = labels[np.argmax(prediction)]

        st.subheader(f"📊 ระดับแผล: {predicted_label}")
        st.write("🔢 ความมั่นใจ: {:.2f}%".format(np.max(prediction) * 100))

        if predicted_label == 'รุนแรง':
            st.error("❗ ควรรีบพบแพทย์ทันที")
        elif predicted_label == 'ปานกลาง':
            st.warning("⚠️ ควรดูแลอย่างใกล้ชิด และหมั่นล้างแผล")
        else:
            st.success("✅ เบื้องต้นปลอดภัย ดูแลความสะอาดสม่ำเสมอ")

