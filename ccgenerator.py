import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

st.set_page_config(page_title="CC Generator PRO v8.6 - OpenAI Ready", page_icon="💳", layout="wide")

fake_kr = Faker('ko_KR')
fake_us = Faker('en_US')

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
    else:
        fake = fake_kr
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
    cvv = str(random.randint(1000, 9999)) if length == 15 else str(random.randint(100, 999))
    brand = "AMEX" if length == 15 else ("VISA" if number[0] == '4' else "MASTERCARD")

    name = fake.name()
    phone = fake.phone_number()
    email = fake.email()

    if country == "United States":
        street = fake.street_address()
        city = fake.city()
        state = fake.state_abbr()
        zip_code = fake.zipcode()
        billing_address = f"{street}, {city}, {state} {zip_code}, USA"
    else:
        street = "N/A"
        city = "N/A"
        state = "N/A"
        zip_code = "N/A"
        billing_address = fake.address()

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
        "ZIP Code": zip_code,
        "Billing Address": billing_address,
    }

# ==================== GIAO DIỆN ====================
st.title("💳 CC Generator PRO v8.6 - OpenAI Payment Ready")
st.caption("Đầy đủ Street, City, State, ZIP + Hướng dẫn copy cho OpenAI")

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
    num_cards = st.number_input("Số lượng thẻ", min_value=1, max_value=300, value=20)
    include_extra = st.toggle("Thêm Phone & Email", value=True)
    generate_btn = st.form_submit_button("🚀 GENERATE FOR OPENAI", type="primary", use_container_width=True)

if generate_btn:
    with st.spinner("Đang sinh thẻ..."):
        cards = []
        for _ in range(num_cards):
            card = generate_card(country, bank_option, custom_bin)
            if not include_extra:
                card.pop("Phone", None)
                card.pop("Email", None)
            cards.append(card)

        df = pd.DataFrame(cards)
        st.success(f"✅ Đã tạo {num_cards} thẻ {country} - Sẵn sàng điền vào OpenAI")

        st.dataframe(df, use_container_width=True, height=700)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Tải CSV", csv, f"openai_{country.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

        st.subheader("📋 Hướng dẫn điền form OpenAI (Copy từng cột)")
        st.info("""
        **Name on card**          → Cardholder Name  
        **Card number**           → Số thẻ  
        **Expiry**                → Expiry  
        **CVV**                   → CVV  
        **Street / Line 1**       → Street  
        **City**                  → City  
        **State**                 → State (chỉ US)  
        **ZIP / Postal Code**     → ZIP Code  
        **Country**               → Country  
        **Purchasing as a business** → Để trống (không tick)
        """)

st.caption("💡 v8.6 - Đã tách đầy đủ Street, City, State, ZIP theo yêu cầu của Stripe/OpenAI 2026")
