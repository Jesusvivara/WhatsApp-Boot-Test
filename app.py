flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://kowkodrilo:b0rnt0d13@cluster0.bqc7b.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["Pasteleria-Ejemplar"]
usuarios = db["Usuarios"]
pedidos = db["Pedidos"]

app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("WhatsApp:", "")
    res = MessagingResponse()
    user = usuarios.find_one({"number": number})
    if bool(user) == False:
        res.message("Hola, gracias por contactarnos *Pasteleria Ejemplar*.\nPuedes elegir una de las siguientes opciones: "
                    "\n\n*Escribe el numero de la opcion a elegir*\n\n 1️⃣ *Contactarnos* \n 2️⃣ *Ordenar bocadillos* \n 3️⃣ *Horarios de Trabajo* \n 4️⃣ "" *Nuestra Dirección*")
        usuarios.insert_one({"number": number, "status": "main", "messages": []})

    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Porfavor ingresa el numero de la opcion a elegir")
            return str(res)

        if option == 1:
            res.message("Puedes contactarnos atraves de nuestro telefono o e-mail.\n\n*Cel*: 991234 56789 \n*E-mail* : contact@Pasteleria-ejemplar.io")

        elif option == 2:
            res.message("*List@ para ordenar*.")
            usuarios.update_one(
                {"number": number}, {"$set": {"status": "ordering"}})
            res.message("Puedes elegir entre una de las siguientes opciones de Snacks: \n\n1️⃣ Red Velvet  \n2️⃣ Dark Forest \n3️⃣ Ice Cream Cake"
                "\n4️⃣ Plum Cake \n5️⃣ Sponge Cake \n6️⃣ Genoise Cake \n7️⃣ Angel Cake \n8️⃣ Carrot Cake \n9️⃣ Fruit Cake  \n0️⃣ menu principal")

        elif option == 3:
            res.message("Trabajamos de Lunes a Viernes de *9 a.m. a 5 p.m*.")

        elif option == 4:
            res.message("Tenemos multiples tiendas alrededor de la ciudad. nuestra tienda principal 🏪 esta ubicada en *454, New Delhi*")
        else:
            res.message("Porfavor ingresa el numero de la opcion a elegir")
            return str(res)

    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Porfavor ingresa el numero de la opcion a elegir")
            return str(res)
        if option == 0:
            usuarios.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("Elige una de las siguientes opciones: \n*Escribe el numero de la opcion a elegir*\n\n 1️⃣ "
                        "*Contactarnos* \n 2️⃣ *Ordenar bocadillos* \n 3️⃣ *Horarios de Trabajo* \n 4️⃣ "" *Nuestra "
                        "Dirección*")
        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake", "Dark Forest Cake", "Ice Cream Cake", "Plum Cake", "Sponge Cake", "Genoise Cake", "Angel Cake", "Carrot Cake", "Fruit Cake"]
            selected = cakes[option -1]
            usuarios.update_one({"number": number}, {"$set": {"status": "address"}})
            usuarios.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Excelente eleccion")
            res.message("Por favor confirma tu direccion para realizar el pedido")
        else:
            res.message("Porfavor ingresa el numero de la opcion valida")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Gracias por comprar con nosotros 😊")
        res.message(f"Tu orden {selected} esta en nuestra lista de espera y sera entregada dentro de 1 hora aproximadamente")
        pedidos.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        usuarios.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message(
            "Hola, gracias por contactarnos de nuevo *Pasteleria Ejemplar*.\nPuedes elegir una de las siguientes opciones: "
            "\n\n*Escribe el numero de la opcion a elegir*\n\n 1️⃣ *Contactarnos* \n 2️⃣ *Ordenar bocadillos* \n 3️⃣ *Horarios de Trabajo* \n 4️⃣ "" *Nuestra Dirección*")
        usuarios.update_one({"number": number}, {"$set": {"status": "main"}})

    usuarios.update_one({"number": number}, {"$push": {"messages": {"text": text, "date:": datetime.now()}}})
    return str(res)

if __name__ == "__main__":
    app.run()
