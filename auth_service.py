# firestore_service.py
import firebase_admin
from firebase_admin import credentials, auth
from google.cloud import firestore
from google.oauth2 import service_account


# Load Firebase service account credentials
SERVICE_ACCOUNT_FILE = "firebase-adminsdk.json"
PROJECT_ID = "taskmanager-456507"  # Replace with your actual Firebase project ID

cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'projectId': PROJECT_ID
    })

# Export Firestore DB client using credentials
firestore_credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
db = firestore.Client(credentials=firestore_credentials, project=PROJECT_ID)

async def validate_firebase_token(id_token: str):
    try:
        if id_token:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
    return None
