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

def save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya_diterima):
    df = pd.DataFrame([[nama_penerima, keterangan_biaya, total_biaya_diterima]], columns=['nama_penerima', 'keterangan_biaya', 'total_biaya_diterima'])
    if os.path.exists(CSV_PENGELUARAN):
        df_existing = pd.read_csv(CSV_PENGELUARAN)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(CSV_PENGELUARAN, index=False)

def generate_receipt(nama, keterangan, biaya, total, receipt_type):
    pdf = FPDF()
    pdf.add_page()

    # Add logo if exists
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=8, w=33)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="SD IT ARAHMAN", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="JATIMULYO", ln=True, align='C')
    pdf.ln(10)

    if receipt_type == 'spp':
        pdf.cell(0, 10, txt="Kwitansi Pembayaran SPP", ln=True, align='C')
        details = [
            ("Nama Siswa", nama),
            ("Kelas", keterangan),
            ("Bulan", biaya),
            ("Jumlah Pembayaran", f"Rp {total:,}"),
        ]
    elif receipt_type == 'gaji':
        pdf.cell(0, 10, txt="Kwitansi Pembayaran Gaji Guru", ln=True, align='C')
        details = [
            ("Nama Guru", nama),
            ("Bulan Gaji", keterangan),
            ("Gaji", f"Rp {biaya:,}"),
            ("Tunjangan", f"Rp {total:,}")
        ]
    elif receipt_type == 'daftar_ulang':
        pdf.cell(0, 10, txt="Kwitansi Pembayaran Daftar Ulang", ln=True, align='C')
        details = [
            ("Nama Siswa", nama),
            ("Kelas", keterangan),
            ("Biaya Daftar Ulang", f"Rp {biaya:,}"),
            ("Pembayaran", f"Rp {total:,}")
        ]
    else:  # pengeluaran
        pdf.cell(0, 10, txt="Kwitansi Pengeluaran", ln=True, align='C')
        details = [
            ("Nama Penerima", nama),
            ("Keterangan", keterangan),
            ("Total Biaya yang Diterima", f"Rp {total:,}")
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

        if selected == "Pembayaran SPP":
        st.title("Pembayaran SPP")
        st.write(df_spp)
        
        selected_spp = st.multiselect("Pilih data SPP untuk diunduh kwitansinya:", df_spp.index)
        
        if selected_spp:
            for i in selected_spp:
                spp_receipt = st.download_button(
                    label=f"Unduh Kwitansi SPP untuk {df_spp['Nama Siswa'][i]}",
                    data=generate_receipt(df_spp["Nama Siswa"][i], df_spp["Kelas"][i], df_spp["Jumlah Pembayaran"][i], 'SPP'),
                    file_name=f"kwitansi_spp_{df_spp['Nama Siswa'][i]}.pdf",
                    mime="application/pdf",
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
                st.success("Data Gaji Guru berhasil disimpan!")

        st.write(df_gaji)
        if not df_gaji.empty:
            gaji_receipt = st.download_button(
                label="Unduh Kwitansi Gaji",
                data=generate_receipt(nama_guru, bulan_gaji, gaji, tunjangan, 'gaji'),
                file_name="kwitansi_gaji_guru.pdf",
                mime="application/pdf",
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
                st.success("Data Daftar Ulang berhasil disimpan!")

        st.write(df_daftar_ulang)
        if not df_daftar_ulang.empty:
            daftar_ulang_receipt = st.download_button(
                label="Unduh Kwitansi Daftar Ulang",
                data=generate_receipt(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, 'daftar_ulang'),
                file_name="kwitansi_daftar_ulang.pdf",
                mime="application/pdf",
            )

    elif selected == "Pengeluaran":
        st.title("Pengeluaran")
        with st.form("pengeluaran_form"):
            nama_penerima = st.text_input("Nama Penerima")
            keterangan_biaya = st.text_area("Keterangan Biaya")
            total_biaya_diterima = st.number_input("Total Biaya yang Diterima", min_value=0)
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya_diterima)
                st.success("Data Pengeluaran berhasil disimpan!")

        st.write(df_pengeluaran)
        if not df_pengeluaran.empty:
            pengeluaran_receipt = st.download_button(
                label="Unduh Kwitansi Pengeluaran",
                data=generate_receipt(nama_penerima, keterangan_biaya, total_biaya_diterima, 0, 'pengeluaran'),
                file_name="kwitansi_pengeluaran.pdf",
                mime="application/pdf",
            )

    elif selected == "Laporan Keuangan":
        st.title("Laporan Keuangan")

        st.write("Pembayaran SPP")
        st.write(df_spp)

        st.write("Gaji Guru")
        st.write(df_gaji)

        st.write("Daftar Ulang")
        st.write(df_daftar_ulang)

        st.write("Pengeluaran")
        st.write(df_pengeluaran)

        if not df_spp.empty or not df_gaji.empty or not df_daftar_ulang.empty or not df_pengeluaran.empty:
            export_button = st.download_button(
                label="Unduh Laporan Excel",
                data=export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran),
                file_name="laporan_keuangan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

if __name__ == "__main__":
    main()
