//Q5: ประวัติการส่งผลของหน่วยเลือกตั้ง Y (Audit Trail)
//ต้องการดูทุก version ที่ส่งมา เรียงตามเวลา

db.vote_submissions.find({ 
    station_id: "BKK-Z1-U001" 
})
.sort({ timestamp: -1 })
.projection({ timestamp: 1, ballot_type: 1, stats: 1, reporter_id: 1 })


//plan: IXSCAN (Index Scan) บน { station_id: 1, ... }
//totalKeysExamined: เท่ากับจำนวนครั้งที่หน่วยนี้ส่ง (เช่น 2-3 ครั้ง)