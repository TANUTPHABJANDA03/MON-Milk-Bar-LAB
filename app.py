import streamlit as st
import os
import requests
import datetime
import time
import gspread
from google import genai
from google.genai import types

# ==================== UI SETUP & BRANDING ====================
st.set_page_config(page_title="FitBite AI - Smart Order", page_icon="🥗", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "order_summary" not in st.session_state:
    st.session_state.order_summary = None

st.markdown("""
    <style>
    .stApp { background-color: #0b0f12 !important; color: #ffffff !important; }
    .info-card { background-color: #161c20; padding: 12px; border-radius: 10px; border: 1px solid #2e7d32; text-align: center; margin-bottom: 10px; }
    h1, h2, h3, .stSubheader { color: #4caf50 !important; font-family: 'Kanit', sans-serif; }
    .stMarkdown, p, li { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID")

# ==================== FUNCTION: GOOGLE SHEETS CONNECTOR ====================
def save_to_sheets(data_list):
    try:
        creds_dict = {
            "type": "service_account",
            "project_id": "mon-milk-bar-ai", 
            "private_key": st.secrets["GOOGLE_PRIVATE_KEY"].replace('\\n', '\n'),
            "client_email": st.secrets["GOOGLE_SERVICE_ACCOUNT_EMAIL"],
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(st.secrets["GOOGLE_SHEETS_ID"])
        worksheet = sh.get_worksheet(0)
        worksheet.append_row(data_list)
        st.success("📝 บันทึกข้อมูลออเดอร์ลง Google Sheets เรียบร้อย!")
        return True
    except Exception as e:
        st.error(f"❌ บันทึกลง Sheets ไม่สำเร็จ: {e}")
        return False

# ==================== FUNCTION: TELEGRAM ALERT ====================
def send_to_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN.strip()}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID.strip(), "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=15)
    except Exception: pass

# ==================== FUNCTION: READ KNOWLEDGE BASE ====================
def get_knowledge_base():
    try:
        with open("knowledge/fitbite_kb.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "คลังข้อมูลโภชนาการร้าน FitBite"

# ==================== MAIN UI DISPLAY ====================
st.title("🥗 FitBite AI")
st.markdown("### *Personalized Nutritionist & Smart Form Order*")

col_time, col_deliv = st.columns(2)
with col_time: st.markdown("<div class='info-card'><span style='color: #4caf50;'>🕒 เปิดบริการทุกวัน</span><br>09:00 น. - 18:00 น.</div>", unsafe_allow_html=True)
with col_deliv: st.markdown("<div class='info-card'><span style='color: #ff9800;'>🛵 รอบจัดส่งเดลิเวอรี</span><br>11:00 | 14:00 | 17:00</div>", unsafe_allow_html=True)

st.subheader("📋 ฟอร์มสั่งซื้ออาหาร")
customer_name = st.text_input("👤 ชื่อลูกค้า:")
customer_phone = st.text_input("📞 เบอร์โทร:")

mains = [
    "1. สลัดอกไก่ย่างพริกไทยดำ (119.-)", 
    "2. ข้าวไรซ์เบอร์รี่ปลากระพงนึ่ง (149.-)", 
    "3. พาสต้าโฮลวีทซอสเพสโต้กุ้ง (159.-)",
    "4. สเต็กแซลมอนย่างเกลือพร้อมผักเคียง (199.-)",
    "5. ข้าวคีนัวผัดกะเพราอกไก่สับ (129.-)",
    "6. สลัดเต้าหู้ย่างซอสเทอริยากิ (99.-)"
]
selected_mains = st.multiselect("🥗 เมนูหลัก:", mains)

addons = [
    "เพิ่มอกไก่ย่าง (+40.-)", 
    "เพิ่มไข่ต้ม (+15.-)", 
    "เพิ่มอะโวคาโด (+35.-)",
    "เพิ่มไข่ดาวน้ำ (+15.-)",
    "เพิ่มแซลมอนย่าง (+70.-)",
    "เพิ่มฟักทองย่าง (+20.-)"
]
selected_addons = st.multiselect("➕ ท็อปปิ้งเสริม:", addons)

allergy = st.text_input("⚠️ อาหารที่แพ้ / ไม่กิน:")

tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
delivery_date = st.date_input(
    "📅 เลือกวันที่จัดส่ง (สั่งวันนี้รับวันพรุ่งนี้เป็นต้นไป):", 
    value=tomorrow_date, 
    min_value=tomorrow_date
)
delivery_date_str = delivery_date.strftime("%Y-%m-%d")

slot = st.selectbox("📦 รอบจัดส่ง:", ["รอบเช้า (11:00 น.)", "รอบบ่าย (14:00 น.)", "รอบเย็น (17:00 น.)"])
address = st.text_area("📍 ที่อยู่จัดส่งแบบละเอียด:")

if st.button("🛒 ยืนยันการสั่งซื้อ"):
    if not customer_name or not customer_phone or not selected_mains or not address:
        st.warning("กรุณากรอกข้อมูลสำคัญให้ครบถ้วนก่อนสั่งซื้อค่ะบอส!")
    else:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        addons_str = ", ".join(selected_addons) if selected_addons else "ไม่มี"
        allergy_str = allergy if allergy else "ไม่มี"
        
        # 🔍 [จุดแก้ไขสำคัญ] ย้าย delivery_date_str มาต่อท้ายสุดของแถว เพื่อให้บันทึกลงคอลัมน์ I ใน Google Sheets
        order_list = [
            current_time, customer_name, customer_phone,
            ", ".join(selected_mains), addons_str,
            allergy_str, slot, address, delivery_date_str
        ]
        
        save_to_sheets(order_list)
        
        tg_msg = (
            f"🚀 *มีออเดอร์ใหม่เข้าค่ะบอส!*\n\n"
            f"👤 *ลูกค้า:* {customer_name}\n"
            f"📞 *เบอร์:* {customer_phone}\n"
            f"🥗 *เมนูหลัก:* {', '.join(selected_mains)}\n"
            f"➕ *ท็อปปิ้ง:* {addons_str}\n"
            f"⚠️ *แพ้อาหาร:* {allergy_str}\n"
            f"📅 *วันที่จัดส่ง:* {delivery_date_str}\n"
            f"📦 *รอบจัดส่ง:* {slot}\n"
            f"📍 *ที่อยู่จัดส่ง:* {address}"
        )
        send_to_telegram(tg_msg)
        
        prompt_data = (
            f"สรุปรายการและโภชนาการด่วน: ลูกค้าชื่อ {customer_name} สั่งเมนูหลัก {', '.join(selected_mains)} "
            f"ท็อปปิ้ง {addons_str} แพ้อาหาร: {allergy_str}"
        )
        
        if GOOGLE_API_KEY:
            try:
                client = genai.Client(api_key=GOOGLE_API_KEY.strip())
                sys_inst = f"คุณคือ FitBite AI สรุปราคา คำนวณแคลอรี่ และสารอาหารหลัก (โปรตีน, คาร์บ, ไขมัน) เป็นกรัม จากคลังข้อมูลนี้เท่านั้น:\n{get_knowledge_base()}"
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_data,
                    config=types.GenerateContentConfig(system_instruction=sys_inst, temperature=0.2)
                )
                st.session_state.order_summary = res.text
            except Exception as e:
                err_text = str(e)
                if "429" in err_text or "RESOURCE_EXHAUSTED" in err_text:
                    st.session_state.order_summary = "⚠️ โควตา API รายวันของบัญชีฟรีหมดแล้วครับบอส! กรุณากดปุ่มสร้าง API Key อันใหม่ใน Google AI Studio มาเปลี่ยนในไฟล์ secrets นะครับ"
                else:
                    st.session_state.order_summary = f"❌ ระบบดึงข้อมูลขัดข้อง: {err_text}"
        else:
            st.session_state.order_summary = "❌ ไม่พบ GOOGLE_API_KEY ในระบบ"
            
        st.rerun()

# ==================== DISPLAY AREA ====================
st.markdown("---")

if st.session_state.order_summary:
    st.subheader("🧾 ใบเสร็จรับเงินและโภชนาการจาก AI")
    with st.chat_message("model"):
        st.markdown(st.session_state.order_summary)
    st.markdown("---")

if st.session_state.chat_history:
    st.subheader("💬 ห้องแชทสนทนากับหมอโภชนาการ FitBite")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

if user_chat := st.chat_input("พิมพ์พูดคุยสอบถามข้อมูลเมนูอาหารเพิ่มเติมได้ที่นี่..."):
    st.session_state.chat_history.append({"role": "user", "text": user_chat})
    
    if GOOGLE_API_KEY:
        try:
            client = genai.Client(api_key=GOOGLE_API_KEY.strip())
            sys_inst = f"คุณคือ FitBite AI ผู้ช่วยตอบคำถามโภชนาการและแนะนำเมนูอาหารให้กับลูกค้า อ้างอิงตามคลังข้อมูลร้าน:\n{get_knowledge_base()}"
            
            formatted_contents = []
            for m in st.session_state.chat_history:
                role_tag = "user" if m["role"] == "user" else "model"
                formatted_contents.append({"role": role_tag, "parts": [{"text": m["text"]}]})
                
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=formatted_contents,
                config=types.GenerateContentConfig(system_instruction=sys_inst, temperature=0.5)
            )
            st.session_state.chat_history.append({"role": "model", "text": res.text})
        except Exception as e:
            err_text = str(e)
            if "429" in err_text or "RESOURCE_EXHAUSTED" in err_text:
                st.session_state.chat_history.append({"role": "model", "text": "⚠️ โควตาการคุยของคีย์ฟรีหมดแล้วครับบอส ต้องสลับใช้คีย์ใหม่ใน AI Studio ครับ"})
            else:
                st.session_state.chat_history.append({"role": "model", "text": f"เกิดข้อผิดพลาด: {err_text}"})
    else:
        st.session_state.chat_history.append({"role": "model", "text": "❌ ไม่พบ GOOGLE_API_KEY ในระบบ"})
            
    st.rerun()
    # Ready for Demo Day 2026!
    # Sales Logger System Checked