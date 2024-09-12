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
        'id': pd.Timestamp.now().strftime('%Y%m%d%H%M%S'),
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

def generate_receipt(id, nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Generate a well-formatted payment receipt as a PDF."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title section
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Kwitansi Pembayaran SPP", ln=True, align='C')
    pdf.ln(10)
    
    # Detail section
    pdf.set_font("Arial", size=12)
    details = [
        ("ID Pembayaran", id),
        ("Nama Siswa", nama_siswa),
        ("Kelas", kelas),
        ("Bulan", bulan),
        ("Jumlah Pembayaran", f"Rp {jumlah:,}"),
        ("Biaya SPP per Bulan", f"Rp {biaya_spp:,}"),
        ("Total Tagihan SPP 1 Tahun", f"Rp {biaya_spp * 12:,}"),
        ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
    ]
    
    for label, value in details:
        pdf.cell(100, 10, txt=label, border=1)
        pdf.cell(100, 10, txt=f": {value}", border=1, ln=True)
    
    # Signature section
    pdf.ln(10)
    pdf.cell(200, 10, txt="Tanda Terima", ln=True, align='R')
    
    # Output to BytesIO
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return pdf_output

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
                df = pd.read_csv(csv_path)
                latest_entry = df.iloc[-1]
                id = latest_entry['id']
                pdf_receipt = generate_receipt(id, nama_siswa, kelas, bulan, jumlah, biaya_spp)
                st.download_button(label="Download Kwitansi Pembayaran SPP", data=pdf_receipt, file_name=f"Kwitansi_SPP_{id}.pdf", mime='application/pdf')
            else:
                st.error("Semua field harus diisi!")

    st.subheader("Cari Pembayaran SPP")
    search_by = st.selectbox("Cari berdasarkan:", ["Nama Siswa", "Kelas"])
    search_value = st.text_input(f"Masukkan {search_by}")

    if search_value:
        df_spp = pd.read_csv(os.path.join(TEMP_DIR, 'pembayaran_spp.csv'))
        if search_by == "Nama Siswa":
            df_filtered = df_spp[df_spp['nama_siswa'].str.contains(search_value, case=False, na=False)]
        else:
            df_filtered = df_spp[df_spp['kelas'].str.contains(search_value, case=False, na=False)]
        
        st.dataframe(df_filtered)

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
