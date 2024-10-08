import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import io
import logging
from streamlit_option_menu import option_menu
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller


# Set up logging
logging.basicConfig(level=logging.INFO)

def initialize_driver():
    """Initialize the Selenium WebDriver."""
    try:
        # Install chromedriver automatically
        chromedriver_autoinstaller.install()

        options = Options()
        options.headless = False  # Set to True for headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")

        driver = webdriver.Chrome(service=Service(), options=options)
        return driver
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {e}")
        st.error("Driver tidak dapat diinisialisasi. Coba lagi nanti.")
        return None

# Valid URLs for scraping
VALID_URLS = {
    "Shopee": "https://shopee.co.id/product/",
    "Tokopedia": "https://www.tokopedia.com/",
    "Bukalapak": "https://www.bukalapak.com/"
}

def scrape_product(driver, product_url, platform):
    driver.get(product_url)
    try:
        if platform == "Shopee":
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._3e_UQe')))
            product_name = driver.find_element(By.CSS_SELECTOR, 'div._3e_UQe').text
            price = driver.find_element(By.CSS_SELECTOR, 'div._3n5NQd').text
            description = driver.find_element(By.CSS_SELECTOR, 'div._1DpsGB').text
            photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img._1eZ12s')
        elif platform == "Tokopedia":
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.css-1z7w6s2')))
            product_name = driver.find_element(By.CSS_SELECTOR, 'h1.css-1z7w6s2').text
            price = driver.find_element(By.CSS_SELECTOR, 'span.css-o0fgw0').text
            description = driver.find_element(By.CSS_SELECTOR, 'div.css-1c5uq6j').text
            photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img.css-1gk1d34')
        elif platform == "Bukalapak":
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-title')))
            product_name = driver.find_element(By.CSS_SELECTOR, 'h1.product-title').text
            price = driver.find_element(By.CSS_SELECTOR, 'span.price').text
            description = driver.find_element(By.CSS_SELECTOR, 'div.description').text
            photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img.image')

        photos = [img.get_attribute('src') for img in photo_elements]
    except Exception as e:
        logging.error(f"Error scraping {platform}: {e}")
        st.error(f"Error scraping {platform}: {e}")
        return pd.DataFrame(columns=['Product Name', 'Price', 'Description', 'Photos'])

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description],
        'Photos': [photos]
    }
    return pd.DataFrame(data)

def main():
    st.title("Scraping Produk Marketplace")
    st.markdown("### Mengambil data produk dari Shopee, Tokopedia, dan Bukalapak")

    # Sidebar menu
    with st.sidebar:
        selected = option_menu("Menu", ["Home", "Scrape Data"],
                               icons=['house', 'cloud-upload'],
                               menu_icon="cast", default_index=1)

    if selected == "Home":
        st.write("Selamat datang di aplikasi scraping produk!")
        st.write("Pilih menu 'Scrape Data' untuk mulai mengambil data produk.")

    elif selected == "Scrape Data":
        platform = st.selectbox("Pilih Platform", ["Shopee", "Tokopedia", "Bukalapak"])
        product_url = st.text_input("Masukkan URL Produk")

        # Validasi URL
        if product_url and not product_url.startswith(VALID_URLS[platform]):
            st.error("URL tidak valid untuk platform yang dipilih.")
        else:
            if st.button("Scrape Data"):
                driver = initialize_driver()
                if driver is not None:
                    with st.spinner("Mengambil data..."):
                        scraped_data = scrape_product(driver, product_url, platform)
                    driver.quit()

                    if not scraped_data.empty:
                        st.success("Scraping berhasil!")
                        st.write(scraped_data[['Product Name', 'Price', 'Description']])
                        
                        # Display product photos
                        st.subheader("Foto Produk")
                        for photo in scraped_data['Photos'][0]:
                            st.image(photo, use_column_width=True)
                        
                        # Simpan hasil scraping ke CSV
                        csv_io = io.StringIO()
                        scraped_data.to_csv(csv_io, index=False)
                        csv_io.seek(0)
                        
                        st.download_button(
                            label="Download CSV",
                            data=csv_io.getvalue(),
                            file_name="scraped_data.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error("Tidak ada data yang ditemukan untuk URL yang diberikan.")
