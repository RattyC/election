import pymongo
from faker import Faker
import random
import hashlib
import json
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Config
DB_URI = "mongodb://localhost:27017/"
DB_NAME = "election_2026_secure"
client = pymongo.MongoClient(DB_URI)
db = client[DB_NAME]
fake = Faker('th_TH')

# Reset DB
db.drop_collection("polling_stations")
db.drop_collection("vote_transactions")
db.drop_collection("parties")
db.drop_collection("candidates")

print("Generating Secure Data...")

# 1. Helper Functions for Security
def calculate_hash(data):
    """SHA-256 Hashing"""
    encoded = json.dumps(data, sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()

# 2. Setup Master Data (Parties, Candidates) - (ย่อส่วนเพื่อความกระชับ)
parties = [{"_id": i, "name": f"พรรค {fake.company()}"} for i in range(1, 58)]
db.parties.insert_many(parties)
candidates = [] # (สมมติว่าสร้างแล้วตามโจทย์เดิม)

# 3. Create Polling Stations (with Security Keys)
stations = []
station_ids = []
for i in range(50000): # 50,000 stations
    s_id = f"S{i:05d}"
    stations.append({
        "_id": s_id,
        "province": random.choice(["Bangkok", "Chiang Mai", "Phuket"]),
        "constituency_id": random.randint(1, 400),
        "total_eligible_voters": 1000, # Fixed eligible per station
        "station_public_key": f"PUB_KEY_{s_id}", 
        "last_transaction_hash": "GENESIS_HASH",
        "current_sequence": 0
    })
    station_ids.append(s_id)
    if len(stations) >= 5000:
        db.polling_stations.insert_many(stations)
        stations = []
if stations: db.polling_stations.insert_many(stations)

# 4. Generate Secure Vote Transactions
transactions = []
target_stations = random.sample(station_ids, 20000) # 20,000 active stations

for s_id in target_stations:
    # แต่ละหน่วยส่งผล 1-3 ครั้ง (มีการแก้คะแนน)
    num_txns = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]
    prev_hash = "GENESIS_HASH"
    
    for seq in range(1, num_txns + 1):
        # จำลองคะแนน
        turnout = random.randint(500, 900) # ไม่เกิน eligible (1000)
        
        # Chance of Fraud (บัตรเขย่ง)
        is_fraud = random.random() < 0.01 # 1% fraud
        ballots = turnout + 5 if is_fraud else turnout 
        
        payload = {
            "voter_turnout": turnout,
            "total_ballots": ballots,
            "results": [{"id": p["_id"], "score": int(ballots/10)} for p in parties[:5]], # Simplified
            "stats": {"good": ballots-10, "bad": 5, "no_vote": 5}
        }
        
        # Integrity Check
        status = "ACCEPTED"
        if ballots > turnout or turnout > 1000:
            status = "REJECTED" # ระบบ Block อัตโนมัติ

        # Cryptographic Process
        data_hash = calculate_hash(payload)
        
        txn = {
            "station_id": s_id,
            "ballot_type": "party_list",
            "sequence_no": seq,
            "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(1, 120)),
            "payload": payload,
            "integrity_status": status,
            "prev_hash": prev_hash,
            "data_hash": data_hash,
            "reporter_signature": f"SIG_{s_id}_{seq}"
        }
        transactions.append(txn)
        prev_hash = data_hash # Link hash for next sequence

    if len(transactions) >= 5000:
        db.vote_transactions.insert_many(transactions)
        transactions = []

if transactions: db.vote_transactions.insert_many(transactions)
print("Finished Secure Data Generation.")