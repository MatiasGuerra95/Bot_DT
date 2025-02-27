import logging
import os
import time
import traceback
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Configurar logging
log_file = "sigo_rut.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Cargar variables de entorno
load_dotenv()
USUARIO = os.getenv("MVS_SIGO_USER")
PASSWORD = os.getenv("MVS_SIGO_PASS")

# Configurar opciones de Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

finiquitos_seleccionados = 0

def acceder_a_sigo():
    try:
        logging.info("🚀 Accediendo a la página de inicio de sesión...")
        driver.get("http://35.184.233.114/MVS_SIGO/")
        
        usuario_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "user")))
        password_input = driver.find_element(By.ID, "pass")

        usuario_input.send_keys(USUARIO)
        password_input.send_keys(PASSWORD)
        logging.info("✅ Credenciales ingresadas correctamente.")

        driver.find_element(By.ID, "btnLogn").click()
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "enlace5")))
        logging.info("🎯 Inicio de sesión exitoso.")

    except Exception as e:
        logging.error(f"❌ Error en inicio de sesión: {str(e)}")

def acceder_a_solicitud_finiquitos():
    try:
        enlace_finiquitos = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "enlace5"))
        )
        driver.execute_script("arguments[0].click();", enlace_finiquitos)
        logging.info("📂 Accediendo a 'Solicitud de Finiquitos'.")
    except Exception as e:
        logging.error(f"❌ Error al acceder a Solicitud de Finiquitos: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────────
# 🔹 **Función para seleccionar el tipo de finiquito 'DT'**
# ─────────────────────────────────────────────────────────────────────────────
def seleccionar_tipo_dt():
    """Muestra el dropdown de 'TIPO FINIQUITO' y elige la opción 'DT'."""
    try:
        logging.info("📌 Seleccionando tipo finiquito 'DT'...")

        # 1) Haz clic en "label_tipo" (muestra el select)
        label_tipo = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "label_tipo"))
        )
        label_tipo.click()
        logging.info("✅ Se hizo clic en 'TIPO FINIQUITO'.")

        # 2) Espera a que aparezca el contenedor 'input_tipo'
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "input_tipo"))
        )

        # 3) Haz clic en el select #filtro_tipo
        input_tipo = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "filtro_tipo"))
        )
        input_tipo.click()
        logging.info("✅ Se hizo clic en #filtro_tipo.")

        # 4) Elige la opción "DT" en la lista
        dt_opcion_xpath = "//ul[contains(@class, 'dropdown-content')]/li/span[text()='DT']"
        try:
            dt_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, dt_opcion_xpath))
            )
            dt_option.click()
        except:
            # Forzamos el click vía JavaScript si el .click() nativo falla
            driver.execute_script(
                f"document.evaluate(\"{dt_opcion_xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();"
            )

        time.sleep(2)
        logging.info("✅ Tipo DT filtrado correctamente.")

    except Exception as e:
        logging.error(f"❌ Error al seleccionar tipo DT: {str(e)}")

def seleccionar_estado():
    try:
        logging.info("📌 Seleccionando estado 'Enviado al Representante'...")

        estado_label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "label_estado"))
        )
        estado_label.click()
        logging.info("✅ Se hizo clic en 'ESTADO'.")

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "input_estado"))
        )

        input_estado = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "input_estado"))
        )
        input_estado.click()
        logging.info("✅ Se hizo clic en input_estado.")

        estado_opcion_xpath = "//ul[contains(@class, 'dropdown-content')]/li/span[text()='Enviado al representante']"
        try:
            estado_opcion = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, estado_opcion_xpath))
            )
            estado_opcion.click()
        except:
            driver.execute_script(
                f"document.evaluate(\"{estado_opcion_xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();"
            )

        time.sleep(3)
        logging.info("✅ Estado filtrado correctamente.")

    except Exception as e:
        logging.error(f"❌ Error al seleccionar Estado: {str(e)}")

# AQUÍ está el cambio, llamamos "cambia('rut')" antes de escribir
def buscar_rut_y_filtrar(rut):
    try:
        logging.info(f"🔍 Buscando finiquitos para RUT: {rut}")

        # 1) Forzamos que se muestre el input con la función cambia('rut')
        driver.execute_script("cambia('rut')")
        time.sleep(1)

        # 2) Esperamos el input #filtro_rut
        input_rut = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "filtro_rut"))
        )

        # 3) Si hay algo previo, limpiamos
        if input_rut.get_attribute('value'):
            input_rut.clear()

        # 4) Escribimos el RUT
        input_rut.click()
        input_rut.send_keys(rut)
        driver.execute_script("arguments[0].dispatchEvent(new Event('keyup'))", input_rut)

        time.sleep(2)
        # 5) Seleccionar estado
        seleccionar_tipo_dt()
        seleccionar_estado()
        time.sleep(3)

        # 6) Revisar si hay registros
        registros = driver.find_elements(By.CSS_SELECTOR, "table.highlight tbody tr")
        if not registros:
            logging.info(f"❌ No hay finiquitos disponibles para el RUT {rut}. Pasando al siguiente.")
            return False

        logging.info(f"📄 Se encontraron {len(registros)} registros para el RUT {rut}.")
        return True

    except Exception as e:
        logging.error(f"❌ Error en la búsqueda y filtrado del RUT: {str(e)}")
        return False

def seleccionar_finiquito_mas_reciente():
    try:
        logging.info("📌 Seleccionando el finiquito más reciente...")

        registros = driver.find_elements(By.CSS_SELECTOR, "table.highlight tbody tr")
        if not registros:
            logging.info("❌ No hay finiquitos disponibles.")
            return False

        logging.info(f"📄 {len(registros)} registros encontrados.")

        finiquitos = []
        for registro in registros:
            try:
                checkbox = registro.find_element(By.CSS_SELECTOR, "input.check_listado")
                finiquitos.append(checkbox)
            except:
                continue

        if not finiquitos:
            return False

        driver.execute_script("arguments[0].click();", finiquitos[0])
        logging.info("✅ Se seleccionó el finiquito más reciente.")
        return True

    except Exception as e:
        logging.error(f"❌ Error al seleccionar el finiquito más reciente: {str(e)}")
        return False

def limpiar_rut():
    try:
        input_rut = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "filtro_rut"))
        )
        input_rut.clear()
        driver.execute_script("arguments[0].dispatchEvent(new Event('keyup'))", input_rut)
        logging.info("✅ RUT eliminado.")
        time.sleep(2)  
    except Exception as e:
        logging.error(f"❌ Error al limpiar el RUT: {str(e)}")

def procesar_finiquitos_por_rut(ruts):
    global finiquitos_seleccionados
    for rut in ruts:
        if buscar_rut_y_filtrar(rut):
            if seleccionar_finiquito_mas_reciente():
                finiquitos_seleccionados += 1
                if finiquitos_seleccionados >= 100:
                    cargar_masivo_dt()
                    break
        limpiar_rut()

def cargar_masivo_dt():
    try:
        logging.info("📥 Iniciando Carga Masiva DT...")
        boton_carga = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DtBtn")))
        driver.execute_script("arguments[0].click();", boton_carga)
        logging.info("✅ Carga Masiva DT completada.")
        time.sleep(5)
    except Exception as e:
        logging.error(f"❌ Error al presionar Carga Masiva DT: {str(e)}")

# 🏁 Script
try:
    acceder_a_sigo()
    acceder_a_solicitud_finiquitos()
    ruts_a_buscar = [        "20377094-4", "18711238-9", "17313121-6", "17284160-0", "11861000-8",
        "16682157-6", "21558400-3", "26219984-3", "26351131-K", "10561637-6", "18526700-8", "20403582-2",
        "16939469-5", "16391428-K", "20601312-5", "13556074-K", "19844229-1", "9806190-8", "18049274-7",
        "18530794-8", "10243463-3", "19782685-1", "25931059-8", "16070368-7", "21239969-8", "20580274-6",
        "13133505-9", "18347442-1", "19117060-1", "26137820-5", "26366014-5", "17571894-K", "9794737-6",
        "19600589-7", "16928306-0", "18838659-8", "21014686-5", "6403005-1", "26462461-4", "19428812-3",
        "20400058-1", "18532162-2", "17243198-4", "19784171-0", "17516498-7", "7575506-6", "12643411-1",
        "20635664-2", "27146175-5", "11090857-1", "8408540-5", "15898989-1", "20406222-6", "20517342-0",
        "17625970-1", "19208302-8", "19385908-9", "27119460-9", "20517261-0", "9226432-7", "9169749-1",
        "15419192-5", "13056726-6", "17060452-0", "7470230-9", "13453235-1", "19559408-2", "15388759-4",
        "19733892-K", "10402177-8", "10293229-3", "12841380-4", "10071471-K", "13175187-7", "16006517-6",
        "16150471-8", "9980373-8", "20157101-4", "26919893-1", "8441972-9", "17339809-3", "18969946-8",
        "17383363-6", "10176871-6", "18670691-9", "18816438-2", "11848551-3", "20817498-3", "14138209-8",
        "13026724-6", "10148096-8", "9195430-3", "18528384-4", "13698988-K", "27113544-0", "19544729-2",
        "18976522-3", "18047488-9", "20598834-3", "10230748-8", "12942387-0", "7376716-4", "19247068-4",
        "15400850-0", "19257848-5", "14498577-K", "16940208-6", "19117448-8", "19856865-1", "17400166-9",
        "15985802-2", "12750847-K", "13263629-K", "18168658-8", "13049509-5", "19733635-8", "11668811-5",
        "18178054-1", "17902434-9", "17681974-K", "18676802-7", "18494630-0", "21283021-6", "17484122-5",
        "14353015-9", "26768861-3", "14385764-6", "16932553-7", "10304977-6", "18029959-9", "9170595-8",
        "26679274-3", "18358770-6", "26802028-4", "19921769-0", "19746358-9", "20227897-3", "17451904-8",
        "16631250-7", "20332908-3", "11208836-9", "16786309-4", "26749413-4", "19800620-3", "20202007-0",
        "14091237-9", "14024990-4", "20381786-K", "19134653-K", "18087722-3", "17103520-1", "16248825-2",
        "21574475-2", "20404977-7", "10760539-8", "13668169-9", "18116297-K", "18064594-2", "17555105-0",
        "19711999-3", "11875145-0", "18676747-0", "9383236-1", "26649039-9", "25972222-5", "18632928-7",
        "11405212-4", "20224846-2", "18743018-6", "17052396-2", "13904237-9", "16979539-8", "19915869-4",
        "19500046-8", "25563580-8", "12900011-2", "18026183-4", "27129584-7", "19497301-2", "9382199-8",
        "19117789-4", "11685143-1", "10911158-9", "19548341-8", "9703230-0", "18469744-0", "17689232-3",
        "12354298-3", "20403191-6", "7746355-0", "19427512-9", "26400954-5", "8853018-7", "20597718-K",
        "18364144-1", "26791417-6", "27227638-2", "20059620-K", "16912965-7", "18266426-K", "12820635-3",
        "18180027-5", "19940462-8", "18931215-6", "15887829-1", "27048955-9", "27005291-6", "18323829-9",
        "20330030-1", "17353709-3", "11879799-K", "10107849-3", "27365952-8", "13976446-3", "16054394-9",
        "17191374-8", "17117695-6", "7925441-K", "15421758-4", "19116381-8", "20205503-6", "19219276-5",
        "16103337-5", "24900673-4", "25074316-5", "8344724-9", "18050116-9", "20410774-2", "17668966-8",
        "25691366-6", "20041023-8", "14050223-5", "26588297-8", "18834599-9", "13247909-7", "14441190-0",
        "15930575-9", "12239089-6", "15432766-5", "9905629-0", "19062173-1", "13266760-8", "19369993-6",
        "19934310-6", "28403307-8", "8120059-9", "16363740-5", "9314008-7", "10981563-2", "25654287-0",
        "11725300-7", "12715755-3", "20571236-4", "22176350-5", "27013610-9", "17143878-0", "9775361-K",
        "18519091-9", "15175880-0", "18589971-3", "20461104-1", "16769652-K", "21909473-6", "16903613-6"]  # etc.
    procesar_finiquitos_por_rut(ruts_a_buscar)
finally:
    driver.quit()
    logging.info("🏁 Script finalizado y navegador cerrado.")
