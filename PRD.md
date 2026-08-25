# PRD — Village Meeting AI

**Version:** 1.0  
**Status:** Ready for Technical Foundation  
**Primary Platform:** Mobile-first PWA  
**Primary Language:** Thai  
**Timezone:** Asia/Bangkok

## 1. Product Vision

Village Meeting AI คือเว็บแอปสำหรับช่วยผู้รับผิดชอบบันทึกการประชุมหมู่บ้าน ตั้งแต่เริ่มประชุมจนได้รายงานฉบับสมบูรณ์พร้อมเผยแพร่

เปลี่ยนกระบวนการ:

`อัดเสียง → ฟังย้อนหลัง → จดเอง → สรุปเอง → พิมพ์รายงาน → ทำ PDF → ส่งให้ชาวบ้าน`

เป็น:

`บันทึกเสียง → AI ถอดเสียง → AI แบ่งวาระ → AI สรุป → ตรวจสอบมติ → ตรวจรายงาน → PDF → เผยแพร่`

เป้าหมายคือ ลดภาระการทำรายงานหลังประชุม โดยยังให้มนุษย์ตรวจสอบข้อมูลสำคัญก่อนเผยแพร่

## 2. Users

### ผู้บันทึกการประชุม

สามารถสร้างการประชุม เพิ่มวาระ บันทึกเสียง ทำเครื่องหมายช่วงสำคัญ ตรวจ Transcript ตรวจผล AI ยืนยัน/แก้ไขมติ แก้ร่างรายงาน ยืนยัน Final Report สร้าง PDF เผยแพร่รายงาน และลบไฟล์เสียงเมื่อกระบวนการสำเร็จ

### ชาวบ้าน / บุคคลทั่วไป

ไม่ต้อง Login สามารถเปิด Public Report อ่านรายงานฉบับเต็ม ดาวน์โหลด PDF และแชร์ลิงก์ได้ แต่แก้ไขไม่ได้

## 3. Meeting Types

รองรับอย่างน้อย:

- ประชุมประจำเดือนหมู่บ้าน
- ประชุมคณะกรรมการ
- ประชาคมหมู่บ้าน
- ประชุมโครงการ
- ประชุมร่วมกับ อบต.
- ประชุมร่วมกับหน่วยงานราชการ
- ประชุมกับหน่วยงานภายนอก
- อื่น ๆ

## 4. Core Workflow

```text
Home
 → สร้างการประชุม
 → เพิ่มวาระ (ถ้ามี)
 → เลือกโหมดถอดเสียง
 → เริ่มบันทึก
 → ทำเครื่องหมายช่วงสำคัญ
 → จบประชุม
 → ถอดเสียง
 → AI วิเคราะห์
 → แบ่งวาระ
 → สรุปแต่ละวาระ
 → เสนอมติที่เป็นไปได้
 → วิเคราะห์เรื่องที่ต้องดำเนินการ
 → ผู้บันทึก Review
 → สร้าง Draft Report
 → แก้ไข
 → ยืนยัน Final Report
 → สร้าง PDF
 → เผยแพร่
 → ผู้ใช้ยืนยันลบไฟล์เสียง
```

## 5. Screens

V1 ประกอบด้วย:

1. Home
2. Create Meeting
3. Agenda
4. Recording
5. End Meeting Confirmation
6. Processing
7. Transcript
8. AI Review
9. Follow-up Items
10. Draft Report
11. Final Report
12. Publish
13. Public Report
14. Meeting History
15. Meeting Detail
16. Settings

รายละเอียด UX ดู `docs/UX-FLOW.md`

## 6. Create Meeting

Required fields:

- Title
- Meeting Date
- Start Time
- Location
- Meeting Type

Optional:

- Agenda

Transcription Mode:

- Live transcription
- Post-meeting transcription

## 7. Recording

ต้องแสดง:

- ชื่อการประชุม
- Recording status
- Duration
- Audio level/waveform
- Live transcript ถ้าเปิดใช้งาน

Controls:

- Pause / Resume
- Important Marker
- End Meeting

Important Marker ต้องเก็บ timestamp และ Meeting ID เพื่อให้ AI ให้น้ำหนักบริเวณนั้นในการวิเคราะห์

## 8. Processing Pipeline

แสดงสถานะอย่างน้อย:

- Upload audio
- Prepare audio
- Transcribe
- Speaker separation
- Agenda analysis
- Important point analysis
- Resolution detection
- Follow-up detection
- Draft report generation

ผู้ใช้สามารถออกจากหน้า Processing ได้ โดยสถาปัตยกรรมต้องไม่พึ่งการเปิดหน้าเดิมค้างไว้เมื่อระบบ backend รองรับ

## 9. Transcript

Transcript ต้องแบ่งผู้พูดเป็น:

- ผู้พูด 1
- ผู้พูด 2
- ผู้พูด 3
- ...

V1 ไม่ต้องระบุชื่อจริงจากเสียง

แต่ละ segment ต้องเก็บเวลา และแสดง Important Marker ในช่วงที่เกี่ยวข้อง

## 10. AI Analysis

AI ต้องสร้าง Structured Data สำหรับ:

- Agenda
- Summary
- Discussion
- Possible Resolutions
- Follow-up Items
- Responsible Party
- Due Date ถ้ามี
- Important Topics

กฎสำคัญ:

- ห้ามสร้างข้อมูลที่ไม่มีหลักฐานใน Transcript
- ถ้าไม่ทราบ ให้คืน `null` หรือ `ยังไม่ระบุ`
- Resolution เป็นเพียงข้อเสนอจนกว่ามนุษย์จะยืนยัน

## 11. Agenda Detection

ถ้ามี Agenda ล่วงหน้า AI ต้องพยายามจับคู่ Transcript กับ Agenda เดิม

ถ้าไม่มี AI สามารถเสนอ Agenda จากหัวข้อที่สนทนาได้

## 12. Resolution Detection

AI เสนอ “มติที่เป็นไปได้” เท่านั้น

ผู้บันทึกเลือก:

- ยืนยัน
- แก้ไข
- ไม่ใช่มติ

เฉพาะมติที่ยืนยันแล้วเท่านั้นที่เข้า Final Report

## 13. Follow-up Detection

AI ตรวจหา:

- เรื่องที่ต้องทำ
- รายละเอียด
- ผู้รับผิดชอบ
- Due Date ถ้ามี

ถ้าไม่มีหลักฐานเรื่องผู้รับผิดชอบหรือกำหนดเวลา ต้องไม่เดา

## 14. Draft & Final Report

Draft Report ประกอบด้วย:

- ข้อมูลการประชุม
- ระเบียบวาระ
- สาระสำคัญ
- รายละเอียดการหารือ
- มติที่ยืนยันแล้ว
- เรื่องที่ต้องดำเนินการ

ผู้บันทึกแก้ไขได้ทั้งหมดก่อน Final

เมื่อกด `ยืนยันรายงานฉบับจริง` ระบบสร้าง Snapshot และเปลี่ยนสถานะเป็น `FINAL`

## 15. PDF

สร้าง PDF A4 ในแนว Modern + Formal

ต้องอ่านง่ายทั้งมือถือ Desktop และกระดาษพิมพ์

ประกอบด้วย:

- ชื่อรายงาน
- ชื่อการประชุม
- วันที่ เวลา สถานที่
- Agenda
- Summary/Discussion
- Confirmed Resolution
- Follow-up
- Page number
- Generated date

## 16. Publishing

Final Report สามารถเผยแพร่เป็น Public Page และสร้าง Public URL

ผู้เข้าชมไม่ต้อง Login สามารถ:

- อ่านรายงานฉบับเต็ม
- ดาวน์โหลด PDF
- แชร์ URL

ไม่สามารถแก้ไขหรือ Comment ใน V1

## 17. Audio Lifecycle

```text
Recording
 → Upload
 → Transcription
 → AI Processing
 → Human Review
 → Final Report
 → User confirms deletion
 → Delete audio
```

ระบบต้องไม่อนุญาตให้ลบเสียงก่อน Transcript, AI Processing และ Final Report สำเร็จ

## 18. Meeting Status

ใช้สถานะ:

- `DRAFT`
- `RECORDING`
- `PROCESSING`
- `REVIEW_REQUIRED`
- `REPORT_DRAFT`
- `FINAL`
- `PUBLISHED`

## 19. Meeting History

V1 ค้นหาได้จาก:

- ชื่อการประชุม
- วันที่

ยังไม่ทำ Semantic Search แต่ Data Model ต้องไม่ปิดทางการเพิ่มในอนาคต

## 20. Settings

### Village Information
- ชื่อหมู่บ้าน
- ตำบล
- อำเภอ
- จังหวัด

### Meeting
- Default transcription mode
- Default meeting type

### AI
- Language: Thai

### Document
- PDF A4

## 21. UX Principles

- Mobile First
- One Primary Action per screen
- Large touch targets
- Thai-first UI
- Low cognitive load ระหว่างประชุม
- Modern Civic / Community visual direction

## 22. Recommended V1 Architecture

- Frontend: Mobile-first PWA
- Backend/API: Google Apps Script Web App
- AI: Gemini API
- Speech-to-Text: isolated service adapter
- Database: Google Sheets
- Storage: Google Drive

## 23. Non-Goals V1

ยังไม่ทำ:

- เช็กชื่อผู้เข้าประชุม
- Member account สำหรับชาวบ้าน
- OTP
- Online voting
- Voice identity
- Face recognition
- AI Search
- AI Chat
- Comment
- Full task management
- Multi-step approval workflow
- LINE Login
- Native Android/iOS

## 24. Future Extensions

- AI Meeting Search
- Ask Meeting AI
- Resolution Tracker
- Village Project Tracker
- LINE Integration
- Meeting Statistics

## 25. Definition of Done — V1

- [ ] สร้างการประชุม
- [ ] เพิ่ม Agenda
- [ ] บันทึกเสียง
- [ ] Pause/Resume
- [ ] Mark ช่วงสำคัญ
- [ ] จบการประชุม
- [ ] ถอดเสียงภาษาไทย
- [ ] แยก Speaker
- [ ] AI แบ่ง Agenda
- [ ] AI สรุปแต่ละ Agenda
- [ ] AI เสนอมติ
- [ ] ผู้ใช้ยืนยัน/แก้มติ
- [ ] AI สร้าง Follow-up
- [ ] สร้าง Draft Report
- [ ] แก้รายงาน
- [ ] Finalize Report
- [ ] สร้าง PDF
- [ ] Public Report
- [ ] ดาวน์โหลด PDF
- [ ] แชร์ Public URL
- [ ] ลบ Audio หลัง Final
- [ ] ประวัติการประชุม
- [ ] ค้นหาจากชื่อและวันที่

## 26. Product Principle

> AI มีหน้าที่ช่วยฟัง ช่วยจัดระเบียบ และช่วยร่าง แต่ข้อมูลสำคัญ เช่น มติและรายงานฉบับจริง ต้องผ่านการตรวจของมนุษย์ก่อนเผยแพร่
