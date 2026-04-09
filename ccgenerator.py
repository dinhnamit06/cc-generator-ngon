import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

st.set_page_config(page_title="CC Generator PRO v9.8 - Expiry Fixed", page_icon="💳", layout="wide")

fake_us = Faker('en_US')

# ==================== TÊN HÀN ROMANIZED ====================
KOREAN_SURNAMES = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoo", "Shin", "Han", "Lim", "Song", "Jo", "Yoon"]
KOREAN_FIRST_NAMES = ["Seo-jun","Ha-jun","Do-yoon","Min-jun","Ji-ho","Si-woo","Eun-woo","Tae-o","Ye-jun","Seon-woo",
                      "Seo-yun","Seo-ah","Ha-yoon","Ji-an","A-rin","Ha-eun","Ji-woo","Seo-a","Yi-seo","A-yun"]

def generate_korean_name():
    return f"{random.choice(KOREAN_SURNAMES)} {random.choice(KOREAN_FIRST_NAMES)}"

def generate_korean_address():
    districts = ["Gangnam-gu", "Seocho-gu", "Mapo-gu", "Yongsan-gu", "Songpa-gu"]
    streets = ["Teheran-ro", "Gangnam-daero", "Seolleung-ro", "Yeoksam-ro"]
    num = random.randint(10, 999)
    district = random.choice(districts)
    street = random.choice(streets)
    postal = f"{random.randint(10000, 99999)}"
    return {
        "street": f"{street} {num}",
        "city": f"Seoul, {district}",
        "postal": postal,
        "full": f"{street} {num}, {district}, Seoul, {postal}, South Korea"
    }

# ==================== BIN ====================
KOREA_BANKS = {
    "Shinhan Bank": ["451842","457972","426066","457901"],
    "Hana Bank": ["425940","426271","426578"],
}

USA_BANKS = {
    "Chase": ["414720","414740","403116","406045","411432"],
    "Bank of America": ["400906","474480","549191"],
    "Capital One": ["414720","434256"],
}

def generate_card(country, bank_name, custom_bin=None):
    if country == "United States":
        fake = fake_us
        banks_dict = USA_BANKS
        is_amex = bank_name == "American Express" or (custom_bin and str(custom_bin).startswith(('34','37')))
        length = 15 if is_amex else 16
        street = fake.street_address()
        city = fake.city()
        state = fake.state_abbr()
        postal = fake.zipcode()
        billing_address = f"{street}, {city}, {state} {postal}, USA"
        name = fake.name()
    else:
        fake = fake_us
        banks_dict = KOREA_BANKS
        length = 16
        name = generate_korean_name()
        addr = generate_korean_address()
        street = addr["street"]
        city = addr["city"]
        state = "Seoul"
        postal = addr["postal"]
        billing_address = addr["full"]

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

    # Expiry được giảm xuống mức thực tế (2-6 năm)
    expiry = (datetime.now() + timedelta(days=random.randint(730, 2190))).strftime('%m/%y')

    cvv = str(random.randint(100, 999))
    brand = "AMEX" if length == 15 else ("VISA" if number[0] == '4' else "MASTERCARD")

    return {
        "Country": country,
        "Cardholder Name": name,
        "Ngân hàng": bank_name.replace("All ", ""),
        "Brand": brand,
        "BIN": number[:6],
        "Số thẻ": number,
        "Expiry": expiry,
        "CVV": cvv,
        "Street": street,
        "City": city,
        "State": state,
        "Postal Code": postal,
        "Billing Address": billing_address,
    }

# ==================== GIAO DIỆN ====================
st.title("💳 CC Generator PRO v9.7 - Expiry Fixed")
st.caption("Expiry đã rút ngắn xuống 2-6 năm (thực tế hơn)")

col1, col2 = st.columns(2)
with col1:
    country = st.selectbox("Quốc gia", ["United States", "South Korea"], index=0)
with col2:
    if country == "United States":
        bank_list = list(USA_BANKS.keys())
    else:
        bank_list = list(KOREA_BANKS.keys())
    bank_option = st.selectbox("Ngân hàng", bank_list)

custom_bin = st.text_input("Custom BIN (tùy chọn)", "")

with st.form("generate_form"):
    num_cards = st.number_input("Số lượng thẻ", 1, 100, 5)
    generate_btn = st.form_submit_button("🚀 GENERATE", type="primary", use_container_width=True)

if generate_btn:
    cards = [generate_card(country, bank_option, custom_bin) for _ in range(num_cards)]
    df = pd.DataFrame(cards)
    st.success(f"✅ Đã tạo {num_cards} thẻ")
    st.dataframe(df, use_container_width=True)

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
{card['State']}""", language="text")

st.caption("💡 v9.7 - Expiry đã được rút ngắn để tránh lỗi 'Số thẻ không chính xác'")
