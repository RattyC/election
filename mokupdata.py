import pymongo
from faker import Faker
import random
import hashlib
import json
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
import os

# Config
DB_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "election_2026_secure"
client = pymongo.MongoClient(DB_URI)
db = client[DB_NAME]
fake = Faker('th_TH')

db.drop_collection("polling_stations")
db.drop_collection("vote_transactions")
db.drop_collection("parties")
db.drop_collection("candidates") 

print("Generating Secure Data...")

# 1. Helper Functions
def calculate_hash(data):
    """SHA-256 Hashing for Integrity Check"""
    encoded = json.dumps(data, sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()

# 2. Master Data: Parties & Candidates (เติมให้ครบตามโจทย์)
parties = [{"_id": i, "name": f"พรรค {fake.company()}"} for i in range(1, 58)]
db.parties.insert_many(parties)
print(f"✅ Generated {len(parties)} Parties")

# สร้าง Candidate จำลอง (สมมติเขตละ 10 คน * 400 เขต = 4000 คน)
candidates = []
for i in range(1, 4001):
    candidates.append({
        "_id": i,
        "name": fake.name(),
        "party_id": random.choice(parties)["_id"],
        "constituency_id": (i % 400) + 1,
        "candidate_no": random.randint(1, 20)
    })
db.candidates.insert_many(candidates)
print(f"✅ Generated {len(candidates)} Candidates")

# 3. Polling Stations
stations = []
station_ids = []
for i in range(50000): 
    s_id = f"S{i:05d}"
    stations.append({
        "_id": s_id,
        "province": random.choice(["Bangkok", "Chiang Mai", "Phuket", "Khon Kaen"]),
        "constituency_id": random.randint(1, 400),
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
print("✅ Generated Polling Stations")

# 4. Generate Secure Vote Transactions
transactions = []
target_stations = random.sample(station_ids, 20000) 

for s_id in target_stations:
    # แต่ละหน่วยส่งผล 1-3 ครั้ง (Sequence)
    num_txns = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]
    
    # ต้องแยก Chain สำหรับ Party List และ Constituency หรือรวมกันก็ได้ 
    # ในที่นี้สมมติส่งแยก Transaction กัน แต่ใช้ Sequence ต่อเนื่องกัน
    prev_hash = "GENESIS_HASH"
    current_seq = 0
    
    for _ in range(num_txns):
        current_seq += 1
        
        # สุ่มว่าจะส่งบัตรประเภทไหน (หรือส่งทั้งคู่)
        b_type = random.choice(["party_list", "constituency"])
        
        # จำลองตัวเลข
        turnout = random.randint(500, 900)
        
        # Fraud Logic (บัตรเขย่ง)
        is_fraud = random.random() < 0.01 
        ballots = turnout + 5 if is_fraud else turnout 
        
        # Math Logic: เกลี่ยคะแนนให้ผลรวมตรงกับบัตรดี
        bad_votes = random.randint(0, 20)
        no_votes = random.randint(0, 20)
        good_votes = ballots - bad_votes - no_votes
        
        # สร้าง Results ตามประเภทบัตร
        results_data = []
        if b_type == "party_list":
            # สุ่ม 5 พรรค แบ่งคะแนนกัน
            chosen_parties = random.sample(parties, 5)
            # แบ่งคะแนนแบบสุ่มให้รวมได้ good_votes
            points = sorted([random.randint(0, good_votes) for _ in range(4)])
            scores = [points[0]] + [points[i+1]-points[i] for i in range(3)] + [good_votes-points[3]]
            for idx, p in enumerate(chosen_parties):
                results_data.append({"id": p["_id"], "score": scores[idx]})
        else:
            # สุ่มผู้สมัครในเขต (สมมติ ID มั่วๆ เพื่อความเร็ว หรือดึงจริงก็ได้)
            # เพื่อความง่าย ใช้ ID 1-10
            cands = [{"id": x, "score": 0} for x in range(1, 6)]
            # แบ่งคะแนนเหมือนด้านบน
            points = sorted([random.randint(0, good_votes) for _ in range(4)])
            scores = [points[0]] + [points[i+1]-points[i] for i in range(3)] + [good_votes-points[3]]
            for idx, c in enumerate(cands):
                c["score"] = scores[idx]
            results_data = cands

        payload = {
            "voter_turnout": turnout,
            "total_ballots": ballots,
            "results": results_data,
            "stats": {"good": good_votes, "bad": bad_votes, "no_vote": no_votes}
        }
        
        # Integrity Check
        status = "ACCEPTED"
        if ballots > turnout or turnout > 1000:
            status = "REJECTED"

        # Cryptographic Process
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
print("✅ Finished Secure Data Generation.")