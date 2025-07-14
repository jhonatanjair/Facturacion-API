from reportlab.pdfgen import canvas

def generar_pdf_factura(ruta_pdf, datos):
    venta = datos["venta"]
    items = datos["items"]
    tipo = datos.get("tipo_operacion", "gravada")

    c = canvas.Canvas(ruta_pdf)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 800, "FACTURA ELECTRÓNICA")

    c.setFont("Helvetica", 10)
    y = 780
    c.drawString(100, y, f"Tipo de operación: {tipo}")
    y -= 20

    for i, item in enumerate(items, 1):
        descripcion = item["producto"]
        cantidad = item["cantidad"]
        precio = item["precio_base"]
        c.drawString(100, y, f"{i}. {descripcion} - Cantidad: {cantidad} - Precio: {precio}")
        y -= 15

    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, y, f"Total a pagar: S/ {venta.get('total_pagar', 0):.2f}")
    y -= 15

    # Agregar detalles especiales según el tipo
    c.setFont("Helvetica", 10)
    if tipo == "ventaExonerada":
        c.drawString(100, y, "Esta venta está EXONERADA de IGV.")
    elif tipo == "ventaConPercepcion":
        perc = venta.get("percepcion", {}).get("monto_percibido", 0)
        c.drawString(100, y, f"Se aplica percepción: S/ {perc:.2f}")
    elif tipo == "transferenciaGratuita":
        c.drawString(100, y, "Transferencia gratuita de bienes.")
    elif tipo == "ventaConBonificaciones":
        c.drawString(100, y, "Incluye productos con bonificación.")
    elif tipo == "ventaCredito":
        cuotas = venta.get("cuotas", [])
        for cuota in cuotas:
            y -= 15
            c.drawString(100, y, f"Cuota: S/ {cuota['monto']} - Vence: {cuota['fecha_vencimiento']}")
    else:
        c.drawString(100, y, "Operación gravada con IGV.")

    c.save()
