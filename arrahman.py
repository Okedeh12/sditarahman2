import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF
from streamlit_option_menu import option_menu
from datetime import datetime
import matplotlib.pyplot as plt

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
        os.rename(file_path, new_file_path)

def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, receipt_type):
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

def generate_expense_receipt(nama_penerima, keterangan_biaya, total_biaya):
    return generate_receipt(nama_penerima, keterangan_biaya, '', total_biaya, total_biaya, 'pengeluaran')

def load_data():
    df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP) if os.path.exists(CSV_PEMBAYARAN_SPP) else pd.DataFrame()
    df_gaji = pd.read_csv(CSV_GAJI_GURU) if os.path.exists(CSV_GAJI_GURU) else pd.DataFrame()
    df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG) if os.path.exists(CSV_DAFTAR_ULANG) else pd.DataFrame()
    df_pengeluaran = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    return df_spp, df_gaji, df_daftar_ulang, df_pengeluaran

def export_to_excel(spp_df, gaji_df, daftar_ulang_df, pengeluaran_df):
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            spp_df.to_excel(writer, sheet_name='Pembayaran SPP', index=False)
            gaji_df.to_excel(writer, sheet_name='Gaji Guru', index=False)
            daftar_ulang_df.to_excel(writer, sheet_name='Daftar Ulang', index=False)
            pengeluaran_df.to_excel(writer, sheet_name='Pengeluaran', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()

def plot_financial_data(df_spp, df_gaji, df_pengeluaran):
    fig, ax = plt.subplots(2, 2, figsize=(12, 10))

    # Total Payments
    total_payments = df_spp['jumlah'].sum() if not df_spp.empty else 0
    ax[0, 0].bar(['Total Pembayaran'], [total_payments], color='blue')
    ax[0, 0].set_title('Total Pembayaran SPP')

    # Total Salaries
    total_salaries = df_gaji[['gaji', 'tunjangan']].sum().sum() if not df_gaji.empty else 0
    ax[0, 1].bar(['Total Gaji dan Tunjangan'], [total_salaries], color='green')
    ax[0, 1].set_title('Total Gaji dan Tunjangan')

    # Total Expenses
    total_expenses = df_pengeluaran['total_biaya'].sum() if not df_pengeluaran.empty else 0
    ax[1, 0].bar(['Total Pengeluaran'], [total_expenses], color='red')
    ax[1, 0].set_title('Total Pengeluaran')

    # Net Profit
    net_profit = total_payments - total_salaries - total_expenses
    ax[1, 1].bar(['Laba Bersih'], [net_profit], color='purple')
    ax[1, 1].set_title('Laba Bersih')

    for a in ax.flat:
        a.grid(True)

    plt.tight_layout()
    return fig

def main():
    st.set_page_config(page_title="Sistem Keuangan", layout="wide")
    st.title("Sistem Keuangan Sekolah")

    with st.sidebar:
        selected = option_menu("Menu", ["Halaman Owner", "Laporan Bulanan"], icons=["house", "file-text"], menu_icon="cast")

    if selected == "Halaman Owner":
        st.subheader("Laporan Keuangan Sekolah")

        df_spp, df_gaji, df_daftar_ulang, df_pengeluaran = load_data()
        
        # Plot data
        fig = plot_financial_data(df_spp, df_gaji, df_pengeluaran)
        st.pyplot(fig)

        # Export to Excel
        if st.button("Export to Excel"):
            excel_data = export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran)
            st.download_button("Download Excel File", excel_data, "laporan_keuangan.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif selected == "Laporan Bulanan":
        st.subheader("Form Laporan Bulanan")

        with st.form(key='data_form'):
            report_type = st.selectbox("Pilih Jenis Laporan", ["Pembayaran SPP", "Gaji Guru", "Daftar Ulang", "Pengeluaran"])
            if report_type == "Pembayaran SPP":
                nama_siswa = st.text_input("Nama Siswa")
                kelas = st.text_input("Kelas")
                bulan = st.text_input("Bulan")
                jumlah = st.number_input("Jumlah Pembayaran", min_value=0)
                biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0)
                
                if st.form_submit_button("Simpan Pembayaran SPP"):
                    save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                    st.success("Pembayaran SPP berhasil disimpan!")
                    
            elif report_type == "Gaji Guru":
                nama_guru = st.text_input("Nama Guru")
                bulan_gaji = st.text_input("Bulan Gaji")
                gaji = st.number_input("Gaji", min_value=0)
                tunjangan = st.number_input("Tunjangan", min_value=0)
                
                if st.form_submit_button("Simpan Gaji Guru"):
                    save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
                    st.success("Gaji Guru berhasil disimpan!")
                    
            elif report_type == "Daftar Ulang":
                nama_siswa = st.text_input("Nama Siswa")
                kelas = st.text_input("Kelas")
                biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang", min_value=0)
                pembayaran = st.number_input("Pembayaran", min_value=0)
                tahun = st.text_input("Tahun")
                
                if st.form_submit_button("Simpan Daftar Ulang"):
                    save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun)
                    st.success("Daftar Ulang berhasil disimpan!")
                    
            elif report_type == "Pengeluaran":
                nama_penerima = st.text_input("Nama Penerima")
                keterangan_biaya = st.text_input("Keterangan Biaya")
                total_biaya = st.number_input("Total Biaya", min_value=0)
                uploaded_file = st.file_uploader("Upload Bukti Pengeluaran (Opsional)", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Simpan Pengeluaran"):
                    file_path = uploaded_file.name if uploaded_file else None
                    if uploaded_file:
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.read())
                    save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, file_path)
                    st.success("Pengeluaran berhasil disimpan!")
                    if uploaded_file:
                        st.image(uploaded_file, caption='Bukti Pengeluaran', use_column_width=True)
                    
if __name__ == "__main__":
    main()
