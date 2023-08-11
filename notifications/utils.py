def change_for_whatsapp(number):
    return f"whatsapp:" + number


def parse_number(number):
    number = number.replace(" ", "")
    if number.startswith("+91"):
        number = number[3:]
    elif number.startswith("0"):
        number = number[1:]
    return number
