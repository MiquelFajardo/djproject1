from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User

class MySeleniumTests(StaticLiveServerTestCase):
    # carregar una BD de test
    #fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
	# Crear el superusuari
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        cls.selenium.quit()
        super().tearDownClass()

    def login(self, username, password):
        selenium = self.selenium
        selenium.get(f"{self.live_server_url}/admin/")
        # login
        selenium.find_element(By.NAME, "username").send_keys(username)
        selenium.find_element(By.NAME, "password").send_keys(password)
        selenium.find_element(By.XPATH, "//input[@type='submit']").click()

    def test(self):
        # Login superusuari
        s = self.selenium
        self.login("isard","pirineus")
        print("Login superusuari")

        # Crear usuari staff
        s.find_element(By.LINK_TEXT, "Users").click()
        s.find_element(By.LINK_TEXT, "ADD USER").click()
        s.find_element(By.NAME, "username").send_keys("staff")
        s.find_element(By.NAME, "password1").send_keys("pirineus_staff")
        s.find_element(By.NAME, "password2").send_keys("pirineus_staff")
        s.find_element(By.NAME, "_save").click()
        s.find_element(By.NAME, "is_staff").click()
        select = Select(s.find_element(By.ID, "id_user_permissions_from"))
        select.select_by_visible_text("Authentication and Authorization | user | Can view user")
        s.find_element(By.CSS_SELECTOR, "#id_user_permissions_add").click()
        s.find_element(By.NAME, "_save").click()
        print("Usuari staff creat")

        # Crear 3 usuaris
        for i in range(1, 4):
           s.find_element(By.LINK_TEXT, "ADD USER").click()
           s.find_element(By.NAME, "username").send_keys(f"usuari{i}")
           s.find_element(By.NAME, "password1").send_keys("pirineus_usuari")
           s.find_element(By.NAME, "password2").send_keys("pirineus_usuari")
           s.find_element(By.NAME, "_save").click()
           s.find_element(By.NAME, "_save").click()
           print(f"usuari{i} creat")

        # Logout superusuari
        s.find_element(By.XPATH, "//form[@id='logout-form']//button[@type='submit']").click()
        print("Superusuari logout")

        # Login staff
        self.login("staff", "pirineus_staff")
        print("Login staff")

        # Comprvoar que pot veure els usuaris
        s.find_element(By.LINK_TEXT, "Users").click()
        WebDriverWait(s, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#result_list tbody tr th.field-username a")))
        llista_usuaris = [u.text for u in s.find_elements(By.CSS_SELECTOR, "#result_list tbody tr th.field-username a")]
        print("Usuaris visbles per staff:", llista_usuaris)
        self.assertIn("usuari1", " ".join(llista_usuaris))
        self.assertIn("usuari2", " ".join(llista_usuaris))
        self.assertIn("usuari3", " ".join(llista_usuaris))

        # Comprovar que no pot afegir usuaris
        try:
           s.find_element(By.LINK_TEXT, "ADD USER")
           pot_afegir = True
        except:
           pot_afegir = False

        self.assertFalse(pot_afegir, "El usuari no pot afegir usuaris")
        print(f"El usuari staff pot crear usuaris: {pot_afegir}")
