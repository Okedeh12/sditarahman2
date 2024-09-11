import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

import os
if not os.path.exists(DB_PATH):
    st.error(f"Database file does not exist: {DB_PATH}")
    
chmod 644 path/to/your/database_sekolah.db

def create_tables():
    conn = get_db_connection()
    c = conn.cursor()
    # Create tables
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


DB_PATH = 'path/to/your/database_sekolah.db'
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Failed to connect to the database: {e}")
        raise


# Define the path to the SQLite database
DB_PATH = 'path/to/database_sekolah.db'

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Function to create tables if they do not exist
def create_tables():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS pembayaran_spp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_siswa TEXT,
            kelas TEXT,
            bulan TEXT,
            jumlah INTEGER,
            biaya_spp INTEGER,
            tanggal TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS gaji_guru (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_guru TEXT,
            bulan TEXT,
            gaji INTEGER,
            tunjangan INTEGER,
            tanggal TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Function to save SPP payment to SQLite and CSV
def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    conn = get_db_connection()
    c = conn.cursor()
    
    tanggal = datetime.now().strftime('%Y-%m-%d')
    
    try:
        c.execute("INSERT INTO pembayaran_spp (nama_siswa, kelas, bulan, jumlah, biaya_spp, tanggal) VALUES (?, ?, ?, ?, ?, ?)", 
                  (nama_siswa, kelas, bulan, jumlah, biaya_spp, tanggal))
        conn.commit()

        # Save to session state
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
        st.error(f"Database operation failed: {e}")
    
    finally:
        conn.close()

# Function to save teacher salary data to SQLite
def save_gaji_guru(nama_guru, bulan, gaji, tunjangan):
    conn = get_db_connection()
    c = conn.cursor()
    
    tanggal = datetime.now().strftime('%Y-%m-%d')
    
    try:
        c.execute('INSERT INTO gaji_guru (nama_guru, bulan, gaji, tunjangan, tanggal) VALUES (?, ?, ?, ?, ?)',
                  (nama_guru, bulan, gaji, tunjangan, tanggal))
        conn.commit()
    except sqlite3.OperationalError as e:
        st.error(f"Database operation failed: {e}")
    finally:
        conn.close()

# Function to generate a PDF receipt
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

# Initialize the database and create tables
create_tables()

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

# Main content based on selected menu
if selected == "Pembayaran SPP":
    st.title("Pembayaran SPP")
    st.write("Halaman untuk pembayaran SPP siswa.")

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

    st.subheader("Pencarian")
    search_nama = st.text_input("Cari Nama Siswa")
    search_kelas = st.selectbox("Cari Kelas", ["Semua"] + ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])

    conn = get_db_connection()
    c = conn.cursor()

    query = "SELECT * FROM pembayaran_spp"
    if search_nama:
        query += f" WHERE nama_siswa LIKE '%{search_nama}%'"
    if search_kelas != "Semua":
        query += f" AND kelas = '{search_kelas}'"
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['Total Tagihan SPP 1 Tahun (Rp)'] = df['biaya_spp'] * 12
    df['SPP yang Sudah Terbayar (Rp)'] = df.groupby(['nama_siswa', 'kelas'])['jumlah'].transform('sum')
    df['Sisa Tagihan SPP (Rp)'] = df['Total Tagihan SPP 1 Tahun (Rp)'] - df['SPP yang Sudah Terbayar (Rp)']
    
    st.subheader("Data Pembayaran SPP")
    st.table(df)

    selected_siswa = st.selectbox("Pilih Siswa untuk Kwitansi", options=df["nama_siswa"].unique())
    selected_kelas = st.selectbox("Pilih Kelas", options=df["kelas"].unique())

    siswa_data = df[(df["nama_siswa"] == selected_siswa) & (df["kelas"] == selected_kelas)]

    if not siswa_data.empty:
        siswa_row = siswa_data.iloc[0]
        pdf = generate_receipt(siswa_row["nama_siswa"], siswa_row["kelas"], siswa_row["bulan"], siswa_row["jumlah"], siswa_row["biaya_spp"])
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        st.download_button(
            label="Download Kwitansi Siswa",
            data=pdf_output,
            file_name=f"Kwitansi_SPP_{siswa_row['nama_siswa']}_{siswa_row['bulan']}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Tidak ada data yang sesuai untuk kwitansi.")

elif selected == "Laporan Keuangan":
    st.title("Laporan Keuangan")
    st.write("Halaman untuk laporan keuangan.")
    # Implement reporting features here

elif selected == "Pengelolaan Gaji Guru":
    st.title("Pengelolaan Gaji Guru")
    st.write("Halaman untuk pengelolaan gaji guru.")

    with st.form("gaji_form"):
        nama_guru = st.text_input("Nama Guru")
        bulan_gaji = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        gaji = st.number_input("Gaji (Rp)", min_value=0)
        tunjangan = st.number_input("Tunjangan (Rp)", min_value=0)
        submitted_gaji = st.form_submit_button("Simpan Gaji")

        if submitted_gaji:
            save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
            st.success(f"Gaji guru {nama_guru} berhasil disimpan!")
