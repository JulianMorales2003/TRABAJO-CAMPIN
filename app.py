from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Menú del local
menu = [
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
]

# Pedido actual
pedido_actual = []

# Historial de pedidos finalizados
historial_pedidos = []

# Total efectivo
total_efectivo = 0

# Total efectivo
total_datafono = 0

@app.route("/")
def index():
    total = sum(item["precio_unitario"] * item["cantidad"] for item in pedido_actual)
    return render_template("index.html", menu=menu, pedido=pedido_actual, total=total, historial=historial_pedidos, efectivo=total_efectivo, datafono=total_datafono)

@app.route("/agregar", methods=["POST"])
def agregar():
    producto_id = int(request.form["producto_id"])
    cantidad = int(request.form["cantidad"])

    producto = next((p for p in menu if p["id"] == producto_id), None)
    if producto:
        existente = next((item for item in pedido_actual if item["id"] == producto_id), None)
        if existente:
            existente["cantidad"] += cantidad
        else:
            pedido_actual.append({
                "id": producto["id"],
                "nombre": producto["nombre"],
                "precio_unitario": producto["precio"],
                "cantidad": cantidad
            })

    return redirect("/")

@app.route("/actualizar", methods=["POST"])
def actualizar():
    producto_id = int(request.form["producto_id"])
    nueva_cantidad = int(request.form["nueva_cantidad"])
    item = next((item for item in pedido_actual if item["id"] == producto_id), None)
    if item:
        if nueva_cantidad <= 0:
            pedido_actual.remove(item)
        else:
            item["cantidad"] = nueva_cantidad
    return redirect("/")

@app.route("/finalizar", methods=["POST"])
def finalizar():
    global pedido_actual, historial_pedidos, total_efectivo, total_datafono

    metodo = request.form["metodo_pago"]
    total = sum(item["precio_unitario"] * item["cantidad"] for item in pedido_actual)

    historial_pedidos.append({
        "items": list(pedido_actual),
        "total": total,
        "metodo_pago": metodo
    })

    if metodo == "efectivo":
        total_efectivo += total
    else:
        total_datafono += total

    pedido_actual.clear()
    return redirect("/")

@app.route("/reiniciar")
def reiniciar():
    pedido_actual.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
