import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

st.set_page_config(page_title="CC Generator PRO v9.5 - OpenAI Fixed Korea", page_icon="💳", layout="wide")

fake_us = Faker('en_US')

# ==================== TÊN HÀN ROMANIZED ====================
KOREAN_SURNAMES = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoo", "Shin", "Han", "Lim", "Song", "Jo", "Yoon"]
KOREAN_FIRST_NAMES = ["Seo-jun","Ha-jun","Do-yoon","Min-jun","Ji-ho","Si-woo","Eun-woo","Tae-o","Ye-jun","Seon-woo",
                      "Seo-yun","Seo-ah","Ha-yoon","Ji-an","A-rin","Ha-eun","Ji-woo","Seo-a","Yi-seo","A-yun"]

def generate_korean_name():
    return f"{random.choice(KOREAN_SURNAMES)} {random.choice(KOREAN_FIRST_NAMES)}"

def generate_korean_address():
    cities = ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju", "Ulsan"]
    districts = ["Gangnam-gu", "Seocho-gu", "Jongno-gu", "Mapo-gu", "Yongsan-gu", "Songpa-gu"]
    streets = ["Teheran-ro", "Gangnam-daero", "Seolleung-ro", "Yeoksam-ro", "Samseong-ro"]
    street_num = random.randint(10, 999)
    city = random.choice(cities)
    district = random.choice(districts)
    street = random.choice(streets)
    postal = f"{random.randint(10000, 99999)}"
    return {
        "street": f"{street} {street_num}",
        "city": f"{city}, {district}",
        "postal": postal,
        "billing_address": f"{street} {street_num}, {district}, {city}, {postal}, South Korea"
    }

# ==================== BIN DATABASE ====================
KOREA_BANKS = {
    "All Korea": ["451842","457972","425940","426066","426271","457901","515594","532092","553423"],
    "Shinhan Bank": ["451842","457972","426066","457901"],
    "Hana Bank": ["425940","426271","426578"],
    "KB Kookmin Bank": ["532092","553423","554481"],
    "Hyundai Card": ["515594","531408"],
}

USA_BANKS = {
    "All US": ["414720","414740","403116","406045","411432","400906","474480","549191","6011"],
    "Chase": ["414720","414740","403116","406045","411432"],
    "Bank of America": ["400906","474480","549191"],
    "Capital One": ["414720","434256"],
    "American Express": ["34","37"],
    "Discover": ["6011","644","65"],
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
    else:  # South Korea
        fake = fake_us
        banks_dict = KOREA_BANKS
        length = 16
        addr = generate_korean_address()
        street = addr["street"]
        city = addr["city"]
        state = city.split(",")[0] if "," in city else city
        postal = addr["postal"]
        billing_address = addr["billing_address"]

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
    cvv = str(random.randint(1000, 9999)) if length == 15 else str(random.randint(100, 999))
    brand = "AMEX" if length == 15 else ("VISA" if number[0] == '4' else "MASTERCARD")

    name = fake.name() if country == "United States" else generate_korean_name()
    phone = fake.phone_number()
    email = fake.email()

    return {
        "Country": country,
        "Cardholder Name": name,
        "Ngân hàng": bank_name.replace("All ", ""),
        "Brand": brand,
        "BIN": number[:6],
        "Số thẻ": number,
        "Expiry": expiry,
        "CVV": cvv,
        "Phone": phone,
        "Email": email,
        "Street": street,
        "City": city,
        "State": state,
        "Postal Code": postal,
        "Billing Address": billing_address,
    }

# ==================== GIAO DIỆN ====================
st.title("💳 CC Generator PRO v9.5 - Korea Civilian Address")
st.caption("Đã sinh address dân sự thật cho Hàn Quốc (không còn DPO)")

col1, col2 = st.columns(2)
with col1:
    country = st.selectbox("Quốc gia", ["United States", "South Korea"], index=1, key="country_select")
with col2:
    if country == "United States":
        bank_list = list(USA_BANKS.keys())
    else:
        bank_list = list(KOREA_BANKS.keys())
    bank_option = st.selectbox("Ngân hàng", bank_list, key="bank_select")

custom_bin = st.text_input("Custom BIN (tùy chọn)", placeholder="426066 (Shinhan)")

with st.form("generate_form"):
    num_cards = st.number_input("Số lượng thẻ", min_value=1, max_value=100, value=5)
    include_extra = st.toggle("Thêm Phone & Email", value=True)
    generate_btn = st.form_submit_button("🚀 GENERATE", type="primary", use_container_width=True)

if generate_btn:
    with st.spinner("Đang sinh thẻ..."):
        cards = [generate_card(country, bank_option, custom_bin) for _ in range(num_cards)]
        if not include_extra:
            for c in cards:
                c.pop("Phone", None)
                c.pop("Email", None)

        df = pd.DataFrame(cards)
        st.success(f"✅ Đã tạo {num_cards} thẻ {country}")
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
{card['State']}""", language="text")

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Tải CSV", csv, f"openai_v9.5_{country.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

st.caption("💡 v9.5 - Address Hàn đã là địa chỉ dân sự thật (Seoul, Busan...)")
