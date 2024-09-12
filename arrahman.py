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

def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp, tahun):
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
        'tahun': tahun,
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

def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, tahun):
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
        # Use a placeholder or handle the missing logo gracefully
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt="Logo Tidak Ditemukan", ln=True, align='C')

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
        ("Tahun", tahun),
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

def save_pengeluaran(nama_penerima_dana, keterangan_dana, total_biaya):
    """Save school expense details to CSV."""
    df = pd.DataFrame([{
        'nama_penerima_dana': nama_penerima_dana,
        'keterangan_dana': keterangan_dana,
        'total_biaya': total_biaya,
        'tanggal': datetime.now().strftime('%Y-%m-%d')
    }])

    if os.path.exists(CSV_PENGELUARAN):
        df_existing = pd.read_csv(CSV_PENGELUARAN)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(CSV_PENGELUARAN, index=False)
    return CSV_PENGELUARAN

def generate_expense_receipt(nama_penerima_dana, keterangan_dana, total_biaya):
    """Generate a well-formatted expense receipt as a PDF."""
    pdf = FPDF()
    pdf.add_page()

    # School details
    school_name = "SD IT ARAHMAN"
    school_address = "JATIMULYO"

    # Add logo
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=8, w=33)  # Adjust x, y, and w as needed
    else:
        # Use a placeholder or handle the missing logo gracefully
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt="Logo Tidak Ditemukan", ln=True, align='C')

    # Title section
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=school_name, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=school_address, ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Kwitansi Pengeluaran", ln=True, align='C')
    pdf.ln(10)
    
    # Detail section
    pdf.set_font("Arial", size=12)
    details = [
        ("Nama Penerima Dana", nama_penerima_dana),
        ("Keterangan Dana", keterangan_dana),
        ("Total Biaya", f"Rp {total_biaya:,}"),
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
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)

    return pdf_output

def to_excel(df, filename):
    """Convert DataFrame to Excel file using openpyxl."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.save()
    output.seek(0)
    return output

def load_data():
    """Load existing data from CSV files."""
    data_spp = pd.read_csv(CSV_PEMBAYARAN_SPP) if os.path.exists(CSV_PEMBAYARAN_SPP) else pd.DataFrame()
    data_gaji = pd.read_csv(CSV_GAJI_GURU) if os.path.exists(CSV_GAJI_GURU) else pd.DataFrame()
    data_pengeluaran = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    return data_spp, data_gaji, data_pengeluaran

def main():
    st.title("Aplikasi Pengelolaan Keuangan Sekolah")
    
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["Pengelolaan SPP", "Pengelolaan Gaji", "Pengelolaan Pengeluaran", "Semua Laporan"],
            icons=["house", "person", "file-earmark", "file-earmark"],
            default_index=0
        )

    df_spp, df_gaji, df_pengeluaran = load_data()

    if selected == "Pengelolaan SPP":
        st.subheader("Form Pembayaran SPP")
        nama_siswa = st.text_input("Nama Siswa")
        kelas = st.text_input("Kelas")
        bulan = st.text_input("Bulan")
        jumlah = st.number_input("Jumlah Pembayaran", min_value=0)
        biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0)
        tahun = st.selectbox("Tahun", options=[datetime.now().year - 1, datetime.now().year, datetime.now().year + 1])

        if st.button("Simpan Pembayaran"):
            if nama_siswa and kelas and bulan and jumlah >= 0 and biaya_spp >= 0:
                save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp, tahun)
                st.success("Data Pembayaran SPP berhasil disimpan.")
            else:
                st.error("Silakan lengkapi semua kolom dengan benar.")

    elif selected == "Pengelolaan Gaji":
        st.subheader("Form Pengelolaan Gaji Guru")
        nama_guru = st.text_input("Nama Guru")
        bulan_gaji = st.text_input("Bulan")
        gaji = st.number_input("Gaji", min_value=0)
        tunjangan = st.number_input("Tunjangan", min_value=0)

        if st.button("Simpan Gaji"):
            if nama_guru and bulan_gaji and gaji >= 0:
                save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
                st.success("Data Gaji Guru berhasil disimpan.")
            else:
                st.error("Silakan lengkapi semua kolom dengan benar.")

    elif selected == "Pengelolaan Pengeluaran":
        st.subheader("Form Pengelolaan Pengeluaran")
        nama_penerima_dana = st.text_input("Nama Penerima Dana")
        keterangan_dana = st.text_input("Keterangan Dana")
        total_biaya = st.number_input("Total Biaya", min_value=0)

        if st.button("Simpan Pengeluaran"):
            if nama_penerima_dana and keterangan_dana and total_biaya >= 0:
                save_pengeluaran(nama_penerima_dana, keterangan_dana, total_biaya)
                st.success("Data Pengeluaran berhasil disimpan.")
            else:
                st.error("Silakan lengkapi semua kolom dengan benar.")
        
        st.subheader("Upload Kwitansi Pembayaran")
        uploaded_file = st.file_uploader("Upload File Kwitansi", type=["pdf", "jpg", "png"])
        if uploaded_file:
            # Save the uploaded file
            with open(os.path.join(PERSISTENT_DIR, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getvalue())
            st.success("File kwitansi berhasil diunggah.")

    elif selected == "Semua Laporan":
        st.title("Semua Laporan")
        st.write("Halaman untuk mengunduh semua laporan dalam format Excel.")

        if not df_spp.empty:
            st.subheader("Laporan Pembayaran SPP")
            st.download_button(
                label="Download Laporan Pembayaran SPP",
                data=to_excel(df_spp, 'laporan_pembayaran_spp.xlsx'),
                file_name='laporan_pembayaran_spp.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("Data Pembayaran SPP tidak tersedia.")

        if not df_gaji.empty:
            st.subheader("Laporan Gaji Guru")
            st.download_button(
                label="Download Laporan Gaji Guru",
                data=to_excel(df_gaji, 'laporan_gaji_guru.xlsx'),
                file_name='laporan_gaji_guru.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("Data Gaji Guru tidak tersedia.")

        if not df_pengeluaran.empty:
            st.subheader("Laporan Pengeluaran")
            st.download_button(
                label="Download Laporan Pengeluaran",
                data=to_excel(df_pengeluaran, 'laporan_pengeluaran.xlsx'),
                file_name='laporan_pengeluaran.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("Data Pengeluaran tidak tersedia.")

if __name__ == "__main__":
    main()
