def squares(a):
    for i in range (a+1):
        yield i**2

def evennumbers(b):
    for bob in range (0,b+1,2):
        yield bob

def divisible_by_3_and_4 (c):
    for k in range(c):
        l = k*12
        if l > c:
            break
        else:
            yield l
def squares_between_a_b(a,b):
    for i in range(a,b+1):
        yield i**2
def from_a_to_zero(kk):
    for au in range(kk, 0, -1):
        yield au
b,c = map(int, input().split())
for j in squares(b):
    print(j, end = " ")
print("\n")
for k in evennumbers(b):
    print(k, end = ",")
print("\n")
for l in divisible_by_3_and_4(b):
    print(l, end = " ")
print("\n")
for m in squares_between_a_b(b,c):
    print(m, end= " ")
print("\n")
for n in from_a_to_zero(b):
    print(n, end= " ")