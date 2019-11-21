import uuid
import collections

code_list = []
code_list_v2 = []

def randomcode(codelenght=10):
    random = str(uuid.uuid4())
    random = random.upper()
    return random[0:codelenght]

x = int(input('Hur många koder vill du ha?\n'))

for i in range(x):
    code_list.append(randomcode(7))

for code in code_list:
    if not code in code_list_v2:
        code_list_v2.append(code)

print(code_list_v2)

def your_code():
    for element in range(len(code_list_v2)):
        print('                                       Här är din kod: ', code_list_v2[element], '\n\n\n\n')

print(your_code)

file = open('code.txt', 'w')
file.write(str(code_list_v2))