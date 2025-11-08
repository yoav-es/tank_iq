from app.models import FuelEntry
from app.database import init_db, insert_entry, update_entry, delete_entry
# main.py


def get_entry_input():
    """
    Collects user input for a new or updated fuel entry.
    """
    date = input("Date (YYYY\MM\DD): ")
    liters = float(input("Liters filled: "))
    price = float(input("Price per liter: "))
    distance = float(input("Distance driven since last refuel (km): "))
    notes = input("Notes (optional): ")
    return FuelEntry(date, liters, price, distance, notes)


def main():
    """
    Main CLI loop for interacting with the fuel entry database.
    """
    init_db()
    print("📘 TankIQ Fuel Logger")

    while True:
        print("\nChoose an action:")
        print("1. Insert new entry")
        print("2. Update existing entry")
        print("3. Delete entry")
        print("4. Exit")

        choice = input("Enter choice (1–4): ")

        if choice == "1":
            entry = get_entry_input()
            insert_entry(entry)
            print(f"✅ Entry saved. Total cost: {entry.total_cost}, Consumption: {entry.fuel_consumption} L/100km")

        elif choice == "2":
            entry_id = int(input("Enter ID of entry to update: "))
            updated_entry = get_entry_input()
            update_entry(entry_id, updated_entry)
            print("🔄 Entry updated.")

        elif choice == "3":
            entry_id = int(input("Enter ID of entry to delete: "))
            delete_entry(entry_id)
            print("🗑️ Entry deleted.")

        elif choice == "4":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1–4.")


if __name__ == "__main__":
    main()