import os, json
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
        doc_ref = db.collection("sneakerReleases").document(doc_id)
        batch.set(doc_ref, item)
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
