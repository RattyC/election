//submission ล่าสุดของหน่วยเลือกตั้ง Y (ต่อ ballotType)
// หาแบบ Party List ล่าสุด
db.vote_submissions.find({ 
    station_id: "BKK-Z1-U001",
    ballot_type: "party_list"
})
.sort({ timestamp: -1 })
.limit(1)
.projection({ timestamp: 1, ballot_type: 1, stats: 1, reporter_id: 1 })

//plan: IXSCAN (Index Scan) บน { station_id: 1, ballot_type: 1, timestamp: -1 }
//totalKeysExamined: 1