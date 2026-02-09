db.vote_submissions.aggregate([
    { $match: { ballot_type: "party_list" } },
    { $sort: { station_id: 1, timestamp: -1 } }, // Sort เพื่อให้ document ล่าสุดอยู่บนสุดของแต่ละกลุ่ม
    {
        $group: {
        _id: "$station_id",
        latest_results: { $first: "$results" } // เลือกเฉพาะผลล่าสุดของหน่วยนี้
        }
    },
    { $unwind: "$latest_results" },
    {
        $group: {
        _id: "$latest_results.party_id",
        total_votes: { $sum: "$latest_results.score" }
        }
    },
    { $sort: { total_votes: -1 } },
    { $limit: 10 },
    {
        $lookup: {
        from: "parties",
        localField: "_id",
        foreignField: "_id",
        as: "party_info"
        }
    }
])