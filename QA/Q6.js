//submission ล่าสุดของหน่วยเลือกตั้ง Y (ต่อ ballotType)
// หาแบบ Party List ล่าสุด
db.vote_transactions.find(
    { station_id: "S12345", ballot_type: "party_list", integrity_status: "ACCEPTED" }
)
.sort({ sequence_no: -1 })
.limit(1)

//plan: IXSCAN (Index Scan) บน { station_id: 1, ballot_type: 1, timestamp: -1 }
//totalKeysExamined: 1