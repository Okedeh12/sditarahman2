import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os
import stat
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

# Define the database path
DB_PATH = 'path/to/your/database_sekolah.db'

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
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
    conn.close()

# Check if the file exists, create it if necessary, and set permissions
if not os.path.exists(DB_PATH):
    # Create an empty file if it does not exist
    open(DB_PATH, 'w').close()
    # Set permissions: read and write for the owner
    os.chmod(DB_PATH, stat.S_IRUSR | stat.S_IWUSR)
    print(f"Database file created: {DB_PATH}")

# Initialize the database and create tables
create_tables()

# Function to save SPP payment to SQLite and CSV
def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    conn = get_db_connection()
    c = conn.cursor()
    tanggal = datetime.now().strftime('%Y-%m-%d')
    c.execute("INSERT INTO pembayaran_spp (nama_siswa, kelas, bulan, jumlah, tanggal) VALUES (?, ?, ?, ?, ?)", 
              (nama_siswa, kelas, bulan, jumlah, tanggal))
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

# Function to save teacher salary to SQLite
def save_gaji_guru(nama_guru, bulan, gaji, tunjangan):
    tanggal = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO gaji_guru (nama_guru, bulan, gaji, tunjangan, tanggal) VALUES (?, ?, ?, ?, ?)',
              (nama_guru, bulan, gaji, tunjangan, tanggal))
    conn.commit()
    conn.close()

# Function to generate a payment receipt as a PDF
def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp):
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
    return pdf

# Setup Streamlit sidebar
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

# Content based on selected menu
if selected == "Pembayaran SPP":
    st.title("Pembayaran SPP")
    st.write("Halaman untuk pembayaran SPP siswa.")

    # Form for inputting SPP payment
    with st.form("pembayaran_form"):
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.selectbox("Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
        bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        biaya_spp = st.number_input("Biaya SPP per Bulan (Rp)", min_value=0)
        jumlah = st.number_input("Jumlah Pembayaran (Rp)", min_value=0)

        submitted = st.form_submit_button("Bayar")
        
        if submitted:
            save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
            st.success(f"Pembayaran SPP untuk {nama_siswa} berhasil ditambahkan!")

            # Generate PDF receipt
            pdf = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp)
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)
            st.download_button(
                label="Download Kwitansi",
                data=pdf_output,
                file_name=f"Kwitansi_SPP_{nama_siswa}_{bulan}.pdf",
                mime="application/pdf"
            )

    # Search functionality
    st.subheader("Pencarian")
    search_nama = st.text_input("Cari Nama Siswa")
    search_kelas = st.selectbox("Cari Kelas", ["Semua"] + ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])

    filtered_data = st.session_state.get('pembayaran_spp', pd.DataFrame())
    if search_nama:
        filtered_data = filtered_data[filtered_data["Nama Siswa"].str.contains(search_nama, case=False)]
    if search_kelas != "Semua":
        filtered_data = filtered_data[filtered_data["Kelas"] == search_kelas]

    # Adding columns for Total Tagihan, SPP Terbayar, and Sisa Tagihan
    filtered_data['Total Tagihan SPP 1 Tahun (Rp)'] = filtered_data['Biaya SPP/Bulan'] * 12
    filtered_data['SPP yang Sudah Terbayar (Rp)'] = filtered_data.groupby(['Nama Siswa', 'Kelas'])['Jumlah Pembayaran'].transform('sum')
    filtered_data['Sisa Tagihan SPP (Rp)'] = filtered_data['Total Tagihan SPP 1 Tahun (Rp)'] - filtered_data['SPP yang Sudah Terbayar (Rp)']

    st.subheader("Data Pembayaran SPP")
    st.table(filtered_data)

    # Select student for receipt download
    selected_siswa = st.selectbox("Pilih Siswa untuk Kwitansi", options=filtered_data["Nama Siswa"].unique())
    selected_kelas = st.selectbox("Pilih Kelas", options=filtered_data["Kelas"].unique())

    siswa_data = filtered_data[(filtered_data["Nama Siswa"] == selected_siswa) & (filtered_data["Kelas"] == selected_kelas)]

    if not siswa_data.empty:
        siswa_row = siswa_data.iloc[0]
        pdf = generate_receipt(siswa_row["Nama Siswa"], siswa_row["Kelas"], siswa_row["Bulan"], siswa_row["Jumlah Pembayaran"], siswa_row["Biaya SPP/Bulan"])
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        st.download_button(
            label="Download Kwitansi",
            data=pdf_output,
            file_name=f"Kwitansi_SPP_{selected_siswa}.pdf",
            mime="application/pdf"
        )

elif selected == "Pengelolaan Gaji Guru":
    st.title("Pengelolaan Gaji Guru")
    st.write("Halaman untuk pengelolaan gaji guru.")

    # Form for inputting teacher salary
    with st.form("gaji_form"):
        nama_guru = st.text_input("Nama Guru")
        bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        gaji = st.number_input("Gaji (Rp)", min_value=0)
        tunjangan = st.number_input("Tunjangan (Rp)", min_value=0)

        submitted = st.form_submit_button("Simpan")
        
        if submitted:
            save_gaji_guru(nama_guru, bulan, gaji, tunjangan)
            st.success(f"Gaji guru {nama_guru} berhasil ditambahkan!")

    # Display teacher salaries
    conn = get_db_connection()
    query = "SELECT * FROM gaji_guru"
    df_gaji_guru = pd.read_sql(query, conn)
    conn.close()

    st.subheader("Data Gaji Guru")
    st.table(df_gaji_guru)

elif selected == "Laporan Keuangan":
    st.title("Laporan Keuangan")
    st.write("Halaman untuk laporan keuangan.")

    # Fetch SPP payments and teacher salaries
    conn = get_db_connection()
    df_spp = pd.read_sql("SELECT * FROM pembayaran_spp", conn)
    df_gaji = pd.read_sql("SELECT * FROM gaji_guru", conn)
    conn.close()

    # Data visualization
    if not df_spp.empty:
        st.subheader("Laporan Pembayaran SPP")
        df_spp['Jumlah Pembayaran'] = pd.to_numeric(df_spp['jumlah'], errors='coerce')
        df_spp.groupby(['bulan']).agg({'Jumlah Pembayaran': 'sum'}).plot(kind='bar', title='Pembayaran SPP per Bulan')
        st.pyplot(plt.gcf())

    if not df_gaji.empty:
        st.subheader("Laporan Gaji Guru")
        df_gaji['gaji'] = pd.to_numeric(df_gaji['gaji'], errors='coerce')
        df_gaji['tunjangan'] = pd.to_numeric(df_gaji['tunjangan'], errors='coerce')
        df_gaji.groupby(['bulan']).agg({'gaji': 'sum', 'tunjangan': 'sum'}).plot(kind='bar', title='Gaji Guru per Bulan')
        st.pyplot(plt.gcf())
