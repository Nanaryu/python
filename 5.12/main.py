import re
from traceback import print_exc
input_file = open("in.txt", "r", encoding="utf-8")
input_data = input_file.read()
input_data = re.sub(r"[^a-zA-Z\n ąćśńłóężź]+", "", input_data)
input_data = input_data.split(" ")
dict_append = open("dict.txt", "a", encoding="utf-8")
dict_read = open("dict.txt", "r", encoding="utf-8")
dict_write = open("dict.txt", "w", encoding="utf-8")
word_count = {}
try:
    dict_read_data = dict_read.read()
    dict_read_data = dict_read_data.split("\n")
    if len(dict_read_data) > 1:
        for line in dict_read_data:
            word_amount = line.split(": ") 
            if word_amount[0] in word_count:
                word_count[word_amount[0]] += int(word_amount[1])
            else:
                word_count[word_amount[0]] = int(word_amount[1]) + 1
                
        not_in_dict = set(input_data) - set(dict_read_data)
        not_in_dict = set(not_in_dict)

        for word in not_in_dict:
            if len(word) > 1:
                word_count[word] = 1

        total_str = f""
        for word in word_count:
            total_str += f"{word.lower()}: {word_count[word]}\n"
        print(total_str)
        dict_write.write(total_str)
    else:
        for word in input_data:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

        input_only_unique = set(input_data)
        for word in input_only_unique:
            if len(word) > 1:
                word_count[word] = 1
        total_str = f""
        for word in word_count:
            total_str += f"{word.lower()}: {word_count[word]}\n"
        print(dict_read.read())
        dict_write.write(total_str)
    '''
    if dict_read.read() == "":
        for word in input_data:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

        input_only_unique = set(input_data)
        for word in input_only_unique:
            if len(word) > 1:
                word_count[word] = 1
        total_str = f""
        for word in word_count:
            total_str += f"{word.lower()}: {word_count[word]}\n"
        print(dict_read.read())
        dict_write.write(total_str)
    else:
        dict_read_data = dict_read.read()
        dict_read_data = dict_read_data.split("\n")
        for line in dict_read_data:
            word_amount = line.split(": ") 
            if word_amount[0] in word_count:
                word_count[word_amount[0]] += int(word_amount[1])
            else:
                word_count[word_amount[0]] = int(word_amount[1]) + 1
                
        not_in_dict = set(input_data) - set(dict_read_data)
        not_in_dict = set(not_in_dict)

        for word in not_in_dict:
            if len(word) > 1:
                word_count[word] = 1

        total_str = f""
        for word in word_count:
            total_str += f"{word.lower()}: {word_count[word]}\n"
        print(total_str)
        dict_write.write(total_str)
    '''
except Exception as e:
    print(f"ERROR: {e}")
    print_exc()
finally:
    dict_write.close()