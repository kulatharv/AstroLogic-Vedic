def calculate_dispositors(chart):

    house_lords = chart["house_lords"]
    planets_by_house = chart["planets_by_house"]

    dispositors = {}

    for house, planet_list in planets_by_house.items():

        for p in planet_list:

            planet = p["planet"]
            sign = p["sign"]

            # Find lord of that sign
            for h, data in house_lords.items():
                if data["sign"] == sign:
                    dispositor = data["lord"]
                    dispositors[planet] = dispositor
                    break

    return dispositors
