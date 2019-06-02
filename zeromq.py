import zmq
import gzip

# from ctx import ctx
import codecs
from gzip import GzipFile
import gzip
from io import StringIO, BytesIO
import zlib
import xmltodict

# Socket to talk to server
import json
import xmltodict


from lxml import etree
from lxml import objectify
import pprint

pp = pprint.PrettyPrinter(indent=0)



context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect ("tcp://pubsub.besteffort.ndovloket.nl:7658")
socket.setsockopt_string(zmq.SUBSCRIBE, "/ARR/KV15messages")




# yeet = []
while True:
    message1 = socket.recv_multipart()
    address = message1[0]
    # contents = address.join(message1[1:])
    con = address.join(message1[1:])
    # print(address)
    # count = 0
    # for x in con:
    #     print(type(x))
    #     count += 1
    #    
    try: message = gzip.decompress(con)
    except OSError: pass
    # message = str(message,'utf-8-sig')
    # for x in message:
    #     print(x)
    # # message = message
    # # contents = GzipFile('','r',0,StringIO(con)).read()
    # parser = etree.XMLParser(ns_clean=True)
    
    # tree = etree.parse(BytesIO(message), parser)
    # root =  tree.getroot()

    # users = document.find('{http://bison.connekt.nl/tmi8/kv6/msg}KV6posinfo')
    # for node in users.getchildren():
    #     if node.tag == "{http://bison.connekt.nl/tmi8/kv6/msg}ONROUTE":
    #         for child in node.getchildren():
    #             if child.tag == '{http://bison.connekt.nl/tmi8/kv6/msg}vehiclenumber':
    #                 print(child.tag, child.attrib)


    pp.pprint(str(message,'utf-8-sig'))


    # vp = []
    # ch = []

    # for child in root.findall("{http://bison.connekt.nl/tmi8/kv6/msg}KV6posinfo"):

    #     pp.pprint(child[1])
    #     try:
    #         vp.append({
    #             "type":child[0].tag,
    #             "datacode":child[0][0].text,
    #             "lpn":child[0][1].text,
    #             "opday":child[0][2].text,
    #             "jnum":child[0][3].text,
    #             "reinforcenum":child[0][4].text,
    #             "ustopcode":child[0][5].text,
    #             "pseqnum":child[0][6].text,
    #             "timestamp":child[0][7].text,
    #             "source":child[0][8].text,
    #             "vehiclenum":child[0][9].text,
    #             "punct":child[0][10].text,
    #         })
    #     except: pass
    # with open('data.json', 'a') as outfile:  
    #         json.dump(vp, outfile)




    # for group in document.findall('KV6posinfo'):
    #     pp.pprint(group)
    # with open('data.json', 'a') as outfile:  
    #     json.dump(vp, outfile)
    # tree = etree.parse(address)

    # root = objectify.Element(message)
    # print(root.timestamp)

    # print(etree.tostring(tree.getroot()))
    
    # p = etree.tostring(tree.getroot())

    # print(p)

    # print(type(message))

    #wip 
    # conte = xmltodict.parse(message)
    # # pp.pprint()
    # for x in conte.items():
    #     for p in x:
    #         yeet.append(p)




    # print(y)
    
# pp.pprint(yeet)
# file = open('message1.xml'.format(),"a")
# file.write(message)




# main = objectify.fromstring(message)
# print((main.KV6posinfo[]))             # content
# main.object1[1]             # contenbar
# main.object1[0].get("attr") # name
# main.test                   # me


# for x in conte.keys():
#     print(x[0])
    # for y in x:
    #     print(y)
    # root = ET.fromstring(contents)
    # for child in root:
    #     print(child.tag)
    
    # for neighbor in root.findall('{http://bison.connekt.nl/tmi8/kv6/msg}KV6posinfo'):
    #     for child in neighbor:
    #         # print(child.tag)
    #         for childd in child:
    #             print(childd.tag)

    


    
    # msg2 = msg.decode('utf-8', errors="ignore")
    # msg3 = str(msg)
    # print(msg2)
    # data = str(msg,'utf-16')
    # plain_string_again  = gzip.decompress(msg)


    # f = open("demofile2.txt", "w")
    # f.write(msg2)
    # f.close()

    