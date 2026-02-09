//Q5: ประวัติการส่งผลของหน่วยเลือกตั้ง Y (Audit Trail)
//ต้องการดูทุก version ที่ส่งมา เรียงตามเวลา
db.vote_transactions.createIndex(
    { station_id: 1, ballot_type: 1, sequence_no: -1 },
    { name: "idx_station_lookup" }
    );
db.vote_transactions.aggregate(
    { $match: { station_id: "S00001" } },
    { $sort: { sequence_no: 1 } },
    { $project: {
        sequence_no: 1, 
        ballot_type: 1,
        timestamp: 1, 
        "payload.stats": 1, 
        integrity_status: 1, 
        prev_hash: 1, 
    data_hash: 1 
}})
//plan: IXSCAN (Index Scan) บน { station_id: 1, ... }
//totalKeysExamined: เท่ากับจำนวนครั้งที่หน่วยนี้ส่ง (เช่น 2-3 ครั้ง)