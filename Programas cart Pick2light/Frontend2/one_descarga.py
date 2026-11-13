import requests, json

import io
import barcode
from barcode.writer import ImageWriter
from PIL import Image

# Send a basic GET request
def getter():
    url_ords = "https://qaws.onestcloud.mx:8085/ords/onewms_qa/madden/ordenes?t_ent=1&cuenta=55"
    url_surt = "https://qaws.onestcloud.mx:8085/ords/onewms_qa/asistente/surtido"
    url_cnta = "https://qaws.onestcloud.mx:8085/ords/onewms_qa/asistente/pedidos/335"
    response = requests.get(url_ords)
    my_doc = response.json()
    # Check if the request was successful (200 OK)
    ordenes = my_doc["ORDENES"]
    for doc in ordenes:
        print(doc['DOCTO_ENT_ID'], len(doc['DOCTO_ENT_ID']))

    return None

def QA():
    oleada = {
    "Oleada":"OL00001",
    "Pedidos":[
        {'Pedido':'D-13625001','detalle':[
            {'sku':'V02-542512','CANT_PED':1,'CANT_CONF':0,'pasillo':'A','lado':'1','nivel':'1','fondo':'3'},
            #{'sku':'V01-145103','CANT_PED':1,'CANT_CONF':0,'pasillo':'C','lado':'1','nivel':'2','fondo':'5'},
            #{'sku':'V03-542512','CANT_PED':1,'CANT_CONF':0,'pasillo':'D','lado':'2','nivel':'3','fondo':'7'},
            #{'sku':'V01-145003','CANT_PED':1,'CANT_CONF':0,'pasillo':'D','lado':'2','nivel':'3','fondo':'9'}
        ]},
        #{'Pedido':'KA1451229','detalle':[
            #{'sku':'494114','CANT_PED':2,'CANT_CONF':0,'pasillo':'B','lado':'1','nivel':'2','fondo':'3'},
            #{'sku':'580204','CANT_PED':2,'CANT_CONF':0,'pasillo':'B','lado':'2','nivel':'2','fondo':'6'},
            #{'sku':'427625','CANT_PED':2,'CANT_CONF':0,'pasillo':'C','lado':'2','nivel':'2','fondo':'9'}
        #]},
        #{'Pedido':'PED22006005','detalle':[
        #    {'sku':'V01-145103','CANT_PED':1,'CANT_CONF':0,'pasillo':'A','lado':'2','nivel':'1','fondo':'2'},
            #{'sku':'V03-542512','CANT_PED':1,'CANT_CONF':0,'pasillo':'D','lado':'1','nivel':'3','fondo':'4'}
        #]},
        #{'Pedido':'TO2200438','detalle':[
        #    {'sku':'V01-145003','CANT_PED':3,'CANT_CONF':0,'pasillo':'B','lado':'1','nivel':'2','fondo':'6'},
            #{'sku':'V02-542512','CANT_PED':2,'CANT_CONF':0,'pasillo':'C','lado':'1','nivel':'2','fondo':'8'}
        #]}
    ],
    'Recorrido':[
        {'Pedido':'D-13625001','sku':'V02542512','CANT_PED':1,'CANT_CONF':0,'pasillo':'A','lado':'1','nivel':'1','fondo':'3'},
        #{'Pedido':'PED22006005','sku':'V01145103','CANT_PED':1,'CANT_CONF':0,'pasillo':'A','lado':'2','nivel':'1','fondo':'2'},

        #{'Pedido':'KA1451229','sku':'494114','CANT_PED':2,'CANT_CONF':0,'pasillo':'B','lado':'1','nivel':'2','fondo':'3'},
        #{'Pedido':'TO2200438','sku':'V01145003','CANT_PED':3,'CANT_CONF':0,'pasillo':'B','lado':'1','nivel':'2','fondo':'6'},
        #{'Pedido':'KA1451229','sku':'580204','CANT_PED':2,'CANT_CONF':0,'pasillo':'B','lado':'2','nivel':'2','fondo':'6'},

        #{'Pedido':'D-13625001','sku':'V01145103','CANT_PED':1,'CANT_CONF':0,'pasillo':'C','lado':'1','nivel':'2','fondo':'5'},
        #{'Pedido':'TO2200438','sku':'V02542512','CANT_PED':2,'CANT_CONF':0,'pasillo':'C','lado':'1','nivel':'2','fondo':'8'},
        #{'Pedido':'KA1451229','sku':'427625','CANT_PED':2,'CANT_CONF':0,'pasillo':'C','lado':'2','nivel':'2','fondo':'9'},

        #{'Pedido':'PED22006005','sku':'V03542512','CANT_PED':1,'CANT_CONF':0,'pasillo':'D','lado':'1','nivel':'3','fondo':'4'},
        #{'Pedido':'D-13625001','sku':'V03542512','CANT_PED':1,'CANT_CONF':0,'pasillo':'D','lado':'2','nivel':'3','fondo':'7'},
        #{'Pedido':'D-13625001','sku':'V01145003','CANT_PED':1,'CANT_CONF':0,'pasillo':'D','lado':'2','nivel':'3','fondo':'9'}
    ]

    }
    return oleada



def generate_and_show_barcode(data: str):
    bytes_stream = io.BytesIO()
    barcode_class = barcode.get_barcode_class('code128')
    my_barcode = barcode_class(data, writer=ImageWriter())
    my_barcode.write(bytes_stream)
    bytes_stream.seek(0)
    img = Image.open(bytes_stream)
    #img.show()

    return img
