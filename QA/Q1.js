db.vote_transactions.aggregate([
    { $match: { ballot_type: "party_list", integrity_status: "ACCEPTED" } },
    { $sort: { station_id: 1, sequence_no: -1 } },
    {
        $group: {
            _id: "$station_id", // เลือกเฉพาะ seq ล่าสุดของหน่วย
            latest_payload: { $first: "$payload" }
        }
    },
    { $unwind: "$latest_payload.results" },
    {
        $group: {
            _id: "$latest_payload.results.id",
            total_votes: { $sum: "$latest_payload.results.score" }
        }
    },
    { $sort: { total_votes: -1 } },
    { $limit: 10 },
    { $lookup: { from: "parties", localField: "_id", foreignField: "_id", as: "party_info" } }
])