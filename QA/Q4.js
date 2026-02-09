db.vote_transactions.createIndex(
    { ballot_type: 1, integrity_status: 1, station_id: 1, sequence_no: -1 },
    { name: "idx_dashboard_agg" }
);
db.vote_transactions.aggregate([
    {
        $lookup: {
            from: "polling_stations",
            localField: "station_id",
            foreignField: "_id",
            as: "station_info"
        }
    },
    { $unwind: "$station_info" },

    {
        $match: {
            "station_info.province": "Bangkok",
            "ballot_type": "party_list",
            "integrity_status": "ACCEPTED"
        }
    },

    { $sort: { station_id: 1, sequence_no: -1 } },
    {
        $group: {
            _id: "$station_id",
            latest_doc: { $first: "$$ROOT" }
        }
    },
    { $unwind: "$latest_doc.payload.results" },
    {
        $group: {
            _id: "$latest_doc.payload.results.id", 
            total_votes: { $sum: "$latest_doc.payload.results.score" }
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