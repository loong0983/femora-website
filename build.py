#!/usr/bin/env python3
"""Bina laman FEMORA daripada config.json -> dist/

Guna:  python3 build.py            (bina; medan kosong ditanda kuning)
       python3 build.py --ketat    (gagal jika masih ada medan kosong — guna sebelum go-live)
"""
import datetime
import html
import json
import math
import pathlib
import shutil
import sys
from urllib.parse import quote

AKAR = pathlib.Path(__file__).resolve().parent
SRC = AKAR / "src"
DIST = AKAR / "dist"
cfg = json.loads((AKAR / "config.json").read_text(encoding="utf-8"))

DRAF = bool(cfg.get("draf", True))
JENAMA = cfg.get("jenama") or "FEMORA"
TAHUN = datetime.date.today().year
kosong = []  # medan yang belum diisi


def e(s):
    return html.escape(str(s), quote=True)


def isi(label):
    """Penanda untuk maklumat yang belum diberi."""
    if label not in kosong:
        kosong.append(label)
    return f'<mark class="isi">[isi: {e(label)}]</mark>'


def v(kunci, label, sumber=None):
    nilai = (sumber if sumber is not None else cfg).get(kunci)
    if nilai in (None, "", [], {}):
        return isi(label)
    return e(nilai)


def ada(kunci, sumber=None):
    nilai = (sumber if sumber is not None else cfg).get(kunci)
    return nilai not in (None, "", [], {}, "tiada", False)


def tiada(kunci):
    """Pengguna sengaja tetapkan 'tiada' -> sembunyikan terus."""
    return cfg.get(kunci) == "tiada"


def harga(h):
    if h in (None, ""):
        return isi("harga")
    if isinstance(h, (int, float)):
        return "RM" + (f"{h:.0f}" if float(h).is_integer() else f"{h:.2f}")
    return e(h)


def harga_teks(h):
    if h in (None, ""):
        return ""
    if isinstance(h, (int, float)):
        return "RM" + (f"{h:.0f}" if float(h).is_integer() else f"{h:.2f}")
    return str(h)


WA_NOMBOR = "".join(ch for ch in str(cfg.get("whatsapp") or "") if ch.isdigit())
if not WA_NOMBOR:
    kosong.append("nombor WhatsApp (format 60123456789)")


def wa(teks):
    return f"https://wa.me/{WA_NOMBOR}?text={quote(teks)}"


WA_TANYA = wa(f"Salam, saya nak tahu lebih lanjut tentang {JENAMA}.")

# ------------------------------------------------------------------ ikon
I_WA = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 1.8a8.2 8.2 0 1 1-4.2 15.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 0 1 12 3.8zM8.6 7.3c-.2 0-.5 0-.7.3-.3.3-1 .9-1 2.300s1 2.700 1.200 2.900c.1.2 2 3.200 5 4.400 2.500 1 3 .8 3.500.700.500 0 1.700-.700 2-1.400.200-.700.200-1.300.100-1.400l-.500-.300-1.700-.900c-.200 0-.400-.100-.600.200l-.800 1c-.100.200-.300.200-.500.100a6.700 6.700 0 0 1-2-1.200 7.400 7.400 0 0 1-1.400-1.700c-.100-.300 0-.400.100-.500l.400-.500.300-.400v-.500l-.800-1.900c-.200-.500-.400-.400-.600-.400z"/></svg>'
I_SEMAK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.500 4.500L19 7.500"/></svg>'
I_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
I_PERIUK = '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 15h22v6a8 8 0 0 1-8 8h-6a8 8 0 0 1-8-8z"/><path d="M3 15h28M13 9c0-2 2-2 2-4M20 9c0-2 2-2 2-4"/><path d="M5 5l24 24" stroke-width="2.2"/></svg>'
I_SUKAT = '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h24l-3 14a3 3 0 0 1-3 2H11a3 3 0 0 1-3-2z"/><path d="M12 17h4M12 21.500h6M17 12V6"/></svg>'
I_LABEL = '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="7" y="4" width="20" height="26" rx="3"/><path d="M12 11h10M12 16h10M12 21h6"/></svg>'
I_PERISAI = '<svg viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 4l11 4v8c0 7-4.500 11.500-11 14C10.500 27.500 6 23 6 16V8z"/><path d="M12 16.500l3.500 3.500 6.500-7"/></svg>'


# ------------------------------------------------------------------ komponen
def rajah(hidup=False, kapsyen=True):
    titik = []
    for k in range(8):
        sudut = math.radians(-90 + 22.5 + k * 45)
        x = 180 + 160 * math.cos(sudut)
        y = 180 + 160 * math.sin(sudut)
        titik.append(f'<circle class="r-titik" style="--i:{k}" cx="{x:.1f}" cy="{y:.1f}" r="9"/>')
    kelas = "rajah rajah--hidup" if hidup else "rajah"
    kap = '<figcaption>2 herba utama, dikelilingi 8 herba Ba Zhen</figcaption>' if kapsyen else ""
    return f'''<figure class="{kelas}">
  <svg viewBox="0 0 360 360" role="img" aria-label="Rajah formula: Kacip Fatimah dan Manjakani sebagai dua herba utama, dikelilingi lapan herba Ba Zhen">
    <circle class="r-orbit" cx="180" cy="180" r="160"/>
    {"".join(titik)}
    <circle class="r-bulat" cx="124" cy="180" r="82" fill="#3f7d5f" fill-opacity=".94"/>
    <circle class="r-bulat r-bulat--2" cx="236" cy="180" r="82" fill="#b02f66" fill-opacity=".9"/>
    <text class="r-nama" x="100" y="172" text-anchor="middle">Kacip</text>
    <text class="r-nama" x="100" y="196" text-anchor="middle">Fatimah</text>
    <text class="r-latin" x="100" y="214" text-anchor="middle">Labisia pumila</text>
    <text class="r-nama" x="262" y="184" text-anchor="middle">Manjakani</text>
    <text class="r-latin" x="262" y="202" text-anchor="middle">Quercus infectoria</text>
  </svg>
  {kap}
</figure>'''


def foto(fail, alt, bentuk=""):
    kelas = "foto" + (f" foto--{bentuk}" if bentuk else "")
    nota = f'<span class="foto__nota">{e(fail)}</span>' if DRAF else ""
    return (f'<div class="{kelas}">{nota}'
            f'<img src="img/{e(fail)}" alt="{e(alt)}" loading="lazy" onerror="this.remove()"></div>')


def butang_tempah(kelas="butang--utama", teks=None):
    return f'<a class="butang {kelas}" href="tempah.html">{e(teks or "Tempah " + JENAMA)}</a>'


def butang_tanya(kelas="butang--garis"):
    return f'<a class="butang {kelas}" href="{e(WA_TANYA)}" target="_blank" rel="noopener">{I_WA}Tanya di WhatsApp</a>'


LAPAN = [
    ("Dang Gui", "akar angelika", "Angelica sinensis", "Akar"),
    ("Chuan Xiong", "rizom lovage Sichuan", "Ligusticum chuanxiong", "Rizom"),
    ("Bai Shao", "akar peony putih", "Paeonia lactiflora", "Akar"),
    ("Shu Di Huang", "akar rehmannia", "Rehmannia glutinosa", "Akar yang dikukus"),
    ("Ren Shen", "ginseng", "Panax ginseng", "Akar"),
    ("Bai Zhu", "rizom atractylodes", "Atractylodes macrocephala", "Rizom"),
    ("Fu Ling", "kulat poria", "Poria cocos", "Kulat"),
    ("Gan Cao", "akar manis", "Glycyrrhiza uralensis", "Akar"),
]

AMARAN = '''<div class="amaran">
  <p><b>Sebelum mula:</b> jangan ambil jika anda hamil. Jika anda menyusu, merancang untuk hamil, ada penyakit kronik,
  atau sedang mengambil ubat (contohnya ubat cair darah atau ubat hormon), tanya doktor atau ahli farmasi dahulu.</p>
</div>'''


def cara_ambil_html():
    langkah = cfg.get("cara_ambil") or []
    if not langkah:
        langkah = [
            {"tajuk": "Ikut sukatan pada label",
             "isi_html": isi("sukatan dan waktu ambil, cth. 2 kapsul selepas sarapan")},
            {"tajuk": "Ambil pada waktu yang sama setiap hari",
             "isi": "Letak kotak di tempat yang anda nampak, contohnya sebelah cerek atau di meja solek, supaya tak terlupa."},
            {"tajuk": "Simpan dengan betul",
             "isi": "Tutup rapat dan simpan di tempat kering, jauh daripada cahaya matahari terus."},
        ]
    li = []
    for l in langkah:
        badan = l.get("isi_html") or e(l.get("isi", ""))
        li.append(f'<li><div><h3>{e(l["tajuk"])}</h3><p>{badan}</p></div></li>')
    return '<ol class="langkah">' + "".join(li) + "</ol>"


def pakej_html():
    kad = []
    for i, p in enumerate(cfg.get("pakej") or [], start=1):
        pilihan = bool(p.get("pilihan"))
        lencana = '<span class="pakej__lencana">Pilihan ramai</span>' if pilihan else ""
        asal = f'<p class="pakej__asal">{harga(p["harga_asal"])}</p>' if p.get("harga_asal") else '<p class="pakej__asal"></p>'
        nota = e(p.get("nota") or "")
        kad.append(f'''<div class="pakej__kad{" pakej__kad--pilihan" if pilihan else ""}">
  {lencana}
  <h3 class="pakej__nama">{e(p["nama"])}</h3>
  <p class="pakej__label">{e(p.get("label") or "")}</p>
  <p class="pakej__harga">{harga(p.get("harga"))}</p>
  {asal}
  <p class="pakej__nota">{nota}</p>
  <a class="butang {"butang--utama" if pilihan else "butang--garis"}" href="tempah.html#pakej-{i}">Pilih {e(p["nama"])}</a>
</div>''')
    return '<div class="pakej">' + "".join(kad) + "</div>"


def fakta_html():
    butir = ["Kacip Fatimah, Manjakani dan 8 herba Ba Zhen"]
    if not tiada("no_mal"):
        butir.append("Berdaftar KKM: " + v("no_mal", "no. pendaftaran MAL"))
    if not tiada("halal"):
        butir.append("Halal: " + v("halal", "status / badan pensijilan halal"))
    if cfg.get("gmp"):
        butir.append("Dikilangkan di kilang GMP")
    if (cfg.get("penghantaran") or {}).get("cod"):
        butir.append("Boleh bayar semasa terima (COD)")
    li = "".join(f"<li>{I_SEMAK}<span>{b}</span></li>" for b in butir)
    return f'<div class="fakta"><div class="bekas"><ul>{li}</ul></div></div>'


# ------------------------------------------------------------------ soalan lazim
def soalan_semua():
    peng = cfg.get("penghantaran") or {}
    bayar = cfg.get("cara_bayar") or []
    bayar_html = e(", ".join(bayar)) if bayar else isi("cara bayaran, cth. FPX, kad, COD")
    lapan_nama = ", ".join(n for n, *_ in LAPAN)

    produk = [
        (f"Apa itu {JENAMA}?",
         f"<p>{JENAMA} ialah produk herba tradisional untuk wanita. Bahan utamanya Kacip Fatimah dan Manjakani, "
         f"dua herba kewanitaan warisan Melayu, dilengkapi ramuan klasik lapan herba Ba Zhen.</p>"
         f"<p>Bentuk produk: {v('bentuk', 'bentuk produk, cth. kapsul / minuman sachet')}. "
         f"Kandungan sekotak: {v('kandungan_sekotak', 'kandungan sekotak, cth. 60 kapsul')}.</p>"),
        (f"Apa bahan dalam {JENAMA}?",
         f"<p>Dua bahan utama: ekstrak Kacip Fatimah (<i>Labisia pumila</i>) dan ekstrak Manjakani (<i>Quercus infectoria</i>).</p>"
         f"<p>Bahan sokongan: lapan herba Ba Zhen, iaitu {e(lapan_nama)}. "
         f"Butiran penuh ada di halaman <a href=\"bahan.html\">Bahan</a>.</p>"),
        ("Ba Zhen itu apa? Sesuai ke untuk orang Melayu?",
         "<p>Ba Zhen bermaksud “lapan khazanah”. Ia ramuan herba Cina klasik yang sudah digunakan beratus tahun, "
         "terutamanya oleh wanita. Dalam resipi klasik, kesemua lapan bahannya berasal daripada tumbuhan dan kulat, tanpa bahan haiwan.</p>"
         "<p>Ramai wanita Melayu sudah biasa dengan herba Cina seperti dang gui dan ginseng dalam sup dan jamu moden. "
         "Ba Zhen hanyalah gabungan lapan herba seumpama itu dalam satu resipi.</p>"),
    ]
    if not tiada("halal"):
        produk.append((f"Adakah {JENAMA} halal?",
                       f"<p>Status halal: {v('halal', 'status / badan pensijilan halal')}.</p>"))
    if not tiada("no_mal"):
        produk.append((f"Adakah {JENAMA} berdaftar dengan KKM?",
                       f"<p>Ya. Nombor pendaftaran: {v('no_mal', 'no. pendaftaran MAL')}. "
                       f"Anda boleh semak sendiri nombor ini di laman carian produk NPRA (npra.gov.my).</p>"))

    guna = [
        ("Bagaimana cara ambil?",
         cara_ambil_html() + "<p style=\"margin-top:1rem\">Sentiasa ikut arahan pada label produk.</p>"),
        ("Siapa yang tidak sesuai mengambilnya?",
         "<p>Jangan ambil jika anda hamil. Dapatkan nasihat doktor atau ahli farmasi dahulu jika anda:</p>"
         "<ul><li>sedang menyusu atau merancang untuk hamil;</li>"
         "<li>mengambil ubat cair darah, ubat hormon atau ubat tetap yang lain;</li>"
         "<li>ada penyakit kronik atau bakal menjalani pembedahan;</li>"
         "<li>berumur bawah 18 tahun.</li></ul>"),
        ("Berapa lama baru nampak kesan?",
         "<p>Setiap orang berbeza, jadi kami tidak menjanjikan kesan dalam tempoh tertentu. "
         "Herba tradisional diamalkan secara konsisten mengikut sukatan, bukan diambil untuk kesan segera.</p>"),
        ("Ada kesan sampingan?",
         "<p>Berhenti mengambilnya dan berjumpa doktor jika anda mengalami ruam, sakit perut, pening, "
         "pendarahan luar biasa atau sebarang reaksi yang merisaukan. Jangan ambil melebihi sukatan pada label.</p>"),
        (f"Bolehkah {JENAMA} menggantikan ubat doktor?",
         f"<p>Tidak. {JENAMA} ialah produk tradisional, bukan ubat untuk merawat penyakit. "
         "Jika anda ada masalah kesihatan, teruskan rawatan dan ikut nasihat doktor anda.</p>"),
    ]

    beli = [
        ("Bagaimana cara tempah?",
         "<p>Pilih pakej di halaman <a href=\"tempah.html\">Tempah</a>, isi nama dan alamat, kemudian tekan butang hantar. "
         "Butiran tempahan anda akan dibuka di WhatsApp. Kami sahkan tempahan dan cara bayaran di situ.</p>"),
        ("Apa cara bayaran yang diterima?", f"<p>{bayar_html}.</p>"),
        ("Berapa kos dan tempoh penghantaran?",
         f"<p>Semenanjung: {v('kos_semenanjung', 'kos pos Semenanjung', peng)}. "
         f"Sabah dan Sarawak: {v('kos_sabah_sarawak', 'kos pos Sabah/Sarawak', peng)}.</p>"
         f"<p>Tempoh: {v('tempoh', 'tempoh penghantaran, cth. 2 hingga 4 hari bekerja', peng)}. "
         f"Kurier: {v('kurier', 'nama kurier', peng)}.</p>"),
        ("Boleh pulangkan barang?",
         f"<p>{v('polisi_pemulangan', 'polisi pemulangan, cth. dalam 7 hari jika rosak atau salah hantar')}</p>"
         "<p>Butiran lanjut di halaman <a href=\"polisi.html\">Polisi</a>.</p>"),
    ]
    return [("Tentang produk", produk), ("Cara guna dan keselamatan", guna), ("Tempahan dan penghantaran", beli)]


def soalan_blok(senarai):
    return "".join(
        f'<details><summary>{e(s)}</summary><div class="jawapan">{j}</div></details>' for s, j in senarai)


# ------------------------------------------------------------------ rangka
NAV = [("index.html", "Utama"), ("bahan.html", "Bahan"), ("index.html#cara-ambil", "Cara ambil"),
       ("tentang.html", "Tentang"), ("soalan-lazim.html", "Soalan lazim")]


def pixel():
    pid = "".join(ch for ch in str(cfg.get("meta_pixel_id") or "") if ch.isdigit())
    if not pid:
        return ""
    return ("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
            "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;"
            "n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];"
            "s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');"
            f"fbq('init','{pid}');fbq('track','PageView');</script>")


def rangka(fail, tajuk, huraian, badan, bar=True):
    domain = (cfg.get("domain") or "").strip().rstrip("/")
    if domain and not domain.startswith("http"):
        domain = "https://" + domain
    kanon = f'<link rel="canonical" href="{e(domain)}/{"" if fail == "index.html" else e(fail)}">' if domain else ""
    og_img = f'<meta property="og:image" content="{e(domain)}/img/og-image.jpg">' if domain else ""
    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == fail else ""}>{e(t)}</a>' for h, t in NAV)
    draf_bar = ('<div class="draf-bar"><div class="bekas"><strong>Pratonton draf.</strong> '
                'Tanda kuning ialah maklumat yang belum diisi dalam config.json.</div></div>') if DRAF else ""
    bar_html = (f'<div class="bar-tempah">{butang_tempah()}</div>') if bar else ""
    syarikat = e(cfg.get("syarikat") or JENAMA)
    mal = "" if tiada("no_mal") or not ada("no_mal") else f" No. pendaftaran: {e(cfg['no_mal'])}."
    robots = '<meta name="robots" content="noindex">' if DRAF else ""
    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(tajuk)}</title>
<meta name="description" content="{e(huraian)}">
{robots}
{kanon}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(tajuk)}">
<meta property="og:description" content="{e(huraian)}">
<meta property="og:locale" content="ms_MY">
{og_img}
<meta name="theme-color" content="#3d1535">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%233d1535'/%3E%3Ccircle cx='25' cy='32' r='14' fill='%233f7d5f'/%3E%3Ccircle cx='39' cy='32' r='14' fill='%23b02f66' fill-opacity='.9'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gloock&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/site.css">
{pixel()}
</head>
<body class="{"ada-bar" if bar else ""}">
<a class="langkau" href="#kandungan">Terus ke kandungan</a>
{draf_bar}
<header class="kepala">
  <div class="bekas kepala__dalam">
    <a class="jenama" href="index.html">{e(JENAMA)}</a>
    <button class="nav-suis" type="button" aria-controls="nav" aria-expanded="false" aria-label="Buka menu">{I_MENU}</button>
    <nav class="nav" id="nav" aria-label="Utama">
      {nav}
      <a class="butang butang--emas" href="tempah.html">Tempah</a>
    </nav>
  </div>
</header>
<div class="songket" aria-hidden="true"></div>
<main id="kandungan">
{badan}
</main>
<div class="songket" aria-hidden="true"></div>
<footer class="kaki">
  <div class="bekas">
    <div class="kaki__grid">
      <div>
        <a class="jenama" href="index.html">{e(JENAMA)}</a>
        <p>Kacip Fatimah dan Manjakani, diperkaya lapan herba Ba Zhen. Digunakan secara tradisional untuk kesihatan wanita.</p>
      </div>
      <div>
        <h2>Laman</h2>
        <ul>
          <li><a href="bahan.html">Bahan</a></li>
          <li><a href="tentang.html">Tentang {e(JENAMA)}</a></li>
          <li><a href="soalan-lazim.html">Soalan lazim</a></li>
          <li><a href="polisi.html">Polisi privasi, penghantaran dan pemulangan</a></li>
        </ul>
      </div>
      <div>
        <h2>Hubungi</h2>
        <ul>
          <li><a href="{e(WA_TANYA)}" target="_blank" rel="noopener">WhatsApp {("+" + WA_NOMBOR) if WA_NOMBOR else isi("nombor WhatsApp")}</a></li>
          <li>{v("emel", "emel")}</li>
          <li><a href="tempah.html">Tempah {e(JENAMA)}</a></li>
        </ul>
      </div>
    </div>
    <div class="kaki__penafian">
      <p>Ini ialah produk tradisional. Kenyataan di laman ini berdasarkan kegunaan tradisi dan bukan nasihat perubatan.
      {e(JENAMA)} tidak bertujuan mendiagnosis, merawat, menyembuhkan atau mencegah sebarang penyakit.
      Jangan ambil jika hamil. Jika menyusu atau sedang mengambil ubat, dapatkan nasihat doktor dahulu.</p>
      <p>&copy; {TAHUN} {syarikat}.{mal}</p>
    </div>
  </div>
</footer>
{bar_html}
<script src="js/site.js" defer></script>
</body>
</html>
'''


# ------------------------------------------------------------------ halaman: utama
def hal_utama():
    lapan_li = "".join(f"<li><div><b>{e(n)}</b> <span>{e(m)}</span></div></li>" for n, m, *_ in LAPAN)

    sebab = [
        (I_PERIUK, "Tak perlu merebus", "Herba sudah diproses dan disukat. Tiada periuk, tiada bau akar kayu di dapur."),
        (I_SUKAT, "Sukatan sama setiap hari", "Tiada agak-agak segenggam atau secubit. Setiap sajian sama kandungannya."),
        (I_LABEL, "Setiap bahan dinamakan", "Kesemua sepuluh herba disenaraikan pada label dan di laman ini. Tiada “ramuan rahsia”."),
    ]
    if not tiada("no_mal"):
        sebab.append((I_PERISAI, "Berdaftar dengan KKM",
                      f"Nombor pendaftaran {v('no_mal', 'no. pendaftaran MAL')}, boleh disemak di laman NPRA."))
    sebab_html = "".join(f"<div>{ik}<h3>{e(t)}</h3><p>{p}</p></div>" for ik, t, p in sebab)

    testi = cfg.get("testimoni") or []
    testi_html = ""
    if testi:
        kad = "".join(
            f'<blockquote><p>“{e(t["teks"])}”</p><cite>{e(t["nama"])}'
            f'{", " + e(t["lokasi"]) if t.get("lokasi") else ""}</cite></blockquote>' for t in testi)
        testi_html = f'''<section class="blok blok--kelopak">
  <div class="bekas">
    <div class="blok__kepala"><h2>Kata pelanggan kami</h2>
    <p>Pengalaman setiap orang berbeza. Ini perkongsian pelanggan sebenar, dengan izin mereka.</p></div>
    <div class="testi">{kad}</div>
  </div>
</section>'''

    ringkas = soalan_semua()
    pilihan_soalan = [ringkas[0][1][2], ringkas[1][1][1], ringkas[1][1][2], ringkas[2][1][0]]

    badan = f'''
<section class="hero">
  <div class="bekas hero__grid">
    <div>
      <h1>Kacip Fatimah dan Manjakani, diperkaya lapan herba Ba Zhen.</h1>
      <p class="hero__sub">{e(JENAMA)} menghimpunkan dua herba kewanitaan warisan Melayu bersama ramuan klasik lapan herba, untuk amalan penjagaan dalaman wanita setiap hari.</p>
      <div class="butang-baris">
        {butang_tempah("butang--emas")}
        <a class="butang butang--garis" href="bahan.html">Kenali bahannya</a>
      </div>
      <p class="hero__tuntutan">Digunakan secara tradisional untuk kesihatan wanita.</p>
    </div>
    <div class="hero__rajah">{rajah(hidup=True)}</div>
  </div>
</section>
{fakta_html()}

<section class="blok blok--putih">
  <div class="bekas dua dua--foto-kecil">
    {foto("produk.jpg", f"Kotak {JENAMA} bersama daun Kacip Fatimah dan buah manjakani", "gerbang")}
    <div>
      <h2>Amalan nenek kita, tanpa periuk dan akar kayu.</h2>
      <p class="pendek">Dulu, ibu dan nenek merebus Kacip Fatimah selepas bersalin dan menyimpan manjakani dalam balang di dapur. Amalannya masih elok. Yang berubah cuma masa kita.</p>
      <p class="pendek">{e(JENAMA)} menyediakan herba yang sama dalam bentuk {v("bentuk", "bentuk produk, cth. kapsul / minuman sachet")}, dengan sukatan yang tetap. Ambil, dan teruskan hari anda.</p>
      <div class="butang-baris">{butang_tempah()}</div>
    </div>
  </div>
</section>

<section class="blok blok--kelopak">
  <div class="bekas">
    <div class="blok__kepala">
      <h2>Dua herba yang wanita Melayu kenal sejak dulu.</h2>
      <p>Kedua-duanya bahan utama {e(JENAMA)}, dan kedua-duanya sudah lama ada dalam jamu dan amalan berpantang kita.</p>
    </div>
    <div class="herba">
      <article class="herba__kad">
        {foto("kacip-fatimah.jpg", "Pokok Kacip Fatimah dengan daun hijau gelap di lantai hutan")}
        <div class="herba__isi">
          <h3>Kacip Fatimah</h3>
          <p class="herba__latin">Labisia pumila</p>
          <p>Herba renek dari lantai hutan hujan Malaysia. Secara tradisinya direbus dan diminum wanita untuk penjagaan selepas bersalin dan kesihatan sistem peranakan.</p>
          <p><a href="bahan.html#kacip-fatimah">Baca tentang Kacip Fatimah</a></p>
        </div>
      </article>
      <article class="herba__kad herba__kad--manjakani">
        {foto("manjakani.jpg", "Buah manjakani kering berwarna coklat dalam mangkuk kayu")}
        <div class="herba__isi">
          <h3>Manjakani</h3>
          <p class="herba__latin">Quercus infectoria</p>
          <p>Buah kecil yang keras dan kelat daripada pokok oak. Kaya dengan tanin, dan turun-temurun menjadi bahan jamu untuk penjagaan dalaman wanita, terutamanya selepas bersalin.</p>
          <p><a href="bahan.html#manjakani">Baca tentang Manjakani</a></p>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="blok blok--daun">
  <div class="bekas dua">
    <div>
      <h2>Dilengkapi Ba Zhen, ramuan lapan herba.</h2>
      <p class="pendek">Ba Zhen bermaksud “lapan khazanah”. Ramuan herba Cina klasik ini secara tradisinya diambil wanita untuk menyokong darah dan tenaga. Dalam {e(JENAMA)}, ia bahan sokongan kepada dua herba utama.</p>
      <ul class="lapan">{lapan_li}</ul>
      <p style="margin-top:1.6rem"><a href="bahan.html#ba-zhen">Lihat butiran lapan herba</a></p>
    </div>
    {foto("ba-zhen.jpg", "Lapan jenis herba kering Ba Zhen disusun dalam piring kecil", "petak")}
  </div>
</section>

<section class="blok blok--putih">
  <div class="bekas">
    <div class="blok__kepala">
      <h2>Siapa yang biasa mengamalkannya?</h2>
      <p>Herba-herba ini sudah lama menjadi sebahagian daripada penjagaan diri wanita pada pelbagai peringkat hidup.</p>
    </div>
    <ul class="siapa">
      <li><h3>Ibu yang baru habis pantang</h3><p>Yang mahu meneruskan penjagaan dalaman selepas tempoh berpantang tamat. Jika masih menyusu, tanya doktor dahulu.</p></li>
      <li><h3>Wanita bekerja</h3><p>Yang mahukan satu amalan herba yang ringkas di celah jadual yang padat.</p></li>
      <li><h3>Isteri yang menjaga diri</h3><p>Yang menganggap penjagaan dalaman sama penting dengan penjagaan luaran.</p></li>
      <li><h3>Wanita 40-an ke atas</h3><p>Yang mula memberi lebih perhatian kepada kesihatan kewanitaan.</p></li>
    </ul>
  </div>
</section>

<section class="blok blok--kelopak">
  <div class="bekas">
    <div class="blok__kepala"><h2>Kenapa {e(JENAMA)}?</h2></div>
    <div class="sebab">{sebab_html}</div>
  </div>
</section>

<section class="blok blok--putih" id="cara-ambil">
  <div class="bekas dua">
    <div>
      <h2>Cara ambil</h2>
      {cara_ambil_html()}
      <div style="margin-top:1.8rem">{AMARAN}</div>
    </div>
    {foto("cara-ambil.jpg", f"Tangan wanita memegang {JENAMA} bersama segelas air suam", "lebar")}
  </div>
</section>

{testi_html}

<section class="blok blok--kelopak" id="pakej">
  <div class="bekas">
    <div class="blok__kepala">
      <h2>Pilih pakej anda</h2>
      <p>Tempahan disahkan melalui WhatsApp sebelum barang dipos.</p>
    </div>
    {pakej_html()}
  </div>
</section>

<section class="blok blok--putih">
  <div class="bekas">
    <div class="blok__kepala"><h2>Soalan yang selalu ditanya</h2></div>
    <div class="soalan">{soalan_blok(pilihan_soalan)}</div>
    <p style="margin-top:1.6rem"><a href="soalan-lazim.html">Lihat semua soalan lazim</a></p>
  </div>
</section>

<section class="blok blok--gelap seru">
  <div class="bekas">
    <h2>Warisan herba wanita, sedia untuk rutin anda.</h2>
    <p>Pilih pakej, isi alamat, dan kami sahkan tempahan anda di WhatsApp.</p>
    <div class="butang-baris">
      {butang_tempah("butang--emas")}
      {butang_tanya()}
    </div>
  </div>
</section>
'''
    return rangka("index.html",
                  f"{JENAMA} | Kacip Fatimah dan Manjakani, diperkaya lapan herba Ba Zhen",
                  f"{JENAMA} menghimpunkan Kacip Fatimah dan Manjakani bersama ramuan lapan herba Ba Zhen. Digunakan secara tradisional untuk kesihatan wanita.",
                  badan)


# ------------------------------------------------------------------ halaman: bahan
def hal_bahan():
    baris = "".join(
        f"<tr><th scope=\"row\">{e(n)}</th><td>{e(m.capitalize())}</td><td><i>{e(b)}</i></td><td>{e(bhg)}</td></tr>"
        for n, m, b, bhg in LAPAN)
    sahkan = (f'<p class="kecil">{isi("sahkan senarai dan nama herba Ba Zhen ikut label produk sebenar")}</p>'
              if DRAF else "")
    badan = f'''
<section class="tajuk-halaman">
  <div class="bekas">
    <h1>Bahan dalam {e(JENAMA)}</h1>
    <p>Dua herba utama dan lapan herba sokongan. Di sini kami terangkan setiap satunya: dari mana asalnya, bagaimana ia digunakan secara tradisi, dan apa yang kajian tahu setakat ini.</p>
  </div>
</section>

<section class="blok blok--putih">
  <div class="bekas dua">
    <div class="prosa">
      <h2>Satu formula, sepuluh herba</h2>
      <p>Kacip Fatimah dan Manjakani ialah teras penjagaan dalaman wanita Melayu, jadi kedua-duanya menjadi bahan utama. Ba Zhen pula ramuan Cina klasik yang tumpuannya pada darah dan tenaga. Ia melengkapkan dua herba utama, bukan menggantikannya.</p>
      <p>Malaysia tempat dua tradisi herba ini hidup berjiran. {e(JENAMA)} menghimpunkannya dalam satu sajian.</p>
    </div>
    <div style="max-width:380px;margin-inline:auto;width:100%">{rajah()}</div>
  </div>
</section>

<section class="blok blok--kelopak" id="kacip-fatimah">
  <div class="bekas dua dua--foto-kecil">
    {foto("kacip-fatimah.jpg", "Pokok Kacip Fatimah dengan daun hijau gelap di lantai hutan", "gerbang")}
    <div class="prosa">
      <h2>Kacip Fatimah</h2>
      <p class="herba__latin">Labisia pumila. Juga dikenali sebagai Selusuh Fatimah.</p>
      <p>Kacip Fatimah ialah herba renek yang tumbuh di lantai hutan hujan Malaysia, di tempat yang redup dan lembap. Daunnya hijau gelap dan tumbuh rapat ke tanah.</p>
      <h3>Dalam amalan tradisi</h3>
      <p>Bidan kampung merebus daun dan akarnya untuk diminum ibu selepas bersalin. Menurut Jabatan Perhutanan Semenanjung Malaysia, herba ini secara tradisinya digunakan untuk mengekalkan sistem peranakan wanita yang sihat, dan ia antara bahan paling popular dalam jamu berpantang.</p>
      <h3>Apa kata kajian</h3>
      <p>Kacip Fatimah antara herba tempatan yang paling banyak dikaji. Penyelidik menemui sebatian fitoestrogen di dalamnya, dan beberapa kajian meneliti kegunaannya untuk wanita menopaus. Kajian klinikal pada manusia masih terhad, sebab itu kami hanya menyatakan kegunaan tradisinya.</p>
    </div>
  </div>
</section>

<section class="blok blok--putih" id="manjakani">
  <div class="bekas dua dua--foto-kecil dua--terbalik">
    {foto("manjakani.jpg", "Buah manjakani kering berwarna coklat dalam mangkuk kayu", "gerbang")}
    <div class="prosa">
      <h2>Manjakani</h2>
      <p class="herba__latin">Quercus infectoria. Dalam bahasa Inggeris: oak gall.</p>
      <p>Manjakani bukan buah sebenar. Ia ketumbuhan bulat dan keras yang terbentuk pada ranting sejenis pokok oak dari Asia Barat. Ia sampai ke Alam Melayu melalui perdagangan rempah, lalu menjadi bahan tetap dalam jamu wanita.</p>
      <h3>Dalam amalan tradisi</h3>
      <p>Manjakani ditumbuk halus dan dicampur dalam jamu atau makjun untuk penjagaan dalaman wanita, terutamanya dalam tempoh berpantang. Rasanya sangat kelat.</p>
      <h3>Apa kata kajian</h3>
      <p>Rasa kelat itu datang daripada tanin dan asid galik, sebatian yang bersifat astringen. Kajian makmal ada meneliti sifat antioksidan dan antimikrob ekstraknya. Bukti klinikal pada manusia masih sedikit, jadi kami tidak membuat tuntutan melebihi kegunaan tradisinya.</p>
    </div>
  </div>
</section>

<section class="blok blok--daun" id="ba-zhen">
  <div class="bekas dua dua--foto-kecil">
    {foto("ba-zhen.jpg", "Lapan jenis herba kering Ba Zhen disusun dalam piring kecil", "petak")}
    <div>
      <h2>Ba Zhen, lapan herba sokongan</h2>
      <p class="pendek">Ba Zhen (八珍) bermaksud “lapan khazanah”. Resipinya berusia ratusan tahun dan menggabungkan dua ramuan asas perubatan tradisional Cina: empat herba untuk darah dan empat herba untuk tenaga, atau <i>qi</i>.</p>
      <p class="pendek">Dalam masyarakat Cina, ia lazim direbus sebagai sup dan diminum wanita selepas haid tamat. Dalam resipi klasik, kesemua lapan bahannya daripada tumbuhan dan kulat, tanpa bahan haiwan.</p>
    </div>
  </div>
  <div class="bekas" style="margin-top:2.5rem">
    <div class="jadual-balut">
      <table class="jadual" style="--garis: rgba(255,255,255,.2)">
        <thead><tr><th scope="col">Nama herba</th><th scope="col">Nama biasa</th><th scope="col">Nama botani</th><th scope="col">Bahagian</th></tr></thead>
        <tbody>{baris}</tbody>
      </table>
    </div>
    {sahkan}
  </div>
</section>

<section class="blok blok--putih">
  <div class="bekas">
    <div class="prosa">
      <h2>Keselamatan dahulu</h2>
      {AMARAN}
      <p style="margin-top:1.2rem">Senarai penuh soalan tentang cara guna ada di <a href="soalan-lazim.html">Soalan lazim</a>.</p>
      <div class="butang-baris">{butang_tempah()}{butang_tanya()}</div>
    </div>
  </div>
</section>
'''
    return rangka("bahan.html", f"Bahan dalam {JENAMA}: Kacip Fatimah, Manjakani dan Ba Zhen",
                  f"Kenali sepuluh herba dalam {JENAMA}: Kacip Fatimah, Manjakani dan lapan herba Ba Zhen, serta kegunaan tradisinya.",
                  badan)


# ------------------------------------------------------------------ halaman: tentang
def hal_tentang():
    badan = f'''
<section class="tajuk-halaman">
  <div class="bekas">
    <h1>Tentang {e(JENAMA)}</h1>
    <p>Herba warisan wanita, disediakan untuk cara hidup hari ini.</p>
  </div>
</section>

<section class="blok blok--putih">
  <div class="bekas dua">
    <div class="prosa">
      <h2>Dari dapur nenek ke rutin harian</h2>
      <p>Hampir setiap keluarga Melayu ada cerita tentang jamu. Periuk akar kayu di atas dapur selepas kakak bersalin. Balang manjakani di rak. Pesanan mak supaya “jaga dalam” sama seperti jaga luar.</p>
      <p>Ilmunya masih ada, tetapi tidak ramai yang sempat merebus herba setiap hari. {e(JENAMA)} dibuat supaya amalan itu boleh diteruskan dengan cara yang lebih mudah.</p>
      <h2>Dua tradisi, satu ramuan</h2>
      <p>Di Malaysia, kedai jamu dan kedai sinseh sudah lama berjiran. {e(JENAMA)} mengambil yang terbaik daripada kedua-duanya: Kacip Fatimah dan Manjakani daripada warisan Melayu sebagai bahan utama, dan lapan herba Ba Zhen daripada tradisi Cina sebagai pelengkap.</p>
    </div>
    {foto("warisan.jpg", "Herba kering, lesung batu dan kain batik di atas meja kayu", "gerbang")}
  </div>
</section>

<section class="blok blok--kelopak">
  <div class="bekas">
    <div class="blok__kepala"><h2>Pegangan kami</h2></div>
    <div class="sebab">
      <div><h3>Kami namakan setiap bahan</h3><p>Kesemua sepuluh herba disenaraikan pada label dan di halaman <a href="bahan.html">Bahan</a>.</p></div>
      <div><h3>Kami tak janji keajaiban</h3><p>Herba tradisional bukan ubat segera. Kami tidak menjanjikan kesan dalam tempoh tertentu, dan produk ini tidak menggantikan nasihat doktor.</p></div>
      <div><h3>Kami jawab soalan anda</h3><p>Sebelum atau selepas membeli, tanya kami apa sahaja tentang produk di WhatsApp.</p></div>
    </div>
  </div>
</section>

<section class="blok blok--putih">
  <div class="bekas">
    <div class="prosa">
      <h2>Maklumat syarikat</h2>
      <div class="jadual-balut">
      <table class="jadual">
        <tbody>
          <tr><th scope="row">Syarikat</th><td>{v("syarikat", "nama syarikat")}</td></tr>
          <tr><th scope="row">No. pendaftaran SSM</th><td>{v("no_ssm", "no. SSM")}</td></tr>
          <tr><th scope="row">Alamat</th><td>{v("alamat_syarikat", "alamat syarikat")}</td></tr>
          {"" if tiada("no_mal") else f'<tr><th scope="row">No. pendaftaran KKM</th><td>{v("no_mal", "no. pendaftaran MAL")}</td></tr>'}
          <tr><th scope="row">WhatsApp</th><td>{("+" + WA_NOMBOR) if WA_NOMBOR else isi("nombor WhatsApp")}</td></tr>
          <tr><th scope="row">Emel</th><td>{v("emel", "emel")}</td></tr>
        </tbody>
      </table>
      </div>
      <div class="butang-baris">{butang_tempah()}{butang_tanya()}</div>
    </div>
  </div>
</section>
'''
    return rangka("tentang.html", f"Tentang {JENAMA}",
                  f"{JENAMA} menghimpunkan herba kewanitaan warisan Melayu dan ramuan klasik Ba Zhen untuk wanita hari ini.",
                  badan)


# ------------------------------------------------------------------ halaman: soalan lazim
def hal_soalan():
    kumpulan = "".join(f"<h2>{e(t)}</h2>{soalan_blok(s)}" for t, s in soalan_semua())
    badan = f'''
<section class="tajuk-halaman">
  <div class="bekas">
    <h1>Soalan lazim</h1>
    <p>Tak jumpa jawapan yang anda cari? Tanya kami terus di WhatsApp.</p>
  </div>
</section>
<section class="blok blok--putih">
  <div class="bekas">
    <div class="soalan">{kumpulan}</div>
    <div class="butang-baris" style="margin-top:2.4rem">{butang_tempah()}{butang_tanya()}</div>
  </div>
</section>
'''
    return rangka("soalan-lazim.html", f"Soalan lazim | {JENAMA}",
                  f"Jawapan kepada soalan lazim tentang {JENAMA}: bahan, cara ambil, keselamatan, tempahan dan penghantaran.",
                  badan)


# ------------------------------------------------------------------ halaman: tempah
NEGERI = ["Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang", "Perak", "Perlis", "Pulau Pinang",
          "Sabah", "Sarawak", "Selangor", "Terengganu", "W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya"]


def hal_tempah():
    peng = cfg.get("penghantaran") or {}
    senarai = cfg.get("pakej") or []
    lalai = next((i for i, p in enumerate(senarai, 1) if p.get("pilihan")), 1)
    pilih = []
    for i, p in enumerate(senarai, start=1):
        pilih.append(f'''<label>
  <input type="radio" name="pakej" value="{i}" data-nama="{e(p["nama"])}" data-harga="{e(harga_teks(p.get("harga")))}"{" checked" if i == lalai else ""}>
  <span><b>{e(p["nama"])}</b><small>{e(p.get("label") or "")}</small></span>
  <span class="harga">{harga(p.get("harga"))}</span>
</label>''')
    bayar = list(cfg.get("cara_bayar") or [])
    bayar_html = ""
    if bayar:
        ops = "".join(f"<option>{e(b)}</option>" for b in bayar)
        bayar_html = f'''<div class="medan"><label for="bayaran">Cara bayar</label>
<select id="bayaran" name="bayaran">{ops}</select></div>'''
    negeri = "".join(f"<option>{e(n)}</option>" for n in NEGERI)

    badan = f'''
<section class="tajuk-halaman">
  <div class="bekas">
    <h1>Tempah {e(JENAMA)}</h1>
    <p>Isi borang ini dan butiran tempahan anda akan dibuka di WhatsApp. Kami sahkan jumlah dan cara bayaran di situ sebelum barang dipos.</p>
  </div>
</section>

<section class="blok blok--kelopak">
  <div class="bekas tempah">
    <form class="borang" id="borang-tempah" novalidate data-whatsapp="{e(WA_NOMBOR)}" data-jenama="{e(JENAMA)}">
      <fieldset>
        <legend>1. Pilih pakej</legend>
        <div class="pilih">{"".join(pilih)}</div>
      </fieldset>

      <fieldset>
        <legend>2. Maklumat penghantaran</legend>
        <div class="medan" data-wajib>
          <label for="nama">Nama penuh</label>
          <input id="nama" name="nama" type="text" autocomplete="name" required>
          <p class="ralat">Masukkan nama penerima.</p>
        </div>
        <div class="medan" data-wajib>
          <label for="telefon">No. telefon</label>
          <input id="telefon" name="telefon" type="tel" inputmode="tel" autocomplete="tel" placeholder="cth. 012-345 6789" required>
          <p class="ralat">Masukkan nombor telefon yang boleh dihubungi kurier.</p>
        </div>
        <div class="medan" data-wajib>
          <label for="alamat">Alamat penuh</label>
          <textarea id="alamat" name="alamat" autocomplete="street-address" required></textarea>
          <p class="ralat">Masukkan alamat penghantaran.</p>
        </div>
        <div class="medan-baris">
          <div class="medan" data-wajib>
            <label for="poskod">Poskod</label>
            <input id="poskod" name="poskod" type="text" inputmode="numeric" autocomplete="postal-code" maxlength="5" required>
            <p class="ralat">Poskod mesti 5 angka.</p>
          </div>
          <div class="medan" data-wajib>
            <label for="negeri">Negeri</label>
            <select id="negeri" name="negeri" autocomplete="address-level1" required>
              <option value="">Pilih negeri</option>{negeri}
            </select>
            <p class="ralat">Pilih negeri.</p>
          </div>
        </div>
        {bayar_html}
        <div class="medan">
          <label for="catatan">Catatan (jika ada)</label>
          <input id="catatan" name="catatan" type="text">
        </div>
      </fieldset>

      <button class="butang butang--utama" type="submit">{I_WA}Hantar tempahan ke WhatsApp</button>
      <p class="kecil" style="margin-top:.9rem">Maklumat anda hanya digunakan untuk memproses tempahan ini. Lihat <a href="polisi.html">polisi privasi</a>.</p>

      <div class="sedia" id="sedia" aria-live="polite">
        <h2 style="font-size:1.4rem">Tempahan anda sedia dihantar</h2>
        <p>Jika WhatsApp tidak terbuka sendiri, tekan butang di bawah. Tempahan hanya sampai kepada kami selepas anda menekan “Send” di WhatsApp.</p>
        <pre id="mesej-pratonton"></pre>
        <a class="butang butang--utama" id="pautan-whatsapp" href="{e(WA_TANYA)}" target="_blank" rel="noopener">{I_WA}Buka WhatsApp</a>
      </div>
    </form>

    <aside class="ringkasan">
      <h2>Selepas anda hantar</h2>
      <ul>
        <li>Kami balas di WhatsApp untuk sahkan tempahan dan jumlah bayaran.</li>
        <li>Kos pos Semenanjung: {v("kos_semenanjung", "kos pos Semenanjung", peng)}</li>
        <li>Kos pos Sabah dan Sarawak: {v("kos_sabah_sarawak", "kos pos Sabah/Sarawak", peng)}</li>
        <li>Tempoh penghantaran: {v("tempoh", "tempoh penghantaran, cth. 2 hingga 4 hari bekerja", peng)}</li>
        {"<li>Boleh bayar semasa terima (COD).</li>" if peng.get("cod") else ""}
      </ul>
      {AMARAN}
      <p style="margin:1.2rem 0 0">Ada soalan dulu? <a href="{e(WA_TANYA)}" target="_blank" rel="noopener">Tanya di WhatsApp</a></p>
    </aside>
  </div>
</section>
'''
    return rangka("tempah.html", f"Tempah {JENAMA}",
                  f"Tempah {JENAMA} melalui WhatsApp. Pilih pakej, isi alamat, dan kami sahkan tempahan anda.",
                  badan, bar=False)


# ------------------------------------------------------------------ halaman: polisi
def hal_polisi():
    peng = cfg.get("penghantaran") or {}
    badan = f'''
<section class="tajuk-halaman">
  <div class="bekas">
    <h1>Polisi</h1>
    <p>Privasi, penghantaran, pemulangan dan penafian.</p>
  </div>
</section>
<section class="blok blok--putih">
  <div class="bekas">
    <div class="prosa">
      <h2 id="privasi">Privasi</h2>
      <p>Apabila anda membuat tempahan, kami mengumpul nama, nombor telefon dan alamat penghantaran anda. Maklumat ini digunakan untuk memproses tempahan, menghantar barang dan menghubungi anda tentang tempahan tersebut.</p>
      <ul>
        <li>Kami berkongsi nama, nombor telefon dan alamat anda dengan syarikat kurier untuk tujuan penghantaran sahaja.</li>
        <li>Kami tidak menjual maklumat peribadi anda kepada pihak ketiga.</li>
        <li>Laman ini mungkin menggunakan kuki dan piksel pengiklanan (contohnya Meta Pixel) untuk mengukur keberkesanan iklan.</li>
        <li>Anda boleh meminta kami menyemak, membetulkan atau memadam maklumat anda dengan menghubungi kami di WhatsApp atau emel, selaras dengan Akta Perlindungan Data Peribadi 2010.</li>
      </ul>

      <h2 id="penghantaran">Penghantaran</h2>
      <p>Kos pos Semenanjung: {v("kos_semenanjung", "kos pos Semenanjung", peng)}. Sabah dan Sarawak: {v("kos_sabah_sarawak", "kos pos Sabah/Sarawak", peng)}.</p>
      <p>Tempoh penghantaran: {v("tempoh", "tempoh penghantaran, cth. 2 hingga 4 hari bekerja", peng)}. Kurier: {v("kurier", "nama kurier", peng)}. Nombor penjejakan dihantar melalui WhatsApp selepas barang dipos.</p>

      <h2 id="pemulangan">Pemulangan dan bayaran balik</h2>
      <p>{v("polisi_pemulangan", "polisi pemulangan, cth. dalam 7 hari jika rosak atau salah hantar")}</p>

      <h2 id="penafian">Penafian</h2>
      <p>{e(JENAMA)} ialah produk tradisional. Maklumat di laman ini berdasarkan kegunaan tradisi herba berkenaan dan disediakan untuk pengetahuan umum. Ia bukan nasihat perubatan.</p>
      <p>Produk ini tidak bertujuan mendiagnosis, merawat, menyembuhkan atau mencegah sebarang penyakit. Kesan pada setiap individu berbeza. Jangan ambil jika hamil. Jika anda menyusu, ada masalah kesihatan atau sedang mengambil ubat, dapatkan nasihat doktor atau ahli farmasi sebelum menggunakannya.</p>

      <h2>Hubungi kami</h2>
      <p>{v("syarikat", "nama syarikat")} ({v("no_ssm", "no. SSM")})<br>{v("alamat_syarikat", "alamat syarikat")}<br>
      WhatsApp: {("+" + WA_NOMBOR) if WA_NOMBOR else isi("nombor WhatsApp")}<br>Emel: {v("emel", "emel")}</p>
    </div>
  </div>
</section>
'''
    return rangka("polisi.html", f"Polisi | {JENAMA}",
                  f"Polisi privasi, penghantaran dan pemulangan {JENAMA}.", badan)


def hal_404():
    badan = f'''
<section class="tajuk-halaman">
  <div class="bekas">
    <h1>Halaman tidak dijumpai</h1>
    <p>Pautan ini mungkin sudah berubah. Kembali ke halaman utama atau terus ke borang tempahan.</p>
    <div class="butang-baris"><a class="butang butang--emas" href="index.html">Ke halaman utama</a>{butang_tempah("butang--garis")}</div>
  </div>
</section>
'''
    return rangka("404.html", f"Halaman tidak dijumpai | {JENAMA}", "Halaman tidak dijumpai.", badan, bar=False)


# ------------------------------------------------------------------ bina
def bina():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "css").mkdir(parents=True)
    (DIST / "js").mkdir()
    (DIST / "img").mkdir()
    shutil.copy(SRC / "site.css", DIST / "css" / "site.css")
    shutil.copy(SRC / "site.js", DIST / "js" / "site.js")
    if (AKAR / "img").is_dir():
        for f in (AKAR / "img").iterdir():
            if f.is_file():
                shutil.copy(f, DIST / "img" / f.name)

    halaman = {
        "index.html": hal_utama, "bahan.html": hal_bahan, "tentang.html": hal_tentang,
        "soalan-lazim.html": hal_soalan, "tempah.html": hal_tempah, "polisi.html": hal_polisi,
        "404.html": hal_404,
    }
    for nama, fn in halaman.items():
        (DIST / nama).write_text(fn(), encoding="utf-8")

    domain = (cfg.get("domain") or "").strip().rstrip("/")
    if domain and not domain.startswith("http"):
        domain = "https://" + domain
    (DIST / ".htaccess").write_text(
        "ErrorDocument 404 /404.html\n"
        "RedirectMatch 404 /\\.git\n"
        "<IfModule mod_expires.c>\n  ExpiresActive On\n  ExpiresByType image/jpeg \"access plus 30 days\"\n"
        "  ExpiresByType image/webp \"access plus 30 days\"\n  ExpiresByType text/css \"access plus 7 days\"\n"
        "  ExpiresByType application/javascript \"access plus 7 days\"\n</IfModule>\n"
        "<IfModule mod_deflate.c>\n  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml\n</IfModule>\n",
        encoding="utf-8")
    robots = "User-agent: *\n" + ("Disallow: /\n" if DRAF else "Allow: /\n")
    if domain and not DRAF:
        robots += f"Sitemap: {domain}/sitemap.xml\n"
        urls = "".join(
            f"<url><loc>{domain}/{'' if n == 'index.html' else n}</loc></url>" for n in halaman if n != "404.html")
        (DIST / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
            encoding="utf-8")
    (DIST / "robots.txt").write_text(robots, encoding="utf-8")

    print(f"Siap: {len(halaman)} halaman -> {DIST}")
    if kosong:
        print(f"\nBelum diisi ({len(kosong)}):")
        for k in kosong:
            print("  -", k)
        if "--ketat" in sys.argv:
            sys.exit("\nGAGAL (--ketat): lengkapkan config.json dahulu.")
    if not (cfg.get("testimoni") or []):
        print("\nNota: tiada testimoni dalam config.json, jadi seksyen testimoni disembunyikan.")


if __name__ == "__main__":
    bina()
