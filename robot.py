import glob
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from dotenv import load_dotenv
import os
import time

# Configuración de logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler("dt_bot.log", mode="w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# Cargar variables de entorno
load_dotenv()
RUT = os.getenv("RUT")
CLAVE_UNICA = os.getenv("CLAVE_UNICA")

# Directorio de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "finiquitos")

def setup_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    service = Service("/usr/local/bin/chromedriver") 
    return webdriver.Chrome(service=service, options=options)

def iniciar_sesion(driver):
    try:
        logger.info("Navegando al portal DT.")
        driver.get("https://midt.dirtrab.cl/welcome")

        # Clic en "Iniciar sesión"
        logger.info("Clic en 'Iniciar sesión'.")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "nuevaSesion"))
        ).click()

        # Ingresar credenciales de Clave Única
        logger.info("Ingresando credenciales.")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "uname"))
        ).send_keys(RUT)
        driver.find_element(By.ID, "pword").send_keys(CLAVE_UNICA)
        driver.find_element(By.ID, "login-submit").click()
        logger.info("Inicio de sesión completado.")

    except Exception as e:
        logger.error(f"Error en el inicio de sesión: {e}")
        raise

def navegar_perfil_empleador(driver):
    try:
        # Seleccionar "Empleador"
        logger.info("Seleccionando 'Empleador'.")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "btn-empleador"))
        ).click()

        # Seleccionar "Empleador Persona Jurídica"
        logger.info("Seleccionando 'Empleador Persona Jurídica'.")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Empleador Persona Jurídica")]'))
        ).click()

        # Seleccionar la empresa
        logger.info("Seleccionando la empresa.")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "76333204-7 EMPRESA DE SERVICIOS TRANSITORIOS MVS SPA")]'))
        ).click()

    except Exception as e:
        logger.error(f"Error navegando al perfil de empleador: {e}")
        raise

def navegar_a_finiquitos_masivos(driver):
    try:
        # Expandir "Contratos de Trabajo y Despido"
        logger.info("Expandiendo 'Contratos de Trabajo y Despido'.")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "accordion-title") and contains(text(), "Contratos de Trabajo y Despido")]'))
        ).click()

        # Seleccionar "Finiquito Laboral Electrónico"
        logger.info("Seleccionando 'Finiquito Laboral Electrónico'.")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Finiquito Laboral Electrónico")]'))
        ).click()

        # Seleccionar "Ingreso de finiquito masivo"
        logger.info("Seleccionando 'Ingreso de finiquito masivo'.")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Ingreso de finiquito masivo")]'))
        ).click()
        logger.info("'Ingreso de finiquito masivo' seleccionado con éxito.")

    except Exception as e:
        logger.error(f"Error navegando a la sección de finiquitos masivos: {e}")
        raise

def obtener_csv_mas_reciente():
        """ Encuentra el archivo CSV más reciente en la carpeta 'finiquitos'. """
        list_of_files = glob.glob(os.path.join(DOWNLOAD_DIR, "Informe DT #*.csv"))
        if not list_of_files:
            logger.error("❌ No se encontró ningún archivo CSV en la carpeta 'finiquitos'.")
            return None
        latest_file = max(list_of_files, key=os.path.getctime)  # Obtener el más reciente
        logger.info(f"📂 Archivo CSV más reciente encontrado: {latest_file}")
        return latest_file

def subir_archivo(driver, file_path):
    """ Sube el archivo CSV más reciente en la página de MiDT. """
    try:
        # Esperar a que la página cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//label[@for='file_upload']"))
        )

        # Intentar encontrar el input file real (oculto)
        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")

        if file_input:
            # Subir el archivo CSV
            file_input.send_keys(file_path)
            logger.info(f"📤 Archivo '{file_path}' cargado correctamente.")

            # Esperar a que el botón 'Cargar Finiquitos' se habilite
            upload_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Cargar finiquitos') and not(@disabled)]"))
            )
            
            # Hacer clic en el botón
            upload_btn.click()
            logger.info("✅ Se hizo clic en 'Cargar Finiquitos'.")
            time.sleep(10)  # Espera adicional para la carga

        else:
            logger.error("❌ No se encontró el input real para la carga del archivo.")

    except Exception as e:
        logger.error(f"❌ Error al subir el archivo: {e}")


def validar_flujo():
    driver = setup_driver()
    try:
        iniciar_sesion(driver)
        navegar_perfil_empleador(driver)
        navegar_a_finiquitos_masivos(driver)

        # Obtener el archivo CSV más reciente
        latest_csv = obtener_csv_mas_reciente()
        if latest_csv:
            subir_archivo(driver, latest_csv)

        logger.info("Flujo validado exitosamente hasta la carga del archivo.")

    except Exception as e:
        logger.error(f"Error validando el flujo: {e}")
    finally:
        driver.quit()
        logger.info("Driver cerrado.")


if __name__ == "__main__":
    validar_flujo()

