import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import io
import time
from streamlit_option_menu import option_menu
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def initialize_driver():
    try:
        options = Options()
        options.headless = False  # Set to True for headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")

        # Initialize the driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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

def scrape_shopee(product_url, progress):
    driver = initialize_driver()
    if driver is None:
        return pd.DataFrame()

    driver.get(product_url)
    progress.progress(20)  # Update progress

    time.sleep(2)  # Wait for page to load
    progress.progress(40)  # Update progress

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._3e_UQe')))
        product_name = driver.find_element(By.CSS_SELECTOR, 'div._3e_UQe').text
        price = driver.find_element(By.CSS_SELECTOR, 'div._3n5NQd').text
        description = driver.find_element(By.CSS_SELECTOR, 'div._1DpsGB').text
        
        photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img._1eZ12s')
        photos = [img.get_attribute('src') for img in photo_elements]
        
        variant_elements = driver.find_elements(By.CSS_SELECTOR, 'div._3X1D2m')
        variants = [variant.text for variant in variant_elements]

        progress.progress(80)  # Update progress
    except Exception as e:
        logging.error(f"Error scraping Shopee: {e}")
        st.error(f"Terjadi kesalahan saat mengambil data dari Shopee: {e}")
        return pd.DataFrame(columns=['Product Name', 'Price', 'Description', 'Variants', 'Photos'])
    finally:
        driver.quit()
        progress.progress(100)  # Complete progress

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description],
        'Variants': [', '.join(variants)],
        'Photos': [photos]
    }
    return pd.DataFrame(data)

def scrape_tokopedia(product_url, progress):
    driver = initialize_driver()
    if driver is None:
        return pd.DataFrame()

    driver.get(product_url)
    progress.progress(20)  # Update progress

    time.sleep(2)
    progress.progress(40)  # Update progress

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.css-1z7w6s2')))
        product_name = driver.find_element(By.CSS_SELECTOR, 'h1.css-1z7w6s2').text
        price = driver.find_element(By.CSS_SELECTOR, 'span.css-o0fgw0').text
        description = driver.find_element(By.CSS_SELECTOR, 'div.css-1c5uq6j').text
        
        photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img.css-1gk1d34')
        photos = [img.get_attribute('src') for img in photo_elements]
        
        variant_elements = driver.find_elements(By.CSS_SELECTOR, 'div.css-1e8u7w8')
        variants = [variant.text for variant in variant_elements]

        progress.progress(80)  # Update progress
    except Exception as e:
        logging.error(f"Error scraping Tokopedia: {e}")
        st.error(f"Terjadi kesalahan saat mengambil data dari Tokopedia: {e}")
        return pd.DataFrame(columns=['Product Name', 'Price', 'Description', 'Variants', 'Photos'])
    finally:
        driver.quit()
        progress.progress(100)  # Complete progress

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description],
        'Variants': [', '.join(variants)],
        'Photos': [photos]
    }
    return pd.DataFrame(data)

def scrape_bukalapak(product_url, progress):
    driver = initialize_driver()
    if driver is None:
        return pd.DataFrame()

    driver.get(product_url)
    progress.progress(20)  # Update progress

    time.sleep(2)
    progress.progress(40)  # Update progress

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-title')))
        product_name = driver.find_element(By.CSS_SELECTOR, 'h1.product-title').text
        price = driver.find_element(By.CSS_SELECTOR, 'span.price').text
        description = driver.find_element(By.CSS_SELECTOR, 'div.description').text
        
        photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img.image')
        photos = [img.get_attribute('src') for img in photo_elements]
        
        variant_elements = driver.find_elements(By.CSS_SELECTOR, 'div.variant-title')
        variants = [variant.text for variant in variant_elements]

        progress.progress(80)  # Update progress
    except Exception as e:
        logging.error(f"Error scraping Bukalapak: {e}")
        st.error(f"Terjadi kesalahan saat mengambil data dari Bukalapak: {e}")
        return pd.DataFrame(columns=['Product Name', 'Price', 'Description', 'Variants', 'Photos'])
    finally:
        driver.quit()
        progress.progress(100)  # Complete progress

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description],
        'Variants': [', '.join(variants)],
        'Photos': [photos]
    }
    return pd.DataFrame(data)

def main():
    st.title("Scraping Produk Marketplace")
    st.markdown("### Mengambil data produk dari Shopee, Tokopedia, dan Bukalapak")

    with st.sidebar:
        selected = option_menu("Menu", 
                               ["Home", "Scrape Data"],
                               icons=['house', 'cloud-upload'],
                               menu_icon="cast", 
                               default_index=1)

    if selected == "Home":
        st.write("Selamat datang di aplikasi scraping produk!")
        st.write("Pilih menu 'Scrape Data' untuk mulai mengambil data produk.")

    elif selected == "Scrape Data":
        platform = st.selectbox("Pilih Platform", ["Shopee", "Tokopedia", "Bukalapak"])
        product_url = st.text_input("Masukkan URL Produk")

        if product_url and not product_url.startswith(VALID_URLS[platform]):
            st.error("URL tidak valid untuk platform yang dipilih.")
        else:
            if st.button("Scrape Data"):
                progress = st.progress(0)  # Initialize progress bar
                if platform == "Shopee":
                    scraped_data = scrape_shopee(product_url, progress)
                elif platform == "Tokopedia":
                    scraped_data = scrape_tokopedia(product_url, progress)
                elif platform == "Bukalapak":
                    scraped_data = scrape_bukalapak(product_url, progress)
                else:
                    st.error("Platform tidak dikenal")
                    return
                
                if not scraped_data.empty:
                    st.success("Scraping berhasil!")
                    st.write(scraped_data[['Product Name', 'Price', 'Description', 'Variants']])
                    
                    st.subheader("Foto Produk")
                    for photo in scraped_data['Photos'][0]:
                        st.image(photo, use_column_width=True)
                    
                    # Save scraping results to CSV
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
            else:
                st.error("Harap masukkan URL produk.")

if __name__ == "__main__":
    main()
