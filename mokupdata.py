import pymongo
from faker import Faker
import random
import hashlib
import json
from datetime import datetime, timedelta, timezone
import os
from bson.objectid import ObjectId

# --- CONFIG ---
DB_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "election_2026_secure"
client = pymongo.MongoClient(DB_URI)
db = client[DB_NAME]
fake = Faker('th_TH')

# --- CLEANUP ---
print("Cleaning old data...")
db.drop_collection("polling_stations")
db.drop_collection("vote_transactions")
db.drop_collection("parties")
db.drop_collection("candidates_constituency") # ใช้ชื่อนี้ตาม Query
db.drop_collection("constituencies")

print("Generating Consistent Data...")

# Helper Function
def calculate_hash(data):
    encoded = json.dumps(data, sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()

# 1. PARTIES
parties = [{"_id": i, "name": f"พรรค {fake.company()}"} for i in range(1, 58)]
db.parties.insert_many(parties)
print(f"✅ Generated {len(parties)} Parties")

# 2. CONSTITUENCIES
constituencies = []
provinces = ["Bangkok", "Chiang Mai", "Khon Kaen", "Phuket", "Chonburi", "Nakhon Ratchasima"]
for i in range(1, 401):
    constituencies.append({
        "_id": i,
        "province": random.choice(provinces),
        "zone": (i % 10) + 1,
        "total_seats": 1
    })
db.constituencies.insert_many(constituencies)
print(f"✅ Generated {len(constituencies)} Constituencies")

# 3. CANDIDATES (สำคัญ: เก็บ ID ไว้ใช้งานต่อ)
candidates_list = []
candidates_by_constituency = {} # Map เก็บ candidates แยกตามเขต

# สร้างผู้สมัครเขตละ 10 คน
id_counter = 1
for const in constituencies:
    candidates_by_constituency[const["_id"]] = []
    
    for no in range(1, 11):
        c_doc = {
            "_id": id_counter, # ใช้ Integer ID เพื่อให้ง่ายและตรงกันแน่นอน
            "name": fake.name(),
            "party_id": random.choice(parties)["_id"],
            "constituency_id": const["_id"],
            "candidate_no": no
        }
        candidates_list.append(c_doc)
        candidates_by_constituency[const["_id"]].append(c_doc) # เก็บไว้สุ่มตอนทำ txn
        id_counter += 1
        
db.candidates_constituency.insert_many(candidates_list)
print(f"✅ Generated {len(candidates_list)} Candidates (IDs matched)")

# 4. POLLING STATIONS
stations = []
station_ids = []
for i in range(50000): 
    s_id = f"S{i:05d}"
    target_const = random.choice(constituencies) # สุ่มเขต
    
    stations.append({
        "_id": s_id,
        "province": target_const["province"],
        "constituency_id": target_const["_id"],
        "total_eligible_voters": 1000,
        "station_public_key": f"PUB_KEY_{s_id}",
        "last_transaction_hash": "GENESIS_HASH",
        "current_sequence": 0
    })
    station_ids.append(s_id)
    
    if len(stations) >= 5000:
        db.polling_stations.insert_many(stations)
        stations = []
if stations: db.polling_stations.insert_many(stations)
print(f"✅ Generated Polling Stations")

# 5. VOTE TRANSACTIONS
transactions = []
target_stations = random.sample(station_ids, 20000) 

# Cache Station Info เพื่อความเร็ว (ไม่ต้อง query db บ่อยๆ)
station_map = {s["_id"]: s for s in db.polling_stations.find({"_id": {"$in": target_stations}})}

print("Generating Transactions...")
for s_id in target_stations:
    s_info = station_map.get(s_id)
    if not s_info: continue
        
    num_txns = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]
    prev_hash = "GENESIS_HASH"
    current_seq = 0
    
    for _ in range(num_txns):
        current_seq += 1
        b_type = random.choice(["party_list", "constituency"])
        turnout = random.randint(500, 900)
        
        # Logic คะแนน
        is_fraud = random.random() < 0.01 
        ballots = turnout + 5 if is_fraud else turnout 
        bad_votes = random.randint(0, 20)
        no_votes = random.randint(0, 20)
        if ballots < (bad_votes + no_votes): ballots = bad_votes + no_votes + 10
        good_votes = ballots - bad_votes - no_votes
        
        results_data = []
        if b_type == "party_list":
            chosen_parties = random.sample(parties, 5)
            points = sorted([random.randint(0, good_votes) for _ in range(4)])
            scores = [points[0]] + [points[i+1]-points[i] for i in range(3)] + [good_votes-points[3]]
            for idx, p in enumerate(chosen_parties):
                results_data.append({"id": p["_id"], "score": scores[idx]})
                
        else: # Constituency
            # ดึงผู้สมัคร "จริงๆ" ของเขตนี้มาใช้ (แก้ปัญหา ID ไม่ตรง)
            real_candidates = candidates_by_constituency.get(s_info["constituency_id"], [])
            
            if real_candidates:
                # เลือกมา 5 คนจากเขตนั้น
                chosen_cands = random.sample(real_candidates, min(5, len(real_candidates)))
                points = sorted([random.randint(0, good_votes) for _ in range(len(chosen_cands)-1)])
                # Logic แบ่งคะแนน (simplified)
                if not points: points = [good_votes] 
                else:
                    scores = [points[0]] + [points[i+1]-points[i] for i in range(len(points)-1)] + [good_votes-points[-1]]
                    
                for idx, c in enumerate(chosen_cands):
                    # สำคัญ: ใช้ _id ของจริงจาก collection candidates
                    score_val = scores[idx] if idx < len(scores) else 0
                    results_data.append({"id": c["_id"], "score": score_val})

        payload = {
            "voter_turnout": turnout,
            "total_ballots": ballots,
            "results": results_data, # ตอนนี้ ID ตรงกับ Master Data แล้ว
            "stats": {"good": good_votes, "bad": bad_votes, "no_vote": no_votes}
        }
        
        status = "ACCEPTED"
        if ballots > turnout or turnout > 1000: status = "REJECTED"

        data_hash = calculate_hash(payload)
        txn = {
            "station_id": s_id,
            "ballot_type": b_type,
            "sequence_no": current_seq,
            "timestamp": datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 120)),
            "payload": payload,
            "integrity_status": status,
            "prev_hash": prev_hash,
            "data_hash": data_hash,
            "reporter_signature": f"SIG_{s_id}_{current_seq}"
        }
        transactions.append(txn)
        prev_hash = data_hash 

    if len(transactions) >= 5000:
        db.vote_transactions.insert_many(transactions)
        transactions = []

if transactions: db.vote_transactions.insert_many(transactions)
print("✅ Finished Consistent Data Generation.")