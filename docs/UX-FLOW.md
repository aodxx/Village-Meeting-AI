# UX Flow — Village Meeting AI

## Design Direction

**Modern Civic / Community**

- Mobile-first
- Light UI
- Card-based interface
- Rounded corners
- Large Thai text
- Large touch targets
- One primary action per screen
- Low cognitive load while meeting is in progress

## Navigation

Bottom navigation has only 3 items:

1. หน้าแรก
2. การประชุม
3. ตั้งค่า

The main `เริ่มการประชุมใหม่` CTA lives on Home instead of the bottom navigation.

## Screen 1 — Home

Purpose: start a new meeting quickly and resume unfinished work.

Show:

- App / village name
- Large `เริ่มการประชุมใหม่` button
- Recent meetings
- Unfinished report cards
- Processing status cards

## Screen 2 — Create Meeting

Fields:

- ชื่อการประชุม
- วันที่
- เวลา
- สถานที่
- ประเภทการประชุม
- วาระ (optional)

Transcription mode:

- ถอดเสียงสด
- ถอดหลังประชุม

Primary CTA: `เริ่มการประชุม`

## Screen 3 — Agenda

User can:

- add agenda
- edit
- delete
- reorder
- skip

If skipped, AI may propose agendas after transcription.

## Screen 4 — Recording

Keep the screen minimal.

Show:

- Meeting title
- Recording indicator
- Timer
- Waveform/audio level
- Latest live transcript when enabled

Primary controls:

- Pause/Resume
- ⭐ สำคัญ
- จบประชุม

## Important Marker Interaction

One tap only.

After tap show temporary confirmation:

`⭐ บันทึกช่วงสำคัญแล้ว 00:38:24`

Do not open a form or interrupt the meeting.

## Screen 5 — End Confirmation

Show recording duration and ask for confirmation.

Actions:

- กลับไปประชุม
- จบและประมวลผล

## Screen 6 — Processing

Show step-by-step status:

- อัปโหลดเสียง
- ถอดเสียง
- แยกผู้พูด
- วิเคราะห์วาระ
- วิเคราะห์ประเด็นสำคัญ
- ตรวจหามติ
- วิเคราะห์เรื่องติดตาม
- สร้างร่างรายงาน

User may leave this screen. Processing continues from persisted backend job state; the user does not need to keep this screen open. The UI should show that batch transcription can take time and provide refresh/retry states rather than suggesting that the job is complete immediately.

For `LIVE` mode, the text shown during recording is a preview. After the meeting ends, the system runs post-meeting transcription again; the resulting speaker-separated transcript is the authoritative input for AI analysis and the report flow.

## Screen 7 — Transcript

Display transcript as speaker blocks:

- ผู้พูด 1
- ผู้พูด 2
- ผู้พูด 3

Each block includes timestamp.

The transcript screen shows normalized generic labels only (`ผู้พูด 1`, `ผู้พูด 2`, ...). It must not imply that a label is a verified person identity. A live preview may be replaced by the authoritative post-meeting transcript after processing completes.

Segments around important markers receive a visible ⭐ indicator.

## Screen 8 — AI Review

Group results by agenda.

Each agenda card shows:

- AI summary
- discussion summary
- possible resolution
- follow-up items

Possible resolution actions:

- ยืนยันมติ
- แก้ไข
- ไม่ใช่มติ

This is the primary human-in-the-loop checkpoint.

## Screen 9 — Follow-up Items

Each item shows:

- เรื่องที่ต้องทำ
- รายละเอียด
- ผู้รับผิดชอบ
- กำหนดเวลา if found

If unknown, display `ยังไม่ระบุ` rather than inferred information.

## Screen 10 — Draft Report

Editable sections:

- ข้อมูลการประชุม
- ระเบียบวาระ
- สาระสำคัญ
- รายละเอียดการหารือ
- มติที่ยืนยันแล้ว
- เรื่องที่ต้องดำเนินการ

Primary CTA: `ยืนยันรายงานฉบับจริง`

## Screen 11 — Final Report

After finalization:

- ดูรายงาน
- สร้าง/ดาวน์โหลด PDF
- เผยแพร่
- แชร์
- จัดการไฟล์เสียง

Audio deletion remains an explicit user action after system checks pass.

## Screen 12 — Publish Preview

Show exactly what the public will see.

Primary CTA: `เผยแพร่รายงาน`

After publish show:

- Copy public link
- Share
- Download PDF

## Public Report

No login required.

Show:

- Meeting title
- Date/time/location
- Full final report
- Confirmed resolutions
- Follow-up information included in the final report

Actions:

- ดาวน์โหลด PDF
- แชร์รายงาน

No edit and no comment in V1.

## Meeting History

Search only by:

- meeting title
- date

Cards show status:

- กำลังประมวลผล
- รอตรวจรายงาน
- ร่างรายงาน
- รายงานฉบับจริง
- เผยแพร่แล้ว

## Meeting Detail

Tabs:

1. รายงาน
2. Transcript
3. มติ
4. ไฟล์

## Settings

Village:

- ชื่อหมู่บ้าน
- ตำบล
- อำเภอ
- จังหวัด

Meeting:

- default meeting type
- default transcription mode

Document:

- A4
- Modern + Formal

## UX Guardrails

1. Do not require typing during active recording.
2. Never hide recording state.
3. Ending a meeting requires confirmation.
4. AI-detected resolutions are never final automatically.
5. Audio deletion requires explicit confirmation and backend eligibility checks.
6. Public view must never expose editing controls or internal system metadata.
