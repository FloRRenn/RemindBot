from ultils.db_action import Database

db = Database("emotion")

for _ in range(4):
  print(db.get_random({"type": "happy"}))