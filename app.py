from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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

                if tipo == "interactive":
                    return 0
                
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]
                    
                    #para guardar en la base de datos
                    #agregar_mensajes_log(json.dumps(text))
                    #agregar_mensajes_log(json.dumps(numero))

                    enviar_mensaje_whatsapp(text,numero)


        return jsonify({'message':'EVENT_RECEIVED'})
    
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})


#Para responder el mensaje
def enviar_mensaje_whatsapp(texto,number):
    texto = texto.lower()

    if "hola" in texto:
        data ={
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Hola ¿Como estas? Bienvenido al TAM Bot Test, prueba de bot con RENDER"
                }
            }
    else:
        data ={
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Este es otro texto de,  TAM Bot Test, prueba de bot con RENDER"
                }
            }
    #convertir el diccionario a formato json
    data = json.dumps(data)

    #datos de WETA
    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAARFt0chSDgBOZC4ZBkaF0dlVi63BScd5mxSKOwh0eKKjZBORX91sWhHx5Xp8HwBiSmBKRuJjbjDSZA3wzsgKY5BkwgAi3bgnQljV3Df1T8ZBrpHe8gxakMvsMXDSTWuUhfBHhZB2Fz2uBFN5LIEV2cklyzX7NoyO0QJHiL4s7L547ZBiumebooRKkBVioZA2AeKZCNMNaHvEujGiMMSuS8YN3O4sipr7DqGa4WYZD"

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