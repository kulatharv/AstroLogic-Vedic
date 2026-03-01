def detect_advanced_yogas(chart):

    yogas = []
    house_lords = chart["house_lords"]
    planets_by_house = chart["planets_by_house"]

    # Reverse map: planet → house
    planet_house = {}
    for house, plist in planets_by_house.items():
        for p in plist:
            planet_house[p["planet"]] = house

    # ------------------------
    # 1️⃣ Raj Yoga
    # Kendra (1,4,7,10) + Trikona (1,5,9)
    # ------------------------

    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]

    kendra_lords = [house_lords[h]["lord"] for h in kendra_houses]
    trikona_lords = [house_lords[h]["lord"] for h in trikona_houses]

    for kl in kendra_lords:
        if kl in trikona_lords:
            yogas.append("Raj Yoga")

    # ------------------------
    # 2️⃣ Dhana Yoga
    # 2nd and 11th lord connection
    # ------------------------

    second_lord = house_lords[2]["lord"]
    eleventh_lord = house_lords[11]["lord"]

    if planet_house.get(second_lord) == planet_house.get(eleventh_lord):
        yogas.append("Dhana Yoga")

    # ------------------------
    # 3️⃣ Gajakesari Yoga
    # Moon + Jupiter in Kendra
    # ------------------------

    if "Moon" in planet_house and "Jupiter" in planet_house:
        moon_house = planet_house["Moon"]
        jupiter_house = planet_house["Jupiter"]

        if abs(moon_house - jupiter_house) in [0, 3, 6, 9]:
            yogas.append("Gajakesari Yoga")

    # ------------------------
    # 4️⃣ Vipreet Raj Yoga
    # Dusthana lords in dusthana
    # ------------------------

    dusthana_houses = [6, 8, 12]

    for h in dusthana_houses:
        lord = house_lords[h]["lord"]
        if planet_house.get(lord) in dusthana_houses:
            yogas.append("Vipreet Raj Yoga")

    return list(set(yogas))
