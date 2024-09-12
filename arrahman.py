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
    
# Fungsi untuk mendapatkan koneksi database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

    # Fungsi untuk menyimpan pembayaran SPP ke database
    def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
        conn = get_db_connection()
        c = conn.cursor()
        
        total_tagihan = biaya_spp * 12
        tagihan_terbayar = jumlah
        sisa_tagihan = total_tagihan - tagihan_terbayar
        
        # Simpan data pembayaran ke database
        c.execute('''INSERT INTO pembayaran_spp 
                     (nama_siswa, kelas, bulan, jumlah_pembayaran, total_tagihan_spp, tagihan_spp_terbayar, sisa_tagihan)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                  (nama_siswa, kelas, bulan, jumlah, total_tagihan, tagihan_terbayar, sisa_tagihan))
        conn.commit()
        conn.close()
    
    # Fungsi untuk generate kwitansi (contoh saja, perlu disesuaikan dengan kebutuhan)
    def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp):
        # Logika untuk menghasilkan PDF kwitansi, ini hanya contoh placeholder
        pdf_output = f"Kwitansi Pembayaran SPP\nNama: {nama_siswa}\nKelas: {kelas}\nBulan: {bulan}\nJumlah: {jumlah}\nBiaya SPP: {biaya_spp}"
        return pdf_output
    
    # Cek apakah data pembayaran sudah ada di session state, jika belum ambil dari database
    if 'pembayaran_spp' not in st.session_state:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM pembayaran_spp')
        data_spp = c.fetchall()
        conn.close()
        df_spp = pd.DataFrame(data_spp, columns=["ID", "Nama Siswa", "Kelas", "Bulan", "Jumlah Pembayaran", "Total Tagihan SPP 1 Tahun", "Tagihan SPP yang Sudah Terbayar", "Sisa Tagihan yang Belum Terbayar", "Tanggal"])
        st.session_state.pembayaran_spp = df_spp
    
    # Simulasi input data pembayaran SPP menggunakan form
    with st.form("pembayaran_form"):
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.selectbox("Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
        bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        jumlah = st.number_input("Jumlah Pembayaran", min_value=0)
        biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0)
        
        submit_button = st.form_submit_button("Simpan")
        if submit_button:
            # Simpan data pembayaran ke database
            save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
            st.success("Pembayaran SPP berhasil disimpan.")
            
            # Update session state dataframe
            st.session_state.pembayaran_spp = st.session_state.pembayaran_spp.append({
                "Nama Siswa": nama_siswa,
                "Kelas": kelas,
                "Bulan": bulan,
                "Jumlah Pembayaran": jumlah,
                "Total Tagihan SPP 1 Tahun": biaya_spp * 12,
                "Tagihan SPP yang Sudah Terbayar": jumlah,
                "Sisa Tagihan yang Belum Terbayar": (biaya_spp * 12) - jumlah
            }, ignore_index=True)
            
            # Simpan DataFrame ke CSV
            st.session_state.pembayaran_spp.to_csv(os.path.join("TEMP_DIR", 'pembayaran_spp.csv'), index=False)
            
            # Generate and download receipt
            pdf_output = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp)
            st.download_button("Download Kwitansi", pdf_output, file_name="kwitansi.pdf", mime="application/pdf")
            
elif selected == "Laporan Keuangan":
    st.title("Laporan Keuangan")
    st.write("Laporan keuangan sekolah yang berisi rincian pembayaran SPP dan gaji guru.")
    
    # Load data pembayaran SPP
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM pembayaran_spp')
    data_spp = c.fetchall()
    conn.close()

    df_spp = pd.DataFrame(data_spp, columns=["ID", "Nama Siswa", "Kelas", "Bulan", "Jumlah Pembayaran", "Total Tagihan SPP 1 Tahun", "Tagihan SPP yang Sudah Terbayar", "Sisa Tagihan yang Belum Terbayar", "Tanggal"])

    st.subheader("Laporan Pembayaran SPP")
    st.write(df_spp)

    # Download laporan SPP sebagai CSV
    st.download_button(
        label="Download Laporan SPP (CSV)",
        data=df_spp.to_csv(index=False),
        file_name="laporan_spp.csv",
        mime="text/csv"
    )

elif selected == "Pengelolaan Gaji Guru":
    st.title("Pengelolaan Gaji Guru")
    st.write("Halaman untuk pengelolaan gaji guru.")
    
    # Simulasi input data gaji guru menggunakan form
    with st.form("gaji_form"):
        nama_guru = st.text_input("Nama Guru")
        bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        gaji = st.number_input("Gaji Pokok", min_value=0)
        tunjangan = st.number_input("Tunjangan", min_value=0)
        
        submit_button = st.form_submit_button("Simpan")
        if submit_button:
            save_gaji_guru(nama_guru, bulan, gaji, tunjangan)
            st.success("Gaji guru berhasil disimpan.")
            
            # Update the session state dataframe (if needed)
            # You can add functionality to display or download CSV as needed
