//Q3: ความคืบหน้าการรายงานผล (Reporting Progress)
//นับจำนวนหน่วยที่ไม่ซ้ำกัน (Distinct Station) ที่ส่งข้อมูลเข้ามาแล้ว เทียบกับจำนวนหน่วยทั้งหมด

db.vote_transactions.createIndex(
    { ballot_type: 1, integrity_status: 1, station_id: 1, sequence_no: -1 },
    { name: "idx_dashboard_agg" }
);
db.vote_transactions.aggregate([
    { $match: { integrity_status: "ACCEPTED" } },

    //  Group ตามประเภทบัตร และเก็บ station_id ใส่ Set (เพื่อไม่ให้นับซ้ำ)
    {
        $group: {
            _id: "$ballot_type",
            reported_stations: { $addToSet: "$station_id" }
        }
    },

    {
        $project: {
            ballot_type: "$_id",
            count: { $size: "$reported_stations" }
        }
    }
])
