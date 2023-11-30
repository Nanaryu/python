def how_close(correct, sample): 
    distance = 0
    for c, s in zip(correct, sample):
        if c != s:
            distance += 1
    return distance
for _ in range(int(input())): 
    dict_len, words_len = map(int, input().split())
    dct = dict()
    for i in range(dict_len):
        word = input()
        length = len(word)
        if length in dct.keys(): 
            dct[length].append(word)
        else:
            dct[length] = [word]
answer = []
for i in range(words_len):
    word = input()
    best_match = len(word)
    for correct_word in dct[len(word)]:
        dist = how_close(correct_word, word)
        if dist < best_match:
            best_match = dist
            best_word = correct_word
    answer.append(best_word)
for word in answer:
    print(word)