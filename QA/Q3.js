//Q3: ความคืบหน้าการรายงานผล (Reporting Progress)
//นับจำนวนหน่วยที่ไม่ซ้ำกัน (Distinct Station) ที่ส่งข้อมูลเข้ามาแล้ว เทียบกับจำนวนหน่วยทั้งหมด

// 1. หาจำนวนหน่วยทั้งหมด (Total Stations)
// db.polling_stations.countDocuments({})

// 2. หาจำนวนหน่วยที่รายงานแล้ว (Reported Stations) แยกตามประเภทบัตร
db.vote_transactions.aggregate([
    { $match: { integrity_status: "ACCEPTED" } },
    { $group: { _id: "$station_id" } }, // นับ Distinct Stations
    { $count: "reported_stations_count" }
])
 //ใช้ Index { ballot_type: 1 } 