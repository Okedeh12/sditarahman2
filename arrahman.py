import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import plotly.express as px
from streamlit_option_menu import option_menu
from datetime import datetime

# Define file paths
CSV_PEMBAYARAN_SPP = 'data/pembayaran_spp.csv'
CSV_GAJI_GURU = 'data/gaji_guru.csv'
CSV_DAFTAR_ULANG = 'data/daftar_ulang.csv'
CSV_PENGELUARAN = 'data/pengeluaran.csv'
PERSISTENT_DIR = 'data/uploads'
LOGO_PATH = 'data/HN.png'

# Ensure data directories exist
os.makedirs('data', exist_ok=True)
os.makedirs(PERSISTENT_DIR, exist_ok=True)

# Functions to save different types of data
def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    df = pd.DataFrame([[nama_siswa, kelas, bulan, jumlah, biaya_spp]], columns=['nama_siswa', 'kelas', 'bulan', 'jumlah', 'biaya_spp'])
    if os.path.exists(CSV_PEMBAYARAN_SPP):
        df_existing = pd.read_csv(CSV_PEMBAYARAN_SPP)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_PEMBAYARAN_SPP, index=False)

def save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan):
    df = pd.DataFrame([[nama_guru, bulan_gaji, gaji, tunjangan]], columns=['nama_guru', 'bulan_gaji', 'gaji', 'tunjangan'])
    if os.path.exists(CSV_GAJI_GURU):
        df_existing = pd.read_csv(CSV_GAJI_GURU)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_GAJI_GURU, index=False)

def save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun):
    df = pd.DataFrame([[nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun]], columns=['nama_siswa', 'kelas', 'biaya_daftar_ulang', 'pembayaran', 'tahun'])
    if os.path.exists(CSV_DAFTAR_ULANG):
        df_existing = pd.read_csv(CSV_DAFTAR_ULANG)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_DAFTAR_ULANG, index=False)

def save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, file_path=None):
    df = pd.DataFrame([[nama_penerima, keterangan_biaya, total_biaya]], columns=['nama_penerima', 'keterangan_biaya', 'total_biaya'])
    if os.path.exists(CSV_PENGELUARAN):
        df_existing = pd.read_csv(CSV_PENGELUARAN)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_PENGELUARAN, index=False)
    
    # Save uploaded file if available
    if file_path:
        new_file_path = os.path.join(PERSISTENT_DIR, os.path.basename(file_path))
        with open(new_file_path, "wb") as f:
            f.write(file_path.read())

# Function to generate receipt
def generate_receipt(nama, kelas, bulan, jumlah, biaya, receipt_type):
    pdf = FPDF()
    pdf.add_page()
    
    # School details
    school_name = "SD IT ARAHMAN"
    school_address = "JATIMULYO"

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
            ("Nama Siswa", nama),
            ("Kelas", kelas),
            ("Bulan", bulan),
            ("Jumlah Pembayaran", f"Rp {jumlah:,}"),
            ("Biaya SPP per Bulan", f"Rp {biaya:,}"),
            ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
        ]
    elif receipt_type == "daftar_ulang":
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Kwitansi Pembayaran Daftar Ulang", ln=True, align='C')
        pdf.ln(10)
        details = [
            ("Nama Siswa", nama),
            ("Kelas", kelas),
            ("Biaya Daftar Ulang", f"Rp {biaya:,}"),
            ("Pembayaran", f"Rp {jumlah:,}"),
            ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
        ]
    elif receipt_type == "gaji":
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Kwitansi Pembayaran Gaji Guru", ln=True, align='C')
        pdf.ln(10)
        details = [
            ("Nama Guru", nama),
            ("Bulan Gaji", kelas),
            ("Gaji", f"Rp {jumlah:,}"),
            ("Tunjangan", f"Rp {biaya:,}"),
            ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
        ]
    else:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Kwitansi Pengeluaran", ln=True, align='C')
        pdf.ln(10)
        details = [
            ("Nama Penerima", nama),
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

def generate_expense_receipt(nama_penerima, keterangan_biaya, total_biaya):
    return generate_receipt(nama_penerima, keterangan_biaya, '', total_biaya, total_biaya, 'pengeluaran')

# Load data from CSV files
def load_data():
    df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP) if os.path.exists(CSV_PEMBAYARAN_SPP) else pd.DataFrame()
    df_gaji = pd.read_csv(CSV_GAJI_GURU) if os.path.exists(CSV_GAJI_GURU) else pd.DataFrame()
    df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG) if os.path.exists(CSV_DAFTAR_ULANG) else pd.DataFrame()
    df_pengeluaran = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    return df_spp, df_gaji, df_daftar_ulang, df_pengeluaran

# Export data to Excel
def export_to_excel(spp_df, gaji_df, daftar_ulang_df, pengeluaran_df):
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            spp_df.to_excel(writer, sheet_name='Pembayaran SPP', index=False)
            gaji_df.to_excel(writer, sheet_name='Gaji Guru', index=False)
            daftar_ulang_df.to_excel(writer, sheet_name='Daftar Ulang', index=False)
            pengeluaran_df.to_excel(writer, sheet_name='Pengeluaran', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()

# Calculate net profit and details
def calculate_net_profit(df_spp, df_daftar_ulang, df_gaji, df_pengeluaran):
    total_spp = df_spp['jumlah'].sum()
    total_daftar_ulang = df_daftar_ulang['pembayaran'].sum()
    total_gaji = df_gaji[['gaji', 'tunjangan']].sum().sum()
    total_pengeluaran = df_pengeluaran['total_biaya'].sum()
    net_profit = total_spp + total_daftar_ulang - total_gaji - total_pengeluaran
    return total_spp, total_daftar_ulang, total_gaji, total_pengeluaran, net_profit

# Plot graphs
def plot_graphs(df_spp, df_daftar_ulang, df_pengeluaran):
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))

    # Total Pembayaran SPP dan Daftar Ulang
    ax[0].bar(['Total Pembayaran SPP', 'Total Pembayaran Daftar Ulang'], [df_spp['jumlah'].sum(), df_daftar_ulang['pembayaran'].sum()])
    ax[0].set_ylabel('Jumlah')
    ax[0].set_title('Total Pembayaran SPP dan Daftar Ulang')

    # Pengeluaran
    ax[1].bar(df_pengeluaran['keterangan_biaya'], df_pengeluaran['total_biaya'])
    ax[1].set_ylabel('Total Biaya')
    ax[1].set_title('Pengeluaran Berdasarkan Keterangan')
    ax[1].tick_params(axis='x', rotation=90)

    plt.tight_layout()
    fig_output = BytesIO()
    plt.savefig(fig_output, format='png')
    plt.close(fig_output)
    fig_output.seek(0)

    return fig_output

def main():
    st.set_page_config(page_title="Aplikasi Keuangan", layout="wide")
    
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["Pembayaran SPP", "Pengelolaan Gaji Guru", "Daftar Ulang", "Pengeluaran", "Halaman Owner"],
            icons=["cash", "person", "book", "credit-card", "file-text"],
            default_index=0,
            orientation="vertical"
        )

    df_spp, df_gaji, df_daftar_ulang, df_pengeluaran = load_data()

    if selected == "Pembayaran SPP":
        st.title("Pembayaran SPP")
        with st.form(key='spp_form'):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            bulan = st.text_input("Bulan")
            jumlah = st.number_input("Jumlah Pembayaran", min_value=0)
            biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0)
            submit_button = st.form_submit_button(label='Simpan')
            if submit_button:
                save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.success("Data Pembayaran SPP berhasil disimpan.")
                receipt_pdf = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, 'spp')
                st.download_button("Download Kwitansi", receipt_pdf, file_name="kwitansi_pembayaran_spp.pdf")

    elif selected == "Pengelolaan Gaji Guru":
        st.title("Pengelolaan Gaji Guru")
        with st.form(key='gaji_form'):
            nama_guru = st.text_input("Nama Guru")
            bulan_gaji = st.text_input("Bulan Gaji")
            gaji = st.number_input("Gaji", min_value=0)
            tunjangan = st.number_input("Tunjangan", min_value=0)
            submit_button = st.form_submit_button(label='Simpan')
            if submit_button:
                save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
                st.success("Data Gaji Guru berhasil disimpan.")
                receipt_pdf = generate_receipt(nama_guru, bulan_gaji, '', gaji, tunjangan, 'gaji')
                st.download_button("Download Kwitansi", receipt_pdf, file_name="kwitansi_pembayaran_gaji.pdf")

    elif selected == "Daftar Ulang":
        st.title("Daftar Ulang")
        with st.form(key='daftar_ulang_form'):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang", min_value=0)
            pembayaran = st.number_input("Pembayaran", min_value=0)
            tahun = st.text_input("Tahun")
            submit_button = st.form_submit_button(label='Simpan')
            if submit_button:
                save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun)
                st.success("Data Daftar Ulang berhasil disimpan.")
                receipt_pdf = generate_receipt(nama_siswa, kelas, '', pembayaran, biaya_daftar_ulang, 'daftar_ulang')
                st.download_button("Download Kwitansi", receipt_pdf, file_name="kwitansi_pembayaran_daftar_ulang.pdf")

    elif selected == "Pengeluaran":
        st.title("Pengeluaran")
        with st.form(key='pengeluaran_form', clear_on_submit=True):
            nama_penerima = st.text_input("Nama Penerima")
            keterangan_biaya = st.text_input("Keterangan Biaya")
            total_biaya = st.number_input("Total Biaya", min_value=0)
            file_upload = st.file_uploader("Upload File (optional)", type=['pdf', 'jpg', 'png'])
            submit_button = st.form_submit_button(label='Simpan')
            if submit_button:
                save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, file_upload if file_upload else None)
                st.success("Data Pengeluaran berhasil disimpan.")
                receipt_pdf = generate_expense_receipt(nama_penerima, keterangan_biaya, total_biaya)
                st.download_button("Download Kwitansi", receipt_pdf, file_name="kwitansi_pengeluaran.pdf")

    elif selected == "Halaman Owner":
        st.title("Halaman Owner")

        # Calculate and display net profit
        total_spp, total_daftar_ulang, total_gaji, total_pengeluaran, net_profit = calculate_net_profit(df_spp, df_daftar_ulang, df_gaji, df_pengeluaran)
        st.write(f"**Total Pembayaran SPP:** Rp {total_spp:,}")
        st.write(f"**Total Pembayaran Daftar Ulang:** Rp {total_daftar_ulang:,}")
        st.write(f"**Total Gaji Guru:** Rp {total_gaji:,}")
        st.write(f"**Total Pengeluaran:** Rp {total_pengeluaran:,}")
        st.write(f"**Keuntungan Bersih:** Rp {net_profit:,}")

        # Plot and display graphs
        fig_output = plot_graphs(df_spp, df_daftar_ulang, df_pengeluaran)
        st.image(fig_output, caption='Grafik Pembayaran dan Pengeluaran')

        # Export to Excel
        excel_data = export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran)
        st.download_button(
            label="Download Laporan Excel",
            data=excel_data,
            file_name="laporan_keuangan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
