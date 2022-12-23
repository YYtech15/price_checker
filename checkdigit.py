import re

number = re.compile(r"\d{8,13}")
def check_code(item_code: str):
    item_code = item_code.replace("-", "")
    if not number.match(item_code):
        return False
    if len(item_code) == 10:
        return check_ISBN(item_code)
    elif len(item_code) in [13, 8]:
        return check_JAN(item_code)


def check_JAN(jan_code: str):
    length = len(jan_code)
    if length == 8:
        jan_code = "00000"+jan_code
        length = len(jan_code)
    if length == 13:
        even = 0
        odd = 0
        for i in range(1, 12, 2):
            even += int(jan_code[i])
        even *= 3
        for i in range(0, 12, 2):
            odd += int(jan_code[i])
        result = (odd+even) % 10
        if str(10-result) == jan_code[12] or str(result) == jan_code[12]:
            return True
        else:
            return False


def check_ISBN(isbn_code: str):
    result = 0
    print(isbn_code)
    for i in range(0, 10):
        result += int(isbn_code[i])*(10-i)
    if result % 11 == 0:
        return True
    else:
        return check_JAN("978"+isbn_code)


if __name__ == "__main__":
    print(check_code(input("8,10,13桁のJANまたはISBNを入力してください。: ")))
