

a = 8
thing = 0
lista1 = [1,2,3,4,5,6,7,8,9,10]
lista2 = 0

while True:
    if thing == 0:
        if len(lista1[0:]) > a:
            thing -= 1
        else:
            print(lista1[0: thing])
            print(lista1[thing: ])
            break
    else:
        if len(lista1[0: thing]) > a:
            thing -= 1
        else:
            print(lista1[0: thing])
            print(lista1[thing: ])
            break

print(lista1[:])