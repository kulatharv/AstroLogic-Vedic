def activated_houses(chart):

    current_dasha = chart["dasha"]["current_mahadasha"]
    house_lords = chart["house_lords"]
    planets = chart["planets_by_house"]

    activated = []

    # 1️⃣ Houses ruled by Mahadasha lord
    for house, data in house_lords.items():
        if data["lord"] == current_dasha:
            activated.append(house)

    # 2️⃣ House where Mahadasha planet is placed
    for house, planet_list in planets.items():
        for p in planet_list:
            if p["planet"] == current_dasha:
                activated.append(house)

    # Remove duplicates
    activated = list(set(activated))

    return activated
