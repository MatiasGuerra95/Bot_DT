
import logging
import os
import time
import traceback
import pandas as pd
import openpyxl
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Configurar logging
log_file = "sigo.log"
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

# Definir la carpeta de descargas
download_folder = os.path.join(os.getcwd(), "finiquitos")

# Configurar opciones de Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Opcional: Para descargas automáticas
prefs = {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True,
    "profile.default_content_settings.popups": 0,
    "filebrowser.download.dir": download_folder
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 🔄 Función para convertir un archivo .xlsx a .csv
def convertir_csv_utf8_a_csv():
    try:
        # Obtener el archivo más reciente en la carpeta de descargas
        archivos = [f for f in os.listdir(download_folder) if f.endswith(".csv")]
        if not archivos:
            logging.error("❌ No se encontraron archivos .xlsx en la carpeta de finiquitos.")
            return None
        
        archivos.sort(key=lambda x: os.path.getmtime(os.path.join(download_folder, x)), reverse=True)
        archivo_mas_reciente = archivos[0]  # Obtener el archivo más reciente

        archivo_original = os.path.join(download_folder, archivo_mas_reciente)

        logging.info(f"🔄 Convirtiendo archivo: {archivo_original} a formato CSV estándar")

        # Leer el archivo Excel y guardarlo en formato CSV
        df = pd.read_csv(archivo_original, delimiter=",", encoding="utf-8")
        df.to_csv(archivo_original, index=False, sep=",", encoding=None) 

        logging.info(f"✅ Archivo convertido y guardado como: {archivo_original}")
        return archivo_original

    except Exception as e:
        logging.error(f"❌ Error al convertir el archivo .xlsx a .csv: {str(e)}")
        return None

try:
    logging.info("🚀 Iniciando script de automatización...")

    # 1️⃣ Acceder a la página de inicio de sesión
    driver.get("http://35.184.233.114/MVS_SIGO/")
    logging.info("🔑 Accediendo a la página de inicio de sesión.")

    usuario_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "user")))
    password_input = driver.find_element(By.ID, "pass")

    usuario_input.send_keys(USUARIO)
    password_input.send_keys(PASSWORD)
    logging.info("✅ Credenciales ingresadas correctamente.")

    driver.find_element(By.ID, "btnLogn").click()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "enlace5")))
    logging.info("🎯 Inicio de sesión exitoso.")

    # 2️⃣ Acceder a la sección "Solicitud de Finiquitos"
    enlace_finiquitos = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "enlace5"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", enlace_finiquitos)
    driver.execute_script("arguments[0].click();", enlace_finiquitos)
    logging.info("📂 Accediendo a 'Solicitud de Finiquitos'.")

    # 3️⃣ Seleccionar la empresa en el dropdown
    try:
        empresa_label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "label_cliente"))
        )
        empresa_label.click()
        logging.info("📌 Se hizo clic en 'EMPRESA CONTRATANTE'.")

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "input_cliente"))
        )

        input_cliente = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "input_cliente"))
        )
        input_cliente.click()
        time.sleep(2)

        empresa_opcion_xpath = "//ul[contains(@class, 'dropdown-content')]/li/span[text()='Empresa de Servicios Transitorios MVS SPA']"

        try:
            empresa_opcion = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, empresa_opcion_xpath))
            )
            empresa_opcion.click()
        except:
            logging.warning("⚠ Intentando seleccionar Empresa usando JavaScript...")
            driver.execute_script(
                f"document.evaluate(\"{empresa_opcion_xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();"
            )

        logging.info("✅ Empresa seleccionada correctamente.")

    except Exception as e:
        screenshot_path = os.path.join(os.getcwd(), "error_empresa.png")
        driver.save_screenshot(screenshot_path)
        error_details = traceback.format_exc()
        logging.error(f"❌ Error al seleccionar empresa: {str(e)}\n{error_details}")

    # 4️⃣ Seleccionar el Estado
    try:
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

        time.sleep(2)
        
    except Exception as e:
        screenshot_path = os.path.join(os.getcwd(), "error_estado.png")
        driver.save_screenshot(screenshot_path)
        error_details = traceback.format_exc()
        logging.error(f"❌ Error al seleccionar Estado: {str(e)}\n{error_details}")

    # 5️⃣ Seleccionar Monto
    try:
        label_monto = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "label_monto"))
        )
        label_monto.click()

        monto_input = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "filtro_monto"))
        )
        monto_input.clear()
        monto_input.send_keys("0")
        driver.execute_script("arguments[0].dispatchEvent(new Event('keyup'))", monto_input)
        time.sleep(3)
        
    except Exception as e:
        screenshot_path = os.path.join(os.getcwd(), "error_monto.png")
        driver.save_screenshot(screenshot_path)
        error_details = traceback.format_exc()
        logging.error(f"❌ Error al seleccionar Monto: {str(e)}\n{error_details}")

    # 6️⃣ Seleccionar checkboxes con manejo de notificaciones y paginación
    try:
        logging.info("📌 Seleccionando hasta 100 finiquitos válidos...")
        selected_count = 0
        max_attempts = 5  # Máximo de intentos de paginación sin progreso

        while selected_count < 100 and max_attempts > 0:
            # Esperar a que la tabla se cargue
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.highlight"))
            )

            # Obtener checkboxes de la página actual
            checkboxes = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.check_listado"))
            )

            logging.info(f"🔍 Encontrados {len(checkboxes)} checkboxes en la página actual.")

            for checkbox in checkboxes:
                if selected_count >= 100:
                    break

                try:
                    if not checkbox.is_selected():
                        # Seleccionar checkbox
                        driver.execute_script("arguments[0].click();", checkbox)

                        # Esperar y verificar si aparece el mensaje toast de error
                        try:
                            toast_error = WebDriverWait(driver, 2).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.toast.red.darken-2"))
                            )
                            if toast_error:
                                logging.warning("⚠ Finiquito duplicado detectado en toast, deseleccionando...")
                                driver.execute_script("arguments[0].click();", checkbox)  # Deseleccionar
                                continue  # No contar este checkbox

                        except:
                            # Si no hay toast, el checkbox es válido
                            selected_count += 1
                            logging.info(f"✅ Checkbox {selected_count} seleccionado válido")

                        time.sleep(0.3)  # Espera corta para estabilidad

                except Exception as e:
                    logging.warning(f"⚠ Error procesando checkbox: {str(e)}")
                    continue

            logging.info(f"📄 Página procesada - Total seleccionados: {selected_count}")

            # Intentar pasar a la siguiente página numérica (sin chevron)
            try:
                current_page_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'active indigo darken-1')]/a"))
                )
                current_page = int(current_page_element.text.strip())
                logging.info(f"📄 Página actual: {current_page}")

                # Buscar el botón de la siguiente página
                next_page_xpath = f"//li[contains(@class, 'indigo darken-1')]/a[contains(text(), '{current_page + 1}')]"
                next_page_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, next_page_xpath))
                )

                if next_page_btn:
                    driver.execute_script("arguments[0].click();", next_page_btn)
                    logging.info(f"➡️ Avanzando a la página {current_page + 1}")

                    WebDriverWait(driver, 10).until(
                        lambda d: int(d.find_element(By.XPATH, "//li[contains(@class, 'active indigo darken-1')]/a").text.strip()) == current_page + 1
                    )
                    time.sleep(2)  # Espera adicional para estabilidad

                else:
                    logging.info("➡️ No hay más páginas disponibles o ya estamos en la última página.")
                    break

            except Exception as e:
                max_attempts -= 1
                logging.warning(f"⚠ Error navegando a la siguiente página. Intentos restantes: {max_attempts}")
                time.sleep(2)

        logging.info(f"✅ Total final de checkboxes seleccionados: {selected_count}")

    except Exception as e:
        screenshot_path = os.path.join(os.getcwd(), "error_checkboxes.png")
        driver.save_screenshot(screenshot_path)
        error_details = traceback.format_exc()
        logging.error(f"❌ Error crítico en selección de checkboxes: {str(e)}\n{error_details}")


    # 7️⃣ Descargar archivo
    try:
        descarga_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "CARGA MASIVA DT"))
        )
        driver.execute_script("arguments[0].click();", descarga_btn)
        logging.info("📥 Descarga iniciada...")

        time.sleep(5)  # Esperar la descarga (puedes ajustar el tiempo según sea necesario)

        # 🔄 Convertir el archivo descargado de .xlsx a .csv
        nuevo_csv = convertir_csv_utf8_a_csv()
        if nuevo_csv:
            logging.info(f"✅ Archivo CSV final para carga: {nuevo_csv}")
        else:
            logging.error("❌ No se pudo convertir el archivo correctamente.")

    except Exception as e:
        screenshot_path = os.path.join(os.getcwd(), "error_descarga.png")
        driver.save_screenshot(screenshot_path)
        error_details = traceback.format_exc()
        logging.error(f"❌ Error al descargar archivo: {str(e)}\n{error_details}")


finally:
    driver.quit()
    logging.info("🏁 Script finalizado y navegador cerrado.")