import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF
from streamlit_option_menu import option_menu
from datetime import datetime

# Define CSV file paths
CSV_PEMBAYARAN_SPP = 'data/pembayaran_spp.csv'
CSV_GAJI_GURU = 'data/gaji_guru.csv'
CSV_DAFTAR_ULANG = 'data/daftar_ulang.csv'
CSV_PENGELUARAN = 'data/pengeluaran.csv'
PERSISTENT_DIR = 'data/uploads'
LOGO_PATH = 'data/HN.png'  # Ensure your logo file is here

# Ensure data directories exist
os.makedirs('data', exist_ok=True)
os.makedirs(PERSISTENT_DIR, exist_ok=True)

# Load CSV files
def load_data():
    df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP) if os.path.exists(CSV_PEMBAYARAN_SPP) else pd.DataFrame()
    df_gaji = pd.read_csv(CSV_GAJI_GURU) if os.path.exists(CSV_GAJI_GURU) else pd.DataFrame()
    df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG) if os.path.exists(CSV_DAFTAR_ULANG) else pd.DataFrame()
    df_pengeluaran = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    return df_spp, df_gaji, df_daftar_ulang, df_pengeluaran

def export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran):
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_spp.to_excel(writer, sheet_name='Pembayaran SPP', index=False)
            df_gaji.to_excel(writer, sheet_name='Gaji Guru', index=False)
            df_daftar_ulang.to_excel(writer, sheet_name='Daftar Ulang', index=False)
            df_pengeluaran.to_excel(writer, sheet_name='Pengeluaran', index=False)
        buffer.seek(0)
        return buffer.getvalue()

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp, timestamp):
    new_data = pd.DataFrame({
        'nama_siswa': [nama_siswa],
        'kelas': [kelas],
        'bulan': [bulan],
        'jumlah': [jumlah],
        'biaya_spp': [biaya_spp],
        'timestamp': [timestamp]
    })
    if os.path.exists(CSV_PEMBAYARAN_SPP):
        df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP)
        df_spp = pd.concat([df_spp, new_data], ignore_index=True)
    else:
        df_spp = new_data
    df_spp.to_csv(CSV_PEMBAYARAN_SPP, index=False)

def save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan, timestamp):
    new_data = pd.DataFrame({
        'nama_guru': [nama_guru],
        'bulan_gaji': [bulan_gaji],
        'gaji': [gaji],
        'tunjangan': [tunjangan],
        'timestamp': [timestamp]
    })
    if os.path.exists(CSV_GAJI_GURU):
        df_gaji = pd.read_csv(CSV_GAJI_GURU)
        df_gaji = pd.concat([df_gaji, new_data], ignore_index=True)
    else:
        df_gaji = new_data
    df_gaji.to_csv(CSV_GAJI_GURU, index=False)

def save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun, timestamp):
    new_data = pd.DataFrame({
        'nama_siswa': [nama_siswa],
        'kelas': [kelas],
        'biaya_daftar_ulang': [biaya_daftar_ulang],
        'pembayaran': [pembayaran],
        'tahun': [tahun],
        'timestamp': [timestamp]
    })
    if os.path.exists(CSV_DAFTAR_ULANG):
        df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG)
        df_daftar_ulang = pd.concat([df_daftar_ulang, new_data], ignore_index=True)
    else:
        df_daftar_ulang = new_data
    df_daftar_ulang.to_csv(CSV_DAFTAR_ULANG, index=False)

def save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, timestamp):
    new_data = pd.DataFrame({
        'nama_penerima': [nama_penerima],
        'keterangan_biaya': [keterangan_biaya],
        'total_biaya': [total_biaya],
        'timestamp': [timestamp]
    })
    if os.path.exists(CSV_PENGELUARAN):
        df_pengeluaran = pd.read_csv(CSV_PENGELUARAN)
        df_pengeluaran = pd.concat([df_pengeluaran, new_data], ignore_index=True)
    else:
        df_pengeluaran = new_data
    df_pengeluaran.to_csv(CSV_PENGELUARAN, index=False)

def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, receipt_type):
    pdf = FPDF()
    pdf.add_page()

    # School details
    school_name = "SD IT ARAHMAN"
    school_address = "jl. dadapan blok 3 selatan, Jatimulyo, Kec. Jati Agung, Lamsel"

    # Add logo
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=8, w=33)
    else:
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt="Logo Tidak Ditemukan", ln=True, align='C')

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=school_name, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=school_address, ln=True, align='C')
    pdf.ln(10)

    if receipt_type == "spp":
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Kwitansi Pembayaran SPP", ln=True, align='C')
        pdf.ln(10)
        details = [
            ("Nama Siswa", nama_siswa),
            ("Kelas", kelas),
            ("Bulan", bulan),
            ("Jumlah Pembayaran", f"Rp {jumlah:,}"),
            ("Biaya SPP per Bulan", f"Rp {biaya_spp:,}"),
            ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
        ]
    elif receipt_type == "daftar_ulang":
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Kwitansi Pembayaran Daftar Ulang", ln=True, align='C')
        pdf.ln(10)
        details = [
            ("Nama Siswa", nama_siswa),
            ("Kelas", kelas),
            ("Biaya Daftar Ulang", f"Rp {biaya_spp:,}"),
            ("Pembayaran", f"Rp {jumlah:,}"),
            ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
        ]
    elif receipt_type == "gaji":
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Kwitansi Pembayaran Gaji Guru", ln=True, align='C')
        pdf.ln(10)
        details = [
            ("Nama Guru", nama_siswa),
            ("Bulan Gaji", kelas),
            ("Gaji", f"Rp {jumlah:,}"),
            ("Tunjangan", f"Rp {biaya_spp:,}"),
            ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
        ]
    else:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Kwitansi Pengeluaran", ln=True, align='C')
        pdf.ln(10)
        details = [
            ("Nama Penerima", nama_siswa),
            ("Keterangan Biaya", kelas),
            ("Total Biaya", f"Rp {jumlah:,}"),
            ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
        ]

    pdf.set_font("Arial", size=12)
    for label, value in details:
        pdf.cell(100, 10, txt=label, border=1)
        pdf.cell(90, 10, txt=f": {value}", border=1, ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, txt="Tanda Terima", ln=True, align='R')

    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)
    return pdf_output

def main():
    df_spp, df_gaji, df_daftar_ulang, df_pengeluaran = load_data()

    # Logo in the sidebar
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, use_column_width=True)
    else:
        st.sidebar.write("Logo Tidak Ditemukan")

    # Sidebar menu
    with st.sidebar:
        selected = option_menu(
            menu_title="SD IT AR RAHMAN",
            options=["Pembayaran SPP", "Pengelolaan Gaji Guru", "Daftar Ulang", "Pengeluaran", "Laporan Keuangan"],
            icons=["cash", "bar-chart", "person-badge", "clipboard-check", "money"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#f0f2f6"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#ff6f61"},
            }
        )

    # Logic for each menu option
    if selected == "Pembayaran SPP":
        st.title("Pembayaran SPP")
        with st.form("pembayaran_form"):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
            jumlah = st.number_input("Jumlah Pembayaran", min_value=0)
            biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0)
            submitted = st.form_submit_button("Simpan")
            if submitted:
                timestamp = get_current_timestamp()
                save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp, timestamp)
                st.success("Pembayaran SPP berhasil disimpan.")
                pdf = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, "spp")
                st.download_button("Download Kwitansi SPP", data=pdf, file_name="kwitansi_spp.pdf")

    elif selected == "Pengelolaan Gaji Guru":
        st.title("Pengelolaan Gaji Guru")
        with st.form("gaji_form"):
            nama_guru = st.text_input("Nama Guru")
            bulan_gaji = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
            gaji = st.number_input("Gaji", min_value=0)
            tunjangan = st.number_input("Tunjangan", min_value=0)
            submitted = st.form_submit_button("Simpan")
            if submitted:
                timestamp = get_current_timestamp()
                save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan, timestamp)
                st.success("Gaji guru berhasil disimpan.")
                pdf = generate_receipt(nama_guru, bulan_gaji, "", gaji, tunjangan, "gaji")
                st.download_button("Download Kwitansi Gaji", data=pdf, file_name="kwitansi_gaji.pdf")

    elif selected == "Daftar Ulang":
        st.title("Daftar Ulang")
        with st.form("daftar_ulang_form"):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang", min_value=0)
            pembayaran = st.number_input("Jumlah Pembayaran", min_value=0)
            tahun = st.text_input("Tahun")
            submitted = st.form_submit_button("Simpan")
            if submitted:
                timestamp = get_current_timestamp()
                save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun, timestamp)
                st.success("Data daftar ulang berhasil disimpan.")
                pdf = generate_receipt(nama_siswa, kelas, "", pembayaran, biaya_daftar_ulang, "daftar_ulang")
                st.download_button("Download Kwitansi Daftar Ulang", data=pdf, file_name="kwitansi_daftar_ulang.pdf")

    elif selected == "Pengeluaran":
        st.title("Pengeluaran")
        with st.form("pengeluaran_form"):
            nama_penerima = st.text_input("Nama Penerima")
            keterangan_biaya = st.text_input("Keterangan Biaya")
            total_biaya = st.number_input("Total Biaya", min_value=0)
            submitted = st.form_submit_button("Simpan")
            if submitted:
                timestamp = get_current_timestamp()
                save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, timestamp)
                st.success("Data pengeluaran berhasil disimpan.")
                pdf = generate_receipt(nama_penerima, keterangan_biaya, "", total_biaya, "", "pengeluaran")
                st.download_button("Download Kwitansi Pengeluaran", data=pdf, file_name="kwitansi_pengeluaran.pdf")

    elif selected == "Laporan Keuangan":
        st.title("Laporan Keuangan")
        st.subheader("Laporan Pembayaran SPP")
        st.dataframe(df_spp)
        
        st.subheader("Laporan Gaji Guru")
        st.dataframe(df_gaji)
        
        st.subheader("Laporan Daftar Ulang")
        st.dataframe(df_daftar_ulang)
        
        st.subheader("Laporan Pengeluaran")
        st.dataframe(df_pengeluaran)

if __name__ == "__main__":
    main()
