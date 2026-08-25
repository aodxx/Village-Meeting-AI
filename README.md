# Village Meeting AI

ระบบ AI สำหรับบันทึก ถอดเสียง สรุป และจัดทำรายงานการประชุมหมู่บ้าน ตั้งแต่เริ่มประชุมจนถึงเผยแพร่รายงานฉบับเต็มให้ชาวบ้านอ่านผ่านลิงก์สาธารณะ

## เป้าหมาย

เปลี่ยนกระบวนการเดิม:

`อัดเสียง → ฟังย้อนหลัง → จดเอง → สรุปเอง → พิมพ์รายงาน → ทำ PDF → ส่งต่อ`

เป็น:

`บันทึกเสียง → AI ถอดเสียง → แยกวาระ → สรุป → เสนอมติ → ตรวจรายงาน → PDF → เผยแพร่`

AI มีหน้าที่ช่วยฟัง ช่วยจัดระเบียบ และช่วยร่าง แต่ข้อมูลสำคัญ เช่น มติที่ประชุมและรายงานฉบับจริง ต้องผ่านการตรวจของมนุษย์ก่อนเผยแพร่

## ขอบเขต V1

- Mobile-first PWA
- สร้างการประชุมและวาระ
- บันทึกเสียง Pause/Resume
- เลือกถอดเสียงสดหรือหลังประชุม
- ทำเครื่องหมายช่วงสำคัญระหว่างประชุม
- Transcript ภาษาไทย แยกเป็น Speaker 1/2/3
- AI แบ่งวาระและสรุปสาระสำคัญ
- AI เสนอมติที่เป็นไปได้ โดยผู้บันทึกเป็นผู้ยืนยัน
- AI หาเรื่องที่ต้องติดตามและผู้รับผิดชอบเมื่อมีหลักฐานในบทสนทนา
- สร้าง/แก้ไข/ยืนยันรายงานการประชุม
- สร้าง PDF A4 แบบ Modern + Formal
- Public Report ไม่ต้อง Login
- ดาวน์โหลด PDF และแชร์ลิงก์
- ลบไฟล์เสียงหลัง Transcript + AI + Final Report สำเร็จและผู้ใช้ยืนยัน
- ประวัติการประชุมและค้นหาจากชื่อ/วันที่

## สถาปัตยกรรมตั้งต้น

- **Frontend:** Mobile-first PWA
- **Backend/API:** Google Apps Script Web App
- **AI:** Gemini API
- **Speech-to-Text:** Service Layer แยกจาก AI analysis เพื่อเปลี่ยน provider ได้ภายหลัง
- **Database:** Google Sheets
- **Storage:** Google Drive สำหรับไฟล์เสียงชั่วคราวและ PDF
- **Timezone:** Asia/Bangkok
- **Primary Language:** Thai

## เอกสารสำคัญ

- [`PRD.md`](PRD.md) — Product Requirements
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Technical Architecture
- [`docs/DATA-MODEL.md`](docs/DATA-MODEL.md) — Google Sheets/Data Model
- [`docs/API-CONTRACT.md`](docs/API-CONTRACT.md) — API Contract
- [`docs/UX-FLOW.md`](docs/UX-FLOW.md) — Screen & UX Flow
- [`ROADMAP.md`](ROADMAP.md) — แผนพัฒนาเป็น Phase
- [`PROGRESS.md`](PROGRESS.md) — สถานะปัจจุบันและ Next Step
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — แนวทางสำหรับนักพัฒนา
- [`AGENTS.md`](AGENTS.md) — กติกาสำหรับ AI Coding Agent

## สถานะปัจจุบัน

**Phase 0 — Product Foundation**

Product concept, UX architecture และ PRD V1 ถูกกำหนดแล้ว กำลังจัดเตรียม Technical Foundation ก่อนเริ่มเขียนโค้ดจริง

ดูสถานะล่าสุดที่ [`PROGRESS.md`](PROGRESS.md)

## หลักการสำคัญ

1. Human-in-the-loop สำหรับมติและ Final Report
2. AI ห้ามแต่งข้อมูลที่ไม่มีหลักฐานใน Transcript
3. Mobile-first และใช้งานระหว่างประชุมให้น้อยที่สุด
4. Public Report อ่านง่าย ไม่ต้องสมัครสมาชิก
5. ไฟล์เสียงเป็นข้อมูลชั่วคราว ไม่ใช่ฐานข้อมูลหลัก
6. โครงสร้างต้องพร้อมขยายไปสู่ AI Search, Resolution Tracker และ LINE Integration ในอนาคต
