def calculate_aspects(house_data):

    aspect_result = {}

    for house, planets in house_data.items():

        for planet_info in planets:

            planet = planet_info["planet"]
            base_house = house

            aspect_houses = []

            # 7th aspect (all planets)
            seventh = ((base_house + 5) % 12) + 1
            aspect_houses.append(seventh)

            if planet == "Mars":
                aspect_houses.append(((base_house + 3) % 12) + 1)
                aspect_houses.append(((base_house + 7) % 12) + 1)

            elif planet == "Jupiter":
                aspect_houses.append(((base_house + 4) % 12) + 1)
                aspect_houses.append(((base_house + 8) % 12) + 1)

            elif planet == "Saturn":
                aspect_houses.append(((base_house + 2) % 12) + 1)
                aspect_houses.append(((base_house + 9) % 12) + 1)

            aspect_result[planet] = aspect_houses

    return aspect_result
