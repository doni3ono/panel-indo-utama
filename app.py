
import streamlit as st
import urllib.parse

st.set_page_config(
    page_title="Panel Indo Utama",
    page_icon="⚡",
    layout="wide"
)

# =========================
# KONFIGURASI
# =========================
WHATSAPP_NUMBER = "6285379366464"

# =========================
# DATA PRODUK CONTOH
# Nanti bisa diganti sesuai produk asli
# =========================
products = [
    {
        "name": "Panel MDP 400A",
        "price": 18500000,
        "stock": "Tersedia",
        "spec": "Main Breaker 400A | 380/400V | Indoor",
        "image": "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Panel SDP 250A",
        "price": 12500000,
        "stock": "Tersedia",
        "spec": "Main Breaker 250A | 380/400V | Indoor",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Panel ATS-AMF",
        "price": 22500000,
        "stock": "Pre Order",
        "spec": "Automatic Transfer Switch | AMF | Custom Capacity",
        "image": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=900&q=80",
    },
]

# =========================
# FUNGSI
# =========================
def rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")

def whatsapp_link(product):
    message = (
        f"Halo Panel Indo Utama, saya tertarik dengan produk:\n\n"
        f"{product['name']}\n"
        f"Harga: {rupiah(product['price'])}\n"
        f"Spesifikasi: {product['spec']}\n\n"
        f"Mohon informasi lebih lanjut."
    )
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}"

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.hero {
    padding: 32px;
    border-radius: 18px;
    background: linear-gradient(135deg, #0d47a1, #1976d2);
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    margin-bottom: 5px;
}
.product-card {
    padding: 18px;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    background: white;
    margin-bottom: 18px;
}
.price {
    font-size: 24px;
    font-weight: 700;
    color: #0d47a1;
}
.stock {
    font-weight: 600;
}
.footer {
    text-align: center;
    color: #777;
    margin-top: 40px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="hero">
    <h1>⚡ Panel Indo Utama</h1>
    <h3>Solusi Panel Listrik untuk Industri, Gedung, dan Usaha Anda</h3>
    <p>Katalog panel listrik berkualitas dengan pemesanan mudah melalui WhatsApp.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# MENU
# =========================
menu = st.sidebar.radio(
    "Menu",
    ["Beranda", "Katalog Produk", "Tentang Kami", "Kontak"]
)

# =========================
# BERANDA
# =========================
if menu == "Beranda":
    st.header("Selamat Datang di Panel Indo Utama")
    st.write(
        "Kami menyediakan berbagai kebutuhan panel listrik untuk industri, "
        "gedung, fasilitas komersial, dan kebutuhan proyek."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Produk", len(products))
    col2.metric("Pemesanan", "WhatsApp")
    col3.metric("Layanan", "Custom Panel")

    st.subheader("Produk Pilihan")

    cols = st.columns(3)
    for i, product in enumerate(products[:3]):
        with cols[i]:
            st.image(product["image"], use_container_width=True)
            st.subheader(product["name"])
            st.markdown(f'<div class="price">{rupiah(product["price"])}</div>', unsafe_allow_html=True)
            st.write(product["spec"])
            st.write(f"Stok: **{product['stock']}**")
            st.link_button("💬 Pesan via WhatsApp", whatsapp_link(product), use_container_width=True)

# =========================
# KATALOG
# =========================
elif menu == "Katalog Produk":
    st.header("Katalog Produk")

    search = st.text_input("Cari produk", placeholder="Contoh: MDP, SDP, ATS")

    filtered = [
        p for p in products
        if search.lower() in p["name"].lower()
        or search.lower() in p["spec"].lower()
    ]

    if not filtered:
        st.warning("Produk tidak ditemukan.")

    for product in filtered:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(product["image"], use_container_width=True)

        with col2:
            st.subheader(product["name"])
            st.markdown(f'<div class="price">{rupiah(product["price"])}</div>', unsafe_allow_html=True)
            st.write(product["spec"])
            st.write(f"Status stok: **{product['stock']}**")
            st.link_button(
                "💬 Pesan via WhatsApp",
                whatsapp_link(product),
                use_container_width=True
            )

        st.divider()

# =========================
# TENTANG KAMI
# =========================
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

# =========================
# KONTAK
# =========================
elif menu == "Kontak":
    st.header("Hubungi Kami")
    st.write("Untuk pemesanan dan konsultasi produk, silakan hubungi kami.")

    general_message = urllib.parse.quote(
        "Halo Panel Indo Utama, saya ingin bertanya mengenai produk panel listrik."
    )

    st.link_button(
        "💬 WhatsApp Panel Indo Utama",
        f"https://wa.me/{WHATSAPP_NUMBER}?text={general_message}",
        use_container_width=True
    )

    st.write("WhatsApp: **0853-7936-6464**")

st.markdown(
    '<div class="footer">© 2026 Panel Indo Utama</div>',
    unsafe_allow_html=True
)
