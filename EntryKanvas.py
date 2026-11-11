import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from io import BytesIO
import pytz

# Zona Waktu WIB
TZ_WIB = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(TZ_WIB)
hari_ini = waktu_sekarang.strftime("%Y-%m-%d")

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Form Entry Laporan Kanvas",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Styling CSS agar tampilan lebih rapi
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    h1, h2, h3 {
        color: #0f172a;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================
# INISIALISASI & MIGRASI DATABASE SQLITE
# ====================================================
DB_NAME = "laporan_kanvas.db"

def inisialisasi_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kanvas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            nama_promotor TEXT,
            brand TEXT,
            canvas_plan TEXT,
            outlet_beli_ada INTEGER,
            outlet_ks_tb INTEGER,
            outlet_ks_b INTEGER,
            outlet_tb_ada_a INTEGER,
            outlet_tb_ada_p INTEGER,
            outlet_tb_ks INTEGER,
            omset_bungkus INTEGER,
            waktu_submit TEXT
        )
    """)
    conn.commit()

    # Cek & migrasi jika database masih memakai struktur/kolom lama (pic & cp)
    cursor.execute("PRAGMA table_info(kanvas)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'pic' in columns and 'nama_promotor' not in columns:
        cursor.execute("ALTER TABLE kanvas RENAME COLUMN pic TO nama_promotor")
    if 'cp' in columns and 'canvas_plan' not in columns:
        cursor.execute("ALTER TABLE kanvas RENAME COLUMN cp TO canvas_plan")
        
    conn.commit()
    conn.close()

inisialisasi_database()

def muat_data():
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("""
            SELECT id AS ID, tanggal AS Tanggal, nama_promotor AS [Nama Promotor], brand AS Brand, canvas_plan AS [Canvas Plan],
                   outlet_beli_ada AS [Outlet Beli Ada], outlet_ks_tb AS [Outlet Ks Tb], 
                   outlet_ks_b AS [Outlet Ks B], outlet_tb_ada_a AS [Outlet TB Ada A], 
                   outlet_tb_ada_p AS [Outlet TB Ada P], outlet_tb_ks AS [Outlet TB Ks], 
                   omset_bungkus AS [Omset (Bungkus)], waktu_submit AS [Waktu Submit]
            FROM kanvas
            ORDER BY waktu_submit DESC
        """, conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# Notifikasi sukses
if 'notifikasi_sukses' in st.session_state:
    st.balloons()
    st.success(st.session_state.pop('notifikasi_sukses'))

st.markdown("<h2 style='text-align: center;'>📋 Form Entry Laporan Kanvas</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Sistem Perekaman Data Kanvas Lapangan</p>", unsafe_allow_html=True)

# ====================================================
# FORM ENTRY DATA BARU
# ====================================================
with st.form("form_laporan_kanvas"):
    st.markdown("### 📝 Masukkan Data Laporan Baru")
    
    col1, col2 = st.columns(2)
    with col1:
        tanggal_entry = st.date_input("Date", value=datetime.now(TZ_WIB).date())
        promotor_entry = st.text_input("Nama Promotor")
        brand_entry = st.selectbox("Brand", ["Djarum Black Matcha Siro", "Djarum Black Matcha Kuro", "Djarum Black Matcha Kretek", "Lainnya"])
    with col2:
        canvas_plan_entry = st.text_input("Canvas Plan")
        omset_entry = st.number_input("Omset (bungkus)", min_value=0, step=1, value=0)

    st.markdown("---")
    st.markdown("#### 📊 Rincian Outlet")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        outlet_beli_ada = st.number_input("Jumlah Outlet Beli Ada", min_value=0, step=1, value=0)
        outlet_ks_tb = st.number_input("Jumlah Outlet Ks Tb", min_value=0, step=1, value=0)
    with col_b:
        outlet_ks_b = st.number_input("Jumlah Outlet Ks B", min_value=0, step=1, value=0)
        outlet_tb_ada_a = st.number_input("Jumlah Outlet Tidak Beli Ada A", min_value=0, step=1, value=0)
    with col_c:
        outlet_tb_ada_p = st.number_input("Jumlah Outlet Tidak Beli Ada P", min_value=0, step=1, value=0)
        outlet_tb_ks = st.number_input("Jumlah Outlet Tidak Beli Ks", min_value=0, step=1, value=0)

    submit_button = st.form_submit_button("🚀 Simpan Laporan", type="primary")

    if submit_button:
        if not promotor_entry or not canvas_plan_entry:
            st.error("❌ Kolom Nama Promotor dan Canvas Plan wajib diisi!")
        else:
            tgl_str = tanggal_entry.strftime("%Y-%m-%d")
            waktu_str = waktu_sekarang.strftime("%Y-%m-%d %H:%M:%S")
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO kanvas (
                    tanggal, nama_promotor, brand, canvas_plan, outlet_beli_ada, outlet_ks_tb, 
                    outlet_ks_b, outlet_tb_ada_a, outlet_tb_ada_p, outlet_tb_ks, 
                    omset_bungkus, waktu_submit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tgl_str, promotor_entry, brand_entry, canvas_plan_entry, outlet_beli_ada, 
                outlet_ks_tb, outlet_ks_b, outlet_tb_ada_a, outlet_tb_ada_p, 
                outlet_tb_ks, omset_entry, waktu_str
            ))
            conn.commit()
            conn.close()
            
            st.session_state['notifikasi_sukses'] = "🎉 Data laporan kanvas berhasil disimpan ke database!"
            st.rerun()

# ====================================================
# PANEL ADMIN & LOG LAPORAN
# ====================================================
st.markdown("---")
st.markdown("### 📊 Panel Admin & Log Laporan Kanvas")

df_data = muat_data()

if not df_data.empty:
    st.dataframe(df_data, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🛠️ Manajemen Data (Edit, Unduh, & Hapus)")
    
    # ====================================================
    # MENU EDIT ENTRY
    # ====================================================
    with st.expander("✏️ Edit Entry Data (Koreksi Kesalahan Input)"):
        list_id = df_data['ID'].tolist()
        id_dipilih = st.selectbox("Pilih ID Data yang Ingin Di-edit:", list_id)
        
        # Ambil data spesifik berdasarkan ID
        row_edit = df_data[df_data['ID'] == id_dipilih].iloc[0]
        
        with st.form("form_edit_kanvas"):
            st.markdown(f"#### Edit Data ID #{id_dipilih}")
            
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                e_tanggal = st.date_input("Tanggal", value=datetime.strptime(str(row_edit['Tanggal']), "%Y-%m-%d").date())
                e_promotor = st.text_input("Nama Promotor", value=str(row_edit['Nama Promotor']))
                
                # Menentukan index pilihan brand
                list_brand = ["Djarum Black Matcha Siro", "Djarum Black Matcha Kuro", "Djarum Black Matcha Kretek", "Lainnya"]
                idx_brand = list_brand.index(row_edit['Brand']) if row_edit['Brand'] in list_brand else 3
                e_brand = st.selectbox("Brand", list_brand, index=idx_brand)
                
            with e_col2:
                e_canvas_plan = st.text_input("Canvas Plan", value=str(row_edit['Canvas Plan']))
                e_omset = st.number_input("Omset (bungkus)", min_value=0, step=1, value=int(row_edit['Omset (Bungkus)']))

            st.markdown("##### Rincian Outlet")
            e_a, e_b, e_c = st.columns(3)
            with e_a:
                e_outlet_beli_ada = st.number_input("Outlet Beli Ada", min_value=0, step=1, value=int(row_edit['Outlet Beli Ada']))
                e_outlet_ks_tb = st.number_input("Outlet Ks Tb", min_value=0, step=1, value=int(row_edit['Outlet Ks Tb']))
            with e_b:
                e_outlet_ks_b = st.number_input("Outlet Ks B", min_value=0, step=1, value=int(row_edit['Outlet Ks B']))
                e_outlet_tb_ada_a = st.number_input("Outlet TB Ada A", min_value=0, step=1, value=int(row_edit['Outlet TB Ada A']))
            with e_c:
                e_outlet_tb_ada_p = st.number_input("Outlet TB Ada P", min_value=0, step=1, value=int(row_edit['Outlet TB Ada P']))
                e_outlet_tb_ks = st.number_input("Outlet TB Ks", min_value=0, step=1, value=int(row_edit['Outlet TB Ks']))

            btn_update = st.form_submit_button("💾 Perbarui Data", type="primary")

            if btn_update:
                if not e_promotor or not e_canvas_plan:
                    st.error("❌ Nama Promotor dan Canvas Plan tidak boleh kosong!")
                else:
                    tgl_edit_str = e_tanggal.strftime("%Y-%m-%d")
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE kanvas
                        SET tanggal = ?,
                            nama_promotor = ?,
                            brand = ?,
                            canvas_plan = ?,
                            outlet_beli_ada = ?,
                            outlet_ks_tb = ?,
                            outlet_ks_b = ?,
                            outlet_tb_ada_a = ?,
                            outlet_tb_ada_p = ?,
                            outlet_tb_ks = ?,
                            omset_bungkus = ?
                        WHERE id = ?
                    """, (
                        tgl_edit_str, e_promotor, e_brand, e_canvas_plan,
                        e_outlet_beli_ada, e_outlet_ks_tb, e_outlet_ks_b,
                        e_outlet_tb_ada_a, e_outlet_tb_ada_p, e_outlet_tb_ks,
                        e_omset, id_dipilih
                    ))
                    conn.commit()
                    conn.close()

                    st.session_state['notifikasi_sukses'] = f"✏️ Data ID #{id_dipilih} berhasil diperbarui!"
                    st.rerun()

    col_d, col_h = st.columns(2)
    
    # --- DOWNLOAD EXCEL ---
    with col_d:
        st.markdown("#### 📥 Unduh Laporan")
        opsi_unduh = st.selectbox("Pilih Rentang Data:", ["Semua Data", "Hari Ini"])
        
        if opsi_unduh == "Hari Ini":
            df_export = df_data[df_data['Tanggal'] == hari_ini]
        else:
            df_export = df_data.copy()
            
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Laporan Kanvas')
        
        st.download_button(
            label=f"💾 Download Excel ({opsi_unduh})",
            data=output.getvalue(),
            file_name=f"laporan_kanvas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # --- HAPUS DATA ---
    with col_h:
        st.markdown("#### 🗑️ Hapus Data")
        opsi_hapus = st.selectbox("Pilih Data yang Dihapus:", ["Hari Ini", "Semua Data"], key="opt_hapus")
        
        if st.button("🔥 Hapus Data", type="secondary", use_container_width=True):
            st.session_state['konfirmasi_hapus'] = True
            st.session_state['target_hapus'] = opsi_hapus

    if st.session_state.get('konfirmasi_hapus', False):
        st.warning(f"⚠️ Anda akan menghapus data untuk kategori: **{st.session_state['target_hapus']}** secara permanen.")
        password_admin = st.text_input("Masukkan Password Admin:", type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("❌ Batal"):
                st.session_state['konfirmasi_hapus'] = False
                st.rerun()
        with c2:
            if st.button("✅ Ya, Hapus Permanen", type="primary"):
                if password_admin == "admin123":
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    if st.session_state['target_hapus'] == "Hari Ini":
                        cursor.execute("DELETE FROM kanvas WHERE tanggal = ?", (hari_ini,))
                    else:
                        cursor.execute("DELETE FROM kanvas")
                    conn.commit()
                    conn.close()
                    
                    st.session_state.pop('konfirmasi_hapus', None)
                    st.session_state['notifikasi_sukses'] = "🗑️ Data berhasil dihapus."
                    st.rerun()
                else:
                    st.error("❌ Password salah!")
else:
    st.info("📭 Belum ada data laporan kanvas yang tercatat.")
