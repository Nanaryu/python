def gen_pesel(birth_date, gender):
    year = birth_date[0:4]
    month = birth_date[4:6]
    day = birth_date[6:8]

    months = {
        '01': 31,
        '02': 28,
        '03': 31,
        '04': 30,
        '05': 31,
        '06': 30,
        '07': 31,
        '08': 31,
        '09': 30,
        '10': 31,
        '11': 30,
        '12': 31
    }

    centuries = {
        '18': 80,
        '19': 0,
        '20': 20,
        '21': 40,
        '22': 60
    }

    if not (1799 < int(year) < 2300) or not (1 <= int(month) <= 12) or not (1 <= int(day) <= months[month]):
        raise ValueError("Invalid date")

    if gender not in ('K', 'M'):
        raise ValueError("Invalid gender")

    pesels = []

    month = int(month) + centuries[year[0:2]]

    for random_number in range(0, 10000):
        date_part = f"{int(year) % 100:02d}{int(month):02d}{int(day):02d}" # 02 minimum , d is int

        if gender == 'K':
            gender_part = str(random_number + (random_number % 2))
        else:
            gender_part = str(random_number + (1 - (random_number % 2)))

        pesel_nocontrol = date_part + gender_part

        multis = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 1]
        control = sum(int(digit) * weight for digit, weight in zip(pesel_nocontrol, multis))

        pesel = pesel_nocontrol + str((10 - (control % 10)) % 10)
        
        if len(pesel) == 11:
            pesels.append(pesel)

    return pesels

birth_date = "20070620"
gender = "M"

pesel_list = gen_pesel(birth_date, gender)

print(pesel_list)
