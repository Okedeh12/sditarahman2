import sqlite3
import os
import streamlit as st

def get_db_connection():
    """Create a connection to the SQLite database in a writable directory."""
    temp_dir = st.runtime.get_runtime().temp_directory
    db_path = os.path.join(temp_dir, 'database_sekolah.db')
    
    # Connect to the SQLite database
    return sqlite3.connect(db_path)
What this does:
The database file is now stored in a temporary directory that Streamlit allows write access to.
The temporary directory will persist only during the app's runtime and will be reset each time the app is restarted. If you need long-term persistence, you might want to explore cloud-based storage solutions or use a service like Google Drive, AWS S3, etc.
Now, replace your existing get_db_connection function with the one above, and your app should work without encountering the permission error.






Anda bilang:
JADIKAN SATU
ChatGPT bilang:
ChatGPT
Berikut adalah kode lengkap yang sudah digabungkan, menggunakan direktori sementara dari Streamlit untuk mengatasi masalah PermissionError saat menulis ke database:

python
Salin kode
import os
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import streamlit as st
from streamlit_option_menu import option_menu

# Define the function to get a database connection
def get_db_connection():
    """Create a connection to the SQLite database in a writable directory."""
    temp_dir = st.runtime.get_runtime().temp_directory
    db_path = os.path.join(temp_dir, 'database_sekolah.db')
    
    # Connect to the SQLite database
    return sqlite3.connect(db_path)

# Function to create tables
def create_tables():
    """Create the required tables in the SQLite database."""
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        # Create tables if they don't exist
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                         id INTEGER PRIMARY KEY,
                         name TEXT,
                         age INTEGER
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS pembayaran_spp (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         nama_siswa TEXT,
                         kelas TEXT,
                         bulan TEXT,
                         jumlah INTEGER,
                         tanggal TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS gaji_guru (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         nama_guru TEXT,
                         bulan TEXT,
                         gaji INTEGER,
                         tunjangan INTEGER,
                         tanggal TEXT
                    )''')
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"SQLite OperationalError: {e}")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        if conn:
            conn.close()

# Function to save SPP payment
def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Save SPP payment details to SQLite and CSV."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        # Save to SQLite
        c.execute("INSERT INTO pembayaran_spp (nama_siswa, kelas, bulan, jumlah, tanggal) VALUES (?, ?, ?, ?, ?)",
                  (nama_siswa, kelas, bulan, jumlah, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        
        # Save to CSV
        if "pembayaran_spp" not in st.session_state:
            st.session_state.pembayaran_spp = pd.DataFrame(columns=["Nama Siswa", "Kelas", "Bulan", "Jumlah Pembayaran", "Biaya SPP/Bulan"])
        new_row = pd.DataFrame({
            "Nama Siswa": [nama_siswa],
            "Kelas": [kelas],
            "Bulan": [bulan],
            "Jumlah Pembayaran": [jumlah],
            "Biaya SPP/Bulan": [biaya_spp]
        })
        st.session_state.pembayaran_spp = pd.concat([st.session_state.pembayaran_spp, new_row], ignore_index=True)
        st.session_state.pembayaran_spp.to_csv('pembayaran_spp.csv', index=False)
    except sqlite3.OperationalError as e:
        print(f"SQLite OperationalError: {e}")
    except Exception as e:
        print(f"Error saving pembayaran SPP: {e}")

# Function to generate PDF receipt
def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Generate a payment receipt as a PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Kwitansi Pembayaran SPP", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Nama Siswa: {nama_siswa}", ln=True)
    pdf.cell(200, 10, txt=f"Kelas: {kelas}", ln=True)
    pdf.cell(200, 10, txt=f"Bulan: {bulan}", ln=True)
    pdf.cell(200, 10, txt=f"Jumlah Pembayaran: Rp {jumlah}", ln=True)
    pdf.cell(200, 10, txt=f"Biaya SPP per Bulan: Rp {biaya_spp}", ln=True)
    pdf.cell(200, 10, txt=f"Tanggal: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    
    # Save to a BytesIO object
    pdf_output = BytesIO()
    pdf.output(pdf_output, 'F')
    pdf_output.seek(0)  # Move to the start of the BytesIO object

    return pdf_output

# Function to save teacher salary details
def save_gaji_guru(nama_guru, bulan, gaji, tunjangan):
    """Save teacher salary details to SQLite and CSV."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        # Save to SQLite
        c.execute('INSERT INTO gaji_guru (nama_guru, bulan, gaji, tunjangan, tanggal) VALUES (?, ?, ?, ?, ?)',
                  (nama_guru, bulan, gaji, tunjangan, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()

        # Save to CSV
        df_gaji = pd.DataFrame([{
            'Nama Guru': nama_guru,
            'Bulan': bulan,
            'Gaji Pokok': gaji,
            'Tunjangan': tunjangan,
            'Tanggal': datetime.now().strftime('%Y-%m-%d')
        }])
        df_gaji.to_csv('gaji_guru.csv', mode='a', header=not os.path.exists('gaji_guru.csv'), index=False)
    except sqlite3.OperationalError as e:
        print(f"SQLite OperationalError: {e}")
    except Exception as e:
        print(f"Error saving gaji guru: {e}")

# Initialize the database and create tables
create_tables()

# Streamlit App
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Pembayaran SPP", "Laporan Keuangan", "Pengelolaan Gaji Guru"],
        icons=["cash-stack", "bar-chart", "person-badge"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#f0f2f6"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#4CAF50"},
        }
    )

if selected == "Pembayaran SPP":
    st.title("Pembayaran SPP")
    st.write("Halaman untuk pembayaran SPP siswa.")
    
    # Cek apakah data pembayaran sudah ada di session state, jika belum ambil dari database
    if 'pembayaran_spp' not in st.session_state:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM pembayaran_spp')
        data_spp = c.fetchall()
        df_spp = pd.DataFrame(data_spp, columns=["ID", "Nama Siswa", "Kelas", "Bulan", "Jumlah Pembayaran", "Tanggal"])
        st.session_state.pembayaran_spp = df_spp
        conn.close()
    
    # Simulasi input data pembayaran SPP menggunakan form
    with st.form("pembayaran_form"):
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.selectbox("Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
        bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        biaya_spp = st.number_input("Biaya SPP per Bulan (Rp)", min_value=0)
        jumlah = st.number_input("Jumlah Pembayaran (Rp)", min_value=0)
        
        # Tombol submit
        submitted = st.form_submit_button("Bayar")
        
        if submitted:
            save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
            st.success(f"Pembayaran SPP untuk {nama_siswa} berhasil ditambahkan!")
    
            # Generate PDF receipt
            pdf = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp)
            
            # Button to download PDF receipt
            st.download_button(
                label="Download Kwitansi",
                data=pdf,
                file_name=f"Kwitansi_SPP_{nama_siswa}_{bulan}.pdf",
                mime="application/pdf"
            )
    
    # Pencarian Nama Siswa dan Kelas
    st.subheader("Pencarian")
    search_nama = st.text_input("Cari Nama Siswa")
    search_kelas = st.selectbox("Cari Kelas", ["Semua"] + ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
    
    # Filter data berdasarkan pencarian
    filtered_data = st.session_state.pembayaran_spp
    if search_nama:
        filtered_data = filtered_data[filtered_data["Nama Siswa"].str.contains(search_nama, case=False)]
    if search_kelas != "Semua":
        filtered_data = filtered_data[filtered_data["Kelas"] == search_kelas]
    
    # Tampilkan tabel hasil pencarian
    st.write(filtered_data)
        
elif selected == "Laporan Keuangan":
    st.title("Laporan Keuangan")
    st.write("Halaman untuk laporan keuangan.")
    
    # Load and display financial data
    if os.path.exists('pembayaran_spp.csv'):
        df_spp = pd.read_csv('pembayaran_spp.csv')
        st.write("Laporan Pembayaran SPP:")
        st.write(df_spp)
    
    if os.path.exists('gaji_guru.csv'):
        df_gaji = pd.read_csv('gaji_guru.csv')
        st.write("Laporan Gaji Guru:")
        st.write(df_gaji)
    
    # Visualization
    st.subheader("Grafik Pembayaran SPP")
    if os.path.exists('pembayaran_spp.csv'):
        df_spp = pd.read_csv('pembayaran_spp.csv')
        df_spp_grouped = df_spp.groupby('Bulan')['Jumlah Pembayaran'].sum()
        plt.figure(figsize=(10, 6))
        df_spp_grouped.plot(kind='bar')
        plt.title('Total Pembayaran SPP per Bulan')
        plt.xlabel('Bulan')
        plt.ylabel('Jumlah Pembayaran (Rp)')
        st.pyplot(plt)

elif selected == "Pengelolaan Gaji Guru":
    st.title("Pengelolaan Gaji Guru")
    st.write("Halaman untuk pengelolaan gaji guru.")

    with st.form("gaji_form"):
        nama_guru = st.text_input("Nama Guru")
        bulan_gaji = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        gaji = st.number_input("Gaji Pokok (Rp)", min_value=0)
        tunjangan = st.number_input("Tunjangan (Rp)", min_value=0)
        
        submitted = st.form_submit_button("Simpan")
        
        if submitted:
            save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
            st.success(f"Data gaji untuk {nama_guru} berhasil disimpan!")

    st.subheader("Laporan Gaji Guru")
    if os.path.exists('gaji_guru.csv'):
        df_gaji = pd.read_csv('gaji_guru.csv')
        st.write(df_gaji)
