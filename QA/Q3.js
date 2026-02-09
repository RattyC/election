//Q3: ความคืบหน้าการรายงานผล (Reporting Progress)
//นับจำนวนหน่วยที่ไม่ซ้ำกัน (Distinct Station) ที่ส่งข้อมูลเข้ามาแล้ว เทียบกับจำนวนหน่วยทั้งหมด

// 1. หาจำนวนหน่วยทั้งหมด (Total Stations)
// db.polling_stations.countDocuments({})

// 2. หาจำนวนหน่วยที่รายงานแล้ว (Reported Stations) แยกตามประเภทบัตร
db.vote_submissions.aggregate([
    {
        $group: {
        _id: "$ballot_type",
        reported_stations: { $addToSet: "$station_id" } // นับเฉพาะ Station ID ที่ไม่ซ้ำ
        }
    },
    {
        $project: {
        ballot_type: "$_id",
        count: { $size: "$reported_stations" }
        }
    }
])
 //ใช้ Index { ballot_type: 1 } 