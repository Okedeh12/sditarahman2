import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime

# Path Constants
CSV_SPP = 'data_spp.csv'
CSV_GAJI = 'data_gaji.csv'
CSV_DAFTAR_ULANG = 'data_daftar_ulang.csv'
CSV_PENGELUARAN = 'data_pengeluaran.csv'
CSV_KEUNTUNGAN = 'data_keuntungan.csv'
PERSISTENT_DIR = 'persistent_files'
os.makedirs(PERSISTENT_DIR, exist_ok=True)

# Function to Save Data
def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    df = pd.read_csv(CSV_SPP) if os.path.exists(CSV_SPP) else pd.DataFrame()
    new_data = pd.DataFrame([[nama_siswa, kelas, bulan, jumlah, biaya_spp]], 
                            columns=['Nama Siswa', 'Kelas', 'Bulan', 'Jumlah Pembayaran', 'Biaya SPP'])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_SPP, index=False)

def save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan):
    df = pd.read_csv(CSV_GAJI) if os.path.exists(CSV_GAJI) else pd.DataFrame()
    new_data = pd.DataFrame([[nama_guru, bulan_gaji, gaji, tunjangan]], 
                            columns=['Nama Guru', 'Bulan Gaji', 'Gaji', 'Tunjangan'])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_GAJI, index=False)

def save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun):
    df = pd.read_csv(CSV_DAFTAR_ULANG) if os.path.exists(CSV_DAFTAR_ULANG) else pd.DataFrame()
    new_data = pd.DataFrame([[nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun]], 
                            columns=['Nama Siswa', 'Kelas', 'Biaya Daftar Ulang', 'Pembayaran', 'Tahun'])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_DAFTAR_ULANG, index=False)

def save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, file_path=None):
    df = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    new_data = pd.DataFrame([[nama_penerima, keterangan_biaya, total_biaya, file_path]], 
                            columns=['Nama Penerima', 'Keterangan Biaya', 'Total Biaya', 'File Path'])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_PENGELUARAN, index=False)

def save_keuntungan(bulan_tahun, total_pendapatan, total_gaji, total_pengeluaran):
    df = pd.read_csv(CSV_KEUNTUNGAN) if os.path.exists(CSV_KEUNTUNGAN) else pd.DataFrame()
    new_data = pd.DataFrame([[bulan_tahun, total_pendapatan, total_gaji, total_pengeluaran]], 
                            columns=['Bulan-Tahun', 'Total Pendapatan', 'Total Gaji', 'Total Pengeluaran'])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_KEUNTUNGAN, index=False)

# Generate Receipts
def generate_receipt(nama, kelas, bulan, jumlah, biaya, jenis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.cell(200, 10, txt="Sistem Keuangan Sekolah", ln=True, align='C')
    
    # Body
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Nama: {nama}", ln=True)
    pdf.cell(200, 10, txt=f"Kelas: {kelas}", ln=True)
    pdf.cell(200, 10, txt=f"Bulan: {bulan}", ln=True)
    pdf.cell(200, 10, txt=f"Jumlah Pembayaran: Rp {jumlah}", ln=True)
    pdf.cell(200, 10, txt=f"Biaya {jenis}: Rp {biaya}", ln=True)
    
    # Footer
    pdf.ln(10)
    pdf.cell(200, 10, txt="Terima Kasih atas Pembayaran Anda", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin1')

def generate_expense_receipt(nama_penerima, keterangan_biaya, total_biaya):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.cell(200, 10, txt="Sistem Keuangan Sekolah", ln=True, align='C')
    
    # Body
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Nama Penerima: {nama_penerima}", ln=True)
    pdf.cell(200, 10, txt=f"Keterangan Biaya: {keterangan_biaya}", ln=True)
    pdf.cell(200, 10, txt=f"Total Biaya: Rp {total_biaya}", ln=True)
    
    # Footer
    pdf.ln(10)
    pdf.cell(200, 10, txt="Terima Kasih atas Kerjasamanya", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin1')

# Export Data to Excel
def export_to_excel(spp_df, gaji_df, daftar_ulang_df, pengeluaran_df, keuntungan_df):
    with BytesIO() as buffer:
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
        spp_df.to_excel(writer, sheet_name='Pembayaran SPP', index=False)
        gaji_df.to_excel(writer, sheet_name='Gaji Guru', index=False)
        daftar_ulang_df.to_excel(writer, sheet_name='Daftar Ulang', index=False)
        pengeluaran_df.to_excel(writer, sheet_name='Pengeluaran', index=False)
        keuntungan_df.to_excel(writer, sheet_name='Keuntungan', index=False)
        writer.save()
        buffer.seek(0)
        return buffer.getvalue()

# Streamlit App
st.title("Sistem Keuangan Sekolah")

# Sidebar for navigation
with st.sidebar:
    option = option_menu(
        menu_title="Menu",
        options=["Data Pembayaran SPP", "Data Gaji Guru", "Data Daftar Ulang", "Data Pengeluaran", "Data Keuntungan", "Export Data"],
        icons=["cash", "person", "list", "folder", "pie-chart", "cloud-download"],
        default_index=0
    )

if option == "Data Pembayaran SPP":
    st.header("Data Pembayaran SPP")
    spp_df = pd.read_csv(CSV_SPP) if os.path.exists(CSV_SPP) else pd.DataFrame()
    st.dataframe(spp_df)
    
    with st.form(key='form_spp'):
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.text_input("Kelas")
        bulan = st.text_input("Bulan")
        jumlah = st.number_input("Jumlah Pembayaran", min_value=0)
        biaya_spp = st.number_input("Biaya SPP", min_value=0)
        submit_button = st.form_submit_button("Simpan Pembayaran SPP")
        
        if submit_button:
            save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
            st.success("Data Pembayaran SPP telah disimpan!")

elif option == "Data Gaji Guru":
    st.header("Data Gaji Guru")
    gaji_df = pd.read_csv(CSV_GAJI) if os.path.exists(CSV_GAJI) else pd.DataFrame()
    st.dataframe(gaji_df)
    
    with st.form(key='form_gaji'):
        nama_guru = st.text_input("Nama Guru")
        bulan_gaji = st.text_input("Bulan Gaji")
        gaji = st.number_input("Gaji", min_value=0)
        tunjangan = st.number_input("Tunjangan", min_value=0)
        submit_button = st.form_submit_button("Simpan Gaji Guru")
        
        if submit_button:
            save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
            st.success("Data Gaji Guru telah disimpan!")

elif option == "Data Daftar Ulang":
    st.header("Data Daftar Ulang")
    daftar_ulang_df = pd.read_csv(CSV_DAFTAR_ULANG) if os.path.exists(CSV_DAFTAR_ULANG) else pd.DataFrame()
    st.dataframe(daftar_ulang_df)
    
    with st.form(key='form_daftar_ulang'):
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.text_input("Kelas")
        biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang", min_value=0)
        pembayaran = st.number_input("Pembayaran", min_value=0)
        tahun = st.text_input("Tahun")
        submit_button = st.form_submit_button("Simpan Daftar Ulang")
        
        if submit_button:
            save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun)
            st.success("Data Daftar Ulang telah disimpan!")

elif option == "Data Pengeluaran":
    st.header("Data Pengeluaran")
    pengeluaran_df = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    st.dataframe(pengeluaran_df)
    
    with st.form(key='form_pengeluaran'):
        nama_penerima = st.text_input("Nama Penerima")
        keterangan_biaya = st.text_input("Keterangan Biaya")
        total_biaya = st.number_input("Total Biaya", min_value=0)
        file_path = st.file_uploader("Upload Bukti Pengeluaran (Opsional)", type=['pdf', 'jpg', 'png'])
        submit_button = st.form_submit_button("Simpan Pengeluaran")
        
        if submit_button:
            save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, file_path.name if file_path else None)
            st.success("Data Pengeluaran telah disimpan!")

elif option == "Data Keuntungan":
    st.header("Data Keuntungan")
    keuntungan_df = pd.read_csv(CSV_KEUNTUNGAN) if os.path.exists(CSV_KEUNTUNGAN) else pd.DataFrame()
    st.dataframe(keuntungan_df)
    
    with st.form(key='form_keuntungan'):
        bulan_tahun = st.text_input("Bulan-Tahun")
        total_pendapatan = st.number_input("Total Pendapatan", min_value=0)
        total_gaji = st.number_input("Total Gaji", min_value=0)
        total_pengeluaran = st.number_input("Total Pengeluaran", min_value=0)
        submit_button = st.form_submit_button("Simpan Keuntungan")
        
        if submit_button:
            save_keuntungan(bulan_tahun, total_pendapatan, total_gaji, total_pengeluaran)
            st.success("Data Keuntungan telah disimpan!")

elif option == "Export Data":
    st.header("Export Data")
    
    # Load all dataframes
    spp_df = pd.read_csv(CSV_SPP) if os.path.exists(CSV_SPP) else pd.DataFrame()
    gaji_df = pd.read_csv(CSV_GAJI) if os.path.exists(CSV_GAJI) else pd.DataFrame()
    daftar_ulang_df = pd.read_csv(CSV_DAFTAR_ULANG) if os.path.exists(CSV_DAFTAR_ULANG) else pd.DataFrame()
    pengeluaran_df = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    keuntungan_df = pd.read_csv(CSV_KEUNTUNGAN) if os.path.exists(CSV_KEUNTUNGAN) else pd.DataFrame()
    
    # Export to Excel
    excel_data = export_to_excel(spp_df, gaji_df, daftar_ulang_df, pengeluaran_df, keuntungan_df)
    st.download_button(label="Unduh Semua Data dalam Format Excel", data=excel_data, file_name="data_sekolah.xlsx")
