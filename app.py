from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

app = Flask(__name__)

#Coniguración de la base de datos SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Modelo de la tabla log
class Log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default = datetime.utcnow)
    texto = db.Column(db.TEXT)

#Crear la tabla si no existe
with app.app_context():
    db.create_all()

#funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)


@app.route('/')

def index():
    #obtener todos los registros de la base de datos
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros = registros_ordenados)

#agregar información a la base de datos
mensajes_log = []

#Función información a la base de datos
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #gurardar mensajes en la base de datos
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#para agregar mensaje de ejemplo
#agregar_mensajes_log(json.dumps('Test1'))

#Tockin de verificacion para la configuracion 
TOKEN_CODE = 'TRONOSCODE'

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_CODE:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}), 401

#Como esta funcion recibe los mensaje, se agregara la BD
def recibir_mensajes(req):
    
    #esto se oculta para poder ver el mensaje dentro del log
    #req = request.get_json()
    #agregar_mensajes_log(req)

#leyendo un mensaje
    try:
        req = request.get_json()
        entry =  req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        #para identiicar el tipo de dato
        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]

                #guarda log en la base de datos
                agregar_mensajes_log(json.dumps(tipo))#contiene todo el json

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text =messages["interative"]["button_reply"]["id"]

                        numero = messages["from"]

                        enviar_mensaje_whatsapp(text,numero)
                
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensaje_whatsapp(text,numero)

                    #guarda log en la base de datos

                    agregar_mensajes_log(json.dumps(text))
                    #agregar_mensajes_log(json.dumps(numero))
                    #agregar_mensajes_log(json.dumps(messages))


        return jsonify({'message':'EVENT_RECEIVED'})
    
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})


#Para responder el mensaje
def enviar_mensaje_whatsapp(texto,number):
    texto = texto.lower()

    if "hola" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, ¿Cómo estás? Bienvenido."
            }
        }
    elif "1" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "💼 Nuestros servicios son los siguientte \n 1. Servicio \n 2. otros servicios"
            }
        }
    elif "2" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "4.342897934970716",
                "longitude": "-74.36055740298639",
                "name": "Empresa de Servicios Públicos de Fusagasugá",
                "address": "Av las Palmas Nro 4-66 Centro"
            }
        }
    elif "3" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://www.dinamarca.edu.co/pdf/Algebra%20de%20Baldor.pdf",
                "caption": "Algebra de Baldor"
            }
        }
    elif "4" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "audio",
            "audio": {
                "link": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                "caption": "Audio de prueba"
            }
        }
    elif "5" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "text": {
                "preview_url": True,
                "body": "Introducción Servicios TicAll Media https://youtu.be/hpltvTEiRrY to inspire your day!"
            }
        }
    elif "6" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🤙 En breve te contactaremos!!!"
            }
        }
    elif "7" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🗓️ Horario de Atención: Lunes a Viernes. \n 🕐 Horario: 9:00 am a 5:00 pm"
            }
        }
    elif "0" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita mi web https://ticallmedia.com/.com para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información de los Servicios. 💼\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar catalogo en PDF. 📄\n4️⃣. Audio explicando a mayor detalle. 🎧\n5️⃣. Video de Introducción. ⏯️\n6️⃣. Hablar con un Agente. 🙋‍♂️\n7️⃣. Horario de Atención. 🕜 \n0️⃣. Regresar al Menú. 🕜"
            }
        }
    elif "boton" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text" : "¿Confirma su registro..?"
                },
                "footer": {
                    "text" : "Selecciona una de las opciones:"
                },
                "action": {
                    "buttons": [
                        {
                            "type" : "reply",
                            "reply" : {
                                "id" : "btnsi",
                                "title": "Si"
                            } 
                        },{
                            "type" : "reply",
                            "reply" : {
                                "id" : "btnno",
                                "title": "No"
                            } 
                        },{
                            "type" : "reply",
                            "reply" : {
                                "id" : "btntalvez",
                                "title": "Tal Vez"
                            } 
                        }
                    ]
                }                
            }
        }
    elif "btnsi" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Muchas Gracias por aceptar."
            }
        }
    elif "btnno" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Es una lastima."
            }
        }
    elif "btntalvez" in texto:
        data= {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Estare a la espera."
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita mi web https://ticallmedia.com/.com para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información de los Servicios. 💼\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar catalogo en PDF. 📄\n4️⃣. Audio explicando a mayor detalle. 🎧\n5️⃣. Video de Introducción. ⏯️\n6️⃣. Hablar con un Agente. 🙋‍♂️\n7️⃣. Horario de Atención. 🕜 \n0️⃣. Regresar al Menú. 🕜"
            }
        }
    #convertir el diccionario a formato json
    data = json.dumps(data)

    #datos de WETA
    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAARFt0chSDgBOx6u7Rgn2Daqg7AtSiKYiUSoAY8IX2GZCIuT2fvkNhOyYOA7oHCrKZAcD7FeKPNov537ZBC5RQU3CpL9RymKaZBa1EJ0eZBNCD3XmAVkrLZCwdyG0P6vZAfpZAcvWax0g7nbnEZCrBMmd3fTV6B9dalrOIZAzuDkY9oVrZBPr1WAye9FY9LyIAW4k0MSeArnKn3CHl7YVOhZBjX2leZA7F5Pt1LrlVRUZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:

        connection.request("POST","/v22.0/593835203818298/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)

    except Exception as e:
        agregar_mensajes_log(json.dumps(e))

    finally:
        connection.close()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)