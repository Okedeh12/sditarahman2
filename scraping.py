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

# Sitemap yang berisi URL produk yang valid untuk scraping
VALID_URLS = {
    "Shopee": "https://shopee.co.id/product/",
    "Tokopedia": "https://www.tokopedia.com/",
    "Bukalapak": "https://www.bukalapak.com/"
}

def initialize_driver():
    options = Options()
    options.headless = True  # Mode headless untuk menjalankan Chrome tanpa UI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_shopee(product_url):
    driver = initialize_driver()
    driver.get(product_url)
    time.sleep(2)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._3e_UQe')))
        
        product_name = driver.find_element(By.CSS_SELECTOR, 'div._3e_UQe').text
        price = driver.find_element(By.CSS_SELECTOR, 'div._3n5NQd').text
        description = driver.find_element(By.CSS_SELECTOR, 'div._1DpsGB').text
        
        photo_elements = driver.find_elements(By.CSS_SELECTOR, 'img._1eZ12s')
        photos = [img.get_attribute('src') for img in photo_elements]
        
        variant_elements = driver.find_elements(By.CSS_SELECTOR, 'div._3X1D2m')
        variants = [variant.text for variant in variant_elements]
    except Exception as e:
        st.error(f"Error scraping Shopee: {e}")
        return pd.DataFrame(columns=['Product Name', 'Price', 'Description', 'Variants', 'Photos'])
    finally:
        driver.quit()

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

    # Sidebar menu
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

        # Validasi URL
        if product_url:
            if platform == "Shopee" and not ("shopee.co.id/product/" in product_url):
                st.error("URL tidak valid untuk platform Shopee.")
            elif platform == "Tokopedia" and not ("tokopedia.com" in product_url):
                st.error("URL tidak valid untuk platform Tokopedia.")
            elif platform == "Bukalapak" and not ("bukalapak.com" in product_url):
                st.error("URL tidak valid untuk platform Bukalapak.")
            else:
                if st.button("Scrape Data"):
                    if platform == "Shopee":
                        scraped_data = scrape_shopee(product_url)
                    elif platform == "Tokopedia":
                        # Implementasikan fungsi scraping untuk Tokopedia
                        st.error("Scraping untuk Tokopedia belum diimplementasikan.")
                        return
                    elif platform == "Bukalapak":
                        # Implementasikan fungsi scraping untuk Bukalapak
                        st.error("Scraping untuk Bukalapak belum diimplementasikan.")
                        return
                    
                    if not scraped_data.empty:
                        st.success("Scraping berhasil!")
                        st.write(scraped_data[['Product Name', 'Price', 'Description', 'Variants']])
                        
                        st.subheader("Foto Produk")
                        for photo in scraped_data['Photos'][0]:
                            st.image(photo, use_column_width=True)
                        
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
            st.error("Harap masukkan URL produk")

if __name__ == "__main__":
    main()
