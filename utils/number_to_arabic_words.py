import num2words

def number_to_arabic_words(number, currency_name="جنيهاً", sub_currency="قرشاً"):
    try:
        number = float(number)

        pounds = int(number)
        piastres = int(round((number - pounds) * 100))

        parts = []

        if pounds > 0:
            words_pounds = num2words.num2words(pounds, lang="ar")
            parts.append(f"{words_pounds} {currency_name}")

        if piastres > 0:
            words_piastres = num2words.num2words(piastres, lang="ar")
            parts.append(f"{words_piastres} {sub_currency}")

        if not parts:
            return f"صفر {currency_name}"

        return "مطلوب " + " و ".join(parts) + " لا غير"

    except:
        return ""