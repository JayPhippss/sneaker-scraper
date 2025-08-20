import os, json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

def main(json_path):
    # 1. Load service account from env‐var
    sa_json = os.environ["FIREBASE_ADMIN"]
    sa_info = json.loads(sa_json)
    cred = credentials.Certificate(sa_info)
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    data = json.load(open(json_path, encoding="utf-8"))

    # 2. Write into a collection, e.g. "sneakerReleases"
    processed_items = []
    for item in data:
        doc_id = item.get("title")
        iso_date = item.get("release_date")
        if iso_date and len(iso_date) == 10:
            parsed_date = datetime.fromisoformat(iso_date)
        else:
            parsed_date = None

        doc_data = item.copy()
        if parsed_date:
            doc_data["release_date"] = parsed_date
        else:
            doc_data.pop("release_date", None)

        processed_items.append((doc_id, doc_data))

    old_refs = list(db.collection("sneakerReleases").list_documents())

    ops = []
    for ref in old_refs:
        ops.append(("delete", ref))
    for doc_id, doc_data in processed_items:
        ref = db.collection("sneakerReleases").document(doc_id)
        ops.append(("set", ref, doc_data))

    CHUNK_SIZE = 400
    total_deleted = len(old_refs)
    total_written = len(processed_items)

    for i in range(0, len(ops), CHUNK_SIZE):
        batch = db.batch()
        for op in ops[i : i + CHUNK_SIZE]:
            if op[0] == "delete":
                batch.delete(op[1])
            else:
                batch.set(op[1], op[2])
        batch.commit()

    print(f"✅ Replaced collection: deleted {total_deleted}, wrote {total_written}")

if __name__ == "__main__":
    import glob, sys
    # find the latest sneakers_*.json
    files = sorted(glob.glob("sneakers_*.json"))
    if not files:
        print("❌ No JSON file found to upload.")
        sys.exit(1)
    main(files[-1])
