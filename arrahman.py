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

def save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya):
    df = pd.DataFrame([[nama_penerima, keterangan_biaya, total_biaya]], columns=['nama_penerima', 'keterangan_biaya', 'total_biaya'])
    if os.path.exists(CSV_PENGELUARAN):
        df_existing = pd.read_csv(CSV_PENGELUARAN)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_PENGELUARAN, index=False)

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

    if selected == "Pembayaran SPP":
        st.title("Pembayaran SPP")
        with st.form("spp_form"):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            bulan = st.text_input("Bulan")
            jumlah = st.number_input("Jumlah Pembayaran", min_value=0)
            biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0)
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.success("Pembayaran SPP berhasil disimpan!")

        st.write("**Data Pembayaran SPP**")
        st.dataframe(df_spp)

        # Generate and download receipt
        if not df_spp.empty:
            st.write("**Download Kwitansi Pembayaran SPP**")
            for index, row in df_spp.iterrows():
                receipt = generate_receipt(row['nama_siswa'], row['kelas'], row['bulan'], row['jumlah'], row['biaya_spp'], 'spp')
                st.download_button(
                    label=f"Download Kwitansi {row['nama_siswa']} ({row['bulan']})",
                    data=receipt,
                    file_name=f"kwitansi_spp_{row['nama_siswa']}_{row['bulan']}.pdf",
                    mime="application/pdf"
                )

    elif selected == "Pengelolaan Gaji Guru":
        st.title("Pengelolaan Gaji Guru")
        with st.form("gaji_form"):
            nama_guru = st.text_input("Nama Guru")
            bulan_gaji = st.text_input("Bulan Gaji")
            gaji = st.number_input("Gaji", min_value=0)
            tunjangan = st.number_input("Tunjangan", min_value=0)
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
                st.success("Gaji Guru berhasil disimpan!")

        st.write("**Data Gaji Guru**")
        st.dataframe(df_gaji)

        # Generate and download receipt
        if not df_gaji.empty:
            st.write("**Download Kwitansi Gaji Guru**")
            for index, row in df_gaji.iterrows():
                receipt = generate_receipt(row['nama_guru'], row['bulan_gaji'], row['gaji'], row['tunjangan'], row['tunjangan'], 'gaji')
                st.download_button(
                    label=f"Download Kwitansi {row['nama_guru']} ({row['bulan_gaji']})",
                    data=receipt,
                    file_name=f"kwitansi_gaji_{row['nama_guru']}_{row['bulan_gaji']}.pdf",
                    mime="application/pdf"
                )

    elif selected == "Daftar Ulang":
        st.title("Daftar Ulang")
        with st.form("daftar_ulang_form"):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang", min_value=0)
            pembayaran = st.number_input("Pembayaran", min_value=0)
            tahun = st.text_input("Tahun")
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun)
                st.success("Pembayaran Daftar Ulang berhasil disimpan!")

        st.write("**Data Daftar Ulang**")
        st.dataframe(df_daftar_ulang)

        # Generate and download receipt
        if not df_daftar_ulang.empty:
            st.write("**Download Kwitansi Daftar Ulang**")
            for index, row in df_daftar_ulang.iterrows():
                receipt = generate_receipt(row['nama_siswa'], row['kelas'], '', row['pembayaran'], row['biaya_daftar_ulang'], 'daftar_ulang')
                st.download_button(
                    label=f"Download Kwitansi {row['nama_siswa']} ({row['tahun']})",
                    data=receipt,
                    file_name=f"kwitansi_daftar_ulang_{row['nama_siswa']}_{row['tahun']}.pdf",
                    mime="application/pdf"
                )

    elif selected == "Pengeluaran":
        st.title("Pengelolaan Pengeluaran")
        with st.form("pengeluaran_form"):
            nama_penerima = st.text_input("Nama Penerima")
            keterangan_biaya = st.text_input("Keterangan Biaya")
            total_biaya = st.number_input("Total Biaya", min_value=0)
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya)
                st.success("Pengeluaran berhasil disimpan!")

        st.write("**Data Pengeluaran**")
        st.dataframe(df_pengeluaran)

        # Generate and download receipt
        if not df_pengeluaran.empty:
            st.write("**Download Kwitansi Pengeluaran**")
            for index, row in df_pengeluaran.iterrows():
                receipt = generate_expense_receipt(row['nama_penerima'], row['keterangan_biaya'], row['total_biaya'])
                st.download_button(
                    label=f"Download Kwitansi {row['nama_penerima']}",
                    data=receipt,
                    file_name=f"kwitansi_pengeluaran_{row['nama_penerima']}.pdf",
                    mime="application/pdf"
                )

        # Upload file
        st.write("**Upload File CSV Pengeluaran**")
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])
        if uploaded_file:
            try:
                new_data = pd.read_csv(uploaded_file)
                new_data.to_csv(CSV_PENGELUARAN, mode='a', header=False, index=False)
                st.success("File CSV berhasil diupload dan ditambahkan ke data pengeluaran!")
                df_pengeluaran = pd.read_csv(CSV_PENGELUARAN)
                st.dataframe(df_pengeluaran)
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

    elif selected == "Laporan Keuangan":
        st.title("Laporan Keuangan")
        
        # Display dataframes
        st.write("**Laporan Pembayaran SPP**")
        st.dataframe(df_spp)

        st.write("**Laporan Gaji Guru**")
        st.dataframe(df_gaji)

        st.write("**Laporan Daftar Ulang**")
        st.dataframe(df_daftar_ulang)

        st.write("**Laporan Pengeluaran**")
        st.dataframe(df_pengeluaran)

        # Export to Excel
        excel_data = export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran)
        st.download_button(
            label="Download Excel File",
            data=excel_data,
            file_name="laporan_keuangan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
