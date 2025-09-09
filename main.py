from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

receipt_url = "https://www.coopalleanza3-0.it/authentication/dashboard/scontrini-digitali.html"

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
    print(driver.title)
    driver.quit()