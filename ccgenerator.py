import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

st.set_page_config(page_title="CC Generator PRO v8.3 - BIN Validation", page_icon="💳", layout="wide")

fake_kr = Faker('ko_KR')
fake_us = Faker('en_US')

# ==================== BIN HIGH TRUST 2026 ====================
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

def is_valid_bin(bin_input: str, country: str) -> tuple:
    if not bin_input:
        return True, ""
    bin_str = bin_input.strip()
    if not bin_str.isdigit():
        return False, "❌ BIN chỉ được chứa chữ số (0-9)"
    if len(bin_str) < 4 or len(bin_str) > 8:
        return False, "❌ Độ dài BIN phải từ 4 đến 8 chữ số"
    
    banks_dict = USA_BANKS if country == "United States" else KOREA_BANKS
    all_bins = [b for bins in banks_dict.values() for b in bins]
    
    if not any(bin_str.startswith(b) for b in all_bins):
        return False, f"⚠️ BIN '{bin_str}' không phổ biến cho {country}. Vẫn có thể dùng được."
    return True, "✅ BIN hợp lệ và được hỗ trợ"

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
        address = f"{street}, {city}, {state} {zip_code}, USA"
    else:
        address = fake.address()

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
        "Billing Address": address,
    }

# ==================== GIAO DIỆN ====================
st.title("💳 CC Generator PRO v8.3 - BIN Validation")
st.caption("Đã fix lỗi 'cards' not defined + BIN Validation")

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

# BIN Validation
if custom_bin:
    is_valid, msg = is_valid_bin(custom_bin, country)
    if is_valid:
        st.success(msg)
    else:
        st.warning(msg)

with st.form("generate_form"):
    num_cards = st.number_input("Số lượng thẻ", min_value=1, max_value=500, value=30)
    include_extra = st.toggle("Thêm Phone, Email, Full Address", value=True)
    generate_btn = st.form_submit_button("🚀 GENERATE HIGH TRUST", type="primary", use_container_width=True)

# Biến cards được khởi tạo trước
cards = []

if generate_btn:
    with st.spinner("Đang sinh thẻ high trust..."):
        cards = []
        for _ in range(num_cards):
            card = generate_card(country, bank_option, custom_bin)
            if not include_extra:
                card.pop("Phone", None)
                card.pop("Email", None)
            cards.append(card)

        df = pd.DataFrame(cards)
        st.success(f"✅ Đã tạo {num_cards} thẻ {country}")
        st.dataframe(df, use_container_width=True, height=600)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Tải CSV", csv, f"high_trust_{country.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

# History
if 'history' not in st.session_state:
    st.session_state.history = []

if cards:                                   # ← Đã fix lỗi ở đây
    st.session_state.history.extend(cards)

if st.session_state.history:
    with st.expander("📜 Lịch sử các lần generate"):
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

st.caption("💡 v8.3 - Đã sửa lỗi NameError + BIN Validation + Realtime Bank Selection")
