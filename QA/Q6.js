//submission ล่าสุดของหน่วยเลือกตั้ง Y (ต่อ ballotType)
// หาแบบ Party List ล่าสุด
db.vote_transactions.createIndex(
    { station_id: 1, ballot_type: 1, sequence_no: -1 },
    { name: "idx_station_lookup" }
    );
db.vote_transactions.find({ 
    station_id: "S00001",          
    ballot_type: "constituency"    
})
.sort({ sequence_no: -1 })         
.limit(1)                          

