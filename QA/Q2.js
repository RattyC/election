db.vote_submissions.aggregate([
    { $match: { constituency_id: 1, ballot_type: "constituency" } },
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
        _id: "$latest_results.candidate_id",
        total_votes: { $sum: "$latest_results.score" }
        }
    },
    { $sort: { total_votes: -1 } },
    {
        $lookup: {
        from: "candidates",
        localField: "_id",
        foreignField: "_id",
        as: "candidate_info"
        }
    }
])
//ndex { constituency_id: 1, ballot_type: 1, timestamp: -1 } เท่ากับจำนวนผู้สมัครในเขต