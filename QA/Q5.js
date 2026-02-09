//Q5: ประวัติการส่งผลของหน่วยเลือกตั้ง Y (Audit Trail)
//ต้องการดูทุก version ที่ส่งมา เรียงตามเวลา

db.vote_transactions.find(
    { station_id: "S12345" },
    { sequence_no: 1, integrity_status: 1, prev_hash: 1, data_hash: 1, timestamp: 1 }
).sort({ sequence_no: 1 })

//plan: IXSCAN (Index Scan) บน { station_id: 1, ... }
//totalKeysExamined: เท่ากับจำนวนครั้งที่หน่วยนี้ส่ง (เช่น 2-3 ครั้ง)