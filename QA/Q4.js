db.vote_submissions.aggregate([
    { $match: { province: "Bangkok", ballot_type: "party_list" } }, // หรือ constituency
    { $sort: { station_id: 1, timestamp: -1 } },
    {
        $group: {
        _id: "$station_id",
        latest_results: { $first: "$results" }
        }
    },
    { $unwind: "$latest_results" },
    {
        $group: {
        _id: "$latest_results.party_id",
        total_votes: { $sum: "$latest_results.score" }
        }
    }
])