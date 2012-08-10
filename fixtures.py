import db

db.users_coll.drop()

db.create_user("dan", "none_yet")
db.create_user("sean", "none_yet")

print "Dan: %s" % (str(db.user_from_username("dan")["_id"]),)
print "Sean: %s" % (str(db.user_from_username("sean")["_id"]),)
