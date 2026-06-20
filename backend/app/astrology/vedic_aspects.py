def calculate_vedic_aspects(chart):

    planets_by_house = chart["planets_by_house"]

    aspects = {}

    for house, planet_list in planets_by_house.items():

        for p in planet_list:

            planet = p["planet"]

            # Base 7th aspect
            aspect_houses = [((house + 6) % 12) + 1]

            # Mars special
            if planet == "Mars":
                aspect_houses.append(((house + 3) % 12) + 1)
                aspect_houses.append(((house + 7) % 12) + 1)

            # Jupiter special
            if planet == "Jupiter":
                aspect_houses.append(((house + 4) % 12) + 1)
                aspect_houses.append(((house + 8) % 12) + 1)

            # Saturn special
            if planet == "Saturn":
                aspect_houses.append(((house + 2) % 12) + 1)
                aspect_houses.append(((house + 9) % 12) + 1)

            # Rahu/Ketu special (optional classical)
            if planet in ["Rahu", "Ketu"]:
                aspect_houses.append(((house + 4) % 12) + 1)
                aspect_houses.append(((house + 8) % 12) + 1)

            aspects[planet] = list(set(aspect_houses))

    return aspects
