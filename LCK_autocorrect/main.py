n = int(input())

for _ in range(n):
    d_w = input()
    d_w.split(" ")
    d = d_w[0]
    w = d_w[2]
    dic = []
    mis = []
    for i in range(int(d)):
        dic.append(input())
    for i in range(int(w)):
        mis.append(input())
    for word in mis: # word in misspelled
        hindexw = []
        for corword in dic: # correct word in dictionary
            hamming = 0
            ct = list(corword) # single letters of correct word
            wt = list(word) # single letters of word
            lct = len(ct)
            lwt = len(wt)
            max_len = max(lct, lwt)

            if lct < max_len:
                ct.extend([''] * (max_len - lct))
            elif lwt < max_len:
                wt.extend([''] * (max_len - lwt))

            if lct > lwt:
                for i, val in enumerate(wt):
                    if val != ct[i]:
                        hamming += 1
            else:
                for i, val in enumerate(ct):
                    if val != wt[i]:
                        hamming += 1
            hindexw.append(hamming)
        print(hindexw, dic[hindexw.index(min(hindexw))])

'''input
1 
3 5
computer
mouse
program
konpuder
house
compoooo
anagram
oeifeln
'''
'''output
computer
mouse
computer
program
mouse <---- SHOULD BE program
'''
#help