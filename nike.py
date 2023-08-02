from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import Select
import random
from time import sleep

x=input('Enter the size: ')
y=input('Enter the quantity: ')

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

# Get list of user agents.
user_agents = user_agent_rotator.get_user_agents()

user_agent = user_agent_rotator.get_random_user_agent()

# Set Chrome options
chrome_options = uc.ChromeOptions()

# Add the argument and make the browser Headless.
#chrome_options.add_argument("--headless")

# Add a random user agent
#chrome_options.add_argument(f'user-agent={user_agent}')

# Change webdriver attribute to avoid detection
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-running-insecure-content")

# chrome_options.add_argument(r"--user-data-dir=C:\Users\hasna\AppData\Local\Google\Chrome\User Data")
# chrome_options.add_argument('--profile-directory=Profile 3')

driver = uc.Chrome(options=chrome_options)

# Perform random mouse movements
action = ActionChains(driver)
action.move_by_offset(random.randint(1,5), random.randint(1,5))
action.perform()
driver.maximize_window()

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
    """
})



# navigate to a webpage
driver.get('https://www.nike.com/launch/t/womens-dunk-low-gold-suede')

input()
# Wait for the page to load
wait = WebDriverWait(driver, 10)

# Perform random mouse movements
action = ActionChains(driver)
action.move_by_offset(random.randint(1,5), random.randint(1,5))
action.perform()

# Add some random sleep time
sleep(random.uniform(2.5, 4.5))

try:
    actions = ActionChains(driver)

    # Wait for the element to be clickable
    btn = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '{}')]".format(x))))

    # Use JavaScript to scroll to the element
    driver.execute_script("arguments[0].scrollIntoView();", btn)

    # Now use ActionChains to perform the click
    actions.move_to_element(btn).click().perform()
except:
    print("error in first button click")

input()

wait = WebDriverWait(driver, 30)
btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Buy')]")))

# Use JavaScript to scroll to the element
driver.execute_script("arguments[0].scrollIntoView();", btn)

# Now use ActionChains to perform the click
actions.move_to_element(btn).click().perform()


try:
    wait = WebDriverWait(driver, 30)
    btn1 = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Cart')]")))

    # Use JavaScript to scroll to the element
    driver.execute_script("arguments[0].scrollIntoView();", btn1)

    # Now use ActionChains to perform the click
    actions.move_to_element(btn1).click().perform()
except:
    driver.get('https://www.nike.com/cart')


try:
    dropdown_element =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[4]/div/div[1]/div[1]/main/div[2]/div[1]/div[1]/div[2]/div/div[1]/div/div[1]/div[1]/div[3]/div[2]/div/select")))

    # # Open the dropdown
    # dropdown_element.click()

    # # Wait for the option to be visible
    # option_locator = (By.XPATH, f"//option[@value='{y}']")
    # option_element = WebDriverWait(driver, 15).until(EC.visibility_of_element_located(option_locator))
    # Select the value
  #  option_element.click()
    selectD = Select(dropdown_element)
    sleep(3)

    selectD.select_by_value('{}'.format(y))  
except:
    print('Entered quantity is not available! So just buying default quantity')
    pass


sleep(3)
wait = WebDriverWait(driver, 30)
btn1 = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Checkout')]")))

# Use JavaScript to scroll to the element
driver.execute_script("arguments[0].scrollIntoView();", btn1)

# Now use ActionChains to perform the click
actions.move_to_element(btn1).click().perform()



# driver.get('https://www.nike.com/checkout')


#to fill the form
name='John'
lastname='Doe'
address='361 congressional lane Rockville'
email='johndoe@gmail.com'
phone='(148) 445-7879'  #junk daal dein valid 


try:
    addressShow =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#addressSuggestionOptOut")))
    addressShow.click()
    fName =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#lastName")))
    fName.clear()
    fName.send_keys(name)
    lName =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#lastName")))
    lName.clear()
    lName.send_keys(lastname)
    addressI =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#lastName")))
    addressI.clear()
    addressI.send_keys(address)
    cityI =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#city")))
    cityI.clear()
    cityI.send_keys('Lahore')

    pCode =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#postalCode")))
    pCode.clear()
    pCode.send_keys('20852')

    dropdown_element = driver.find_element(By.ID,"state")

    # Create a Select object from the dropdown element
    dropdown = Select(dropdown_element)

    # Select an option by its visible text
    dropdown.select_by_visible_text("Maryland")

    emailL =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#email")))
    emailL.clear()
    emailL.send_keys(email)
    phoneL =  WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#email")))
    phoneL.clear()
    phoneL.send_keys(phone)
except:
    pass

try:
    wait = WebDriverWait(driver, 30)
    btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Save')]")))

    # Use JavaScript to scroll to the element
    driver.execute_script("arguments[0].scrollIntoView();", btn)

    # Now use ActionChains to perform the click
    actions.move_to_element(btn).click().perform()
except:
    print("1st save")

try:
    wait = WebDriverWait(driver, 30)
    btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#modal-root > div > div > div > div > div > section > div.css-1hkd4t6.e1eje3q30 > div > button")))

    # Use JavaScript to scroll to the element
    driver.execute_script("arguments[0].scrollIntoView();", btn)

    # Now use ActionChains to perform the click
    actions.move_to_element(btn).click().perform()
except:
    print("2nd save")
    #modal-root > div > div > div > div > div > section > div.css-1hkd4t6.e1eje3q30 > div > button


# input()
