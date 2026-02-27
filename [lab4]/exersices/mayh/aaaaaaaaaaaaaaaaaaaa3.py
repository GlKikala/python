import math
sides,length = map(int,input().split())

print(sides*length**2 / 4*math.tan(math.pi/sides))