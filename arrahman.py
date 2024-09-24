import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF
from streamlit_option_menu import option_menu
from datetime import datetime
import matplotlib

# Define CSV file paths
CSV_PEMBAYARAN_SPP = 'data/pembayaran_spp.csv'
CSV_GAJI_GURU = 'data/gaji_guru.csv'
CSV_DAFTAR_ULANG = 'data/daftar_ulang.csv'
CSV_PENGELUARAN = 'data/pengeluaran.csv'
PERSISTENT_DIR = 'data/uploads'
LOGO_PATH = 'data/lv.jpeg'

# Ensure data directories exist
os.makedirs('data', exist_ok=True)
os.makedirs(PERSISTENT_DIR, exist_ok=True)

# Load CSV files
CSV_PEMBAYARAN_SPP = 'path_to_spp.csv'
CSV_GAJI_GURU = 'path_to_gaji_guru.csv'
CSV_DAFTAR_ULANG = 'path_to_daftar_ulang.csv'
CSV_PENGELUARAN = 'path_to_pengeluaran.csv'

def load_data():
    df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP) if os.path.exists(CSV_PEMBAYARAN_SPP) else pd.DataFrame()
    df_gaji = pd.read_csv(CSV_GAJI_GURU) if os.path.exists(CSV_GAJI_GURU) else pd.DataFrame()
    df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG) if os.path.exists(CSV_DAFTAR_ULANG) else pd.DataFrame()
    df_pengeluaran = pd.read_csv(CSV_PENGELUARAN) if os.path.exists(CSV_PENGELUARAN) else pd.DataFrame()
    return df_spp, df_gaji, df_daftar_ulang, df_pengeluaran

def export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran):
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_spp.to_excel(writer, sheet_name='Pembayaran SPP', index=False)
            df_gaji.to_excel(writer, sheet_name='Gaji Guru', index=False)
            df_daftar_ulang.to_excel(writer, sheet_name='Daftar Ulang', index=False)
            df_pengeluaran.to_excel(writer, sheet_name='Pengeluaran', index=False)
        return buffer.getvalue()

def calculate_monthly_income(df_spp):
    df_spp['tanggal_pembayaran'] = pd.to_datetime(df_spp['tanggal_pembayaran'])
    df_spp['month'] = df_spp['tanggal_pembayaran'].dt.to_period('M')
    monthly_income = df_spp.groupby('month')['jumlah'].sum().reset_index()
    monthly_income.columns = ['Bulan', 'Total Pendapatan']
    return monthly_income

def calculate_historical_income(df_spp):
    df_spp['tanggal_pembayaran'] = pd.to_datetime(df_spp['tanggal_pembayaran'])
    df_spp['month'] = df_spp['tanggal_pembayaran'].dt.to_period('M')
    historical_income = df_spp.groupby('month')['jumlah'].sum().reset_index()
    historical_income.columns = ['Bulan', 'Total Pendapatan']
    return historical_income

def main():
    df_spp, df_gaji, df_daftar_ulang, df_pengeluaran = load_data()

# Helper function to get current timestamp
def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp, timestamp):
    new_data = pd.DataFrame({
        'nama_siswa': [nama_siswa],
        'kelas': [kelas],
        'bulan': [bulan],
        'jumlah': [jumlah],
        'biaya_spp': [biaya_spp],
        'timestamp': [timestamp]
    })
    if os.path.exists(CSV_PEMBAYARAN_SPP):
        df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP)
        df_spp = pd.concat([df_spp, new_data], ignore_index=True)
    else:
        df_spp = new_data
    df_spp.to_csv(CSV_PEMBAYARAN_SPP, index=False)

def save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan, timestamp):
    new_data = pd.DataFrame({
        'nama_guru': [nama_guru],
        'bulan_gaji': [bulan_gaji],
        'gaji': [gaji],
        'tunjangan': [tunjangan],
        'timestamp': [timestamp]
    })
    if os.path.exists(CSV_GAJI_GURU):
        df_gaji = pd.read_csv(CSV_GAJI_GURU)
        df_gaji = pd.concat([df_gaji, new_data], ignore_index=True)
    else:
        df_gaji = new_data
    df_gaji.to_csv(CSV_GAJI_GURU, index=False)

def save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun, timestamp):
    new_data = pd.DataFrame({
        'nama_siswa': [nama_siswa],
        'kelas': [kelas],
        'biaya_daftar_ulang': [biaya_daftar_ulang],
        'pembayaran': [pembayaran],
        'tahun': [tahun],
        'timestamp': [timestamp]
    })
    if os.path.exists(CSV_DAFTAR_ULANG):
        df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG)
        df_daftar_ulang = pd.concat([df_daftar_ulang, new_data], ignore_index=True)
    else:
        df_daftar_ulang = new_data
    df_daftar_ulang.to_csv(CSV_DAFTAR_ULANG, index=False)

def save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, timestamp):
    new_data = pd.DataFrame({
        'nama_penerima': [nama_penerima],
        'keterangan_biaya': [keterangan_biaya],
        'total_biaya': [total_biaya],
        'timestamp': [timestamp]
    })
    if os.path.exists(CSV_PENGELUARAN):
        df_pengeluaran = pd.read_csv(CSV_PENGELUARAN)
        df_pengeluaran = pd.concat([df_pengeluaran, new_data], ignore_index=True)
    else:
        df_pengeluaran = new_data
    df_pengeluaran.to_csv(CSV_PENGELUARAN, index=False)


def generate_receipt(nama_siswa, kelas, bulan, jumlah, biaya_spp, receipt_type):
    pdf = FPDF()
    pdf.add_page()
    
    # School details
    school_name = "SD IT ARAHMAN"
    school_address = "jl. dadapan blok 3 selatan, Jatimulyo, Kec. Jati Agung, Lamsel"

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
            menu_title="SD IT AR RAHMAN",
            options=["Pembayaran SPP", "Pengelolaan Gaji Guru", "Daftar Ulang", "Pengeluaran", "Laporan Keuangan"],
            icons=["cash", "bar-chart", "person-badge", "clipboard-check", "money"],
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
            nama_siswa = st.text_input("Nama Siswa", key="spp_nama_siswa")
            kelas = st.text_input("Kelas", key="spp_kelas")
            bulan = st.text_input("Bulan", key="spp_bulan")
            jumlah = st.number_input("Jumlah Pembayaran", min_value=0, key="spp_jumlah")
            biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0, key="spp_biaya_spp")
            timestamp = get_current_timestamp()
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp, timestamp)
                df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP)
                st.success("Pembayaran SPP berhasil disimpan!")

        st.write("**Data Pembayaran SPP**")
        search_spp = st.text_input("Cari Siswa", key="search_spp")
        if os.path.exists(CSV_PEMBAYARAN_SPP):
            df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP)
            if search_spp:
                df_spp = df_spp[df_spp['nama_siswa'].str.contains(search_spp, case=False, na=False)]
            st.dataframe(df_spp)

        st.write("**Download Kwitansi Pembayaran SPP**")
        if not df_spp.empty:
            options = list(df_spp.index)
            selected_index = st.selectbox("Pilih Nomor Urut Kwitansi", options)
            if st.button("Download Kwitansi"):
                row = df_spp.loc[selected_index]
                receipt = generate_receipt(row.get('nama_siswa', ''), row.get('kelas', ''), row.get('bulan', ''), row.get('jumlah', 0), row.get('biaya_spp', 0), 'spp')
                st.download_button(
                    label=f"Download Kwitansi {row.get('nama_siswa', '')} ({row.get('bulan', '')})",
                    data=receipt,
                    file_name=f"kwitansi_spp_{row.get('nama_siswa', '')}_{row.get('bulan', '')}.pdf",
                    mime="application/pdf",
                    key=f"download_spp_{selected_index}"
                )

    elif selected == "Pengelolaan Gaji Guru":
        st.title("Pengelolaan Gaji Guru")
        with st.form("gaji_form"):
            nama_guru = st.text_input("Nama Guru", key="gaji_nama_guru")
            bulan_gaji = st.text_input("Bulan Gaji", key="gaji_bulan_gaji")
            gaji = st.number_input("Gaji", min_value=0, key="gaji_gaji")
            tunjangan = st.number_input("Tunjangan", min_value=0, key="gaji_tunjangan")
            timestamp = get_current_timestamp()
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan, timestamp)
                df_gaji = pd.read_csv(CSV_GAJI_GURU)
                st.success("Gaji Guru berhasil disimpan!")

        st.write("**Data Gaji Guru**")
        search_gaji = st.text_input("Cari Guru", key="search_gaji")
        if os.path.exists(CSV_GAJI_GURU):
            df_gaji = pd.read_csv(CSV_GAJI_GURU)
            if search_gaji:
                df_gaji = df_gaji[df_gaji['nama_guru'].str.contains(search_gaji, case=False, na=False)]
            st.dataframe(df_gaji)

        st.write("**Download Kwitansi Gaji Guru**")
        if not df_gaji.empty:
            options = list(df_gaji.index)
            selected_index = st.selectbox("Pilih Nomor Urut Kwitansi", options)
            if st.button("Download Kwitansi"):
                row = df_gaji.loc[selected_index]
                receipt = generate_receipt(row.get('nama_guru', ''), row.get('bulan_gaji', ''), '', row.get('gaji', 0), row.get('tunjangan', 0), 'gaji')
                st.download_button(
                    label=f"Download Kwitansi {row.get('nama_guru', '')} ({row.get('bulan_gaji', '')})",
                    data=receipt,
                    file_name=f"kwitansi_gaji_{row.get('nama_guru', '')}_{row.get('bulan_gaji', '')}.pdf",
                    mime="application/pdf",
                    key=f"download_gaji_{selected_index}"
                )

    elif selected == "Daftar Ulang":
        st.title("Daftar Ulang")
        with st.form("daftar_ulang_form"):
            nama_siswa = st.text_input("Nama Siswa", key="daftar_ulang_nama_siswa")
            kelas = st.text_input("Kelas", key="daftar_ulang_kelas")
            biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang", min_value=0, key="daftar_ulang_biaya_daftar_ulang")
            pembayaran = st.number_input("Pembayaran", min_value=0, key="daftar_ulang_pembayaran")
            tahun = st.text_input("Tahun", key="daftar_ulang_tahun")
            timestamp = get_current_timestamp()
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun, timestamp)
                df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG)
                st.success("Pembayaran Daftar Ulang berhasil disimpan!")

        st.write("**Data Daftar Ulang**")
        search_daftar_ulang = st.text_input("Cari Siswa", key="search_daftar_ulang")
        if os.path.exists(CSV_DAFTAR_ULANG):
            df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG)
            if search_daftar_ulang:
                df_daftar_ulang = df_daftar_ulang[df_daftar_ulang['nama_siswa'].str.contains(search_daftar_ulang, case=False, na=False)]
            st.dataframe(df_daftar_ulang)

        st.write("**Download Kwitansi Daftar Ulang**")
        if not df_daftar_ulang.empty:
            options = list(df_daftar_ulang.index)
            selected_index = st.selectbox("Pilih Nomor Urut Kwitansi", options)
            if st.button("Download Kwitansi"):
                row = df_daftar_ulang.loc[selected_index]
                receipt = generate_receipt(row.get('nama_siswa', ''), row.get('kelas', ''), '', row.get('pembayaran', 0), row.get('biaya_daftar_ulang', 0), 'daftar_ulang')
                st.download_button(
                    label=f"Download Kwitansi {row.get('nama_siswa', '')} ({row.get('tahun', '')})",
                    data=receipt,
                    file_name=f"kwitansi_daftar_ulang_{row.get('nama_siswa', '')}_{row.get('tahun', '')}.pdf",
                    mime="application/pdf",
                    key=f"download_daftar_ulang_{selected_index}"
                )

    elif selected == "Pengeluaran":
        st.title("Pengelolaan Pengeluaran")

        with st.form("pengeluaran_form"):
            nama_penerima = st.text_input("Nama Penerima", key="pengeluaran_nama_penerima")
            keterangan_biaya = st.text_input("Keterangan Biaya", key="pengeluaran_keterangan_biaya")
            total_biaya = st.number_input("Total Biaya", min_value=0, key="pengeluaran_total_biaya")
            timestamp = get_current_timestamp()
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya, timestamp)
                st.success("Pengeluaran berhasil disimpan!")

        st.write("**Data Pengeluaran**")
        if os.path.exists(CSV_PENGELUARAN):
            df_pengeluaran = pd.read_csv(CSV_PENGELUARAN)
            search_pengeluaran = st.text_input("Cari Penerima", key="search_pengeluaran")
            if search_pengeluaran:
                df_pengeluaran = df_pengeluaran[df_pengeluaran['nama_penerima'].str.contains(search_pengeluaran, case=False, na=False)]
            st.dataframe(df_pengeluaran)

            st.write("**Download Kwitansi Pengeluaran**")
            if not df_pengeluaran.empty:
                options = list(df_pengeluaran.index)
                selected_index = st.selectbox("Pilih Nomor Urut Kwitansi", options)
                if st.button("Download Kwitansi"):
                    row = df_pengeluaran.loc[selected_index]
                    receipt = generate_expense_receipt(
                        row.get('nama_penerima', ''),
                        row.get('keterangan_biaya', ''),
                        row.get('total_biaya', 0)
                    )
                    st.download_button(
                        label=f"Download Kwitansi {row.get('nama_penerima', '')}",
                        data=receipt,
                        file_name=f"kwitansi_pengeluaran_{row.get('nama_penerima', '')}.pdf",
                        mime="application/pdf",
                        key=f"download_pengeluaran_{selected_index}"
                    )
        else:
            st.write("Belum ada data pengeluaran.")

# Streamlit app logic
elif selected == "Laporan Keuangan":
    st.title("Laporan Keuangan")
    
    st.write("**Laporan Pembayaran SPP**")
    
    # SPP calculations
    df_spp['Total Tagihan SPP (1 Tahun)'] = df_spp['SPP Per Bulan'] * 12
    df_spp['Sisa Tagihan SPP'] = df_spp['Total Tagihan SPP (1 Tahun)'] - df_spp['Jumlah Bayar']
    st.dataframe(df_spp)

    st.write("**Laporan Gaji Guru**")
    st.dataframe(df_gaji)
    
    st.write("**Total Gaji Guru (1 Bulan)**")
    total_gaji = df_gaji['Total Gaji (1 Bulan)'].sum()
    st.write(f"Total Gaji Guru (1 Bulan): {total_gaji}")

    st.write("**Tabel Historis Gaji Guru**")
    st.dataframe(historical_salaries)

    st.write("**Laporan Pengeluaran**")
    st.dataframe(df_pengeluaran)
    
    st.write("**Total Pengeluaran (1 Bulan)**")
    total_pengeluaran = df_pengeluaran['Total Pengeluaran (1 Bulan)'].sum()
    st.write(f"Total Pengeluaran (1 Bulan): {total_pengeluaran}")

    st.write("**Tabel Historis Pengeluaran**")
    st.dataframe(historical_expenditures)


        # Export to Excel
        excel_data = export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran)
        st.download_button(
            label="Download Excel File",
            data=excel_data,
            file_name="laporan_keuangan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel"
        )

if __name__ == "__main__":
    main()
