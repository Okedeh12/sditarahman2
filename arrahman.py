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

# Define the paths to the CSV files
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
        'total_tagihan_tahun': total_tagihan_tahun,
        'tagihan_sudah_terbayar': tagihan_sudah_terbayar,
        'sisa_tagihan_belum_terbayar': sisa_tagihan_belum_terbayar,
        'tahun': tahun,
        'tanggal': datetime.now().strftime('%Y-%m-%d')
    }])

    if os.path.exists(CSV_PEMBAYARAN_SPP):
        df_existing = pd.read_csv(CSV_PEMBAYARAN_SPP)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(CSV_PEMBAYARAN_SPP, index=False)
    return CSV_PEMBAYARAN_SPP

def save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun):
    """Save re-registration payment details to CSV."""
    total_tagihan = biaya_daftar_ulang
    sisa_tagihan = total_tagihan - pembayaran

    # Create a DataFrame and save to CSV
    df = pd.DataFrame([{
        'nama_siswa': nama_siswa,
        'kelas': kelas,
        'biaya_daftar_ulang': biaya_daftar_ulang,
        'pembayaran': pembayaran,
        'sisa_tagihan': sisa_tagihan,
        'tahun': tahun,
        'tanggal': datetime.now().strftime('%Y-%m-%d')
    }])

    if os.path.exists(CSV_PEMBAYARAN_SPP):
        df_existing = pd.read_csv(CSV_PEMBAYARAN_SPP)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(CSV_PEMBAYARAN_SPP, index=False)
    return CSV_PEMBAYARAN_SPP

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

def save_pengeluaran(nama_penerima, keterangan_dana, total_biaya):
    """Save school expense details to CSV."""
    df = pd.DataFrame([{
        'nama_penerima': nama_penerima,
        'keterangan_dana': keterangan_dana,
        'total_biaya': total_biaya,
        'tanggal': datetime.now().strftime('%Y-%m-%d')
    }])

    if os.path.exists(CSV_PENGELUARAN):
        df_existing = pd.read_csv(CSV_PENGELUARAN)
        df = pd.concat([df_existing, df], ignore_index=True)
    
    df.to_csv(CSV_PENGELUARAN, index=False)
    return CSV_PENGELUARAN

def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, tahun, receipt_type):
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
    pdf.cell(0, 10, txt=f"Kwitansi {receipt_type}", ln=True, align='C')
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
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)

    return pdf_output

def load_data():
    """Load existing data from CSV files."""
    data_spp = pd.read_csv(CSV_PEMBAYARAN_SPP) if os.path.exists(CSV_PEMBAYARAN_SPP) else pd.DataFrame()
    data_gaji = pd.read_csv(CSV_GAJI_GURU) if os.path.exists(CSV_GAJI_GURU) else pd.DataFrame()
    data_pengeluaran = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    return data_spp, data_gaji, data_pengeluaran

# Streamlit App
def main():
    # Load existing data
    df_spp, df_gaji, df_pengeluaran = load_data()

    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Pembayaran SPP", "Daftar Ulang", "Pengelolaan Gaji Guru", "Pengelolaan Pengeluaran", "Semua Laporan"],
            icons=["cash-stack", "list", "person-badge", "file-earmark-text", "files"],
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
            tahun = st.text_input("Tahun")
            submit = st.form_submit_button("Simpan Pembayaran")
            
            if submit:
                if nama_siswa and kelas and bulan and jumlah > 0 and biaya_spp > 0 and tahun:
                    csv_path = save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp, tahun)
                    st.success("Pembayaran berhasil disimpan!")
                    
                    # Generate and offer receipt download
                    pdf_receipt = generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, tahun, "Pembayaran SPP")
                    st.download_button(
                        label="Download Kwitansi Pembayaran SPP", 
                        data=pdf_receipt, 
                        file_name=f"Kwitansi_SPP_{nama_siswa}_{bulan}.pdf", 
                        mime='application/pdf'
                    )
                else:
                    st.error("Semua field harus diisi!")
        
        # Display data from CSV
        if not df_spp.empty:
            st.subheader("Riwayat Pembayaran SPP")
            st.dataframe(df_spp)
            
            st.subheader("Unduh Kwitansi Pembayaran")
            st.write("Pilih data pembayaran SPP untuk diunduh kwitansi.")
            
            selected_row = st.selectbox("Pilih Pembayaran", df_spp.index, format_func=lambda x: f"{df_spp.iloc[x]['nama_siswa']} - {df_spp.iloc[x]['bulan']}")
            
            if st.button("Unduh Kwitansi Terpilih"):
                row = df_spp.iloc[selected_row]
                pdf_receipt = generate_receipt(row['nama_siswa'], row['kelas'], row['bulan'], row['jumlah'], row['biaya_spp'], row['tahun'], "Pembayaran SPP")
                st.download_button(
                    label="Download Kwitansi Pembayaran SPP", 
                    data=pdf_receipt, 
                    file_name=f"Kwitansi_SPP_{row['nama_siswa']}_{row['bulan']}.pdf", 
                    mime='application/pdf'
                )

    elif selected == "Daftar Ulang":
        st.title("Daftar Ulang")
        st.write("Halaman untuk pembayaran daftar ulang siswa.")
        
        with st.form("daftar_ulang_form", clear_on_submit=True):
            nama_siswa = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang 1 Tahun", min_value=0, step=1000)
            pembayaran = st.number_input("Pembayaran", min_value=0, step=1000)
            tahun = st.text_input("Tahun")
            submit = st.form_submit_button("Simpan Pembayaran Daftar Ulang")
            
            if submit:
                if nama_siswa and kelas and biaya_daftar_ulang >= 0 and pembayaran >= 0 and tahun:
                    csv_path = save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun)
                    st.success("Pembayaran daftar ulang berhasil disimpan!")
                    
                    # Generate and offer receipt download
                    pdf_receipt = generate_receipt(nama_siswa, kelas, "", pembayaran, biaya_daftar_ulang, tahun, "Daftar Ulang")
                    st.download_button(
                        label="Download Kwitansi Daftar Ulang", 
                        data=pdf_receipt, 
                        file_name=f"Kwitansi_Daftar_Ulang_{nama_siswa}.pdf", 
                        mime='application/pdf'
                    )
                else:
                    st.error("Semua field harus diisi!")
        
        # Display data from CSV
        if not df_spp.empty:
            st.subheader("Riwayat Pembayaran Daftar Ulang")
            st.dataframe(df_spp[df_spp['biaya_daftar_ulang'].notna()])
            
            st.subheader("Unduh Kwitansi Pembayaran Daftar Ulang")
            st.write("Pilih data pembayaran daftar ulang untuk diunduh kwitansi.")
            
            selected_row = st.selectbox("Pilih Pembayaran Daftar Ulang", df_spp[df_spp['biaya_daftar_ulang'].notna()].index, format_func=lambda x: f"{df_spp.iloc[x]['nama_siswa']}")
            
            if st.button("Unduh Kwitansi Terpilih"):
                row = df_spp.iloc[selected_row]
                pdf_receipt = generate_receipt(row['nama_siswa'], row['kelas'], "", row['pembayaran'], row['biaya_daftar_ulang'], row['tahun'], "Daftar Ulang")
                st.download_button(
                    label="Download Kwitansi Daftar Ulang", 
                    data=pdf_receipt, 
                    file_name=f"Kwitansi_Daftar_Ulang_{row['nama_siswa']}.pdf", 
                    mime='application/pdf'
                )

    elif selected == "Pengelolaan Gaji Guru":
        st.title("Pengelolaan Gaji Guru")
        st.write("Halaman untuk mengelola gaji guru.")
        
        with st.form("gaji_guru_form", clear_on_submit=True):
            nama_guru = st.text_input("Nama Guru")
            bulan_gaji = st.text_input("Bulan")
            gaji = st.number_input("Gaji", min_value=0, step=1000)
            tunjangan = st.number_input("Tunjangan", min_value=0, step=1000)
            submit_gaji = st.form_submit_button("Simpan Gaji")
            
            if submit_gaji:
                if nama_guru and bulan_gaji and gaji >= 0 and tunjangan >= 0:
                    csv_path = save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
                    st.success("Data gaji berhasil disimpan!")
                    
                    # Display the saved data
                    df_gaji = pd.read_csv(csv_path)
                    st.dataframe(df_gaji)
                else:
                    st.error("Semua field harus diisi!")

        # Display data from CSV
        if not df_gaji.empty:
            st.subheader("Riwayat Gaji Guru")
            st.dataframe(df_gaji)

            st.subheader("Unduh Laporan Gaji Guru")
            st.write("Unduh laporan gaji guru dalam bentuk CSV.")
            
            st.download_button(
                label="Download Laporan Gaji Guru", 
                data=open(CSV_GAJI_GURU, 'rb').read(), 
                file_name='laporan_gaji_guru.csv', 
                mime='text/csv'
            )

    elif selected == "Pengelolaan Pengeluaran":
        st.title("Pengelolaan Pengeluaran")
        st.write("Halaman untuk mengelola pengeluaran sekolah.")
        
        with st.form("pengeluaran_form", clear_on_submit=True):
            nama_penerima = st.text_input("Nama Penerima Dana")
            keterangan_dana = st.text_input("Keterangan Dana yang Dikeluarkan")
            total_biaya = st.number_input("Total Biaya", min_value=0, step=1000)
            submit_pengeluaran = st.form_submit_button("Simpan Pengeluaran")
            
            if submit_pengeluaran:
                if nama_penerima and keterangan_dana and total_biaya >= 0:
                    csv_path = save_pengeluaran(nama_penerima, keterangan_dana, total_biaya)
                    st.success("Data pengeluaran berhasil disimpan!")
                    
                    # Display the saved data
                    df_pengeluaran = pd.read_csv(csv_path)
                    st.dataframe(df_pengeluaran)
                else:
                    st.error("Semua field harus diisi!")
        
        st.subheader("Laporan Pengeluaran")
        if not df_pengeluaran.empty:
            st.dataframe(df_pengeluaran)
            
            st.subheader("Unduh Kwitansi Pengeluaran")
            st.write("Pilih data pengeluaran untuk diunduh kwitansi.")
            
            selected_row = st.selectbox("Pilih Pengeluaran", df_pengeluaran.index, format_func=lambda x: f"{df_pengeluaran.iloc[x]['nama_penerima']} - {df_pengeluaran.iloc[x]['keterangan_dana']}")
            
            if st.button("Unduh Kwitansi Terpilih"):
                row = df_pengeluaran.iloc[selected_row]
                pdf_receipt = generate_receipt(row['nama_penerima'], "", "", row['total_biaya'], 0, "", "Pengeluaran")
                st.download_button(
                    label="Download Kwitansi Pengeluaran", 
                    data=pdf_receipt, 
                    file_name=f"Kwitansi_Pengeluaran_{row['nama_penerima']}.pdf", 
                    mime='application/pdf'
                )

        st.subheader("Upload Kwitansi Pembayaran")
        uploaded_file = st.file_uploader("Upload File Kwitansi Pembayaran", type=['pdf'])
        if uploaded_file is not None:
            file_path = os.path.join(PERSISTENT_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File {uploaded_file.name} berhasil diunggah!")

    elif selected == "Semua Laporan":
        st.title("Semua Laporan")
        st.write("Halaman untuk mengunduh semua laporan dalam format Excel.")
        
        def to_excel(df, filename):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                writer.save()
            output.seek(0)
            return output

        if not df_spp.empty:
            st.subheader("Laporan Pembayaran SPP")
            st.download_button(
                label="Download Laporan Pembayaran SPP", 
                data=to_excel(df_spp, 'laporan_pembayaran_spp.xlsx'), 
                file_name='laporan_pembayaran_spp.xlsx', 
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        if not df_gaji.empty:
            st.subheader("Laporan Gaji Guru")
            st.download_button(
                label="Download Laporan Gaji Guru", 
                data=to_excel(df_gaji, 'laporan_gaji_guru.xlsx'), 
                file_name='laporan_gaji_guru.xlsx', 
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        if not df_pengeluaran.empty:
            st.subheader("Laporan Pengeluaran")
            st.download_button(
                label="Download Laporan Pengeluaran", 
                data=to_excel(df_pengeluaran, 'laporan_pengeluaran.xlsx'), 
                file_name='laporan_pengeluaran.xlsx', 
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if __name__ == "__main__":
    main()
