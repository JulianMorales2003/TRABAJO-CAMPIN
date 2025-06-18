from flask import Flask, render_template, request, redirect, session, url_for
import os
from copy import deepcopy

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

# Menú para sede OCCIDENTAL
menu_occidental = [
    {"id": 1, "categoria": "COMIDAS", "nombre": "COMBO HAMBURGUESA + COCA COLA", "precio": 28000},
    {"id": 2, "categoria": "COMIDAS", "nombre": "COMBO PERRO + COCA COLA", "precio": 25000},
    {"id": 3, "categoria": "COMIDAS", "nombre": "PERRO CALIENTE", "precio": 20000},
    {"id": 4, "categoria": "COMIDAS", "nombre": "HAMBURGUESA CON TOCINETA", "precio": 22000},
    {"id": 5, "categoria": "COMIDAS", "nombre": "DEDO DE QUESO", "precio": 10000},
    {"id": 6, "categoria": "COMIDAS", "nombre": "LECHONA", "precio": 20000},
    {"id": 7, "categoria": "COMIDAS", "nombre": "CRISPETAS DE SAL", "precio": 18000},
    {"id": 8, "categoria": "BEBIDAS", "nombre": "COCA COLA ORIGINAL", "precio": 10000},
    {"id": 9, "categoria": "BEBIDAS", "nombre": "COCA COLA ZERO", "precio": 10000},
    {"id": 10, "categoria": "BEBIDAS", "nombre": "GATORADE SURTIDO", "precio": 12000},
    {"id": 11, "categoria": "BEBIDAS", "nombre": "GATORADE ZERO", "precio": 12000},
    {"id": 12, "categoria": "BEBIDAS", "nombre": "AGUA BRISA SIN GAS", "precio": 10000},
    {"id": 13, "categoria": "BEBIDAS", "nombre": "CAFE AMERICANO", "precio": 5000},
    {"id": 14, "categoria": "BEBIDAS", "nombre": "JUGO HIT 200ML", "precio": 5000},
    {"id": 15, "categoria": "BEBIDAS", "nombre": "CERVEZA CERO", "precio": 12000},
]

# Menú para sede NORTE (todo en mayúsculas)
menu_norte = [
    {"id": 1, "categoria": "BEBIDAS", "nombre": "AGUA BRISA SIN GAS", "precio": 8000},
    {"id": 2, "categoria": "BEBIDAS", "nombre": "PONY MALTA PET", "precio": 4000},
    {"id": 3, "categoria": "BEBIDAS", "nombre": "COCA COLA PET", "precio": 8000},
    {"id": 4, "categoria": "BEBIDAS", "nombre": "COCA COLA ZERO", "precio": 8000},
    {"id": 5, "categoria": "BEBIDAS", "nombre": "GATORADE SURTIDO", "precio": 10000},
    {"id": 6, "categoria": "BEBIDAS", "nombre": "GATORADE SIN AZÚCAR", "precio": 10000},
    {"id": 7, "categoria": "BEBIDAS", "nombre": "JUGO EN CAJA HIT", "precio": 4000},
    {"id": 8, "categoria": "BEBIDAS", "nombre": "CAFÉ AMERICANO", "precio": 4000},
    {"id": 9, "categoria": "BEBIDAS", "nombre": "CERVEZA CERO", "precio": 9000},
    {"id": 10, "categoria": "COMIDAS", "nombre": "CRISPETAS DE SAL", "precio": 15000},
    {"id": 11, "categoria": "COMIDAS", "nombre": "PERRO CALIENTE AMERICANO", "precio": 18000},
    {"id": 12, "categoria": "COMIDAS", "nombre": "HAMBURGUESA CON TOCINETA", "precio": 21000},
    {"id": 13, "categoria": "COMIDAS", "nombre": "COMBO SÁNDUCHE + JUGO", "precio": 12000},
    {"id": 14, "categoria": "COMIDAS", "nombre": "DEDO DE QUESO", "precio": 10000},
    {"id": 15, "categoria": "COMIDAS", "nombre": "LECHONA LOCAL", "precio": 20000},
]

@app.route("/")
def seleccionar_sede():
    return render_template("seleccionar_sede.html")

@app.route("/elegir_sede", methods=["POST"])
def elegir_sede():
    sede = request.form["sede"]
    session["sede"] = sede
    session["pedido_actual"] = [].copy()
    session["historial"] = [].copy()
    session["efectivo"] = 0
    session["datafono"] = 0
    return redirect("/menu")

@app.route("/menu")
def index():
    sede = session.get("sede")
    if sede == "OCCIDENTAL":
        menu = menu_occidental
    elif sede == "NORTE":
        menu = menu_norte
    else:
        return redirect("/")

    pedido_actual = session.get("pedido_actual", [])
    historial = session.get("historial", [])
    efectivo = session.get("efectivo", 0)
    datafono = session.get("datafono", 0)
    total = sum(item["precio_unitario"] * item["cantidad"] for item in pedido_actual)

    return render_template("index.html", menu=menu, pedido=pedido_actual, total=total, historial=historial, efectivo=efectivo, datafono=datafono, sede_actual=sede)

@app.route("/agregar", methods=["POST"])
def agregar():
    sede = session.get("sede")
    menu = menu_occidental if sede == "OCCIDENTAL" else menu_norte

    producto_id = int(request.form["producto_id"])
    cantidad = int(request.form["cantidad"])
    pedido = session.get("pedido_actual", [])

    producto = next((p for p in menu if p["id"] == producto_id), None)
    if producto:
        existente = next((item for item in pedido if item["id"] == producto_id), None)
        if existente:
            existente["cantidad"] += cantidad
        else:
            pedido.append({
                "id": producto["id"],
                "nombre": producto["nombre"],
                "precio_unitario": producto["precio"],
                "cantidad": cantidad
            })

    session["pedido_actual"] = pedido
    return redirect("/menu")

@app.route("/actualizar", methods=["POST"])
def actualizar():
    producto_id = int(request.form["producto_id"])
    nueva_cantidad = int(request.form["nueva_cantidad"])
    pedido = session.get("pedido_actual", [])

    item = next((i for i in pedido if i["id"] == producto_id), None)
    if item:
        if nueva_cantidad <= 0:
            pedido.remove(item)
        else:
            item["cantidad"] = nueva_cantidad

    session["pedido_actual"] = pedido
    return redirect("/menu")

@app.route("/finalizar", methods=["POST"])
def finalizar():
    pedido = session.get("pedido_actual", [])
    print("Pedido recibido al finalizar:", pedido)  # DEBUG

    if not pedido:
        print("Pedido vacío, redirigiendo a index")  # DEBUG
        return redirect(url_for("index"))

    total = sum(item["precio_unitario"] * item["cantidad"] for item in pedido)

    metodo_pago = request.form.get("metodo_pago", "sin_definir")

    historial = session.get("historial", [])
    historial.append({
        "pedido": pedido,
        "total": total,
        "metodo_pago": metodo_pago
    })

    # Sumar al total correspondiente
    if metodo_pago == "efectivo":
        session["efectivo"] += total
    elif metodo_pago == "datafono":
        session["datafono"] += total

    session["historial"] = historial
    session["pedido_actual"] = []  # Vaciar el pedido actual

    print("Pedido finalizado y guardado en historial")  # DEBUG
    return redirect(url_for("index"))

@app.route("/reiniciar")
def reiniciar():
    session["pedido_actual"] = []
    return redirect("/menu")

@app.route("/eliminar_pedido/<int:indice>", methods=["POST"])
def eliminar_pedido(indice):
    historial = session.get("historial", [])
    efectivo = session.get("efectivo", 0)
    datafono = session.get("datafono", 0)

    if 0 <= indice < len(historial):
        pedido = historial.pop(indice)
        if pedido["metodo_pago"] == "efectivo":
            efectivo -= pedido["total"]
        elif pedido["metodo_pago"] == "datafono":
            datafono -= pedido["total"]

    session["historial"] = historial
    session["efectivo"] = efectivo
    session["datafono"] = datafono
    return redirect("/menu")

@app.route("/eliminar_todos", methods=["POST"])
def eliminar_todos():
    session["historial"] = []
    session["efectivo"] = 0
    session["datafono"] = 0
    return redirect("/menu")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
