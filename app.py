
import streamlit as st
import requests
import base64
import json
import urllib.parse
import time

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
        f"Halo Panel Indo Utama, saya tertarik dengan produk:\n\n"
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

def save_products(products, commit_message="Update produk Panel Indo Utama"):
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
.hero {
    padding: 34px;
    border-radius: 18px;
    background: linear-gradient(135deg, #0d47a1, #1976d2);
    color: white;
    margin-bottom: 25px;
}
.hero h1 { margin-bottom: 4px; }
.price {
    font-size: 25px;
    font-weight: 800;
    color: #0d47a1;
    margin-bottom: 5px;
}
.card {
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 14px;
    min-height: 100%;
}
.placeholder {
    background: #f3f4f6;
    border-radius: 12px;
    padding: 60px 10px;
    text-align: center;
    color: #6b7280;
}
.footer {
    text-align:center;
    color:#777;
    padding:25px 0;
    margin-top:30px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
products = load_products()

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <h1>⚡ Panel Indo Utama</h1>
    <h3>Solusi Panel Listrik untuk Industri, Gedung, dan Usaha Anda</h3>
    <p>Katalog panel listrik dengan pemesanan mudah melalui WhatsApp.</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# MENU
# =========================================================
menu = st.sidebar.radio(
    "Menu",
    ["Beranda", "Katalog Produk", "Tentang Kami", "Kontak", "Admin Produk"]
)

# =========================================================
# FUNGSI TAMPIL PRODUK
# =========================================================
def show_product_card(product):
    if product.get("image"):
        st.image(product["image"], use_container_width=True)
    else:
        st.markdown('<div class="placeholder">📷 Foto produk belum ditambahkan</div>', unsafe_allow_html=True)

    st.subheader(product["name"])
    st.markdown(f'<div class="price">{rupiah(product["price"])}</div>', unsafe_allow_html=True)
    st.caption(f"{product.get('category','Panel')} • {product.get('stock','')}")
    st.write(product.get("spec", ""))
    if product.get("description"):
        st.write(product["description"])
    st.link_button("💬 Pesan via WhatsApp", whatsapp_link(product), use_container_width=True)

# =========================================================
# BERANDA
# =========================================================
if menu == "Beranda":
    st.header("Selamat Datang di Panel Indo Utama")
    st.write(
        "Kami menyediakan berbagai kebutuhan panel listrik untuk industri, "
        "gedung, fasilitas komersial, dan proyek."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Produk", len(products))
    c2.metric("Pemesanan", "WhatsApp")
    c3.metric("Layanan", "Custom Panel")

    st.subheader("Produk Pilihan")
    cols = st.columns(3)
    for i, product in enumerate(products[:3]):
        with cols[i]:
            show_product_card(product)

# =========================================================
# KATALOG
# =========================================================
elif menu == "Katalog Produk":
    st.header("Katalog Produk")

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
# TENTANG
# =========================================================
elif menu == "Tentang Kami":
    st.header("Tentang Panel Indo Utama")
    st.write(
        "Panel Indo Utama menyediakan panel listrik untuk berbagai kebutuhan "
        "industri, komersial, gedung, dan proyek."
    )
    st.write(
        "Kami melayani kebutuhan panel standar maupun panel yang dibuat "
        "berdasarkan spesifikasi pelanggan."
    )

# =========================================================
# KONTAK
# =========================================================
elif menu == "Kontak":
    st.header("Hubungi Kami")
    general_message = urllib.parse.quote(
        "Halo Panel Indo Utama, saya ingin bertanya mengenai produk panel listrik."
    )
    st.link_button(
        "💬 WhatsApp Panel Indo Utama",
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

st.markdown(
    '<div class="footer">© 2026 Panel Indo Utama</div>',
    unsafe_allow_html=True
)
