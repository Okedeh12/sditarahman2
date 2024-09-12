import requests
import os
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import streamlit as st
from streamlit_option_menu import option_menu

# Define the temporary directory for Streamlit
TEMP_DIR = '/tmp'

def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Save SPP payment details to CSV."""
    total_tagihan_tahun = biaya_spp * 12
    tagihan_sudah_terbayar = jumlah
    sisa_tagihan_belum_terbayar = total_tagihan_tahun - tagihan_sudah_terbayar

    # Create a DataFrame and save to CSV
    df = pd.DataFrame([{
        'nama_siswa': nama_siswa,
        'kelas': kelas,
        'bulan': bulan,
        'jumlah': jumlah,
        'biaya_spp': biaya_spp,
        'total_tagihan_tahun': total_tagihan_tahun,
        'tagihan_sudah_terbayar': tagihan_sudah_terbayar,
        'sisa_tagihan_belum_terbayar': sisa_tagihan_belum_terbayar,
        'tanggal': datetime.now().strftime('%Y-%m-%d')
    }])

    csv_path = os.path.join(TEMP_DIR, 'pembayaran_spp.csv')

    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(csv_path, index=False)
    return csv_path

# Define the path to the logo file
LOGO_PATH = "HN.png"  # Path to your local logo file

def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Generate a well-formatted payment receipt as a PDF."""
    pdf = FPDF()
    pdf.add_page()

    # School details
    school_name = "SD IT ARAHMAN"
    school_address = "JATIMULYO"

    # Add logo
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=8, w=33)  # Adjust x, y, and w as needed
    else:
        print("Logo file not found.")

    # Title section
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=school_name, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=school_address, ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Kwitansi Pembayaran SPP", ln=True, align='C')
    pdf.ln(10)
    
    # Detail section
    pdf.set_font("Arial", size=12)
    details = [
        ("Nama Siswa", nama_siswa),
        ("Kelas", kelas),
        ("Bulan", bulan),
        ("Jumlah Pembayaran", f"Rp {jumlah:,}"),
        ("Biaya SPP per Bulan", f"Rp {biaya_spp:,}"),
        ("Total Tagihan SPP 1 Tahun", f"Rp {biaya_spp * 12:,}"),
        ("Tagihan Sudah Terbayar", f"Rp {jumlah:,}"),
        ("Sisa Tagihan Belum Terbayar", f"Rp {biaya_spp * 12 - jumlah:,}"),
        ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
    ]
    
    for label, value in details:
        pdf.cell(100, 10, txt=label, border=1)
        pdf.cell(90, 10, txt=f": {value}", border=1, ln=True)
    
    # Signature section
    pdf.ln(10)
    pdf.cell(0, 10, txt="Tanda Terima", ln=True, align='R')
    
    # Output to BytesIO
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return pdf_output

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
    
    with st.form("pembayaran_spp_form", clear_on_submit=True):
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.text_input("Kelas")
        bulan = st.text_input("Bulan")
        jumlah = st.number_input("Jumlah Pembayaran", min_value=0, step=1000)
        biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0, step=1000)
        submit = st.form_submit_button("Simpan Pembayaran")
        
        if submit:
            if nama_siswa and kelas and bulan and jumlah > 0 and biaya_spp > 0:
                csv_path = save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.success("Pembayaran berhasil disimpan!")
                
                # Generate and offer receipt download
                pdf_receipt = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.download_button(
                    label="Download Kwitansi Pembayaran SPP", 
                    data=pdf_receipt.getvalue(), 
                    file_name=f"Kwitansi_SPP_{nama_siswa}_{bulan}.pdf", 
                    mime='application/pdf'
                )
            else:
                st.error("Semua field harus diisi!")
    
    # Tampilkan data pembayaran SPP
    if os.path.exists(os.path.join(TEMP_DIR, 'pembayaran_spp.csv')):
        st.subheader("Riwayat Pembayaran SPP")
        df_spp = pd.read_csv(os.path.join(TEMP_DIR, 'pembayaran_spp.csv'))
        st.dataframe(df_spp)

    
def save_gaji_guru(nama_guru, bulan, gaji, tunjangan):
    """Save teacher salary details to CSV."""
    df = pd.DataFrame([{
        'nama_guru': nama_guru,
        'bulan': bulan,
        'gaji': gaji,
        'tunjangan': tunjangan,
        'tanggal': datetime.now().strftime('%Y-%m-%d')
    }])

    csv_path = os.path.join(TEMP_DIR, 'gaji_guru.csv')

    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(csv_path, index=False)
    return csv_path

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
    
    with st.form("pembayaran_spp_form", clear_on_submit=True):
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.text_input("Kelas")
        bulan = st.text_input("Bulan")
        jumlah = st.number_input("Jumlah Pembayaran", min_value=0, step=1000)
        biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0, step=1000)
        submit = st.form_submit_button("Simpan Pembayaran")
        
        if submit:
            if nama_siswa and kelas and bulan and jumlah > 0 and biaya_spp > 0:
                csv_path = save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.success("Pembayaran berhasil disimpan!")
                
                # Generate and offer receipt download
                pdf_receipt = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.download_button(label="Download Kwitansi Pembayaran SPP", data=pdf_receipt, file_name=f"Kwitansi_SPP_{nama_siswa}_{bulan}.pdf", mime='application/pdf')
            else:
                st.error("Semua field harus diisi!")
    
    # Tampilkan data pembayaran SPP
    if os.path.exists(os.path.join(TEMP_DIR, 'pembayaran_spp.csv')):
        st.subheader("Riwayat Pembayaran SPP")
        df_spp = pd.read_csv(os.path.join(TEMP_DIR, 'pembayaran_spp.csv'))
        st.dataframe(df_spp)
        
        st.subheader("Unduh Kwitansi Pembayaran")
        st.write("Pilih data pembayaran SPP untuk diunduh kwitansi.")
        
        selected_row = st.selectbox("Pilih Pembayaran", df_spp.index, format_func=lambda x: f"{df_spp.iloc[x]['nama_siswa']} - {df_spp.iloc[x]['bulan']}")
        
        if st.button("Unduh Kwitansi Terpilih"):
            row = df_spp.iloc[selected_row]
            pdf_receipt = generate_receipt(row['nama_siswa'], row['kelas'], row['bulan'], row['jumlah'], row['biaya_spp'])
            st.download_button(label="Download Kwitansi Pembayaran SPP", data=pdf_receipt, file_name=f"Kwitansi_SPP_{row['nama_siswa']}_{row['bulan']}.pdf", mime='application/pdf')

elif selected == "Laporan Keuangan":
    st.title("Laporan Keuangan")
    st.write("Halaman laporan keuangan sekolah.")
    
    # Tampilkan laporan pembayaran SPP dalam bentuk CSV
    if os.path.exists(os.path.join(TEMP_DIR, 'pembayaran_spp.csv')):
        st.download_button(label="Download Laporan Pembayaran SPP", data=open(os.path.join(TEMP_DIR, 'pembayaran_spp.csv'), 'rb').read(), file_name='laporan_pembayaran_spp.csv', mime='text/csv')
    
    # Tampilkan laporan gaji guru dalam bentuk CSV
    if os.path.exists(os.path.join(TEMP_DIR, 'gaji_guru.csv')):
        st.download_button(label="Download Laporan Gaji Guru", data=open(os.path.join(TEMP_DIR, 'gaji_guru.csv'), 'rb').read(), file_name='laporan_gaji_guru.csv', mime='text/csv')

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
                csv_path = save_gaji_guru(nama_guru, bulan, gaji, tunjangan)
                st.success("Data gaji guru berhasil disimpan!")
            else:
                st.error("Semua field harus diisi!")
