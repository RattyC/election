db.vote_transactions.aggregate([
    {
        $match: {
            // สมมติ lookup station_ids ในเขต X มาแล้ว หรือมี field นี้
            "payload.constituency_id": 1,
            "ballot_type": "constituency",
            "integrity_status": "ACCEPTED"
        }
    },
    { $sort: { station_id: 1, sequence_no: -1 } },
    {
        $group: {
            _id: "$station_id",
            latest_payload: { $first: "$payload" }
        }
    },
    { $unwind: "$latest_payload.results" },
    {
        $group: {
            _id: "$latest_payload.results.candidate_id",
            total_votes: { $sum: "$latest_payload.results.score" }
        }
    },
    { $sort: { total_votes: -1 } }
])