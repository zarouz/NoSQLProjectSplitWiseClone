import sys
import traceback

# Add the backend to the Python path
sys.path.append('backend')

from backend.app import app
from backend.models.expense import Expense
from backend.models.group import Group
from backend.models.user import User

# --- PASTE YOUR UUIDs FROM POSTMAN HERE ---
TEST_GROUP_ID = "bc254c57-1560-4a2f-8017-d29e6b91c635"
TEST_PAYER_ID = "6a4decd1-e7e6-4b7c-a072-79213303c52f" # Alice
TEST_PARTICIPANT_IDS = [
    "6a4decd1-e7e6-4b7c-a072-79213303c52f", # Alice
    "4a61112b-7c26-4ffb-aac3-511ebfc2863b", # Bob
    "9fc7b7c9-b32f-4f48-8c75-482a77d2d6d3"  # Carol
]
# -------------------------------------------

print("--- Starting Expense Debug Script ---")

# We must run this inside the Flask app context
# so that get_db() works
with app.app_context():
    try:
        print(f"Group ID: {TEST_GROUP_ID}")
        print(f"Payer ID: {TEST_PAYER_ID}")
        print(f"Participant IDs: {TEST_PARTICIPANT_IDS}")
        
        print("\n--- Pre-flight Checks ---")
        
        # 1. Check if payer (Alice) is a member
        is_payer_member = Group.is_member(TEST_GROUP_ID, TEST_PAYER_ID)
        print(f"Is Payer (Alice) a member? ... {is_payer_member}")
        
        # 2. Check if all participants are members
        for i, user_id in enumerate(TEST_PARTICIPANT_IDS):
            is_p_member = Group.is_member(TEST_GROUP_ID, user_id)
            print(f"Is Participant {i+1} ({user_id}) a member? ... {is_p_member}")
            
        if not is_payer_member or not all(Group.is_member(TEST_GROUP_ID, pid) for pid in TEST_PARTICIPANT_IDS):
             print("\nERROR: Not all users are members of the group. Stopping.")
             sys.exit()

        print("\n--- Attempting Expense.create ---")
        
        expense = Expense.create(
            description="Debug Test: Hotel Booking",
            amount=9000.0,
            group_id=TEST_GROUP_ID,
            paid_by_id=TEST_PAYER_ID,
            participant_ids=TEST_PARTICIPANT_IDS
        )
        
        if expense:
            print(f"\n--- SUCCESS ---")
            print(f"Created expense: {expense}")
        else:
            print(f"\n--- FAILURE ---")
            print("Expense.create returned None or False.")

    except Exception as e:
        print(f"\n--- SCRIPT CRASHED ---")
        print(f"An exception occurred: {e}")
        traceback.print_exc()

print("\n--- Debug Script Finished ---")