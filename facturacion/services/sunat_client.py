import os
import io
import base64
import zipfile
from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.exceptions import Fault

# Directorios base
BASE_DIR = "files/facturacion_electronica"
DIR_FIRMA = os.path.join(BASE_DIR, "FIRMA")
DIR_CDR = os.path.join(BASE_DIR, "CDR")
DIR_PDF = os.path.join(BASE_DIR, "PDF")

# Crear carpetas si no existen
for path in [DIR_FIRMA, DIR_CDR, DIR_PDF]:
    os.makedirs(path, exist_ok=True)

def guardar_archivo(ruta, contenido_bytes):
    with open(ruta, "wb") as f:
        f.write(contenido_bytes)

def crear_zip_desde_xml(nombre_archivo_xml, xml_bytes):
    """
    Crea un archivo ZIP en memoria con el nombre del XML como archivo dentro.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(nombre_archivo_xml, xml_bytes)
        print("✅ Agregado al ZIP:", nombre_archivo_xml)
    return buffer.getvalue()

def enviar_xml_a_sunat(ruc, usuario, password, tipo_doc, serie, correlativo, xml_bytes, ambiente='beta'):
    # Nombre del archivo XML según formato SUNAT
    nombre_archivo = f"{ruc}-{tipo_doc}-{serie}-{correlativo}.xml"
    nombre_zip = nombre_archivo.replace(".xml", ".zip")

    # WSDL endpoint
    url = (
        "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
        if ambiente == 'beta' else
        "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService?wsdl"
    )

    # Crear ZIP
    zip_bytes = crear_zip_desde_xml(nombre_archivo, xml_bytes)
    contenido_zip_base64 = base64.b64encode(zip_bytes)

    # Guardar XML y ZIP
    ruta_xml = os.path.join(DIR_FIRMA, nombre_archivo)
    ruta_zip = os.path.join(DIR_FIRMA, nombre_zip)
    guardar_archivo(ruta_xml, xml_bytes)
    guardar_archivo(ruta_zip, zip_bytes)

    print(f"📡 Autenticando con SUNAT: {usuario} / {password}")

    # Inicializar cliente SOAP con WSSE
    client = Client(
    wsdl="https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl",
    wsse=UsernameToken("20103129061MODDATOS", "moddatos")
)

    try:
        # Enviar el archivo ZIP
        respuesta = client.service.sendBill(
            fileName=nombre_zip,
            contentFile=contenido_zip_base64
        )

        # Guardar CDR recibido
        nombre_cdr = f"R-{nombre_zip}"
        ruta_cdr = os.path.join(DIR_CDR, nombre_cdr)
        guardar_archivo(ruta_cdr, respuesta)

        # Extraer XML del CDR
        with zipfile.ZipFile(ruta_cdr, 'r') as zip_ref:
            zip_ref.extractall(DIR_CDR)

        # (Opcional) Simular PDF – aquí lo guardamos como ZIP solo por mantener compatibilidad
        ruta_pdf_simulado = os.path.join(DIR_PDF, nombre_zip)
        guardar_archivo(ruta_pdf_simulado, b"PDF SIMULADO")

        return {
            "respuesta_sunat_codigo": "0",
            "respuesta_sunat_descripcion": f"✅ La Factura {nombre_archivo.replace('.xml', '')} ha sido aceptada por SUNAT",
            "ruta_xml": f"http://localhost:8000/{ruta_xml.replace(os.sep, '/')}",
            "ruta_zip": f"http://localhost:8000/{ruta_zip.replace(os.sep, '/')}",
            "ruta_cdr": f"http://localhost:8000/{ruta_cdr.replace(os.sep, '/')}",
            "xml_base64": base64.b64encode(xml_bytes).decode(),
            "cdr_base64": base64.b64encode(respuesta).decode()
        }

    except Fault as e:
        return {
            "error": {
                "codigo": e.code,
                "mensaje": e.message
            }
        }
