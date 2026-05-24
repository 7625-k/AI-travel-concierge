def calculate_budget(days, hotel, food, transport):

    total = (
        (days * hotel)
        + (days * food)
        + transport
    )

    return total