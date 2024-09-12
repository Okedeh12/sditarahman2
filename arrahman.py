import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF
from streamlit_option_menu import option_menu

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
                    st.success("Pembayaran SPP berhasil disimpan!")
                    
                    # Generate and offer receipt download
                    pdf_receipt = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, "spp")
                    st.download_button(
                        label="Download Kwitansi Pembayaran SPP", 
                        data=pdf_receipt, 
                        file_name=f"Kwitansi_Pembayaran_SPP_{nama_siswa}.pdf", 
                        mime='application/pdf'
                    )
                else:
                    st.error("Semua field harus diisi!")
        
        if not df_spp.empty:
            st.subheader("Riwayat Pembayaran SPP")
            st.dataframe(df_spp)

            st.subheader("Unduh Kwitansi Pembayaran SPP")
            st.write("Pilih data pembayaran SPP untuk diunduh kwitansi.")
            
            selected_row = st.selectbox("Pilih Pembayaran", df_spp.index, format_func=lambda x: f"{df_spp.iloc[x]['nama_siswa']} - {df_spp.iloc[x]['bulan']}")
            
            if st.button("Unduh Kwitansi Terpilih"):
                row = df_spp.iloc[selected_row]
                pdf_receipt = generate_receipt(row['nama_siswa'], row['kelas'], row['bulan'], row['jumlah'], row['biaya_spp'], "spp")
                st.download_button(
                    label="Download Kwitansi Pembayaran SPP", 
                    data=pdf_receipt, 
                    file_name=f"Kwitansi_Pembayaran_SPP_{row['nama_siswa']}.pdf", 
                    mime='application/pdf'
                )
    
    elif selected == "Laporan Keuangan":
        st.title("Laporan Keuangan")
        st.write("Halaman laporan keuangan sekolah.")
        
        st.subheader("Laporan Pembayaran SPP")
        st.dataframe(df_spp)
        
        st.subheader("Laporan Gaji Guru")
        st.dataframe(df_gaji)

    elif selected == "Pengelolaan Gaji Guru":
        st.title("Pengelolaan Gaji Guru")
        st.write("Halaman untuk mengelola gaji guru.")
        
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

import os
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import streamlit as st
from streamlit_option_menu import option_menu

# Define the persistent directory for storing CSV files
PERSISTENT_DIR = 'data'
if not os.path.exists(PERSISTENT_DIR):
    os.makedirs(PERSISTENT_DIR)

# Define the path to the CSV files
CSV_PEMBAYARAN_SPP = os.path.join(PERSISTENT_DIR, 'pembayaran_spp.csv')
CSV_GAJI_GURU = os.path.join(PERSISTENT_DIR, 'gaji_guru.csv')
CSV_PENGELUARAN = os.path.join(PERSISTENT_DIR, 'pengeluaran.csv')

# Define the path to the logo file
LOGO_PATH = "assets/HN.png"

def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Save SPP payment details to CSV."""
    total_tagihan_tahun = biaya_spp * 12
    tagihan_sudah_terbayar = jumlah
    sisa_tagihan_belum_terbayar = total_tagihan_tahun - tagihan_sudah_terbayar

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

    if os.path.exists(CSV_PEMBAYARAN_SPP):
        df_existing = pd.read_csv(CSV_PEMBAYARAN_SPP)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(CSV_PEMBAYARAN_SPP, index=False)
    return CSV_PEMBAYARAN_SPP

def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    """Generate a well-formatted payment receipt as a PDF."""
    pdf = FPDF()
    pdf.add_page()

    school_name = "SD IT ARAHMAN"
    school_address = "JATIMULYO"

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
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Kwitansi Pembayaran SPP", ln=True, align='C')
    pdf.ln(10)
    
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
    
    pdf.ln(10)
    pdf.cell(0, 10, txt="Tanda Terima", ln=True, align='R')
    
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
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

    if os.path.exists(CSV_GAJI_GURU):
        df_existing = pd.read_csv(CSV_GAJI_GURU)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(CSV_GAJI_GURU, index=False)
    return CSV_GAJI_GURU

def save_pengeluaran(nama_penerima_dana, keterangan, total_biaya):
    """Save expense details to CSV."""
    df = pd.DataFrame([{
        'nama_penerima_dana': nama_penerima_dana,
        'keterangan': keterangan,
        'total_biaya': total_biaya,
        'tanggal': datetime.now().strftime('%Y-%m-%d')
    }])

    if os.path.exists(CSV_PENGELUARAN):
        df_existing = pd.read_csv(CSV_PENGELUARAN)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(CSV_PENGELUARAN, index=False)
    return CSV_PENGELUARAN

def generate_expense_receipt(nama_penerima_dana, keterangan, total_biaya):
    """Generate a well-formatted expense receipt as a PDF."""
    pdf = FPDF()
    pdf.add_page()

    school_name = "SD IT ARAHMAN"
    school_address = "JATIMULYO"

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
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Kwitansi Pengeluaran", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    details = [
        ("Nama Penerima Dana", nama_penerima_dana),
        ("Keterangan", keterangan),
        ("Total Biaya", f"Rp {total_biaya:,}"),
        ("Tanggal", datetime.now().strftime('%Y-%m-%d'))
    ]
    
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
    """Load existing data from CSV files."""
    data_spp = pd.read_csv(CSV_PEMBAYARAN_SPP) if os.path.exists(CSV_PEMBAYARAN_SPP) else pd.DataFrame()
    data_gaji = pd.read_csv(CSV_GAJI_GURU) if os.path.exists(CSV_GAJI_GURU) else pd.DataFrame()
    data_pengeluaran = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    return data_spp, data_gaji, data_pengeluaran

def to_excel(df, filename):
    """Convert DataFrame to Excel file."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.save()
    output.seek(0)
    return output

def main():
    # Load existing data
    df_spp, df_gaji, df_pengeluaran = load_data()

    # Streamlit app layout
    st.sidebar.title("Menu")
    selected = option_menu(None, ["Pembayaran SPP", "Gaji Guru", "Pengeluaran", "Laporan"], 
        icons=['money', 'cash', 'receipt', 'list'], 
        menu_icon="cast", default_index=0)
    
    if selected == "Pembayaran SPP":
        st.title("Manajemen Pembayaran SPP")
        with st.form("spp_form", clear_on_submit=True):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            bulan = st.text_input("Bulan")
            jumlah = st.number_input("Jumlah Pembayaran", min_value=0, step=1000)
            biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0, step=1000)
            submit_spp = st.form_submit_button("Simpan Pembayaran SPP")
            
            if submit_spp:
                if nama_siswa and kelas and bulan and jumlah >= 0 and biaya_spp >= 0:
                    csv_path = save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                    st.success("Data pembayaran SPP berhasil disimpan!")
                    
                    # Generate and offer receipt download
                    pdf_receipt = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                    st.download_button(
                        label="Download Kwitansi Pembayaran SPP", 
                        data=pdf_receipt, 
                        file_name=f"Kwitansi_Pembayaran_SPP_{nama_siswa}.pdf", 
                        mime='application/pdf'
                    )
                else:
                    st.error("Semua field harus diisi!")

    elif selected == "Gaji Guru":
        st.title("Manajemen Gaji Guru")
        with st.form("gaji_form", clear_on_submit=True):
            nama_guru = st.text_input("Nama Guru")
            bulan = st.text_input("Bulan")
            gaji = st.number_input("Gaji", min_value=0, step=1000)
            tunjangan = st.number_input("Tunjangan", min_value=0, step=1000)
            submit_gaji = st.form_submit_button("Simpan Gaji Guru")
            
            if submit_gaji:
                if nama_guru and bulan and gaji >= 0 and tunjangan >= 0:
                    csv_path = save_gaji_guru(nama_guru, bulan, gaji, tunjangan)
                    st.success("Data gaji guru berhasil disimpan!")

    elif selected == "Pengeluaran":
        st.title("Pengelolaan Pengeluaran")
        st.write("Halaman untuk mengelola pengeluaran sekolah.")
        
        with st.form("pengeluaran_form", clear_on_submit=True):
            nama_penerima_dana = st.text_input("Nama Penerima Dana")
            keterangan = st.text_area("Keterangan Biaya")
            total_biaya = st.number_input("Total Biaya", min_value=0, step=1000)
            submit_pengeluaran = st.form_submit_button("Simpan Pengeluaran") 
            
            if submit_pengeluaran:
                if nama_penerima_dana and keterangan and total_biaya > 0:
                    csv_path = save_pengeluaran(nama_penerima_dana, keterangan, total_biaya)
                    st.success("Data pengeluaran berhasil disimpan!")
                    
                    # Generate and offer receipt download
                    pdf_receipt = generate_expense_receipt(nama_penerima_dana, keterangan, total_biaya)
                    st.download_button(
                        label="Download Kwitansi Pengeluaran", 
                        data=pdf_receipt, 
                        file_name=f"Kwitansi_Pengeluaran_{nama_penerima_dana}.pdf", 
                        mime='application/pdf'
                    )
                else:
                    st.error("Semua field harus diisi!")
        
        if not df_pengeluaran.empty:
            st.subheader("Riwayat Pengeluaran")
            st.dataframe(df_pengeluaran)
            
            st.subheader("Unduh Kwitansi Pengeluaran")
            st.write("Pilih data pengeluaran untuk diunduh kwitansi.")
            
            selected_row = st.selectbox("Pilih Pengeluaran", df_pengeluaran.index, format_func=lambda x: f"{df_pengeluaran.iloc[x]['nama_penerima_dana']}")
            
            if st.button("Unduh Kwitansi Terpilih"):
                row = df_pengeluaran.iloc[selected_row]
                pdf_receipt = generate_expense_receipt(row['nama_penerima_dana'], row['keterangan'], row['total_biaya'])
                st.download_button(
                    label="Download Kwitansi Pengeluaran", 
                    data=pdf_receipt, 
                    file_name=f"Kwitansi_Pengeluaran_{row['nama_penerima_dana']}.pdf", 
                    mime='application/pdf'
                )

        st.subheader("Upload File Kwitansi")
        uploaded_file = st.file_uploader("Pilih file kwitansi untuk diunggah", type=["pdf"])
        
        if uploaded_file is not None:
            file_path = os.path.join(PERSISTENT_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            st.success("File kwitansi berhasil diunggah!")

    elif selected == "Laporan":
        st.title("Laporan Semua Data")
        
        st.subheader("Laporan Pembayaran SPP")
        if not df_spp.empty:
            st.dataframe(df_spp)
            excel_spp = to_excel(df_spp, 'laporan_pembayaran_spp.xlsx')
            st.download_button(
                label="Unduh Laporan Pembayaran SPP (Excel)", 
                data=excel_spp, 
                file_name='laporan_pembayaran_spp.xlsx', 
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.write("Tidak ada data SPP.")

        st.subheader("Laporan Gaji Guru")
        if not df_gaji.empty:
            st.dataframe(df_gaji)
            excel_gaji = to_excel(df_gaji, 'laporan_gaji_guru.xlsx')
            st.download_button(
                label="Unduh Laporan Gaji Guru (Excel)", 
                data=excel_gaji, 
                file_name='laporan_gaji_guru.xlsx', 
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.write("Tidak ada data gaji guru.")

        st.subheader("Laporan Pengeluaran")
        if not df_pengeluaran.empty:
            st.dataframe(df_pengeluaran)
            excel_pengeluaran = to_excel(df_pengeluaran, 'laporan_pengeluaran.xlsx')
            st.download_button(
                label="Unduh Laporan Pengeluaran (Excel)", 
                data=excel_pengeluaran, 
                file_name='laporan_pengeluaran.xlsx', 
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.write("Tidak ada data pengeluaran.")

if __name__ == "__main__":
    main()
