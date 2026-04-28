def basic_prediction(house_data, dasha_lord):

    predictions = []

    # Career
    if dasha_lord in ["Sun", "Saturn"]:
        predictions.append("Career-focused period.")

    # Marriage
    for house, planets in house_data.items():
        if house == 7:
            for p in planets:
                if p["planet"] in ["Venus", "Jupiter"]:
                    predictions.append("Favorable for relationships.")

    # Finance
    for house in [2, 11]:
        if house in house_data:
            predictions.append("Financial activity likely.")

    return predictions
