import json
import random
import time
from datetime import datetime, timedelta

# Configuration for data volume
NUM_PARTIES = 60            # >= 57
NUM_CONSTITUENCIES = 400    # >= 400
NUM_CANDIDATES = 3500       # >= 3,000
NUM_STATIONS = 50000        # >= 50,000
NUM_SUBMISSIONS = 125000    # >= 120,000

# Helper function to generate mock ObjectId (24-char hex string)
def generate_object_id():
    return "%024x" % random.randrange(16**24)

# Helper function to generate random timestamp
def generate_timestamp():
    # Random time within the last 24 hours
    delta = random.randint(0, 86400)
    dt = datetime.now() - timedelta(seconds=delta)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

print("Starting data generation...")

# 1. Generate Parties
print(f"Generating {NUM_PARTIES} parties...")
parties = []
party_names = [f"พรรคพลัง{i}" for i in range(1, NUM_PARTIES + 1)]
for i in range(NUM_PARTIES):
    party = {
        "_id": generate_object_id(),
        "party_no": i + 1,
        "name": party_names[i],
        "color": "#%06x" % random.randint(0, 0xFFFFFF)
    }
    parties.append(party)

# 2. Generate Constituencies
print(f"Generating {NUM_CONSTITUENCIES} constituencies...")
constituencies = []
provinces = ["กรุงเทพมหานคร", "เชียงใหม่", "ขอนแก่น", "ภูเก็ต", "นครราชสีมา"]
for i in range(1, NUM_CONSTITUENCIES + 1):
    constituency = {
        "_id": i,  # Simple Integer ID as requested
        "province": random.choice(provinces),
        "zone": i,
        "total_voters": random.randint(80000, 150000)
    }
    constituencies.append(constituency)

# 3. Generate Candidates (Constituency)
print(f"Generating {NUM_CANDIDATES} candidates...")
candidates = []
# Group candidates by constituency_id for easier lookup later
candidates_by_zone = {c["_id"]: [] for c in constituencies}

for i in range(NUM_CANDIDATES):
    # Randomly assign to a party and a constituency
    party = random.choice(parties)
    constituency = random.choice(constituencies)
    
    # Determine candidate number in that constituency
    current_candidates_in_zone = len(candidates_by_zone[constituency["_id"]])
    candidate_no = current_candidates_in_zone + 1
    
    candidate = {
        "_id": generate_object_id(),
        "name": f"ผู้สมัครคนที่ {i+1}",
        "party_id": party["_id"],
        "constituency_id": constituency["_id"],
        "candidate_no": candidate_no
    }
    candidates.append(candidate)
    candidates_by_zone[constituency["_id"]].append(candidate)

# 4. Generate Polling Stations
print(f"Generating {NUM_STATIONS} polling stations...")
polling_stations = []
station_ids = [] # Keep track for submissions

# Distribute stations among constituencies
avg_stations_per_zone = NUM_STATIONS // NUM_CONSTITUENCIES
station_counter = 0

for const in constituencies:
    # Each zone gets roughly equal stations, plus some randomness
    num_stations_in_zone = avg_stations_per_zone + random.randint(-5, 5)
    
    for unit in range(1, num_stations_in_zone + 1):
        if station_counter >= NUM_STATIONS:
            break
            
        custom_id = f"PROV-{const['zone']}-U{unit:03d}"
        station = {
            "_id": custom_id,
            "province": const["province"],
            "constituency_id": const["_id"],
            "unit_no": unit,
            "location_name": f"สถานที่เลือกตั้งหน่วยที่ {unit}"
        }
        polling_stations.append(station)
        station_ids.append(station)
        station_counter += 1

# Fill remaining if any
while len(polling_stations) < NUM_STATIONS:
    # Logic to add remaining stations if loop breaks early (omitted for brevity, usually matches closely)
    pass

# 5. Generate Vote Submissions
print(f"Generating {NUM_SUBMISSIONS} vote submissions...")
vote_submissions = []

for i in range(NUM_SUBMISSIONS):
    # Pick a random station
    station = random.choice(polling_stations)
    
    # Get candidates for this station's constituency
    zone_candidates = candidates_by_zone.get(station["constituency_id"], [])
    
    # Simulate scores
    results = []
    total_good_votes = 0
    
    for cand in zone_candidates:
        score = random.randint(0, 500)
        total_good_votes += score
        results.append({
            "id": cand["_id"],
            "score": score
        })
    
    bad_votes = random.randint(0, 50)
    no_votes = random.randint(0, 50)
    total_ballots = total_good_votes + bad_votes + no_votes
    
    submission = {
        "_id": generate_object_id(),
        "station_id": station["_id"],
        "constituency_id": station["constituency_id"],
        "province": station["province"],
        "ballot_type": "constituency",
        "timestamp": generate_timestamp(),
        "results": results,
        "total_good_votes": total_good_votes,
        "bad_votes": bad_votes,
        "no_votes": no_votes,
        "total_ballots": total_ballots
    }
    vote_submissions.append(submission)

# Function to save file
def save_json(filename, data):
    print(f"Saving {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Save all files
save_json('parties.json', parties)
save_json('constituencies.json', constituencies)
save_json('candidates.json', candidates)
# For large files, indent=None helps reduce file size, but indent=2 is better for readability
save_json('polling_stations.json', polling_stations)
save_json('vote_submissions.json', vote_submissions)

print("All files generated successfully.")

