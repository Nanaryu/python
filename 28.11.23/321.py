def caesar(tx, key, encode=True):
    tx = list(tx)
    final_str = ""
    if key == 12:
        for letter in tx:
            if encode:
                if letter == " ":
                    final_str += letter
                else:
                    final_str += chr(ord(letter) + 2)
            else:
                if letter == " ":
                    final_str += letter
                else:
                    final_str += chr(ord(letter) - 2)
        return final_str
    else:
        return "Odmowa dostępu."

inr = open("inc.txt","r",encoding="utf-8")

outr = open("outc.txt","w",encoding="utf-8")

encordec = input("Encode or decode?\n")
eodresponse = True

if encordec == "encode":
    eodresponse = True
elif encordec == "decode":
    eodresponse = False
key = int(input("Key: "))

outr.write(caesar(inr.read(), key, encode=eodresponse))

outr.close()