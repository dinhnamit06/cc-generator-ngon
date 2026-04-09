import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

st.set_page_config(page_title="CC Generator PRO v9.5 - Korea Optimized", page_icon="💳", layout="wide")

fake_us = Faker('en_US')

# ==================== TÊN HÀN ROMANIZED HOT ====================
KOREAN_SURNAMES = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoo", "Shin", "Han", "Lim", "Song", "Jo", "Yoon"]
KOREAN_FIRST_NAMES = ["Seo-jun","Ha-jun","Do-yoon","Min-jun","Ji-ho","Si-woo","Eun-woo","Tae-o","Ye-jun","Seon-woo",
                      "Seo-yun","Seo-ah","Ha-yoon","Ji-an","A-rin","Ha-eun","Ji-woo","Seo-a","Yi-seo","A-yun"]

def generate_korean_name():
    return f"{random.choice(KOREAN_SURNAMES)} {random.choice(KOREAN_FIRST_NAMES)}"

def generate_korean_address():
    districts = ["Gangnam-gu", "Seocho-gu", "Jongno-gu", "Mapo-gu", "Yongsan-gu", "Songpa-gu", "Seongbuk-gu"]
    streets = ["Teheran-ro", "Gangnam-daero", "Seolleung-ro", "Yeoksam-ro", "Samseong-ro", "Hannam-daero"]
    street_num = random.randint(10, 999)
    district = random.choice(districts)
    street = random.choice(streets)
    postal = f"{random.randint(10000, 99999)}"
    full_address = f"{street} {street_num}, {district}, Seoul, {postal}, South Korea"
    return {
        "street": f"{street} {street_num}",
        "city": f"Seoul, {district}",
        "postal": postal,
        "billing_address": full_address
    }

# ==================== BIN DATABASE (Ưu tiên Hàn) ====================
KOREA_BANKS = {
    "All Korea": ["451842","457972","425940","426066","426271","457901","515594","532092","553423"],
    "Shinhan Bank": ["451842","457972","426066","457901"],      # BIN tốt nhất cho Hàn
    "Hana Bank": ["425940","426271","426578"],
    "KB Kookmin Bank": ["532092","553423","554481"],
    "Hyundai Card": ["515594","531408"],
}

def generate_card(bank_name, custom_bin=None):
    fake = fake_us
    banks_dict = KOREA_BANKS
    length = 16

    prefix = str(custom_bin).strip() if custom_bin else random.choice(banks_dict.get(bank_name, list(banks_dict.values())[0]))

    # LUHN
    ccnumber = list(prefix)
    while len(ccnumber) < length - 1:
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
    brand = "VISA" if number[0] == '4' else "MASTERCARD"

    name = generate_korean_name()
    phone = fake.phone_number()
    email = fake.email()

    addr = generate_korean_address()

    return {
        "Cardholder Name": name,
        "Ngân hàng": bank_name.replace("All ", ""),
        "Brand": brand,
        "BIN": number[:6],
        "Số thẻ": number,
        "Expiry": expiry,
        "CVV": cvv,
        "Street": addr["street"],
        "City": addr["city"],
        "Postal Code": addr["postal"],
        "Billing Address": addr["billing_address"],
    }

# ==================== GIAO DIỆN ====================
st.title("💳 CC Generator PRO v9.5 - Korea Max Optimized")
st.caption("Address Hàn dân sự thật + Postal Code 5 số + Format OpenAI")

col1, col2 = st.columns(2)
with col1:
    bank_option = st.selectbox("Ngân hàng Hàn", list(KOREA_BANKS.keys()), index=0, key="bank_select")
custom_bin = st.text_input("Custom BIN (tùy chọn - để trống để random)", placeholder="451842 (Shinhan)")

with st.form("generate_form"):
    num_cards = st.number_input("Số lượng thẻ", min_value=1, max_value=100, value=5)
    generate_btn = st.form_submit_button("🚀 GENERATE THẺ HÀN", type="primary", use_container_width=True)

if generate_btn:
    with st.spinner("Đang sinh thẻ Hàn..."):
        cards = [generate_card(bank_option, custom_bin) for _ in range(num_cards)]

        df = pd.DataFrame(cards)
        st.success(f"✅ Đã tạo {num_cards} thẻ Hàn Quốc")
        st.dataframe(df, use_container_width=True, height=700)

        st.subheader("📋 Copy theo đúng form OpenAI")
        for idx, card in enumerate(cards):
            with st.expander(f"Thẻ {idx+1} - {card['Cardholder Name']}"):
                st.code(f"""Card information:
{card['Số thẻ']}   {card['Expiry']}   {card['CVV']}

Name on card:
{card['Cardholder Name']}

Billing address:
{card['Street']}
{card['City']} - {card['Postal Code']}
Seoul""", language="text")

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Tải CSV", csv, f"korea_cards_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

st.caption("💡 v9.5 - Address Hàn dân sự thật + Postal Code chuẩn 5 số")
