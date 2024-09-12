import pandas as pd
import streamlit as st
from io import BytesIO
from fpdf import FPDF

# Define file paths for CSVs
CSV_PEMBAYARAN_SPP = 'pembayaran_spp.csv'
CSV_GAJI_GURU = 'gaji_guru.csv'
CSV_DAFTAR_ULANG = 'daftar_ulang.csv'
CSV_PENGELUARAN = 'pengeluaran.csv'

# Define functions
def save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp):
    data = {'nama_siswa': [nama_siswa], 'kelas': [kelas], 'bulan': [bulan], 'jumlah': [jumlah], 'biaya_spp': [biaya_spp]}
    df = pd.DataFrame(data)
    df.to_csv(CSV_PEMBAYARAN_SPP, mode='a', header=False, index=False)

def save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan):
    data = {'nama_guru': [nama_guru], 'bulan_gaji': [bulan_gaji], 'gaji': [gaji], 'tunjangan': [tunjangan]}
    df = pd.DataFrame(data)
    df.to_csv(CSV_GAJI_GURU, mode='a', header=False, index=False)

def save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun):
    data = {'nama_siswa': [nama_siswa], 'kelas': [kelas], 'biaya_daftar_ulang': [biaya_daftar_ulang], 'pembayaran': [pembayaran], 'tahun': [tahun]}
    df = pd.DataFrame(data)
    df.to_csv(CSV_DAFTAR_ULANG, mode='a', header=False, index=False)

def save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya):
    data = {'nama_penerima': [nama_penerima], 'keterangan_biaya': [keterangan_biaya], 'total_biaya': [total_biaya]}
    df = pd.DataFrame(data)
    df.to_csv(CSV_PENGELUARAN, mode='a', header=False, index=False)

def generate_receipt(nama, kelas, bulan, jumlah, biaya, receipt_type):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Kwitansi {receipt_type.upper()}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Nama: {nama}", ln=True)
    pdf.cell(200, 10, txt=f"Kelas: {kelas}", ln=True)
    pdf.cell(200, 10, txt=f"Bulan: {bulan}", ln=True)
    pdf.cell(200, 10, txt=f"Jumlah: {jumlah}", ln=True)
    pdf.cell(200, 10, txt=f"Biaya: {biaya}", ln=True)
    return BytesIO(pdf.output(dest='S').encode('latin1'))

def export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran):
    with BytesIO() as output:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_spp.to_excel(writer, sheet_name='Pembayaran SPP', index=False)
            df_gaji.to_excel(writer, sheet_name='Gaji Guru', index=False)
            df_daftar_ulang.to_excel(writer, sheet_name='Daftar Ulang', index=False)
            df_pengeluaran.to_excel(writer, sheet_name='Pengeluaran', index=False)
        return output.getvalue()

def main():
    st.title("Sistem Administrasi Sekolah")

    # Load data
    df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP) if pd.io.common.file_exists(CSV_PEMBAYARAN_SPP) else pd.DataFrame()
    df_gaji = pd.read_csv(CSV_GAJI_GURU) if pd.io.common.file_exists(CSV_GAJI_GURU) else pd.DataFrame()
    df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG) if pd.io.common.file_exists(CSV_DAFTAR_ULANG) else pd.DataFrame()
    df_pengeluaran = pd.read_csv(CSV_PENGELUARAN) if pd.io.common.file_exists(CSV_PENGELUARAN) else pd.DataFrame()

    # Sidebar for navigation
    try:
        selected = st.sidebar.radio(
            label="Pilih Halaman",
            options=["Pembayaran SPP", "Pengelolaan Gaji Guru", "Daftar Ulang", "Pengeluaran", "Laporan Keuangan"]
        )
    except TypeError as e:
        st.error(f"An error occurred: {e}")
        return

    if selected == "Pembayaran SPP":
        st.title("Pembayaran SPP")
        with st.form("spp_form"):
            nama_siswa = st.text_input("Nama Siswa", key="spp_nama_siswa")
            kelas = st.text_input("Kelas", key="spp_kelas")
            bulan = st.text_input("Bulan", key="spp_bulan")
            jumlah = st.number_input("Jumlah Pembayaran", min_value=0, key="spp_jumlah")
            biaya_spp = st.number_input("Biaya SPP per Bulan", min_value=0, key="spp_biaya_spp")
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_pembayaran_spp(nama_siswa, kelas, bulan, jumlah, biaya_spp)
                df_spp = pd.read_csv(CSV_PEMBAYARAN_SPP)
                st.success("Pembayaran SPP berhasil disimpan!")

        st.write("**Data Pembayaran SPP**")
        st.dataframe(df_spp)

        st.write("**Pilih Kwitansi untuk Diunduh**")
        if not df_spp.empty:
            selected_rows = st.multiselect(
                "Pilih data untuk diunduh",
                options=[f"{row['nama_siswa']} ({row['bulan']})" for index, row in df_spp.iterrows()],
                format_func=lambda x: x
            )
            for index, row in df_spp.iterrows():
                if f"{row['nama_siswa']} ({row['bulan']})" in selected_rows:
                    receipt = generate_receipt(row.get('nama_siswa', ''), row.get('kelas', ''), row.get('bulan', ''), row.get('jumlah', 0), row.get('biaya_spp', 0), 'spp')
                    st.download_button(
                        label=f"Download Kwitansi {row.get('nama_siswa', '')} ({row.get('bulan', '')})",
                        data=receipt,
                        file_name=f"kwitansi_spp_{row.get('nama_siswa', '')}_{row.get('bulan', '')}.pdf",
                        mime="application/pdf",
                        key=f"download_spp_{index}"
                    )

    elif selected == "Pengelolaan Gaji Guru":
        st.title("Pengelolaan Gaji Guru")
        with st.form("gaji_form"):
            nama_guru = st.text_input("Nama Guru", key="gaji_nama_guru")
            bulan_gaji = st.text_input("Bulan Gaji", key="gaji_bulan_gaji")
            gaji = st.number_input("Gaji", min_value=0, key="gaji_gaji")
            tunjangan = st.number_input("Tunjangan", min_value=0, key="gaji_tunjangan")
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_gaji_guru(nama_guru, bulan_gaji, gaji, tunjangan)
                df_gaji = pd.read_csv(CSV_GAJI_GURU)
                st.success("Gaji Guru berhasil disimpan!")

        st.write("**Data Gaji Guru**")
        st.dataframe(df_gaji)

        st.write("**Pilih Kwitansi untuk Diunduh**")
        if not df_gaji.empty:
            selected_rows = st.multiselect(
                "Pilih data untuk diunduh",
                options=[f"{row['nama_guru']} ({row['bulan_gaji']})" for index, row in df_gaji.iterrows()],
                format_func=lambda x: x
            )
            for index, row in df_gaji.iterrows():
                if f"{row['nama_guru']} ({row['bulan_gaji']})" in selected_rows:
                    receipt = generate_receipt(row.get('nama_guru', ''), '', row.get('bulan_gaji', ''), '', row.get('gaji', 0), 'gaji')
                    st.download_button(
                        label=f"Download Kwitansi {row.get('nama_guru', '')} ({row.get('bulan_gaji', '')})",
                        data=receipt,
                        file_name=f"kwitansi_gaji_{row.get('nama_guru', '')}_{row.get('bulan_gaji', '')}.pdf",
                        mime="application/pdf",
                        key=f"download_gaji_{index}"
                    )

    elif selected == "Daftar Ulang":
        st.title("Daftar Ulang")
        with st.form("daftar_ulang_form"):
            nama_siswa = st.text_input("Nama Siswa", key="daftar_ulang_nama_siswa")
            kelas = st.text_input("Kelas", key="daftar_ulang_kelas")
            biaya_daftar_ulang = st.number_input("Biaya Daftar Ulang", min_value=0, key="daftar_ulang_biaya_daftar_ulang")
            pembayaran = st.number_input("Jumlah Pembayaran", min_value=0, key="daftar_ulang_pembayaran")
            tahun = st.text_input("Tahun", key="daftar_ulang_tahun")
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_daftar_ulang(nama_siswa, kelas, biaya_daftar_ulang, pembayaran, tahun)
                df_daftar_ulang = pd.read_csv(CSV_DAFTAR_ULANG)
                st.success("Data Daftar Ulang berhasil disimpan!")

        st.write("**Data Daftar Ulang**")
        st.dataframe(df_daftar_ulang)

        st.write("**Pilih Kwitansi untuk Diunduh**")
        if not df_daftar_ulang.empty:
            selected_rows = st.multiselect(
                "Pilih data untuk diunduh",
                options=[f"{row['nama_siswa']} ({row['tahun']})" for index, row in df_daftar_ulang.iterrows()],
                format_func=lambda x: x
            )
            for index, row in df_daftar_ulang.iterrows():
                if f"{row['nama_siswa']} ({row['tahun']})" in selected_rows:
                    receipt = generate_receipt(row.get('nama_siswa', ''), row.get('kelas', ''), '', '', row.get('biaya_daftar_ulang', 0), 'daftar_ulang')
                    st.download_button(
                        label=f"Download Kwitansi {row.get('nama_siswa', '')} ({row.get('tahun', '')})",
                        data=receipt,
                        file_name=f"kwitansi_daftar_ulang_{row.get('nama_siswa', '')}_{row.get('tahun', '')}.pdf",
                        mime="application/pdf",
                        key=f"download_daftar_ulang_{index}"
                    )

    elif selected == "Pengeluaran":
        st.title("Pengelolaan Pengeluaran")
        with st.form("pengeluaran_form"):
            nama_penerima = st.text_input("Nama Penerima", key="pengeluaran_nama_penerima")
            keterangan_biaya = st.text_input("Keterangan Biaya", key="pengeluaran_keterangan_biaya")
            total_biaya = st.number_input("Total Biaya", min_value=0, key="pengeluaran_total_biaya")
            submitted = st.form_submit_button("Simpan")

            if submitted:
                save_pengeluaran(nama_penerima, keterangan_biaya, total_biaya)
                df_pengeluaran = pd.read_csv(CSV_PENGELUARAN)
                st.success("Data Pengeluaran berhasil disimpan!")

        st.write("**Data Pengeluaran**")
        st.dataframe(df_pengeluaran)

        st.write("**Pilih Kwitansi untuk Diunduh**")
        if not df_pengeluaran.empty:
            selected_rows = st.multiselect(
                "Pilih data untuk diunduh",
                options=[f"{row['nama_penerima']} ({row['keterangan_biaya']})" for index, row in df_pengeluaran.iterrows()],
                format_func=lambda x: x
            )
            for index, row in df_pengeluaran.iterrows():
                if f"{row['nama_penerima']} ({row['keterangan_biaya']})" in selected_rows:
                    receipt = generate_receipt(row.get('nama_penerima', ''), '', '', '', row.get('total_biaya', 0), 'pengeluaran')
                    st.download_button(
                        label=f"Download Kwitansi {row.get('nama_penerima', '')} ({row.get('keterangan_biaya', '')})",
                        data=receipt,
                        file_name=f"kwitansi_pengeluaran_{row.get('nama_penerima', '')}_{row.get('keterangan_biaya', '')}.pdf",
                        mime="application/pdf",
                        key=f"download_pengeluaran_{index}"
                    )

    elif selected == "Laporan Keuangan":
        st.title("Laporan Keuangan")
        if not df_spp.empty or not df_gaji.empty or not df_daftar_ulang.empty or not df_pengeluaran.empty:
            excel_data = export_to_excel(df_spp, df_gaji, df_daftar_ulang, df_pengeluaran)
            st.download_button(
                label="Download Laporan Keuangan",
                data=excel_data,
                file_name="laporan_keuangan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.write("Tidak ada data untuk laporan.")

    elif selected == "Upload Foto":
        st.title("Upload Foto")
        uploaded_file = st.file_uploader("Upload Foto", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            st.success("Foto berhasil diunggah!")

if __name__ == "__main__":
    main()
