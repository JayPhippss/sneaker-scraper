import os, json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

def main(json_path):
    # 1. Load service account from env‐var
    sa_json = os.environ["FIREBASE_SERVICE_ACCOUNT"]
    sa_info = json.loads(sa_json)
    cred = credentials.Certificate(sa_info)
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    data = json.load(open(json_path, encoding="utf-8"))

    # 2. Write into a collection, e.g. "sneakerReleases"
    batch = db.batch()
    for item in data:
        # Use SKU or a firebase-generated ID
        doc_id = item.get("title")

        iso_date = item.get("release_date")
        if iso_date and len(iso_date) == 10:
            parsed_date = datetime.fromisoformat(iso_date)
        else:
            parsed_date = None

        doc_data = item.copy()
        doc_data["release_date"] = parsed_date

        doc_ref = db.collection("sneakerReleases").document(doc_id)
        batch.set(doc_ref, doc_data)
    
    batch.commit()

    print(f"✅ Uploaded {len(data)} documents to Firestore.")

if __name__ == "__main__":
    import glob, sys
    # find the latest sneakers_*.json
    files = sorted(glob.glob("sneakers_*.json"))
    if not files:
        print("❌ No JSON file found to upload.")
        sys.exit(1)
    main(files[-1])
