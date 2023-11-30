for _ in range(int(input())):
    data = input().split(":")
    name = data[0]
    scores = data[1].split(",")
    at_bats = 0
    singles = 0
    doubles = 0
    triples = 0
    homeruns = 0
    for score in scores:
        if score != "BB":
            if score == "K":
                at_bats += 1
            elif score == "1B":
                singles += 1
                at_bats += 1
            elif score == "2B":
                doubles += 1
                at_bats += 1
            elif score == "3B":
                triples += 1
                at_bats += 1
            elif score == "HR":
                homeruns += 1
                at_bats += 1
    if at_bats != 0:
        slg = ((singles)+(2*doubles)+(3*triples)+(4*homeruns))/at_bats
    else:
        slg = 0
    print(f'{name}={"{:.3f}".format(slg)}')