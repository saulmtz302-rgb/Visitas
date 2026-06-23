import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF
from PIL import Image
import io
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Registro de Visitas", page_icon="🏢", layout="centered")

st.title("📝 Control de Visitas y Checklist de Sucursales")
st.write("Completa los datos de la visita, realiza el checklist y firma la conformidad.")

# --- 1. DATOS DE LA VISITA ---
st.header("🏢 Datos de la Sucursal")
col1, col2 = st.columns(2)

with col1:
    sucursal = st.selectbox("Selecciona la Sucursal",
                            ["Sucursal Norte", "Sucursal Centro", "Sucursal Sur", "Sucursal Este"])
    visitante = st.text_input("Nombre del Visitante / Auditor")
with col2:
    fecha = st.date_input("Fecha de la visita", datetime.date.today())
    encargado = st.text_input("Nombre del Encargado de Sucursal")



# --- 2. CHECKLIST NATIVO ---
st.header("✅ Checklist de Inspección")
st.write("Marque los puntos verificados durante la visita:")

# Definimos los puntos del checklist
puntos_control = [
    "Limpieza y orden general de la sucursal",
    "Funcionamiento correcto de equipos y sistemas",
    "Inventario revisado y conciliado",
    "Caja chica y valores asegurados",
    "Cumplimiento de protocolos de seguridad e higiene",
    "Atención al cliente y presentación del personal"
]

# Guardaremos las respuestas en un diccionario
respuestas_checklist = {}
for punto in puntos_control:
    respuestas_checklist[punto] = st.checkbox(punto, value=False)

comentarios = st.text_area("Notas / Comentarios adicionales")



# --- 3. RECUADRO DE FIRMA ---
st.header("✍️ Firma de Conformidad")
st.caption("El encargado debe firmar en el recuadro de abajo:")

# Crear el componente de lienzo para la firma
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Color de fondo si se desea
    stroke_width=3,
    stroke_color="#000000",  # Color del trazo (negro)
    background_color="#FFFFFF",  # Fondo blanco
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="canvas_firma",
)



# --- 4. GENERACIÓN DE EVIDENCIA (PDF) ---
st.header("📄 Generar Evidencia")


def generar_pdf(sucursal, visitante, fecha, encargado, checklist, comentarios, firma_img):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Título
    pdf.cell(190, 10, "REPORTE DE VISITA A SUCURSAL", ln=True, align="C")
    pdf.ln(10)

    # Datos generales
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Datos Generales", ln=True, fill=False)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 6, f"Sucursal: {sucursal}", ln=True)
    pdf.cell(190, 6, f"Fecha: {fecha}", ln=True)
    pdf.cell(190, 6, f"Auditado por: {visitante}", ln=True)
    pdf.cell(190, 6, f"Encargado de Sucursal: {encargado}", ln=True)
    pdf.ln(5)

    # Checklist
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Puntos de Control Evaluados", ln=True)
    pdf.set_font("Arial", "", 11)
    for punto, estado in checklist.items():
        simbolo = "[X]" if estado else "[ ]"
        pdf.cell(190, 6, f"{simbolo} {punto}", ln=True)
    pdf.ln(5)

    # Comentarios
    if comentarios:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, "Comentarios adicionales:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(190, 6, comentarios)
        pdf.ln(5)

    # Firma
    if firma_img is not None:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, "Firma de Conformidad del Encargado:", ln=True)

        # Guardar la imagen de la firma temporalmente en memoria para meterla al PDF
        img_buf = io.BytesIO()
        firma_img.save(img_buf, format='PNG')
        img_buf.seek(0)

        # Insertar firma en el PDF
        pdf.image(img_buf, x=15, w=60)

    return pdf.output()


# Botón para procesar y descargar
if st.button("💾 Procesar y Generar PDF"):
    # Validar que se haya firmado algo
    if canvas_result.image_data is not None:
        # Convertir los datos del canvas a una imagen de Pillow
        img_data = canvas_result.image_data
        firma_pil = Image.fromarray(img_data.astype('uint8'), 'RGBA')

        # Verificar si el lienzo no está vacío (opcional pero recomendado)
        # Generar el PDF en memoria
        pdf_bytes = generar_pdf(
            sucursal, visitante, fecha, encargado, respuestas_checklist, comentarios, firma_pil
        )

        # Botón de descarga de Streamlit
        st.success("¡PDF generado con éxito!")
        st.download_button(
            label="📥 Descargar Evidencia en PDF",
            data=bytes(pdf_bytes),
            file_name=f"Evidencia_{sucursal}_{fecha}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Por favor, solicita la firma del encargado antes de generar el PDF.")