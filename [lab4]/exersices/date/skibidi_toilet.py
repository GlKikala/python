from datetime import date, timedelta, datetime

today = date.today()
for i in range (-2,3):
    print(today+timedelta(days=i))

print("\n")
for i in range (-1,2):
    print(today+timedelta(days=i))

print("\n")

print(datetime.now())


print("\n")

date1 = datetime(2026, 2, 20, 10, 30, 0)
date2 = datetime(2026, 2, 25, 12, 45, 30)
difference = date2 - date1
seconds = difference.total_seconds()
print(seconds)
