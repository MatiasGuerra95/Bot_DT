import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time

# Cargar las credenciales desde .env
load_dotenv()

RUT = os.getenv("RUT")
CLAVE_UNICA = os.getenv("CLAVE_UNICA")
ARCHIVO_CSV = os.getenv("ARCHIVO_CSV")

def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Puedes agregar más configuraciones si lo necesitas
    driver = webdriver.Chrome(executable_path="ruta/a/chromedriver", options=options)
    return driver

def cargar_archivo_dt():
    driver = iniciar_driver()
    try:
        # Accede a la página principal
        driver.get("https://midt.dirtrab.cl/welcome")
        
        # Click en "Iniciar sesión"
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Iniciar sesión")]'))
        ).click()
        
        # Acceso a Clave Única
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "rut"))
        )
        driver.find_element(By.ID, "rut").send_keys(RUT)
        driver.find_element(By.ID, "clave").send_keys(CLAVE_UNICA)
        driver.find_element(By.ID, "btn_ingresar").click()
        
        # Navegar a la carga masiva
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Carga Masiva")]'))
        ).click()

        # Subir archivo
        upload_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "campo_subir_archivo"))
        )
        upload_field.send_keys(ARCHIVO_CSV)

        # Confirmar
        driver.find_element(By.ID, "btn_confirmar").click()
        print("Archivo cargado exitosamente.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    cargar_archivo_dt()
