
import streamlit as st
import requests
import base64
import json
import urllib.parse
import time
import os
import base64
from pathlib import Path

st.set_page_config(
    page_title="Indo Panel Utama",
    page_icon="⚡",
    layout="wide"
)

# =========================================================
# KONFIGURASI
# =========================================================
WHATSAPP_NUMBER = "6285379366464"
GITHUB_API = "https://api.github.com"

DEFAULT_PRODUCTS = [
    {
        "id": "panel-mdp-400a",
        "name": "Panel MDP 400A",
        "price": 18500000,
        "stock": "Tersedia",
        "category": "MDP",
        "spec": "Main Breaker 400A | 380/400V | Indoor",
        "description": "Panel distribusi utama untuk kebutuhan gedung dan industri.",
        "image": ""
    },
    {
        "id": "panel-sdp-250a",
        "name": "Panel SDP 250A",
        "price": 12500000,
        "stock": "Tersedia",
        "category": "SDP",
        "spec": "Main Breaker 250A | 380/400V | Indoor",
        "description": "Sub Distribution Panel untuk distribusi daya.",
        "image": ""
    },
    {
        "id": "panel-ats-amf",
        "name": "Panel ATS-AMF",
        "price": 22500000,
        "stock": "Pre Order",
        "category": "ATS / AMF",
        "spec": "Automatic Transfer Switch | AMF | Custom Capacity",
        "description": "Panel otomatis untuk perpindahan sumber listrik PLN dan genset.",
        "image": ""
    }
]

# =========================================================
# UTILITAS
# =========================================================

def local_image_data_uri(path):
    try:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext = Path(path).suffix.lower().replace(".", "")
        mime = "image/png" if ext == "png" else f"image/{ext}"
        return f"data:{mime};base64,{encoded}"
    except Exception:
        return ""


def rupiah(value):
    try:
        return f"Rp {int(value):,}".replace(",", ".")
    except:
        return "Rp 0"

def slugify(text):
    text = text.lower().strip()
    allowed = []
    for c in text:
        if c.isalnum():
            allowed.append(c)
        elif c in [" ", "-", "_"]:
            allowed.append("-")
    slug = "".join(allowed)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or f"produk-{int(time.time())}"

def whatsapp_link(product):
    message = (
        f"Halo Indo Panel Utama, saya tertarik dengan produk:\n\n"
        f"{product['name']}\n"
        f"Harga: {rupiah(product['price'])}\n"
        f"Spesifikasi: {product.get('spec','')}\n\n"
        f"Mohon informasi lebih lanjut."
    )
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}"

def get_secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

GITHUB_TOKEN = get_secret("GITHUB_TOKEN", "")
GITHUB_REPO = get_secret("GITHUB_REPO", "doni3ono/panel-indo-utama")
ADMIN_PASSWORD = get_secret("ADMIN_PASSWORD", "")

def github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def github_get_file(path):
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}"
    r = requests.get(url, headers=github_headers(), timeout=20)
    if r.status_code == 200:
        return r.json()
    return None

def github_put_file(path, content_bytes, message):
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN belum dipasang di Streamlit Secrets."

    existing = github_get_file(path)
    payload = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode("utf-8"),
        "branch": "main"
    }
    if existing and existing.get("sha"):
        payload["sha"] = existing["sha"]

    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}"
    r = requests.put(url, headers=github_headers(), json=payload, timeout=30)

    if r.status_code in [200, 201]:
        return True, "Berhasil disimpan."
    try:
        msg = r.json().get("message", r.text)
    except:
        msg = r.text
    return False, f"GitHub error {r.status_code}: {msg}"

def github_delete_file(path, message):
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN belum dipasang."
    existing = github_get_file(path)
    if not existing:
        return True, "File tidak ada."
    payload = {
        "message": message,
        "sha": existing["sha"],
        "branch": "main"
    }
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}"
    r = requests.delete(url, headers=github_headers(), json=payload, timeout=30)
    return (r.status_code == 200, r.json().get("message", "Berhasil") if r.content else "Berhasil")

def load_products():
    file_data = github_get_file("products.json")
    if file_data and file_data.get("content"):
        try:
            raw = base64.b64decode(file_data["content"]).decode("utf-8")
            return json.loads(raw)
        except Exception:
            pass
    return DEFAULT_PRODUCTS.copy()

def save_products(products, commit_message="Update produk Indo Panel Utama"):
    content = json.dumps(products, ensure_ascii=False, indent=2).encode("utf-8")
    return github_put_file("products.json", content, commit_message)

def upload_product_image(uploaded_file, product_id):
    if uploaded_file is None:
        return None, "Tidak ada foto."

    ext = uploaded_file.name.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        return None, "Format foto harus JPG, JPEG, PNG, atau WEBP."

    path = f"images/{product_id}.{ext}"
    ok, msg = github_put_file(
        path,
        uploaded_file.getvalue(),
        f"Upload foto {product_id}"
    )
    if not ok:
        return None, msg

    # URL raw GitHub dengan query timestamp untuk menghindari cache lama
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{path}?v={int(time.time())}"
    return url, "Foto berhasil diupload."

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
:root {
    --bg: #07111f;
    --card: rgba(17, 27, 45, 0.72);
    --line: rgba(255,255,255,.10);
    --text: #eaf2ff;
    --muted: #9fb0c6;
    --accent: #4cc9f0;
    --accent2: #7c3aed;
}
.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(76,201,240,.10), transparent 30%),
        radial-gradient(circle at 100% 10%, rgba(124,58,237,.12), transparent 30%),
        linear-gradient(180deg, #06101c 0%, #0a1423 100%);
    color: var(--text);
}
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="stSidebarCollapsedControl"] {
    display: none;
}
header[data-testid="stHeader"] {
    background: rgba(5, 12, 22, .82);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.block-container {
    max-width: 1220px;
    padding-top: 2.3rem;
    padding-bottom: 3rem;
}
.top-brand {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:20px;
    margin-bottom:8px;
}
.brand-mark {
    display:flex;
    align-items:center;
    gap:12px;
    font-size:20px;
    font-weight:850;
    letter-spacing:.4px;
    color:#f8fbff;
}
.brand-icon {
    width:38px;
    height:38px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:12px;
    background:linear-gradient(135deg,#38bdf8,#6366f1);
    box-shadow:0 8px 28px rgba(56,189,248,.22);
}
.nav-wrap {
    padding:8px 10px 4px 10px;
    margin-bottom:18px;
    border-radius:18px;
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.07);
}
div[role="radiogroup"] {
    gap:4px;
}
div[role="radiogroup"] label {
    background:transparent;
    border-radius:12px;
    padding:7px 12px;
}
.hero-grid {
    display:grid;
    grid-template-columns: 1.35fr .65fr;
    gap:26px;
    align-items:center;
}
.hero-visual {
    min-height:310px;
    border-radius:24px;
    border:1px solid rgba(255,255,255,.12);
    background:
      radial-gradient(circle at 70% 20%, rgba(56,189,248,.28), transparent 24%),
      radial-gradient(circle at 35% 70%, rgba(99,102,241,.24), transparent 24%),
      linear-gradient(145deg, rgba(10,25,45,.96), rgba(13,39,65,.88));
    position:relative;
    overflow:hidden;
    box-shadow:inset 0 0 80px rgba(56,189,248,.04);
}
.panel-line {
    position:absolute;
    left:16%;
    right:16%;
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(125,211,252,.8),transparent);
}
.panel-line.l1 { top:28%; }
.panel-line.l2 { top:50%; }
.panel-line.l3 { top:72%; }
.panel-node {
    position:absolute;
    width:54px;
    height:54px;
    border-radius:16px;
    background:rgba(255,255,255,.06);
    border:1px solid rgba(255,255,255,.14);
    box-shadow:0 0 35px rgba(56,189,248,.10);
}
.n1 { left:18%; top:18%; }
.n2 { right:18%; top:39%; }
.n3 { left:30%; bottom:14%; }
.visual-label {
    position:absolute;
    right:18px;
    bottom:18px;
    padding:9px 12px;
    border-radius:12px;
    background:rgba(2,8,23,.55);
    border:1px solid rgba(255,255,255,.10);
    color:#bae6fd;
    font-size:12px;
    font-weight:700;
    letter-spacing:.7px;
}
.cta-row {
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    margin-top:20px;
}
.cta-primary, .cta-secondary {
    display:inline-block;
    text-decoration:none !important;
    padding:11px 16px;
    border-radius:12px;
    font-weight:800;
}
.cta-primary {
    background:linear-gradient(135deg,#38bdf8,#6366f1);
    color:white !important;
}
.cta-secondary {
    background:rgba(255,255,255,.06);
    border:1px solid rgba(255,255,255,.12);
    color:#e5eef9 !important;
}
@media (max-width: 850px) {
    .top-brand img { height:46px !important; max-width:240px !important; }
    .hero-grid { grid-template-columns:1fr; }
    .hero-visual { min-height:220px; }
    .hero-title { font-size:42px !important; }
}
.hero {
    position: relative;
    overflow: hidden;
    padding: 46px 42px;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(8,72,138,.88), rgba(24,48,86,.90)),
        linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.01));
    border: 1px solid rgba(255,255,255,.14);
    box-shadow: 0 24px 80px rgba(0,0,0,.28);
    margin-bottom: 28px;
    backdrop-filter: blur(18px);
}
.hero:after {
    content: "";
    position: absolute;
    width: 320px;
    height: 320px;
    border-radius: 50%;
    right: -90px;
    top: -90px;
    background: radial-gradient(circle, rgba(76,201,240,.35), transparent 68%);
    filter: blur(8px);
}
.eyebrow {
    display:inline-block;
    padding:8px 14px;
    border-radius:999px;
    background:rgba(255,255,255,.10);
    border:1px solid rgba(255,255,255,.15);
    font-size:13px;
    font-weight:700;
    letter-spacing:1.2px;
    margin-bottom:16px;
}
.hero-title {
    font-size:54px;
    line-height:1.06;
    font-weight:850;
    margin:0 0 14px 0;
    max-width:800px;
}
.hero-sub {
    font-size:19px;
    color:#dbeafe;
    max-width:760px;
    margin:0;
}
.ai-card {
    padding:22px;
    border-radius:20px;
    background:linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.03));
    border:1px solid var(--line);
    box-shadow:0 14px 40px rgba(0,0,0,.18);
    backdrop-filter:blur(14px);
    margin-bottom:16px;
}
.ai-badge {
    display:inline-block;
    font-size:12px;
    font-weight:700;
    padding:6px 10px;
    border-radius:999px;
    background:rgba(76,201,240,.12);
    border:1px solid rgba(76,201,240,.35);
    color:#a5f3fc;
    margin-bottom:10px;
}
.product-shell {
    padding:16px;
    border-radius:22px;
    background:rgba(255,255,255,.045);
    border:1px solid var(--line);
    box-shadow:0 12px 32px rgba(0,0,0,.15);
    min-height:100%;
}
.price {
    font-size:26px;
    font-weight:850;
    color:#7dd3fc;
    margin-bottom:6px;
}
.placeholder {
    background:linear-gradient(135deg, rgba(76,201,240,.08), rgba(124,58,237,.08));
    border:1px dashed rgba(255,255,255,.18);
    border-radius:16px;
    padding:64px 10px;
    text-align:center;
    color:var(--muted);
}
.kpi {
    padding:18px;
    border-radius:18px;
    background:rgba(255,255,255,.04);
    border:1px solid var(--line);
    text-align:center;
}
.kpi-value {
    font-size:27px;
    font-weight:850;
    color:#e0f2fe;
}
.kpi-label {
    font-size:13px;
    color:var(--muted);
}
.footer {
    text-align:center;
    color:#7f8ea3;
    padding:32px 0 18px 0;
    margin-top:34px;
    border-top:1px solid rgba(255,255,255,.06);
}
h1,h2,h3 { color:#f8fbff !important; }
p, .stMarkdown { color:#d6deea; }
div[data-testid="stLinkButton"] a,
div[data-testid="stButton"] button {
    border-radius:14px !important;
    font-weight:700 !important;
}

div[data-testid="stImage"] img {
    object-fit: contain;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
products = load_products()


# Support direct links such as ?page=Products
try:
    qp_page = st.query_params.get("page", "")
    if qp_page in ["Home", "About Us", "Products", "Projects", "Partners & Clients", "Certificates", "Contact Us"]:
        st.session_state.page = qp_page
        st.query_params.clear()
except Exception:
    pass


# =========================================================
# TOP BRAND & PUBLIC NAVIGATION
# =========================================================
brand_col1, brand_col2 = st.columns([3, 1])

with brand_col1:
    logo_path = "assets/logo.png"
    if Path(logo_path).exists():
        st.image(logo_path, width=280)
    else:
        st.markdown("""
        <div class="top-brand">
            <div class="brand-mark">
                <div class="brand-icon">⚡</div>
                <div>INDO PANEL UTAMA</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with brand_col2:
    st.markdown(
        """
        <div style="
            text-align:right;
            color:#8ea0b7;
            font-size:13px;
            padding-top:18px;
        ">
            Solusi Panel Listrik Terpercaya
        </div>
        """,
        unsafe_allow_html=True
    )

if "page" not in st.session_state:
    st.session_state.page = "Home"

public_pages = [
    "Home",
    "About Us",
    "Products",
    "Projects",
    "Partners & Clients",
    "Certificates",
    "Contact Us"
]

if st.session_state.page != "Admin Produk":
    st.markdown('<div class="nav-wrap">', unsafe_allow_html=True)
    selected_page = st.radio(
        "Navigation",
        public_pages,
        index=public_pages.index(st.session_state.page) if st.session_state.page in public_pages else 0,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

menu = st.session_state.page

# =========================================================
# HERO — PUBLIC PAGES ONLY
# =========================================================
if menu != "Admin Produk":
    wa_quote = urllib.parse.quote(
        "Halo Indo Panel Utama, saya ingin meminta quotation / konsultasi panel listrik."
    )
    st.markdown(f"""
    <div class="hero">
        <div class="hero-grid">
            <div>
                <div class="eyebrow">⚡ RELIABLE • RESPONSIVE • PROJECT-ORIENTED</div>
                <div class="hero-title">Panel Listrik untuk Proyek Modern.</div>
                <p class="hero-sub">
                    Solusi panel listrik untuk gedung, industri, fasilitas komersial,
                    data center, perumahan, dan berbagai kebutuhan proyek.
                </p>
                <div class="cta-row">
                    <a class="cta-primary" href="?page=Products">Lihat Produk</a>
                    <a class="cta-secondary" href="https://wa.me/{WHATSAPP_NUMBER}?text={wa_quote}" target="_blank">
                        Minta Penawaran
                    </a>
                </div>
            </div>
            <div class="hero-visual">
                <div class="panel-line l1"></div>
                <div class="panel-line l2"></div>
                <div class="panel-line l3"></div>
                <div class="panel-node n1"></div>
                <div class="panel-node n2"></div>
                <div class="panel-node n3"></div>
                <div class="visual-label">SMART POWER DISTRIBUTION</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# FUNGSI TAMPIL PRODUK
# =========================================================
def show_product_card(product):
    st.markdown('<div class="product-shell">', unsafe_allow_html=True)
    if product.get("image"):
        st.image(product["image"], use_container_width=True)
    else:
        st.markdown(
            '<div class="placeholder">📷 Foto produk belum ditambahkan</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<div class="ai-badge">{product.get("category","Panel")} • {product.get("stock","")}</div>',
        unsafe_allow_html=True
    )
    st.subheader(product["name"])
    st.markdown(
        f'<div class="price">{rupiah(product["price"])}</div>',
        unsafe_allow_html=True
    )
    st.write(product.get("spec", ""))
    if product.get("description"):
        st.write(product["description"])
    st.link_button(
        "💬 Konsultasi & Pesan",
        whatsapp_link(product),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# HOME
# =========================================================
if menu == "Home":
    st.markdown("""
    <div class="ai-card">
        <div class="ai-badge">COMPANY PROFILE</div>
        <h2>Keandalan untuk Setiap Panel</h2>
        <p>
            Indo Panel Utama menghadirkan solusi panel listrik untuk kebutuhan
            industri, gedung, fasilitas komersial, dan proyek. Fokus kami adalah
            kesesuaian spesifikasi, kemudahan konsultasi, dan layanan yang responsif.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="kpi"><div class="kpi-value">{len(products)}</div>'
            '<div class="kpi-label">Produk Katalog</div></div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            '<div class="kpi"><div class="kpi-value">Custom</div>'
            '<div class="kpi-label">Panel by Specification</div></div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            '<div class="kpi"><div class="kpi-value">Fast</div>'
            '<div class="kpi-label">WhatsApp Consultation</div></div>',
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            '<div class="kpi"><div class="kpi-value">Project</div>'
            '<div class="kpi-label">Industrial & Commercial</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("## Kategori Produk")
    categories_home = [
        ("⚙️", "Main Distribution Panel", "Distribusi utama untuk gedung dan fasilitas."),
        ("🔌", "Sub Distribution Panel", "Distribusi daya ke area atau beban tertentu."),
        ("🔁", "ATS / AMF Panel", "Perpindahan otomatis PLN dan genset."),
        ("⚡", "Capacitor Bank", "Membantu optimasi faktor daya."),
        ("🧠", "Control Panel", "Panel kontrol untuk kebutuhan mesin dan sistem."),
        ("🛠️", "Custom Panel", "Dibuat sesuai spesifikasi dan kebutuhan proyek.")
    ]
    for row_start in range(0, len(categories_home), 3):
        cols = st.columns(3)
        for j, (icon, title, desc) in enumerate(categories_home[row_start:row_start+3]):
            with cols[j]:
                st.markdown(
                    f"""
                    <div class="ai-card" style="min-height:185px;">
                        <div style="font-size:32px;">{icon}</div>
                        <h3>{title}</h3>
                        <p>{desc}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("## Produk Unggulan")
    cols = st.columns(3)
    for i, product in enumerate(products[:3]):
        with cols[i]:
            show_product_card(product)

    st.markdown("## Sektor Proyek")
    project_sectors = [
        "Office & Commercial",
        "Banking",
        "Hotel & Hospitality",
        "Healthcare",
        "Industrial & Data Center",
        "Residential",
        "Education & Worship",
        "Shopping Center",
        "Transport Facility"
    ]
    sector_html = "".join(
        [f'<span class="ai-badge" style="margin:6px;">{x}</span>' for x in project_sectors]
    )
    st.markdown(
        f'<div class="ai-card">{sector_html}</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="ai-card">
        <div class="ai-badge">WHY INDO PANEL UTAMA</div>
        <h2>Profesional, Responsif, dan Berorientasi Proyek</h2>
        <p>
            Kami membantu pelanggan menentukan solusi berdasarkan fungsi, kapasitas,
            lokasi pemasangan, dan kebutuhan proyek. Untuk kebutuhan khusus,
            kirimkan spesifikasi Anda dan konsultasikan langsung dengan kami.
        </p>
    </div>
    """, unsafe_allow_html=True)

    general_message = urllib.parse.quote(
        "Halo Indo Panel Utama, saya ingin konsultasi kebutuhan panel listrik untuk proyek saya."
    )
    st.link_button(
        "💬 Request Quotation via WhatsApp",
        f"https://wa.me/{WHATSAPP_NUMBER}?text={general_message}",
        use_container_width=True
    )

# =========================================================
# ABOUT
# =========================================================
elif menu == "About Us":
    st.header("About Indo Panel Utama")
    st.markdown("""
    <div class="ai-card">
        <div class="ai-badge">ABOUT COMPANY</div>
        <h2>Electrical Panel Solutions for Modern Projects</h2>
        <p>
            Indo Panel Utama menyediakan panel listrik untuk berbagai kebutuhan
            industri, komersial, gedung, dan proyek. Kami melayani produk standar
            maupun custom sesuai spesifikasi pelanggan.
        </p>
        <p>
            Fokus kami adalah menghadirkan solusi yang jelas spesifikasinya,
            mudah dikonsultasikan, dan relevan dengan kebutuhan lapangan.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="ai-card"><h3>Quality</h3>'
            '<p>Spesifikasi produk disesuaikan dengan kebutuhan penggunaan.</p></div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            '<div class="ai-card"><h3>Reliability</h3>'
            '<p>Fokus pada solusi panel yang andal dan aplikatif.</p></div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            '<div class="ai-card"><h3>Service</h3>'
            '<p>Konsultasi cepat untuk mendukung kebutuhan proyek.</p></div>',
            unsafe_allow_html=True
        )

# =========================================================
# PRODUCTS
# =========================================================
elif menu == "Products":
    st.header("Products")

    search = st.text_input("Cari produk", placeholder="Contoh: MDP, SDP, ATS")
    categories = sorted(set([p.get("category", "Lainnya") for p in products]))
    selected_category = st.selectbox("Kategori", ["Semua"] + categories)

    filtered = []
    for p in products:
        keyword_ok = (
            search.lower() in p.get("name", "").lower()
            or search.lower() in p.get("spec", "").lower()
            or search.lower() in p.get("description", "").lower()
        )
        category_ok = selected_category == "Semua" or p.get("category") == selected_category
        if keyword_ok and category_ok:
            filtered.append(p)

    if not filtered:
        st.info("Produk tidak ditemukan.")
    else:
        for i in range(0, len(filtered), 3):
            cols = st.columns(3)
            for j, product in enumerate(filtered[i:i+3]):
                with cols[j]:
                    show_product_card(product)

# =========================================================
# PROJECTS
# =========================================================
elif menu == "Projects":
    st.header("Projects")
    st.markdown("""
    <div class="ai-card">
        <div class="ai-badge">PROJECT EXPERIENCE</div>
        <h2>Project Portfolio</h2>
        <p>
            Halaman ini disiapkan untuk menampilkan proyek-proyek Indo Panel Utama.
            Foto, nama proyek, lokasi, jenis panel, dan tahun pengerjaan dapat
            ditambahkan setelah data proyek tersedia.
        </p>
    </div>
    """, unsafe_allow_html=True)

    project_groups = [
        ("🏢", "Office & Commercial"),
        ("🏭", "Industrial & Data Center"),
        ("🏨", "Hotel & Hospitality"),
        ("🏥", "Healthcare"),
        ("🏠", "Residential"),
        ("🏬", "Shopping Center"),
        ("🏫", "Education & Worship"),
        ("✈️", "Transportation Facility")
    ]
    for row_start in range(0, len(project_groups), 2):
        cols = st.columns(2)
        for j, (icon, name) in enumerate(project_groups[row_start:row_start+2]):
            with cols[j]:
                st.markdown(
                    f"""
                    <div class="ai-card">
                        <div style="font-size:32px;">{icon}</div>
                        <h3>{name}</h3>
                        <p>Project portfolio coming soon.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# =========================================================
# PARTNERS & CLIENTS
# =========================================================
elif menu == "Partners & Clients":
    st.header("Partners & Clients")
    st.markdown("""
    <div class="ai-card">
        <div class="ai-badge">TRUSTED NETWORK</div>
        <h2>Partners & Clients</h2>
        <p>
            Area ini dapat digunakan untuk menampilkan logo partner, supplier,
            dan klien yang memang memiliki izin untuk ditampilkan secara publik.
        </p>
    </div>
    """, unsafe_allow_html=True)

    for row_start in range(0, 8, 4):
        cols = st.columns(4)
        for j in range(4):
            with cols[j]:
                st.markdown(
                    '<div class="placeholder" style="padding:35px 10px;">CLIENT LOGO</div>',
                    unsafe_allow_html=True
                )

# =========================================================
# CERTIFICATES
# =========================================================
elif menu == "Certificates":
    st.header("Certificates")
    st.markdown("""
    <div class="ai-card">
        <div class="ai-badge">COMPLIANCE & QUALITY</div>
        <h2>Certificates & Standards</h2>
        <p>
            Sertifikat perusahaan, sertifikat produk, atau standar mutu dapat
            ditampilkan di halaman ini setelah file resmi tersedia.
        </p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for c in cols:
        with c:
            st.markdown(
                '<div class="placeholder">CERTIFICATE</div>',
                unsafe_allow_html=True
            )

# =========================================================
# CONTACT
# =========================================================
elif menu == "Contact Us":
    st.header("Contact Us")
    st.markdown("""
    <div class="ai-card">
        <div class="ai-badge">REQUEST A QUOTATION</div>
        <h2>Let’s Discuss Your Panel Requirement</h2>
        <p>
            Kirim kebutuhan panel, kapasitas, fungsi, lokasi pemasangan,
            dan informasi proyek Anda. Kami akan membantu mengarahkan ke solusi
            yang sesuai.
        </p>
    </div>
    """, unsafe_allow_html=True)

    general_message = urllib.parse.quote(
        "Halo Indo Panel Utama, saya ingin meminta quotation / konsultasi panel listrik."
    )
    st.link_button(
        "💬 WhatsApp Indo Panel Utama",
        f"https://wa.me/{WHATSAPP_NUMBER}?text={general_message}",
        use_container_width=True
    )
    st.write("WhatsApp: **0853-7936-6464**")

# =========================================================
# ADMIN
# =========================================================
elif menu == "Admin Produk":
    st.header("🔐 Admin Produk")

    if not ADMIN_PASSWORD:
        st.error("ADMIN_PASSWORD belum dipasang di Streamlit Secrets.")
        st.stop()

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        password = st.text_input("Password Admin", type="password")
        if st.button("Masuk", type="primary"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Password salah.")
        st.stop()

    col_logout, col_status = st.columns([1,3])
    with col_logout:
        if st.button("Keluar Admin"):
            st.session_state.admin_logged_in = False
            st.rerun()
    with col_status:
        if GITHUB_TOKEN:
            st.success("Penyimpanan GitHub aktif.")
        else:
            st.error("GITHUB_TOKEN belum dipasang.")

    tab_add, tab_edit, tab_delete = st.tabs(
        ["➕ Tambah Produk", "✏️ Edit Produk", "🗑️ Hapus Produk"]
    )

    # ---------------- ADD ----------------
    with tab_add:
        st.subheader("Tambah Produk Baru")
        with st.form("add_product_form"):
            name = st.text_input("Nama Produk *")
            category = st.text_input("Kategori", placeholder="Contoh: MDP")
            price = st.number_input("Harga (Rp)", min_value=0, step=100000)
            stock = st.selectbox("Status Stok", ["Tersedia", "Pre Order", "Habis"])
            spec = st.text_area("Spesifikasi Singkat")
            description = st.text_area("Deskripsi")
            photo = st.file_uploader(
                "Upload Foto",
                type=["jpg", "jpeg", "png", "webp"],
                key="add_photo"
            )
            submitted = st.form_submit_button("Simpan Produk", type="primary")

        if submitted:
            if not name.strip():
                st.error("Nama produk wajib diisi.")
            else:
                product_id = slugify(name)
                if any(p.get("id") == product_id for p in products):
                    product_id += f"-{int(time.time())}"

                image_url = ""
                if photo:
                    with st.spinner("Mengupload foto..."):
                        image_url, msg = upload_product_image(photo, product_id)
                    if not image_url:
                        st.error(msg)
                        st.stop()

                new_product = {
                    "id": product_id,
                    "name": name.strip(),
                    "price": int(price),
                    "stock": stock,
                    "category": category.strip() or "Lainnya",
                    "spec": spec.strip(),
                    "description": description.strip(),
                    "image": image_url or ""
                }

                new_products = products + [new_product]
                with st.spinner("Menyimpan produk..."):
                    ok, msg = save_products(
                        new_products,
                        f"Tambah produk {name}"
                    )
                if ok:
                    st.success("✅ Produk berhasil ditambahkan. Website akan diperbarui otomatis.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)

    # ---------------- EDIT ----------------
    with tab_edit:
        st.subheader("Edit Produk")
        if not products:
            st.info("Belum ada produk.")
        else:
            product_map = {p["name"]: p for p in products}
            selected_name = st.selectbox(
                "Pilih produk",
                list(product_map.keys()),
                key="edit_select"
            )
            selected = product_map[selected_name]

            with st.form("edit_product_form"):
                e_name = st.text_input("Nama Produk", value=selected.get("name", ""))
                e_category = st.text_input("Kategori", value=selected.get("category", ""))
                e_price = st.number_input(
                    "Harga (Rp)",
                    min_value=0,
                    value=int(selected.get("price", 0)),
                    step=100000
                )
                stock_options = ["Tersedia", "Pre Order", "Habis"]
                current_stock = selected.get("stock", "Tersedia")
                stock_index = stock_options.index(current_stock) if current_stock in stock_options else 0
                e_stock = st.selectbox("Status Stok", stock_options, index=stock_index)
                e_spec = st.text_area("Spesifikasi", value=selected.get("spec", ""))
                e_description = st.text_area("Deskripsi", value=selected.get("description", ""))
                e_photo = st.file_uploader(
                    "Ganti Foto (kosongkan jika foto lama tetap dipakai)",
                    type=["jpg", "jpeg", "png", "webp"],
                    key="edit_photo"
                )
                save_edit = st.form_submit_button("Simpan Perubahan", type="primary")

            if save_edit:
                updated = selected.copy()
                updated["name"] = e_name.strip()
                updated["category"] = e_category.strip() or "Lainnya"
                updated["price"] = int(e_price)
                updated["stock"] = e_stock
                updated["spec"] = e_spec.strip()
                updated["description"] = e_description.strip()

                if e_photo:
                    with st.spinner("Mengupload foto baru..."):
                        image_url, msg = upload_product_image(e_photo, selected["id"])
                    if not image_url:
                        st.error(msg)
                        st.stop()
                    updated["image"] = image_url

                new_products = [
                    updated if p.get("id") == selected.get("id") else p
                    for p in products
                ]
                with st.spinner("Menyimpan perubahan..."):
                    ok, msg = save_products(
                        new_products,
                        f"Edit produk {e_name}"
                    )
                if ok:
                    st.success("✅ Produk berhasil diperbarui.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)

    # ---------------- DELETE ----------------
    with tab_delete:
        st.subheader("Hapus Produk")
        if not products:
            st.info("Belum ada produk.")
        else:
            delete_map = {p["name"]: p for p in products}
            d_name = st.selectbox(
                "Pilih produk yang akan dihapus",
                list(delete_map.keys()),
                key="delete_select"
            )
            d_product = delete_map[d_name]

            st.warning(f"Produk **{d_name}** akan dihapus.")
            confirm = st.checkbox("Saya yakin ingin menghapus produk ini")

            if st.button("🗑️ Hapus Produk", disabled=not confirm):
                new_products = [
                    p for p in products
                    if p.get("id") != d_product.get("id")
                ]
                with st.spinner("Menghapus produk..."):
                    ok, msg = save_products(
                        new_products,
                        f"Hapus produk {d_name}"
                    )
                if ok:
                    st.success("✅ Produk berhasil dihapus.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)


# =========================================================
# STAFF ACCESS
# =========================================================
if menu != "Admin Produk":
    st.markdown("---")
    staff_col1, staff_col2 = st.columns([6, 1])
    with staff_col2:
        if st.button("🔐 Staff Login", use_container_width=True):
            st.session_state.page = "Admin Produk"
            st.rerun()
else:
    if st.button("← Kembali ke Website"):
        st.session_state.page = "Home"
        st.session_state.admin_logged_in = False
        st.rerun()

st.markdown(
    '<div class="footer">© 2026 Indo Panel Utama • Electrical Panel Solutions</div>',
    unsafe_allow_html=True
)
