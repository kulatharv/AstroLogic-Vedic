def detect_yogas(house_data):

    yogas = []

    # Gajakesari Yoga
    if "Jupiter" in [p["planet"] for h in house_data for p in house_data[h]]:
        for house, planets in house_data.items():
            for p in planets:
                if p["planet"] == "Moon":
                    moon_house = house

        for house, planets in house_data.items():
            for p in planets:
                if p["planet"] == "Jupiter":
                    jupiter_house = house

        if abs(moon_house - jupiter_house) in [0, 4, 7, 10]:
            yogas.append("Gajakesari Yoga")

    # Budh-Aditya Yoga
    for house, planets in house_data.items():
        planet_names = [p["planet"] for p in planets]
        if "Sun" in planet_names and "Mercury" in planet_names:
            yogas.append("Budh-Aditya Yoga")

    return yogas
