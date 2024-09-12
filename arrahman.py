import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF
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

def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    df = pd.DataFrame([[nama_siswa, kelas, bulan, jumlah, biaya_spp]], columns=['nama_siswa', 'kelas', 'bulan', 'jumlah', 'biaya_spp'])
    if os.path.exists(CSV_PEMBAYARAN_SPP):
        df_existing = pd.read_csv(CSV_PEMBAYARAN_SPP)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_PEMBAYARAN_SPP, index=False)
    return CSV_PEMBAYARAN_SPP

def save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan):
    df = pd.DataFrame([[nama_guru, bulan_gaji, gaji, tunjangan]], columns=['nama_guru', 'bulan_gaji', 'gaji', 'tunjangan'])
    if os.path.exists(CSV_GAJI_GURU):
        df_existing = pd.read_csv(CSV_GAJI_GURU)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_GAJI_GURU, index=False)
    return CSV_GAJI_GURU

def save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun):
    df = pd.DataFrame([[nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun]], columns=['nama_siswa', 'kelas', 'biaya_daftar_ulang', 'pembayaran', 'tahun'])
    if os.path.exists(CSV_DAFTAR_ULANG):
        df_existing = pd.read_csv(CSV_DAFTAR_ULANG)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_DAFTAR_ULANG, index=False)
    return CSV_DAFTAR_ULANG

def save_pengeluaran(nama_barang_jasa, keterangan, total_biaya):
    df = pd.DataFrame([[nama_barang_jasa, keterangan, total_biaya]], columns=['nama_barang_jasa', 'keterangan', 'total_biaya'])
    if os.path.exists(CSV_PENGELUARAN):
        df_existing = pd.read_csv(CSV_PENGELUARAN)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_PENGELUARAN, index=False)
    return CSV_PENGELUARAN

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
    else:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Kwitansi Pengeluaran", ln=True, align='C')
        pdf.ln(10)
        details = [
            ("Nama Barang/Jasa", nama_siswa),
            ("Keterangan", kelas),
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

def generate_expense_receipt(nama_barang_jasa, keterangan, total_biaya):
    return generate_receipt(nama_barang_jasa, keterangan, '', total_biaya, total_biaya, 'pengeluaran')

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

def main():
    df_spp, df_gaji, df_daftar_ulang, df_pengeluaran = load_data()

    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Pembayaran SPP", "Laporan Keuangan", "Pengelolaan Gaji Guru", "Daftar Ulang", "Pengeluaran"],
            icons=["cash-stack", "bar-chart", "person-badge", "clipboard-check", "money"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#f0f2f6"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#ff6f61"},
            }
        )

    if selected == "Laporan Keuangan":
        st.title("Laporan Keuangan")
        
        st.write("**Export Data to Excel**")
        if st.button("Export to Excel"):
            excel_data = export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran)
            st.download_button(
                label="Download Excel File",
                data=excel_data,
                file_name="laporan_keuangan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.write("**Laporan Pembayaran SPP**")
        st.dataframe(df_spp)

        st.write("**Laporan Gaji Guru**")
        st.dataframe(df_gaji)

        st.write("**Laporan Daftar Ulang**")
        st.dataframe(df_daftar_ulang)

        st.write("**Laporan Pengeluaran**")
        st.dataframe(df_pengeluaran)
        
        with st.form("gaji_guru_form", clear_on_submit=True):
            nama_guru = st.text_input("Nama Guru")
            bulan_gaji = st.text_input("Bulan Gaji")
            gaji = st.number_input("Gaji", min_value=0, step=1000)
            tunjangan = st.number_input("Tunjangan", min_value=0, step=1000)
            submit_gaji = st.form_submit_button("Simpan Gaji")
            
            if submit_gaji:
                if nama_guru and bulan_gaji and gaji > 0:
                    csv_path = save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
                    st.success("Gaji guru berhasil disimpan!")
                    
                    # Generate and offer receipt download
                    pdf_receipt = generate_receipt(nama_guru, '', bulan_gaji, gaji, tunjangan, "gaji")
                    st.download_button(
                        label="Download Kwitansi Gaji Guru", 
                        data=pdf_receipt, 
                        file_name=f"Kwitansi_Gaji_{nama_guru}.pdf", 
                        mime='application/pdf'
                    )
                else:
                    st.error("Semua field harus diisi!")
        
        if not df_gaji.empty:
            st.subheader("Riwayat Gaji Guru")
            st.dataframe(df_gaji)

            st.subheader("Unduh Kwitansi Gaji Guru")
            st.write("Pilih data gaji guru untuk diunduh kwitansi.")
            
            selected_row = st.selectbox("Pilih Gaji", df_gaji.index, format_func=lambda x: f"{df_gaji.iloc[x]['nama_guru']} - {df_gaji.iloc[x]['bulan_gaji']}")
            
            if st.button("Unduh Kwitansi Terpilih"):
                row = df_gaji.iloc[selected_row]
                pdf_receipt = generate_receipt(row['nama_guru'], '', row['bulan_gaji'], row['gaji'], row['tunjangan'], "gaji")
                st.download_button(
                    label="Download Kwitansi Gaji Guru", 
                    data=pdf_receipt, 
                    file_name=f"Kwitansi_Gaji_{row['nama_guru']}.pdf", 
                    mime='application/pdf'
                )

    elif selected == "Daftar Ulang":
        st.title("Daftar Ulang")
        st.write("Halaman untuk mengelola pembayaran daftar ulang siswa.")
        
        with st.form("daftar_ulang_form", clear_on_submit=True):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang", min_value=0, step=1000)
            pembayaran = st.number_input("Pembayaran", min_value=0, step=1000)
            tahun = st.selectbox("Tahun", options=[str(year) for year in range(2024, 2030)])
            submit_daftar_ulang = st.form_submit_button("Simpan Daftar Ulang")
            
            if submit_daftar_ulang:
                if nama_siswa and kelas and biaya_daftar_ulang > 0 and pembayaran >= 0:
                    csv_path = save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun)
                    st.success("Pembayaran daftar ulang berhasil disimpan!")
                    
                    # Generate and offer receipt download
                    pdf_receipt = generate_receipt(nama_siswa, kelas, '', pembayaran, biaya_daftar_ulang, "daftar_ulang")
                    st.download_button(
                        label="Download Kwitansi Pembayaran Daftar Ulang", 
                        data=pdf_receipt, 
                        file_name=f"Kwitansi_Daftar_Ulang_{nama_siswa}_{tahun}.pdf", 
                        mime='application/pdf'
                    )
                else:
                    st.error("Semua field harus diisi!")

        if not df_daftar_ulang.empty:
            st.subheader("Riwayat Daftar Ulang")
            st.dataframe(df_daftar_ulang)
            
            st.subheader("Unduh Kwitansi Daftar Ulang")
            st.write("Pilih data pembayaran daftar ulang untuk diunduh kwitansi.")
            
            selected_row = st.selectbox("Pilih Pembayaran", df_daftar_ulang.index, format_func=lambda x: f"{df_daftar_ulang.iloc[x]['nama_siswa']} - {df_daftar_ulang.iloc[x]['tahun']}")
            
            if st.button("Unduh Kwitansi Terpilih"):
                row = df_daftar_ulang.iloc[selected_row]
                pdf_receipt = generate_receipt(row['nama_siswa'], row['kelas'], '', row['pembayaran'], row['biaya_daftar_ulang'], "daftar_ulang")
                st.download_button(
                    label="Download Kwitansi Pembayaran Daftar Ulang", 
                    data=pdf_receipt, 
                    file_name=f"Kwitansi_Daftar_Ulang_{row['nama_siswa']}_{row['tahun']}.pdf", 
                    mime='application/pdf'
                )

    elif selected == "Pengeluaran":
        st.title("Pengelolaan Pengeluaran")
        st.write("Halaman untuk mengelola pengeluaran sekolah.")
        
        with st.form("pengeluaran_form", clear_on_submit=True):
            nama_barang_jasa = st.text_input("Nama Barang/Jasa")
            keterangan = st.text_area("Keterangan Biaya")
            total_biaya = st.number_input("Total Biaya", min_value=0, step=1000)
            submit_pengeluaran = st.form_submit_button("Simpan Pengeluaran")
            
            if submit_pengeluaran:
                if nama_barang_jasa and keterangan and total_biaya > 0:
                    csv_path = save_pengeluaran(nama_barang_jasa, keterangan, total_biaya)
                    st.success("Data pengeluaran berhasil disimpan!")
                    
                    # Generate and offer receipt download
                    pdf_receipt = generate_expense_receipt(nama_barang_jasa, keterangan, total_biaya)
                    st.download_button(
                        label="Download Kwitansi Pengeluaran", 
                        data=pdf_receipt, 
                        file_name=f"Kwitansi_Pengeluaran_{nama_barang_jasa}.pdf", 
                        mime='application/pdf'
                    )
                else:
                    st.error("Semua field harus diisi!")
        
        if not df_pengeluaran.empty:
            st.subheader("Riwayat Pengeluaran")
            st.dataframe(df_pengeluaran)
            
            st.subheader("Unduh Kwitansi Pengeluaran")
            st.write("Pilih data pengeluaran untuk diunduh kwitansi.")
            
            selected_row = st.selectbox("Pilih Pengeluaran", df_pengeluaran.index, format_func=lambda x: f"{df_pengeluaran.iloc[x]['nama_barang_jasa']}")
            
            if st.button("Unduh Kwitansi Terpilih"):
                row = df_pengeluaran.iloc[selected_row]
                pdf_receipt = generate_expense_receipt(row['nama_barang_jasa'], row['keterangan'], row['total_biaya'])
                st.download_button(
                    label="Download Kwitansi Pengeluaran", 
                    data=pdf_receipt, 
                    file_name=f"Kwitansi_Pengeluaran_{row['nama_barang_jasa']}.pdf", 
                    mime='application/pdf'
                )

    st.sidebar.markdown("**Upload File Kwitansi:**")
    uploaded_file = st.sidebar.file_uploader("Pilih file kwitansi untuk diunggah", type=["pdf"])
    
    if uploaded_file is not None:
        file_path = os.path.join(PERSISTENT_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.sidebar.success("File kwitansi berhasil diunggah!")

if __name__ == "__main__":
    main()
