import random as r

temporary_code_list = []
finnished_code_list = ["BEAR", "MINK", "SEAL", "KOKO", "GRIS", "HARE", "JOEY"]


def main():
    x = int(input("Hur många koder vill du ha?\n"))
    if x < 36 ** 4:
        for i in range(x - 7):
            temporary_code_list.append(generate_uuid())
        for code in temporary_code_list:
            if not code in finnished_code_list:
                finnished_code_list.append(code)
        file = open("finnished_codes.txt", "w")
        file.write(str(finnished_code_list))
        print(finnished_code_list)
    else:
        print("1 error")


def generate_uuid():
    random_string = ""
    random_str_seq = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    uuid_format = [4]
    for n in uuid_format:
        for i in range(0, n):
            random_string += str(random_str_seq[r.randint(0, len(random_str_seq) - 1)])
    return random_string


if __name__ == "__main__":
    main()
