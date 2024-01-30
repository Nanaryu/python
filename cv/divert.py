import pydivert
from translator import translator

server_ips = {
    "na1": '67.205.136.38',  # na1
    "na2": '192.241.213.34',  # na2
    "na3": '165.227.116.252',  # na3
    'na4': '104.248.70.123',  # na4
    'na5': '192.241.185.164',  # na5
    'na6': '137.184.37.179',  # na6
    'eu1': '165.22.86.15',  # eu1
    'eu2': '167.71.8.250',  # eu2
    'eu3': '82.196.8.119',  # eu3
    'eu4': '188.166.7.70',  # eu4
    'eu5': '104.248.44.233',  # eu5
    'eu6': '164.90.174.224',  # eu6
    'a1': '128.199.66.110',  # a1
    'a2': '159.65.1.161',  # a2
    'a3': '128.199.239.146',  # a3
    'a4': '167.71.202.95',  # a4
    'sa1': '18.228.118.214',  # sa1
    'sa2': '18.231.13.50',  # sa2
    'sa3': '54.233.229.27',  # sa3
    'sa4': '52.67.162.81',  # sa4
    'sa5': '18.231.117.69',  # sa5
    'sa6': '54.207.112.163',  # sa6
    'sa7': '15.228.123.59',  # sa7
    'sa8': '15.228.63.38',  # sa8
}

current_server = server_ips['eu2']

pydivertargs = f"ip.DstAddr == {current_server} or ip.SrcAddr == {current_server} and tcp.PayloadLength > 0"

w = pydivert.WinDivert(pydivertargs)

with w:
    for packet in w:
        data = packet.payload.hex()
        if data:
            if packet.src_addr == current_server and data[2:4] == "3f":
                #data = translator(data, 'server')
                print(f"Server -> {data}")
            elif packet.dst_addr == current_server:
                data = translator(data, 'client')
                #print(f"Client -> {data}")
            w.send(packet)
            