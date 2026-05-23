# app.py
import os
import streamlit as st
from google import genai
from google.genai.errors import APIError
from rag_engine import RAGEngine

# บน HuggingFace เราจะดึงคีย์ผ่านระบบ Secret ของเซิร์ฟเวอร์โดยตรง
api_key_val = os.environ.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL = "gemini-1.5-flash"

@st.cache_resource
def load_rag():
    return RAGEngine("knowledge/milklab_kb.txt")

rag = load_rag()

st.title("🥛 Demi ผู้ช่วย AI ของ MilkLab°")
st.caption("ถามเรื่องเมนู เวลาเปิด หรือข้อมูลร้านได้เลย")

if not api_key_val:
    st.error("❌ ไม่พบ API Key กรุณาตั้งค่า GOOGLE_API_KEY ในหน้า Settings > Variables and secrets ของ HuggingFace ก่อนนะคะ")
    st.stop()

client = genai.Client(api_key=api_key_val)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("ถามอะไรเกี่ยวกับร้านได้เลย..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    context_chunks = rag.search(prompt, top_k=3)
    context = "\n---\n".join(context_chunks)

    full_prompt = f"""คุณคือ Demi ผู้ช่วย AI ของร้าน MilkLab° ตอบเฉพาะจากข้อมูลด้านล่าง
ถ้าไม่พบข้อมูล ให้บอกว่าไม่ทราบ อย่าแต่งข้อมูลเองเด็ดขาด

ข้อมูลร้าน:
{context}

คำถาม: {prompt}"""

    try:
        response = client.models.generate_content(model=MODEL, contents=full_prompt)
        answer = response.text
    except APIError as e:
        answer = f"❌ เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ Google: {e.message}"
    except Exception as e:
        answer = f"❌ เกิดข้อผิดพลาด: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)