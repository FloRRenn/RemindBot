from ultils.db_action import Database

db = Database("reminder")

reminds_list = db.get_all({"type" : "reminder"})
documents_count = reminds_list.count()

print(documents_count)