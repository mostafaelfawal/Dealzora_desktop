def is_number(number):
    try:
        float(number)
        return True
    except:
        return False
