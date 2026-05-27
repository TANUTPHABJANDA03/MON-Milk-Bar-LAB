# 🥗 FitBite AI — Smart Order & Nutritionist Chatbot

ระบบสั่งซื้ออาหารคลีนอัจฉริยะและแชทบอทวิเคราะห์โภชนาการส่วนบุคคลสำหรับร้าน **FitBite** พัฒนาขึ้นด้วย Streamlit และขยายขีดความสามารถด้วยสถาปัตยกรรม RAG ร่วมกับ Gemini API พร้อมระบบจัดการข้อมูลหลังบ้านและแจ้งเตือนอัตโนมัติ (Google Sheets & Telegram) โดยออกแบบมาให้เสถียรและทำงานได้สมบูรณ์แบบบน **Hugging Face Spaces**

## 🚀 ฟีเจอร์เด่นของระบบ (Key Features)

- **Smart Order Form & Auto-Pricing:** ฟอร์มรับออเดอร์อาหารคลีนครบวงจร (ชื่อ, เบอร์โทร, เมนูหลัก, ท็อปปิ้งเสริม, รายการแพ้อาหาร, วันที่และรอบจัดส่ง, ที่อยู่โดยละเอียด) พร้อมระบบแกะตัวเลขและคำนวณราคารวมทั้งหมด (Total Price) ให้โดยอัตโนมัติ
- **Google Sheets Integration:** บันทึกข้อมูลออเดอร์ทั้งหมดรวมถึงราคารวมลงใน Google Sheets คอลัมน์ A ถึง J ทันทีผ่านระบบ Google Service Account
- **Hugging Face-Optimized Telegram Notification:** ระบบแจ้งเตือนออเดอร์ใหม่พร้อมสรุปยอดเงินเข้า Telegram ของหลังบ้านทันที โดยปรับแต่งการทำงานเป็นแบบ Synchronous และใช้งาน Proxy Multi-endpoints เพื่อป้องกันปัญหา Hugging Face สั่งฆ่า Thread กลางอากาศ (กันหลุด 100%)
- **AI Nutritionist Receipts (RAG System):** นำรายชื่อเมนูและท็อปปิ้งที่ลูกค้าสั่ง วิ่งไปจับคู่กับฐานข้อมูลดิบในคลังความรู้ร้านอาหาร แล้วส่งให้โมเดล `gemini-3.1-flash Lite ` เพื่อสร้างใบเสร็จ สรุปแคลอรี่ และสารอาหารหลัก (โปรตีน/คาร์บ/ไขมัน) ได้อย่างแม่นยำ ป้องกันการมโนข้อมูล (No Hallucination)
- **Customized UI (Locked Dark Theme):** ปรับแต่งหน้าตาด้วย CSS ชั้นสูง ล็อกหน้าจอให้อยู่ในธีมมืดสุดพรีเมียม แก้ไขปัญหาระบบของ Streamlit ที่ทำให้ตัวหนังสือสีขาวกลืนกับพื้นหลังในช่อง Dropdown, Tag และ Popover เรียบร้อยแล้ว

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

- `app.py` — ไฟล์หลักของโปรเจกต์ ควบคุมทั้งหน้าต่าง UI, ระบบคำนวณราคา, ระบบบันทึก Sheets/Telegram และการเชื่อมต่อกับระบบ AI
- `knowledge/fitbite_kb.txt` — คลังความรู้ (Knowledge Base) ที่เก็บโพยเมนูอาหาร, ราคา, และคุณค่าทางโภชนาการทั้งหมดของร้าน FitBite สำหรับระบบ RAG
- `requirements.txt` — รายชื่อไลบรารีที่ระบบต้องการ เช่น `streamlit`, `google-genai`, `gspread`, `requests`
- `.gitignore` — ใบสั่งห้ามอัปโหลด ป้องกันไม่ให้ไฟล์ความลับอย่าง `.env` หลุดขึ้นไปบน Repository สาธารณะ

## 🔑 การตั้งค่าคีย์ความลับ (Environment Variables & Secrets)

เพื่อความปลอดภัย ห้ามใส่ API Key หรือรหัสผ่านลงในโค้ดหลักเด็ดขาด ให้ทำการตั้งค่าผ่านช่องทาง **Variables and Secrets** บนหน้าเว็บ Hugging Face Spaces (หรือสร้างไฟล์ `.env` หากรันบนเครื่อง Local) ดังนี้:

| ชื่อ Key | รายละเอียดข้อมูล |
| :--- | :--- |
| `GOOGLE_API_KEY` | คีย์สำหรับเรียกใช้งาน Google Gemini API |
| `TELEGRAM_BOT_TOKEN` | โทเค่นที่ได้จาก BotFather สำหรับเปิดใช้บอท Telegram |
| `TELEGRAM_CHAT_ID` | ID ของกลุ่มหรือแชทส่วนตัวที่ต้องการให้แจ้งเตือนออเดอร์เด้งเข้า |
| `GOOGLE_SHEETS_ID` | ID ของไฟล์ Google Sheets หลังบ้านที่ต้องการบันทึกออเดอร์ |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | อีเมลของ Service Account ที่ได้รับสิทธิ์ให้เข้าถึง Sheets |
| `GOOGLE_PRIVATE_KEY` | รหัส Private Key ของ Service Account (รองรับการแปลงเครื่องหมาย `\n`) |

## 🛠️ วิธีการรันใช้งานในเครื่องคอมพิวเตอร์ (Local Development)

1. ติดตั้ง Python (แนะนำเวอร์ชัน 3.11 ขึ้นไป)
2. ติดตั้งแพ็กเกจที่จำเป็นทั้งหมดผ่าน Terminal:
   ```bash
   pip install -r requirements.txt
