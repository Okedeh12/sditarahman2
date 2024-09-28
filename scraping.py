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
        options.headless = False  # Set to False for debugging
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--log-level=ALL")
        options.add_argument("--log-path=/tmp/chromedriver.log")

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

def scrape_shopee(product_url):
    driver = initialize_driver()
    if driver is None:
        return pd.DataFrame(), None

    driver.get(product_url)
    time.sleep(2)  # Wait for page to load

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._3e_UQe')))
        product_name = driver.find_element(By.CSS_SELECTOR, 'div._3e_UQe').text
        price = driver.find_element(By.CSS_SELECTOR, 'div._3n5NQd').text
        description = driver.find_element(By.CSS_SELECTOR, 'div._1DpsGB').text
        
        # Get product photos
        photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img._1eZ12s')
        photos = [img.get_attribute('src') for img in photo_elements]
        
        # Get product variants
        variant_elements = driver.find_elements(By.CSS_SELECTOR, 'div._3X1D2m')
        variants = [variant.text for variant in variant_elements]
        
        # Screenshot
        screenshot = driver.get_screenshot_as_png()
    except Exception as e:
        st.error(f"Error scraping Shopee: {e}")
        return pd.DataFrame(columns=['Product Name', 'Price', 'Description', 'Variants', 'Photos']), None
    finally:
        driver.quit()

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description],
        'Variants': [', '.join(variants)],
        'Photos': [photos]
    }
    return pd.DataFrame(data), screenshot

def scrape_tokopedia(product_url):
    driver = initialize_driver()
    if driver is None:
        return pd.DataFrame(), None

    driver.get(product_url)
    time.sleep(2)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.css-1z7w6s2')))
        product_name = driver.find_element(By.CSS_SELECTOR, 'h1.css-1z7w6s2').text
        price = driver.find_element(By.CSS_SELECTOR, 'span.css-o0fgw0').text
        description = driver.find_element(By.CSS_SELECTOR, 'div.css-1c5uq6j').text
        
        photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img.css-1gk1d34')
        photos = [img.get_attribute('src') for img in photo_elements]
        
        variant_elements = driver.find_elements(By.CSS_SELECTOR, 'div.css-1e8u7w8')
        variants = [variant.text for variant in variant_elements]
        
        # Screenshot
        screenshot = driver.get_screenshot_as_png()
    except Exception as e:
        st.error(f"Error scraping Tokopedia: {e}")
        return pd.DataFrame(columns=['Product Name', 'Price', 'Description', 'Variants', 'Photos']), None
    finally:
        driver.quit()

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description],
        'Variants': [', '.join(variants)],
        'Photos': [photos]
    }
    return pd.DataFrame(data), screenshot

def scrape_bukalapak(product_url):
    driver = initialize_driver()
    if driver is None:
        return pd.DataFrame(), None

    driver.get(product_url)
    time.sleep(2)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-title')))
        product_name = driver.find_element(By.CSS_SELECTOR, 'h1.product-title').text
        price = driver.find_element(By.CSS_SELECTOR, 'span.price').text
        description = driver.find_element(By.CSS_SELECTOR, 'div.description').text
        
        photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img.image')
        photos = [img.get_attribute('src') for img in photo_elements]
        
        variant_elements = driver.find_elements(By.CSS_SELECTOR, 'div.variant-title')
        variants = [variant.text for variant in variant_elements]
        
        # Screenshot
        screenshot = driver.get_screenshot_as_png()
    except Exception as e:
        st.error(f"Error scraping Bukalapak: {e}")
        return pd.DataFrame(columns=['Product Name', 'Price', 'Description', 'Variants', 'Photos']), None
    finally:
        driver.quit()

    data = {
        'Product Name': [product_name],
        'Price': [price],
        'Description': [description],
        'Variants': [', '.join(variants)],
        'Photos': [photos]
    }
    return pd.DataFrame(data), screenshot

def main():
    st.title("Aplikasi Scraping Produk Marketplace")
    st.markdown("### Mengambil data produk dari Shopee, Tokopedia, dan Bukalapak")

    # Sidebar menu
    with st.sidebar:
        selected = option_menu("Menu Utama",
                               ["Home", "Scrape Data"],
                               icons=['house', 'cloud-upload'],
                               menu_icon="cast",
                               default_index=0,
                               styles={
                                   "container": {"padding": "5!important", "background-color": "#f0f2f5"},
                                   "icon": {"font-size": "20px"},
                                   "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "#000000"},
                                   "nav-link-selected": {"background-color": "#c4e3ff"},
                               })

    if selected == "Home":
        st.write("Selamat datang di aplikasi scraping produk!")
        st.write("Pilih menu 'Scrape Data' untuk mulai mengambil data produk.")

    elif selected == "Scrape Data":
        platform = st.selectbox("Pilih Platform", ["Shopee", "Tokopedia", "Bukalapak"])
        product_url = st.text_input("Masukkan URL Produk")

        # Validate URL
        if product_url and not product_url.startswith(VALID_URLS[platform]):
            st.error("URL tidak valid untuk platform yang dipilih.")
        else:
            if st.button("Scrape Data"):
                with st.spinner("Sedang melakukan scraping..."):
                    if platform == "Shopee":
                        scraped_data, screenshot = scrape_shopee(product_url)
                    elif platform == "Tokopedia":
                        scraped_data, screenshot = scrape_tokopedia(product_url)
                    elif platform == "Bukalapak":
                        scraped_data, screenshot = scrape_bukalapak(product_url)
                    else:
                        st.error("Platform tidak dikenal")
                        return
                
                if not scraped_data.empty:
                    st.success("Scraping berhasil!")
                    st.write(scraped_data[['Product Name', 'Price', 'Description', 'Variants']])
                    
                    # Display product photos
                    st.subheader("Foto Produk")
                    for photo in scraped_data['Photos'][0]:
                        st.image(photo, use_column_width=True)
                    
                    # Display screenshot of the scraping process
                    st.subheader("Tampilan Halaman Saat Scraping")
                    st.image(screenshot, use_column_width=True)

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
