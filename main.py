import math
import random
from dotenv import load_dotenv
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

receipt_url = "https://www.coopalleanza3-0.it/authentication/dashboard/scontrini-digitali.html"

# --- 1) Movimento fluido nativo con W3C Actions ---
try:
    from selenium.webdriver.common.actions.action_builder import ActionBuilder
    from selenium.webdriver.common.actions.pointer_input import PointerInput
    W3C_AVAILABLE = True
except Exception:
    W3C_AVAILABLE = False

def smooth_move_to_element(driver, element, duration_ms=800):
    """
    Sposta il mouse verso il centro di 'element' con una transizione fluida
    (richiede Selenium 4 + W3C actions).
    """
    if not W3C_AVAILABLE:
        # Fallback ai micro-passi se W3C non disponibile
        human_like_move_to_element(driver, element, duration=duration_ms/1000.0)
        return

    # Porta l'elemento a vista
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", element)
    rect = element.rect
    target_x = int(rect["x"] + rect["width"] / 2)
    target_y = int(rect["y"] + rect["height"] / 2)

    # Costruisci la sequenza W3C: un solo pointer move con durata
    mouse = PointerInput("mouse" , "mouse")
    actions = ActionBuilder(driver, mouse=mouse)
    # move relativo alla viewport con durata (ms)
    mouse.create_pointer_move(duration=duration_ms, x=target_x, y=target_y)
    actions.perform()

# --- 2) Movimento a micro-passi con traiettoria curva + jitter ---
def human_like_move_to_element(driver, element, duration=0.8, steps=30, jitter_px=2):
    """
    Sposta il mouse 'a mano' verso il centro dell'elemento con piccoli spostamenti,
    seguendo una curva morbida e aggiungendo un po' di jitter.
    Compatibile ovunque (ActionChains).
    """
    # Assicurati che l'elemento sia visibile
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", element)
    rect = element.rect
    cx = rect["x"] + rect["width"] / 2
    cy = rect["y"] + rect["height"] / 2

    # Parti da un punto vicino ma fuori dal centro (per simulare avvicinamento)
    start_offset = (-rect["width"] * 0.4, -rect["height"] * 0.4)
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(element, int(start_offset[0]), int(start_offset[1])).pause(0.05)

    # Traiettoria curva (ease-in-out) verso il centro dell’elemento
    def ease_in_out(t: float) -> float:
        return 0.5 * (1 - math.cos(math.pi * t))

    for i in range(1, steps + 1):
        t = i / steps
        e = ease_in_out(t)
        # Punto intermedio tra start_offset e (0,0) (cioè il centro dell'elemento)
        x_off = int(start_offset[0] * (1 - e))
        y_off = int(start_offset[1] * (1 - e))

        # Jitter leggero
        x_off += random.randint(-jitter_px, jitter_px)
        y_off += random.randint(-jitter_px, jitter_px)

        actions.move_to_element_with_offset(element, x_off, y_off).pause(duration / steps)

    actions.perform()

# --- Esempio d'uso nel tuo main ---
def move_and_click_accept(driver):
    # Aspetta il bottone e simula il movimento realistico, poi click
    accept = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )

    # Prova prima il movimento fluido W3C, altrimenti fallback ai micro-passi
    smooth_move_to_element(driver, accept, duration_ms=900)
    # oppure: human_like_move_to_element(driver, accept, duration=0.9, steps=32, jitter_px=2)

    accept.click()

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.coopalleanza3-0.it/")
    try:
        # Attendi fino a 10 secondi che il bottone diventi cliccabile
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_button.click()
        print("✅ Cookie banner accettato!")
    except Exception as e:
        print("⚠️ Nessun banner trovato o errore:", e)
    WebDriverWait(driver, 10).until(EC.invisibility_of_element((By.ID, "onetrust-banner-sdk")))
    signin_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Accedi")
    actions = ActionChains(driver)
    actions.move_to_element(signin_button).perform()
    #smooth_move_to_element(driver, signin_button, duration_ms=900)
    sleep(5)
    signin_button.click()

    # --- Login ---

    sleep(5)
    input_email = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
    input_password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
    load_dotenv()
    actions.move_to_element(input_email).click().perform()
    sleep(0.7)
    input_email.send_keys(os.getenv("USERNAME"))
    sleep(2)
    input_password.send_keys(os.getenv("PASSWORD"))
    actions.move_to_element(input_password).click().perform()
    sleep(1.3)
    driver.execute_script("window.scrollBy(0, 150);")
    sleep(1.3)
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
    driver.switch_to.default_content()
    sleep(3)
    signin_button = driver.find_element(By.CSS_SELECTOR, "input.btn")
    actions.move_to_element(signin_button).click().perform()
    sleep(10)

    # --- Accesso all'area personale e download scontrini ---
    user_icon = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.dropdown-toggle"))
        )
    
    actions.move_to_element(user_icon).click().perform()
    sleep(2.3)

    receipt_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.linkable:nth-child(2) > div:nth-child(1)")))
    actions.move_to_element(receipt_option).click().perform()
    sleep(10)

    print(driver.title)
    driver.quit()