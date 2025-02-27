import logging
import os
import time
import traceback
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

# Timeouts estándar
SHORT_TIMEOUT = 5
LONG_TIMEOUT = 15

# Reintentos estándar
MAX_REINTENTOS_BOTON = 5
MAX_REINTENTOS_GLOBAL = 5

# Cargar variables de entorno y credenciales
load_dotenv()
USUARIO = os.getenv("MVS_SIGO_USER")
PASSWORD = os.getenv("MVS_SIGO_PASS")

# Configurar logging
log_file = "sigo_subido.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Lista de IDs a procesar
FINIQUITO_IDS = [

]

###############################
# FUNCIONES AUXILIARES
###############################
def iniciar_sesion(driver):
    """
    Entra al sitio y hace login con las credenciales.
    """
    driver.get("http://35.184.233.114/MVS_SIGO/")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "user")))
    driver.find_element(By.ID, "user").send_keys(USUARIO)
    driver.find_element(By.ID, "pass").send_keys(PASSWORD)
    driver.find_element(By.ID, "btnLogn").click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "enlace5")))
    logging.info("Sesión iniciada correctamente.")

def entrar_a_solicitud_finiquitos(driver):
    """
    Hace clic en 'Solicitud de Finiquitos' para mostrar la tabla principal.
    """
    enlace_finiquitos = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "enlace5"))
    )
    driver.execute_script("arguments[0].click();", enlace_finiquitos)
    logging.info("Entrando a 'Solicitud de Finiquitos'...")

def filtrar_por_id(driver, finiquito_id):
    """
    Activa el filtro por ID, escribe el ID y presiona ENTER.
    """
    label_id = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "label_id"))
    )
    label_id.click()

    input_id = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "filtro_id"))
    )
    input_id.clear()
    input_id.send_keys(str(finiquito_id))
    time.sleep(2)
    input_id.send_keys(Keys.ENTER)  # Simular la tecla ENTER

    # Esperar a que la fila del ID esté presente en la tabla
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f"//tr[contains(@onclick, 'solicitudes.Busca({finiquito_id})')]"))
        )
    except TimeoutException:
        logging.warning(f"La tabla no mostró el ID {finiquito_id} tras filtrar.")

    
def verificar_avanza_pago(driver):
    """
    Versión optimizada: Añade espera explícita y chequeo de visibilidad real.
    """
    try:
        # Esperar a que el botón esté visible y con texto exacto
        boton_avanzar = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@id='btnrgt6' and normalize-space(text())='Avanzar a pago']")
            )
        )
        logging.info("Botón 'Avanzar a pago' detectado correctamente.")
        return True
    except TimeoutException:
        return False
    except Exception as e:
        logging.warning(f"Error al verificar botón: {str(e)}")
        return False
    
def entrar_detalle_finiquito(driver, finiquito_id):
    """
    Añadir espera para confirmar que el modal se cargó completamente.
    """
    fila_xpath = f"//tr[contains(@onclick, 'solicitudes.Busca({finiquito_id})')]"
    try:
        # Hacer clic en la fila
        fila_element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, fila_xpath))
        )
        fila_element.click()
        
        # Esperar a que el modal esté completamente cargado
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "btnrgt4"))  # Usar elemento del modal
        )
        logging.info(f"Modal del ID {finiquito_id} cargado correctamente.")
        return True
    except TimeoutException:
        logging.warning(f"Modal no se cargó para ID {finiquito_id}.")
        return False
    
def presionar_subido_dt_reintentos(driver, max_intentos=5):
    """
    Intenta presionar el botón 'Subido al portal DT' hasta 'max_intentos' veces
    si salen toasts rojos/inesperados. Al primer toast verde ('Datos guardados'),
    se detiene. Si ve 'Finiquito sin firma generado', retorna 'SIN_FIRMA'.
    
    Además, si el botón 'Avanzar a pago' (#btnrgt6) está presente,
    retornamos 'SKIP' para saltar este finiquito.
    """
    # 1) Ver si está el botón 'Avanzar a pago'
    if verificar_avanza_pago(driver):
        logging.info("El botón 'Avanzar a pago' está presente => se omite este finiquito (SKIP).")
        refrescar_y_volver(driver)
        return "SKIP"

    # 2) Intentar ubicar y presionar #btnrgt4
    xpath_subido = "//div[@id='btnrgt4' and normalize-space(text())='Subido al portal DT']"

    for intento in range(1, max_intentos + 1):
        logging.info(f"[Reintento {intento}/{max_intentos}] Presionando 'Subido al portal DT'...")

        try:
            subido_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath_subido))
            )
        except TimeoutException:
            logging.warning("No se encontró el botón 'Subido al portal DT' (#btnrgt4).")
            return "NO_BUTTON"

        subido_btn.click()
        logging.info("Se hizo clic en 'Subido al portal DT'.")

        # Esperar toast
        toast_text = esperar_y_leer_toast(driver)
        if not toast_text:
            logging.warning("No apareció ningún toast tras el clic. Reintentando...")
            time.sleep(1)
            continue

        toast_lower = toast_text.lower()
        if "datos guardados" in toast_lower:
            return "DATOS_GUARDADOS"
        elif "finiquito sin firma generado" in toast_lower:
            return "SIN_FIRMA"
        else:
            logging.warning(f"Toast inesperado: '{toast_text}'. Reintento...")
            time.sleep(1)
            continue

    return "OTRO_ERROR"


def esperar_y_leer_toast(driver):
    """
    Espera hasta 5s a que aparezca un toast dentro de #toast-container .toast.
    Devuelve el texto del toast o None si no aparece.
    """
    try:
        toast_div = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#toast-container .toast"))
        )
        return toast_div.text.strip()
    except TimeoutException:
        return None

def cerrar_modal(driver):
    """
    Espera 5s a que desaparezca el botón Subido al portal DT (#btnrgt4) 
    para confirmar el cierre del modal.
    """
    try:
        WebDriverWait(driver, 5).until_not(
            EC.visibility_of_element_located((By.ID, "btnrgt4"))
        )
    except TimeoutException:
        pass  # Si no cierra, no hay más que hacer

def refrescar_y_volver(driver):
    """
    Refresca la página y vuelve a 'Solicitud de Finiquitos'.
    """
    driver.refresh()
    entrar_a_solicitud_finiquitos(driver)
    time.sleep(2)

###############################
# LÓGICA PRINCIPAL
###############################
def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1) Iniciar sesión y entrar a la página de Finiquitos
        iniciar_sesion(driver)
        entrar_a_solicitud_finiquitos(driver)

        for finiquito_id in FINIQUITO_IDS:
            try:
                logging.info(f"=== Procesando ID: {finiquito_id} ===")

                max_reintentos_global = 5
                for intento_global in range(1, max_reintentos_global + 1):
                    logging.info(f"(ID {finiquito_id}) Intento global {intento_global}/{max_reintentos_global}")

                    # Filtrar por ID y entrar al detalle
                    filtrar_por_id(driver, finiquito_id)
                    if not entrar_detalle_finiquito(driver, finiquito_id):
                        # No se halló la fila -> pasamos al siguiente ID
                        break

                    # Presionar con reintentos
                    resultado = presionar_subido_dt_reintentos(driver, max_intentos=5)

                    if resultado == "SKIP":
                        # 'Avanzar a pago' => no hace falta nada
                        break  # pasa al siguiente ID

                    elif resultado == "NO_BUTTON":
                        logging.info("No hay botón 'Subido al portal DT'. Pasamos al siguiente ID.")
                        break

                    elif resultado == "DATOS_GUARDADOS":
                        logging.info("Éxito: 'Datos guardados'. Cerramos modal y refrescamos.")
                        cerrar_modal(driver)
                        refrescar_y_volver(driver)
                        break  # pasa al siguiente ID

                    elif resultado == "SIN_FIRMA":
                        logging.warning("Finiquito sin firma => reintentamos desde cero.")
                        cerrar_modal(driver)
                        refrescar_y_volver(driver)
                        continue  # reintenta el mismo ID en el intento_global

                    else:  # "OTRO_ERROR"
                        logging.warning("Toast de error repetido o no se logró éxito => reintentamos globalmente.")
                        cerrar_modal(driver)
                        refrescar_y_volver(driver)
                        continue  # reintenta el mismo ID en el intento_global

                else:
                    # Si completó los 5 intentos_global sin break => no logramos éxito
                    logging.error(f"No se logró 'Datos guardados' para ID {finiquito_id} tras {max_reintentos_global} reintentos globales.")

            except Exception as e_id:
                logging.error(f"Error con ID {finiquito_id}: {str(e_id)}")
                traceback.print_exc()
                # Continúa con siguiente ID

        logging.info("Proceso finalizado para todos los IDs.")

    except Exception as e:
        logging.error(f"Error general: {str(e)}")
        traceback.print_exc()

    finally:
        driver.quit()
        logging.info("Navegador cerrado.")

if __name__ == "__main__":
    main()