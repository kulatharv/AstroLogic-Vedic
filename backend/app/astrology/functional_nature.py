def classify_functional_nature(lagna_sign, house_lords):

    nature = {}

    for house, data in house_lords.items():

        lord = data["lord"]

        # Trine houses (1, 5, 9) = benefic
        if house in [1, 5, 9]:
            nature[lord] = "Functional Benefic"

        # Dusthana houses (6, 8, 12) = malefic
        elif house in [6, 8, 12]:
            nature[lord] = "Functional Malefic"

        # Maraka houses (2, 7)
        elif house in [2, 7]:
            nature[lord] = "Maraka"

        # Upachaya (3, 10, 11)
        elif house in [3, 10, 11]:
            if lord not in nature:
                nature[lord] = "Neutral / Growth-Oriented"

        else:
            if lord not in nature:
                nature[lord] = "Neutral"

    return nature
