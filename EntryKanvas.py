from datetime import datetime
from io import BytesIO
import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import pytz
import requests
import streamlit as st

# URL Web App dari Google Apps Script Anda
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby_YGCckSCAKhEOxlOMvhD0_dNUn4OM-lOyYLRzbE7aUzhnK5v9BU6ywVf6n1v-U7Y/exec"


def backup_ke_gsh_otomatis(data_dict):
  try:
    requests.post(WEBHOOK_URL, json=data_dict)
  except Exception as e:
    print(f"Gagal backup: {e}")


# Zona Waktu WIB
TZ_WIB = pytz.timezone("Asia/Jakarta")
waktu_sekarang = datetime.now(TZ_WIB)
hari_ini = waktu_sekarang.strftime("%Y-%m-%d")

# Mapping Daftar Promotor dan Zona
PROMOTOR_ZONA = {
    "Achmad Danu Ardi": "Bubutan",
    "Arik Wibisono": "Bubutan",
    "Arum Ganda Fajar Ria": "Bubutan",
    "Candra Budi Eka": "Bubutan",
    "Rofi Wijayanto": "Bubutan",
    "Angga Budi Setiawan": "Gresik Selatan",
    "Dhimas Prayoga": "Gresik Selatan",
    "Hendra": "Gresik Selatan",
    "Rusdianto": "Gresik Selatan",
    "Septian Chandra": "Gresik Selatan",
    "Surya Hadi Pratama": "Gresik Selatan",
    "Alfianto Nur Huda": "Gresik Selatan",
    "Heru Setiawan": "Gresik Selatan",
    "Pisga Andriyanto": "Gresik Selatan",
    "Muhammad Rizky Pratama Putra": "Gresik Selatan",
    "Aldi Dwi Prasetyo": "Gresik Utara",
    "Budi Setyawan": "Gresik Utara",
    "Dwi Nor Fais": "Gresik Utara",
    "Khoirur Rijal": "Gresik Utara",
    "Lurico Umar Raffsanjani": "Gresik Utara",
    "Rahmad Dani": "Gresik Utara",
    "M Holidi": "Gresik Utara",
    "Daniel Arief Kurniawan": "Karangpilang",
    "Dimas Rizky Dermawan": "Karangpilang",
    "Guntur Vicki Prasetyo": "Karangpilang",
    "Zayd Abigail Johansyah": "Karangpilang",
    "Axel Setiawan": "Sawahan",
    "Delpiero Kevin Santoso": "Sawahan",
    "Muhamad Baharudin Yusuf": "Sawahan",
    "Muhammad Luthfi Anshori": "Sawahan",
    "Rendi Wahyudi": "Sawahan",
    "Arik Setiawan": "Tandes",
    "Syarif Usman Fadholi": "Tandes",
    "Surya Wisnu Wibisono": "Tandes",
    "Eko Sucipto": "Tandes",
}

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Form Entry Laporan Kanvas",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Styling CSS agar tampilan lebih rapi
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

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
            zona TEXT,
            brand TEXT,
            canvas_plan INTEGER,
            outlet_beli_ada INTEGER,
            outlet_ks_tb INTEGER,
            outlet_ks_b INTEGER,
            outlet_tb_ada_a INTEGER,
            outlet_tb_ada_p INTEGER,
            outlet_tb_ks INTEGER,
            omset_bungkus INTEGER,
            promsus_10_1 INTEGER,
            promsus_3_1 INTEGER,
            promsus_2_1 INTEGER,
            promsus_1_1 INTEGER,
            promsus_n_mie_instan INTEGER,
            outlet_buka_ecer INTEGER,
            jumlah_rokok_sampling INTEGER,
            jumlah_konsumen_trial INTEGER,
            direct_selling INTEGER,
            waktu_submit TEXT
        )
    """)
  conn.commit()
  conn.close()


inisialisasi_database()


def muat_data():
  conn = sqlite3.connect(DB_NAME)
  try:
    df = pd.read_sql_query(
        """
            SELECT id AS ID, tanggal AS Tanggal, nama_promotor AS [Nama Promotor], zona AS Zona, brand AS Brand, canvas_plan AS [Canvas Plan],
                   outlet_beli_ada AS [Outlet Beli Ada], outlet_ks_tb AS [Outlet Ks Tb], 
                   outlet_ks_b AS [Outlet Ks B], outlet_tb_ada_a AS [Outlet TB Ada A], 
                   outlet_tb_ada_p AS [Outlet TB Ada P], outlet_tb_ks AS [Outlet TB Ks], 
                   omset_bungkus AS [Omset (Bungkus)], 
                   promsus_10_1 AS [Promsus 10+1],
                   promsus_3_1 AS [Promsus 3+1],
                   promsus_2_1 AS [Promsus 2+1],
                   promsus_1_1 AS [Promsus 1+1],
                   promsus_n_mie_instan AS [N+ Mie Instan],
                   outlet_buka_ecer AS [Outlet Buka Ecer],
                   jumlah_rokok_sampling AS [Jumlah Rokok Sampling],
                   jumlah_konsumen_trial AS [Jumlah Konsumen Trial],
                   direct_selling AS [Direct Selling],
                   waktu_submit AS [Waktu Submit]
            FROM kanvas
            ORDER BY waktu_submit DESC
        """,
        conn,
    )
  except Exception:
    df = pd.DataFrame()
  conn.close()
  return df


# Notifikasi sukses
if "notifikasi_sukses" in st.session_state:
  st.balloons()
  st.success(st.session_state.pop("notifikasi_sukses"))

st.markdown(
    "<h2 style='text-align: center;'>📋 Form Entry Laporan Kanvas</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #64748b;'>Sistem Perekaman Data"
    " Kanvas Lapangan</p>",
    unsafe_allow_html=True,
)


def simpan_ke_database(data_preview):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO kanvas (
            tanggal, nama_promotor, zona, brand, canvas_plan, outlet_beli_ada, outlet_ks_tb, 
            outlet_ks_b, outlet_tb_ada_a, outlet_tb_ada_p, outlet_tb_ks, 
            omset_bungkus, promsus_10_1, promsus_3_1, promsus_2_1, promsus_1_1, 
            promsus_n_mie_instan, outlet_buka_ecer, jumlah_rokok_sampling, jumlah_konsumen_trial, 
            direct_selling, waktu_submit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          data_preview["tanggal"],
          data_preview["nama_promotor"],
          data_preview["zona"],
          data_preview["brand"],
          data_preview["canvas_plan"],
          data_preview["outlet_beli_ada"],
          data_preview["outlet_ks_tb"],
          data_preview["outlet_ks_b"],
          data_preview["outlet_tb_ada_a"],
          data_preview["outlet_tb_ada_p"],
          data_preview["outlet_tb_ks"],
          data_preview["omset_bungkus"],
          data_preview["promsus_10_1"],
          data_preview["promsus_3_1"],
          data_preview["promsus_2_1"],
          data_preview["promsus_1_1"],
          data_preview["promsus_n_mie_instan"],
          data_preview["outlet_buka_ecer"],
          data_preview["jumlah_rokok_sampling"],
          data_preview["jumlah_konsumen_trial"],
          data_preview["direct_selling"],
          data_preview["waktu_submit"],
      ),
  )
  conn.commit()
  conn.close()
  backup_ke_gsh_otomatis(data_preview)


# ====================================================
# FORM ENTRY DATA BARU
# ====================================================
if "form_preview_data" not in st.session_state:
  st.session_state["form_preview_data"] = None

if st.session_state["form_preview_data"] is None:
  with st.form("form_laporan_kanvas"):
    st.markdown("### 📝 Masukkan Data Laporan Baru")
    col1, col2 = st.columns(2)
    with col1:
      tanggal_entry = st.date_input("Date", value=datetime.now(TZ_WIB).date())
      promotor_entry = st.selectbox("Nama Promotor", list(PROMOTOR_ZONA.keys()))
      brand_entry = st.selectbox("Brand", ["Djarum 76 Aksara"])
    with col2:
      zona_otomatis = PROMOTOR_ZONA.get(promotor_entry, "-")
      st.text_input("Zona (Otomatis)", value=zona_otomatis, disabled=True)
      canvas_plan_entry = st.number_input(
          "Canvas Plan", min_value=0, step=1, value=0
      )
      omset_entry = st.number_input(
          "Omset (bungkus)", min_value=0, step=1, value=0
      )

    st.markdown("---")
    st.markdown("#### 📊 Rincian Outlet")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
      outlet_beli_ada = st.number_input(
          "Jumlah Outlet Beli Ada", min_value=0, step=1, value=0
      )
      outlet_ks_tb = st.number_input(
          "Jumlah Outlet Ks Tb", min_value=0, step=1, value=0
      )
    with col_b:
      outlet_ks_b = st.number_input(
          "Jumlah Outlet Ks B", min_value=0, step=1, value=0
      )
      outlet_tb_ada_a = st.number_input(
          "Jumlah Outlet Tidak Beli Ada A", min_value=0, step=1, value=0
      )
    with col_c:
      outlet_tb_ada_p = st.number_input(
          "Jumlah Outlet Tidak Beli Ada P", min_value=0, step=1, value=0
      )
      outlet_tb_ks = st.number_input(
          "Jumlah Outlet Tidak Beli Ks", min_value=0, step=1, value=0
      )

    st.markdown("---")
    st.markdown("#### 🎁 Promosi Khusus (Promsus)")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
      promsus_10_1 = st.number_input("10+1", min_value=0, step=1, value=0)
      promsus_1_1 = st.number_input("1+1", min_value=0, step=1, value=0)
    with p2:
      promsus_3_1 = st.number_input("3+1", min_value=0, step=1, value=0)
      promsus_n_mie = st.number_input(
          "N+ Mie Instan", min_value=0, step=1, value=0
      )
    with p3:
      promsus_2_1 = st.number_input("2+1", min_value=0, step=1, value=0)
      outlet_buka_ecer = st.number_input(
          "Outlet Buka Ecer", min_value=0, step=1, value=0
      )
    with p4:
      jml_sampling = st.number_input(
          "Jumlah Rokok Sampling", min_value=0, step=1, value=0
      )
      jml_trial = st.number_input(
          "Jumlah Konsumen Trial", min_value=0, step=1, value=0
      )

    direct_selling = st.number_input("Direct Selling", min_value=0, step=1, value=0)

    st.markdown("---")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
      btn_preview = st.form_submit_button("👁️ Lihat Preview", type="secondary")
    with btn_col2:
      btn_langsung_kirim = st.form_submit_button("🚀 Langsung Kirim", type="primary")

    if btn_preview or btn_langsung_kirim:
      if not promotor_entry:
        st.error("❌ Kolom Nama Promotor wajib diisi!")
      else:
        data_sementara = {
            "tanggal": tanggal_entry.strftime("%Y-%m-%d"),
            "nama_promotor": promotor_entry,
            "zona": PROMOTOR_ZONA.get(promotor_entry, ""),
            "brand": brand_entry,
            "canvas_plan": canvas_plan_entry,
            "outlet_beli_ada": outlet_beli_ada,
            "outlet_ks_tb": outlet_ks_tb,
            "outlet_ks_b": outlet_ks_b,
            "outlet_tb_ada_a": outlet_tb_ada_a,
            "outlet_tb_ada_p": outlet_tb_ada_p,
            "outlet_tb_ks": outlet_tb_ks,
            "omset_bungkus": omset_entry,
            "promsus_10_1": promsus_10_1,
            "promsus_3_1": promsus_3_1,
            "promsus_2_1": promsus_2_1,
            "promsus_1_1": promsus_1_1,
            "promsus_n_mie_instan": promsus_n_mie,
            "outlet_buka_ecer": outlet_buka_ecer,
            "jumlah_rokok_sampling": jml_sampling,
            "jumlah_konsumen_trial": jml_trial,
            "direct_selling": direct_selling,
            "waktu_submit": waktu_sekarang.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if btn_preview:
          st.session_state["form_preview_data"] = data_sementara
          st.rerun()
        elif btn_langsung_kirim:
          simpan_ke_database(data_sementara)
          st.session_state["notifikasi_sukses"] = (
              "🎉 Data laporan kanvas berhasil dikirim langsung ke database!"
          )
          st.rerun()

else:
  st.markdown("### 📋 Preview Data Laporan Baru")
  data_preview = st.session_state["form_preview_data"]
  df_preview_view = pd.DataFrame(
      list(data_preview.items()), columns=["Keterangan", "Nilai"]
  )
  st.dataframe(df_preview_view, use_container_width=True, hide_index=True)

  st.markdown("---")
  col_btn1, col_btn2 = st.columns(2)
  with col_btn1:
    if st.button("❌ Batal / Edit Kembali", use_container_width=True):
      st.session_state["form_preview_data"] = None
      st.rerun()
  with col_btn2:
    if st.button(
        "🚀 Konfirmasi & Simpan Laporan", type="primary", use_container_width=True
    ):
      simpan_ke_database(data_preview)
      st.session_state["form_preview_data"] = None
      st.session_state["notifikasi_sukses"] = (
          "🎉 Data laporan kanvas berhasil disimpan ke database!"
      )
      st.rerun()

# ====================================================
# MONITORING STATUS ENTRY HARI INI
# ====================================================
st.markdown("---")
st.markdown("### 🔍 Monitoring Status Entry Promotor Hari Ini")
st.markdown(
    f"<p style='color: #64748b;'>Tanggal Monitoring: <b>{hari_ini}</b></p>",
    unsafe_allow_html=True,
)

df_data_global = muat_data()
df_hari_ini = (
    df_data_global[df_data_global["Tanggal"] == hari_ini]
    if not df_data_global.empty
    else pd.DataFrame()
)
promotor_sudah_entry = (
    df_hari_ini["Nama Promotor"].dropna().unique().tolist()
    if not df_hari_ini.empty
    else []
)

tab_sudah, tab_belum = st.tabs([
    f"✅ Sudah Entry ({len(promotor_sudah_entry)})",
    f"⚠️ Belum Entry ({len(PROMOTOR_ZONA) - len(promotor_sudah_entry)})",
])

with tab_sudah:
  if not df_hari_ini.empty:
    data_sudah_list = [
        {"Nama Promotor": p, "Zona": PROMOTOR_ZONA.get(p, "-")}
        for p in promotor_sudah_entry
    ]
    st.dataframe(pd.DataFrame(data_sudah_list), use_container_width=True)
  else:
    st.info("📭 Belum ada promotor yang melakukan entry laporan pada hari ini.")

with tab_belum:
  daftar_belum_entry = [
      {"Nama Promotor": promotor, "Zona": zona}
      for promotor, zona in PROMOTOR_ZONA.items()
      if promotor not in promotor_sudah_entry
  ]
  if daftar_belum_entry:
    st.dataframe(pd.DataFrame(daftar_belum_entry), use_container_width=True)
  else:
    st.success("🎉 Seluruh promotor telah melakukan entry laporan hari ini.")

# ====================================================
# AREA ADMIN & REKAPITULASI DENGAN DOWNLOAD GAMBAR PYTHON
# ====================================================
st.markdown("---")
st.markdown("### 🔐 Area Khusus Admin (Log & Rekapitulasi)")

if "admin_authenticated" not in st.session_state:
  st.session_state["admin_authenticated"] = False

if not st.session_state["admin_authenticated"]:
  with st.form("form_password_admin"):
    st.info(
        "⚠️ Panel Admin & Rekapitulasi dilindungi password. Silakan masukkan"
        " password."
    )
    password_input = st.text_input("Password Admin:", type="password")
    if st.form_submit_button("🔓 Buka Area Admin", type="primary"):
      if password_input == "admin123":
        st.session_state["admin_authenticated"] = True
        st.rerun()
      else:
        st.error("❌ Password salah!")
else:
  if st.button("🔒 Kunci Kembali Area Admin"):
    st.session_state["admin_authenticated"] = False
    st.rerun()

  st.markdown("### 📊 Panel Admin & Log Laporan Kanvas")
  df_data = muat_data()

  if not df_data.empty:
    st.dataframe(df_data, use_container_width=True)

  st.markdown("---")
  st.markdown("### 📈 Rekapitulasi Harian & Mingguan")

  df_rekap_data = muat_data()
  if not df_rekap_data.empty:
    df_rekap_data["Tanggal_DT"] = pd.to_datetime(df_rekap_data["Tanggal"])

    col_rk1, col_rk2, col_rk3 = st.columns(3)
    with col_rk1:
      daftar_zona_pilihan = ["Semua Zona"] + sorted(
          list(set(PROMOTOR_ZONA.values()))
      )
      pilih_zona = st.selectbox(
          "Pilih Zona", daftar_zona_pilihan, key="rekap_zona"
      )

    if pilih_zona != "Semua Zona":
      df_filtered_zona = df_rekap_data[df_rekap_data["Zona"] == pilih_zona]
    else:
      df_filtered_zona = df_rekap_data.copy()

    with col_rk2:
      pilih_tahun = st.selectbox(
          "Pilih Tahun",
          sorted(df_filtered_zona["Tanggal_DT"].dt.year.unique(), reverse=True),
          key="rekap_thn",
      )

    with col_rk3:
      df_filtered_tahun = df_filtered_zona[
          df_filtered_zona["Tanggal_DT"].dt.year == pilih_tahun
      ]
      list_minggu = sorted(
          df_filtered_tahun["Tanggal_DT"].dt.isocalendar().week.unique(),
          reverse=True,
      )
      pilih_minggu = st.selectbox(
          "Pilih Minggu ke- (Week)", list_minggu, key="rekap_mg"
      )

    df_mingguan = df_filtered_tahun[
        df_filtered_tahun["Tanggal_DT"].dt.isocalendar().week == pilih_minggu
    ]

    if not df_mingguan.empty:
      mapping_hari = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat"}
      df_mingguan["Nama Hari"] = df_mingguan["Tanggal_DT"].dt.weekday.map(
          mapping_hari
      )
      daftar_hari_kolom = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
      rekap_harian_dict = {}

      for hari in daftar_hari_kolom:
        df_hari = df_mingguan[df_mingguan["Nama Hari"] == hari]
        if not df_hari.empty:
          tgl_str = df_hari["Tanggal"].iloc[0]
          tgl_formatted = datetime.strptime(tgl_str, "%Y-%m-%d").strftime(
              "%d/%m/%Y"
          )
          total_armada = df_hari["Nama Promotor"].nunique()
          beli_ada = df_hari["Outlet Beli Ada"].sum()
          beli_ks_tb = df_hari["Outlet Ks Tb"].sum()
          beli_ks_b = df_hari["Outlet Ks B"].sum()
          tba_aktif = df_hari["Outlet TB Ada A"].sum()
          tba_pasif = df_hari["Outlet TB Ada P"].sum()
          kosong = df_hari["Outlet TB Ks"].sum()
          outlet_buka_ecer = df_hari["Outlet Buka Ecer"].sum()
          call = (
              beli_ada + beli_ks_tb + beli_ks_b + tba_aktif + tba_pasif + kosong
          )
          total_omset = df_hari["Omset (Bungkus)"].sum()
          total_outlet_beli = beli_ada + beli_ks_tb + beli_ks_b
          avg_dropsize = (
              round(total_omset / total_outlet_beli, 1)
              if total_outlet_beli > 0
              else 0.0
          )
          ec = beli_ada + beli_ks_tb + beli_ks_b
          persen_ec = round((ec / call) * 100, 1) if call > 0 else 0.0
          avail_sesudah = (
              round(
                  (
                      (
                          beli_ada
                          + beli_ks_tb
                          + beli_ks_b
                          + tba_aktif
                          + tba_pasif
                      )
                      / call
                  )
                  * 100,
                  1,
              )
              if call > 0
              else 0.0
          )
          persen_repeat = (
              round(
                  (
                      (beli_ada + beli_ks_tb)
                      / (beli_ada + beli_ks_tb + tba_aktif + tba_pasif)
                  )
                  * 100,
                  1,
              )
              if (beli_ada + beli_ks_tb + tba_aktif + tba_pasif) > 0
              else 0.0
          )
          persen_oos = (
              round((beli_ks_tb / call) * 100, 1) if call > 0 else 0.0
          )
          persen_ecer = (
              round((outlet_buka_ecer / call) * 100, 1) if call > 0 else 0.0
          )

          rekap_harian_dict[hari] = {
              "Tanggal": tgl_formatted,
              "Total Armada": total_armada,
              "Call": call,
              "Beli Ada": beli_ada,
              "Beli Ks Tambah": beli_ks_tb,
              "Beli Ks Baru": beli_ks_b,
              "TBA Aktif": tba_aktif,
              "TBA Pasif": tba_pasif,
              "Kosong": kosong,
              "Total Omset": total_omset,
              "Average Dropsize": avg_dropsize,
              "% Availability Sesudah": f"{avail_sesudah}%",
              "EC": ec,
              "% EC": f"{persen_ec}%",
              "% Repeat": f"{persen_repeat}%",
              "% OOS": f"{persen_oos}%",
              "% Outlet Ecer": f"{persen_ecer}%",
              "Total Sampling": df_hari["Jumlah Rokok Sampling"].sum(),
              "Kontak Konsumen": df_hari["Jumlah Konsumen Trial"].sum(),
              "Laku Direct Selling": df_hari["Direct Selling"].sum(),
          }
        else:
          rekap_harian_dict[hari] = {
              "Tanggal": "-",
              "Total Armada": 0,
              "Call": 0,
              "Beli Ada": 0,
              "Beli Ks Tambah": 0,
              "Beli Ks Baru": 0,
              "TBA Aktif": 0,
              "TBA Pasif": 0,
              "Kosong": 0,
              "Total Omset": 0,
              "Average Dropsize": 0.0,
              "% Availability Sesudah": "0.0%",
              "EC": 0,
              "% EC": "0.0%",
              "% Repeat": "0.0%",
              "% OOS": "0.0%",
              "% Outlet Ecer": "0.0%",
              "Total Sampling": 0,
              "Kontak Konsumen": 0,
              "Laku Direct Selling": 0,
          }

      df_final_rekap = pd.DataFrame(rekap_harian_dict)
      label_zona_judul = (
          f"Zona {pilih_zona}" if pilih_zona != "Semua Zona" else "Semua Zona"
      )

      # Tampilkan Tampilan di Streamlit
      if os.path.exists("76aksara.png"):
        st.image("76aksara.png", use_container_width=True)

      st.markdown(
          f"<h4 style='text-align: center; color: #0f172a;'>Laporan"
          f" Rekapitulasi {label_zona_judul} - Minggu ke {pilih_minggu} -"
          f" {pilih_tahun}</h4>",
          unsafe_allow_html=True,
      )

      st.table(df_final_rekap)

      # ====================================================
      # TOMBOL DOWNLOAD GAMBAR MENGGUNAKAN MATPLOTLIB (DIJAMIN BERHASIL)
      # ====================================================
      st.markdown("---")

      if st.button(
          "📷 Download Gambar Laporan Rekap (PNG)",
          type="primary",
          use_container_width=True,
      ):
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis("off")

        # Masukkan Judul ke dalam Plot Gambar
        ax.text(
            0.5,
            0.95,
            f"Laporan Rekapitulasi {label_zona_judul} - Minggu ke {pilih_minggu} - {pilih_tahun}",
            horizontalalignment="center",
            fontsize=14,
            fontweight="bold",
            transform=ax.transAxes,
        )

        # Render Tabel menjadi Tabel Matplotlib
        table_data = [df_final_rekap.columns.tolist()] + df_final_rekap.values.tolist()
        table = ax.table(
            cellText=table_data,
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)

        buffer_img = BytesIO()
        plt.savefig(
            buffer_img, format="png", bbox_inches="tight", dpi=300
        )
        plt.close(fig)

        st.download_button(
            label="💾 Klik di Sini untuk Unduh File PNG",
            data=buffer_img.getvalue(),
            file_name=f"Rekap_{label_zona_judul}_W{pilih_minggu}_{pilih_tahun}.png".replace(
                " ", "_"
            ),
            mime="image/png",
            use_container_width=True,
        )

    else:
      st.info(
          f"📭 Tidak ada data laporan untuk {pilih_zona} pada Minggu"
          f" ke-{pilih_minggu}."
      )
  else:
    st.info("📭 Belum ada data untuk direkap.")
