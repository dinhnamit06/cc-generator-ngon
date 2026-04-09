import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

st.set_page_config(page_title="CC Generator PRO v9.8 - Korea Postal Fixed", page_icon="💳", layout="wide")

fake_us = Faker('en_US')

# ==================== TÊN HÀN ROMANIZED ====================
KOREAN_SURNAMES = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoo", "Shin", "Han", "Lim", "Song", "Jo", "Yoon"]
KOREAN_FIRST_NAMES = ["Seo-jun","Ha-jun","Do-yoon","Min-jun","Ji-ho","Si-woo","Eun-woo","Tae-o","Ye-jun","Seon-woo",
                      "Seo-yun","Seo-ah","Ha-yoon","Ji-an","A-rin","Ha-eun","Ji-woo","Seo-a","Yi-seo","A-yun"]

def generate_korean_name():
    return f"{random.choice(KOREAN_SURNAMES)} {random.choice(KOREAN_FIRST_NAMES)}"

def generate_korean_postal_code():
    # Sinh postal code Seoul (range được chấp nhận cao nhất)
    return f"{random.randint(1000, 8899):05d}"

def generate_korean_address():
    districts = ["Gangnam-gu", "Seocho-gu", "Mapo-gu", "Yongsan-gu", "Songpa-gu", "Jongno-gu"]
    streets = ["Teheran-ro", "Gangnam-daero", "Seolleung-ro", "Yeoksam-ro"]
    num = random.randint(10, 999)
    district = random.choice(districts)
    street = random.choice(streets)
    postal = generate_korean_postal_code()
    return {
        "street": f"{street} {num}",
        "city": f"Seoul, {district}",
        "postal": postal,
        "full": f"{street} {num}, {district}, Seoul, {postal}, South Korea"
    }

# ==================== BIN DATABASE ====================
KOREA_BANKS = {
    "Shinhan Bank": ["451842","457972","426066","457901"],
    "Hana Bank": ["425940","426271","426578"],
    "KB Kookmin Bank": ["532092","553423","554481"],
}

def generate_card(bank_name, custom_bin=None):
    banks_dict = KOREA_BANKS
    prefix = str(custom_bin).strip() if custom_bin else random.choice(banks_dict.get(bank_name, list(banks_dict.values())[0]))

    # LUHN
    ccnumber = list(prefix)
    while len(ccnumber) < 15:
        ccnumber.append(str(random.randint(0, 9)))
    sum_ = 0
    for i, digit in enumerate(reversed(ccnumber)):
        d = int(digit)
        if i % 2 == 0:
            d *= 2
            if d > 9: d -= 9
        sum_ += d
    check_digit = (10 - (sum_ % 10)) % 10
    ccnumber.append(str(check_digit))
    number = ''.join(ccnumber)

    expiry = (datetime.now() + timedelta(days=random.randint(500, 2800))).strftime('%m/%y')
    cvv = str(random.randint(100, 999))
    name = generate_korean_name()
    addr = generate_korean_address()

    return {
        "Cardholder Name": name,
        "Số thẻ": number,
        "Expiry": expiry,
        "CVV": cvv,
        "Street": addr["street"],
        "City": addr["city"],
        "Postal Code": addr["postal"],
        "Billing Address": addr["full"]
    }

# ==================== GIAO DIỆN ====================
st.title("💳 CC Generator PRO v9.8 - Korea Postal Fixed")
st.caption("Postal Code Hàn chỉ sinh trong range Seoul (01000-08899)")

bank_option = st.selectbox("Ngân hàng Hàn", list(KOREA_BANKS.keys()), index=0)
custom_bin = st.text_input("Custom BIN (tùy chọn)", placeholder="451842")

with st.form("generate_form"):
    num_cards = st.number_input("Số lượng thẻ", min_value=1, max_value=100, value=5)
    generate_btn = st.form_submit_button("🚀 GENERATE", type="primary", use_container_width=True)

if generate_btn:
    cards = [generate_card(bank_option, custom_bin) for _ in range(num_cards)]
    df = pd.DataFrame(cards)
    st.success(f"✅ Đã tạo {num_cards} thẻ Hàn")
    st.dataframe(df, use_container_width=True, height=700)

    st.subheader("📋 Copy cho form")
    for idx, card in enumerate(cards):
        with st.expander(f"Thẻ {idx+1} - {card['Cardholder Name']}"):
            st.code(f"""Card information:
{card['Số thẻ']}   {card['Expiry']}   {card['CVV']}

Name on card:
{card['Cardholder Name']}

Billing address:
{card['Street']}
{card['City']} - {card['Postal Code']}
Seoul, South Korea""", language="text")

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Tải CSV", csv, f"korea_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

st.caption("💡 v9.8 - Postal Code Hàn đã được giới hạn trong range Seoul để tránh lỗi 'format is not recognized'")
