import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

st.set_page_config(page_title="CC Generator PRO v9.7 - Fixed ZIP Code", page_icon="💳", layout="wide")

fake_us = Faker('en_US')
fake_kr = Faker('ko_KR')

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

# ==================== BIN DATABASE ====================
KOREA_BANKS = {
    "Shinhan Bank": ["451842","457972","426066","457901"],
    "Hana Bank": ["425940","426271","426578"],
    "KB Kookmin Bank": ["532092","553423","554481"],
}

USA_BANKS = {
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

        # Sinh address Mỹ đúng cách (Faker sinh full address rồi parse để khớp)
        full_addr = fake.address()
        # Faker address thường có format: "Street, City, State ZIP"
        parts = full_addr.split(', ')
        street = parts[0]
        city_state_zip = parts[1].split(' ')
        city = city_state_zip[0]
        state = city_state_zip[1] if len(city_state_zip) > 2 else city_state_zip[-2]
        postal = city_state_zip[-1]

        billing_address = f"{street}, {city}, {state} {postal}, USA"

    else:  # South Korea
        fake = fake_kr
        banks_dict = KOREA_BANKS
        length = 16
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

    expiry = (datetime.now() + timedelta(days=random.randint(500, 2800))).strftime('%m/%y')
    cvv = str(random.randint(100, 999))
    brand = "AMEX" if length == 15 else ("VISA" if number[0] == '4' else "MASTERCARD")

    name = fake.name() if country == "United States" else generate_korean_name()

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
st.title("💳 CC Generator PRO v9.7 - Fixed ZIP Code US")
st.caption("Đã fix ZIP Code khớp với City + State (Mỹ)")

col1, col2 = st.columns(2)
with col1:
    country = st.selectbox("Quốc gia", ["United States", "South Korea"], index=0, key="country_select")
with col2:
    if country == "United States":
        bank_list = list(USA_BANKS.keys())
    else:
        bank_list = list(KOREA_BANKS.keys())
    bank_option = st.selectbox("Ngân hàng", bank_list, key="bank_select")

custom_bin = st.text_input("Custom BIN (tùy chọn)", placeholder="414720 (Chase)")

with st.form("generate_form"):
    num_cards = st.number_input("Số lượng thẻ", min_value=1, max_value=100, value=10)
    include_extra = st.toggle("Thêm Phone & Email", value=True)
    generate_btn = st.form_submit_button("🚀 GENERATE", type="primary", use_container_width=True)

if generate_btn:
    cards = [generate_card(country, bank_option, custom_bin) for _ in range(num_cards)]
    if not include_extra:
        for c in cards:
            c.pop("Phone", None)
            c.pop("Email", None)

    df = pd.DataFrame(cards)
    st.success(f"✅ Đã tạo {num_cards} thẻ {country}")
    st.dataframe(df, use_container_width=True, height=700)

    st.subheader("📋 Copy cho OpenAI / Google Cloud / Talkpal")
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
    st.download_button("💾 Tải CSV", csv, f"cards_{country.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

st.caption("💡 v9.7 - Đã fix ZIP Code khớp với City + State cho Mỹ")
