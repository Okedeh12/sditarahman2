import os
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import streamlit as st
from streamlit_option_menu import option_menu

# Define the temporary directory for Streamlit
TEMP_DIR = '/tmp'

def get_db_connection():
    """Create a connection to the SQLite database."""
    DB_PATH = os.path.join(TEMP_DIR, 'database_sekolah.db')
    return sqlite3.connect(DB_PATH)

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
                         total_tagihan_tahun INTEGER DEFAULT 0,
                         tagihan_sudah_terbayar INTEGER DEFAULT 0,
                         sisa_tagihan_belum_terbayar INTEGER DEFAULT 0,
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

def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Save SPP payment details to SQLite and CSV."""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Calculate the total yearly fee and update other fields
        total_tagihan_tahun = biaya_spp * 12
        tagihan_sudah_terbayar = jumlah
        sisa_tagihan_belum_terbayar = total_tagihan_tahun - tagihan_sudah_terbayar
        
        # Save to SQLite
        c.execute("INSERT INTO pembayaran_spp (nama_siswa, kelas, bulan, jumlah, total_tagihan_tahun, tagihan_sudah_terbayar, sisa_tagihan_belum_terbayar, tanggal) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ",
                  (nama_siswa, kelas, bulan, jumlah, total_tagihan_tahun, tagihan_sudah_terbayar, sisa_tagihan_belum_terbayar, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        
        # Save to CSV
        if "pembayaran_spp" not in st.session_state:
            st.session_state.pembayaran_spp = pd.DataFrame(columns=["Nama Siswa", "Kelas", "Bulan", "Jumlah Pembayaran", "Biaya SPP/Bulan", "Total Tagihan SPP 1 Tahun", "Tagihan SPP yang Sudah Terbayar", "Sisa Tagihan yang Belum Terbayar"])
        new_row = pd.DataFrame({
            "Nama Siswa": [nama_siswa],
            "Kelas": [kelas],
            "Bulan": [bulan],
            "Jumlah Pembayaran": [jumlah],
            "Biaya SPP/Bulan": [biaya_spp],
            "Total Tagihan SPP 1 Tahun": [total_tagihan_tahun],
            "Tagihan SPP yang Sudah Terbayar": [tagihan_sudah_terbayar],
            "Sisa Tagihan yang Belum Terbayar": [sisa_tagihan_belum_terbayar]
        })
        st.session_state.pembayaran_spp = pd.concat([st.session_state.pembayaran_spp, new_row], ignore_index=True)
        st.session_state.pembayaran_spp.to_csv(os.path.join(TEMP_DIR, 'pembayaran_spp.csv'), index=False)
    except sqlite3.OperationalError as e:
        print(f"SQLite OperationalError: {e}")
    except Exception as e:
        print(f"Error saving pembayaran SPP: {e}")

def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Generate a well-formatted payment receipt as a PDF."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title section
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Kwitansi Pembayaran SPP", ln=True, align='C')
    pdf.ln(10)
    
    # Detail section
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=f"Nama Siswa", border=1)
    pdf.cell(100, 10, txt=f": {nama_siswa}", border=1, ln=True)
    
    pdf.cell(100, 10, txt=f"Kelas", border=1)
    pdf.cell(100, 10, txt=f": {kelas}", border=1, ln=True)
    
    pdf.cell(100, 10, txt=f"Bulan", border=1)
    pdf.cell(100, 10, txt=f": {bulan}", border=1, ln=True)
    
    pdf.cell(100, 10, txt=f"Jumlah Pembayaran", border=1)
    pdf.cell(100, 10, txt=f": Rp {jumlah:,}", border=1, ln=True)
    
    pdf.cell(100, 10, txt=f"Biaya SPP per Bulan", border=1)
    pdf.cell(100, 10, txt=f": Rp {biaya_spp:,}", border=1, ln=True)
    
    # Date and signature section
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Tanggal: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='R')
    pdf.ln(20)
    pdf.cell(200, 10, txt="Tanda Terima", ln=True, align='R')
    
    # Output to BytesIO
    pdf_output = BytesIO()
    pdf_data = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_data)
    pdf_output.seek(0)

    return pdf_output

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
        df_gaji.to_csv(os.path.join(TEMP_DIR, 'gaji_guru.csv'), mode='a', header=not os.path.exists(os.path.join(TEMP_DIR, 'gaji_guru.csv')), index=False)
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
        conn.close()
        df_spp = pd.DataFrame(data_spp, columns=["ID", "Nama Siswa", "Kelas", "Bulan", "Jumlah Pembayaran", "Total Tagihan SPP 1 Tahun", "Tagihan SPP yang Sudah Terbayar", "Sisa Tagihan yang Belum Terbayar", "Tanggal"])
        st.session_state.pembayaran_spp = df_spp
    
    # Form untuk input pembayaran SPP
    with st.form("pembayaran_spp_form", clear_on_submit=True):
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.text_input("Kelas")
        bulan = st.text_input("Bulan")
        jumlah = st.number_input("Jumlah Pembayaran", min_value=0, step=1000)
        biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0, step=1000)
        submit = st.form_submit_button("Simpan Pembayaran")
        
        if submit:
            if nama_siswa and kelas and bulan and jumlah > 0 and biaya_spp > 0:
                save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.success("Pembayaran berhasil disimpan!")
                
                # Generate and offer receipt download
                pdf_receipt = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.download_button(label="Download Kwitansi Pembayaran SPP", data=pdf_receipt, file_name=f"Kwitansi_SPP_{nama_siswa}_{bulan}.pdf", mime='application/octet-stream')
            else:
                st.error("Semua field harus diisi!")
    
    # Tampilkan data pembayaran SPP
    if 'pembayaran_spp' in st.session_state and not st.session_state.pembayaran_spp.empty:
        st.subheader("Riwayat Pembayaran SPP")
        st.dataframe(st.session_state.pembayaran_spp)

elif selected == "Laporan Keuangan":
    st.title("Laporan Keuangan")
    st.write("Halaman laporan keuangan sekolah.")
    
    # Tampilkan laporan pembayaran SPP dalam bentuk CSV
    if os.path.exists(os.path.join(TEMP_DIR, 'pembayaran_spp.csv')):
        st.download_button(label="Download Laporan Pembayaran SPP", data=open(os.path.join(TEMP_DIR, 'pembayaran_spp.csv'), 'rb'), file_name='laporan_pembayaran_spp.csv', mime='text/csv')
    
    # Tampilkan laporan gaji guru dalam bentuk CSV
    if os.path.exists(os.path.join(TEMP_DIR, 'gaji_guru.csv')):
        st.download_button(label="Download Laporan Gaji Guru", data=open(os.path.join(TEMP_DIR, 'gaji_guru.csv'), 'rb'), file_name='laporan_gaji_guru.csv', mime='text/csv')

elif selected == "Pengelolaan Gaji Guru":
    st.title("Pengelolaan Gaji Guru")
    st.write("Halaman untuk pengelolaan gaji guru.")

    # Form untuk input gaji guru
    with st.form("gaji_guru_form", clear_on_submit=True):
        nama_guru = st.text_input("Nama Guru")
        bulan = st.text_input("Bulan")
        gaji = st.number_input("Gaji Pokok", min_value=0, step=100000)
        tunjangan = st.number_input("Tunjangan", min_value=0, step=100000)
        submit = st.form_submit_button("Simpan Gaji Guru")
        
        if submit:
            if nama_guru and bulan and gaji > 0 and tunjangan >= 0:
                save_gaji_guru(nama_guru, bulan, gaji, tunjangan)
                st.success("Data gaji guru berhasil disimpan!")
            else:
                st.error("Semua field harus diisi!")
