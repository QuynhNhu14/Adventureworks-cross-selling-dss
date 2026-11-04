import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="AdventureWorks Cross-selling DSS",
    page_icon="🛒",
    layout="wide",
)

CSV_PATH = "association_rules_FPG_20261104_011732.csv"

@st.cache_data
def load_rules(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    numeric_cols = [
        "Support", "Confidence", "Lift",
        "AntecedentSupport", "ConsequentSupport",
        "Leverage", "Conviction",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=[
        "AntecedentProductName",
        "ConsequentProductName",
        "Support",
        "Confidence",
        "Lift",
    ]).copy()

    return df


def business_action(row: pd.Series) -> str:
    if row["Support"] >= 0.02 and row["Confidence"] >= 0.50 and row["Lift"] >= 2:
        return "Ưu tiên combo và duy trì tồn kho đồng bộ"
    if row["Confidence"] >= 0.50 and row["Lift"] >= 2:
        return "Cross-sell có chọn lọc"
    if row["Lift"] >= 1.20:
        return "Theo dõi hoặc thử khuyến mãi nhỏ"
    return "Ưu tiên thấp"


try:
    rules = load_rules(CSV_PATH)
except FileNotFoundError:
    st.error(
        f"Không tìm thấy {CSV_PATH}. Hãy đặt CSV cùng thư mục với app.py."
    )
    st.stop()

rules["BusinessAction"] = rules.apply(business_action, axis=1)

st.title("AdventureWorks Cross-selling DSS")
st.caption(
    "Gợi ý sản phẩm mua kèm từ FP-Growth và hỗ trợ quyết định bán chéo."
)

with st.sidebar:
    st.header("Bộ lọc")

    antecedents = sorted(rules["AntecedentProductName"].unique())
    selected_product = st.selectbox(
        "Sản phẩm khách đang xem",
        antecedents,
        index=antecedents.index("Cable Lock") if "Cable Lock" in antecedents else 0,
    )

    min_support = st.slider(
        "Support tối thiểu",
        min_value=0.0,
        max_value=float(rules["Support"].max()),
        value=min(0.01, float(rules["Support"].max())),
        step=0.001,
        format="%.3f",
    )

    min_confidence = st.slider(
        "Confidence tối thiểu",
        min_value=0.0,
        max_value=1.0,
        value=0.20,
        step=0.05,
        format="%.2f",
    )

    min_lift = st.slider(
        "Lift tối thiểu",
        min_value=1.0,
        max_value=float(rules["Lift"].max()),
        value=1.20,
        step=0.10,
        format="%.2f",
    )

    top_n = st.slider("Số gợi ý", 3, 20, 5)

filtered_all = rules[
    (rules["Support"] >= min_support)
    & (rules["Confidence"] >= min_confidence)
    & (rules["Lift"] >= min_lift)
].copy()

recommendations = filtered_all[
    filtered_all["AntecedentProductName"] == selected_product
].sort_values(
    ["Confidence", "Lift", "Support"],
    ascending=[False, False, False],
).head(top_n)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng số luật", f"{len(rules):,}")
col2.metric("Confidence trung bình", f"{rules['Confidence'].mean():.2%}")
col3.metric("Lift trung bình", f"{rules['Lift'].mean():.2f}")
col4.metric("Lift lớn nhất", f"{rules['Lift'].max():.2f}")

st.divider()

st.subheader(f"Gợi ý mua kèm cho: {selected_product}")

if recommendations.empty:
    st.warning("Không có luật nào đáp ứng các ngưỡng hiện tại.")
else:
    display_df = recommendations[[
        "ConsequentProductName",
        "Support",
        "Confidence",
        "Lift",
        "BusinessAction",
    ]].rename(columns={
        "ConsequentProductName": "Sản phẩm gợi ý",
        "Support": "Support",
        "Confidence": "Confidence",
        "Lift": "Lift",
        "BusinessAction": "Hành động đề xuất",
    })

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Support": st.column_config.NumberColumn(format="%.2%%"),
            "Confidence": st.column_config.NumberColumn(format="%.2%%"),
            "Lift": st.column_config.NumberColumn(format="%.2f"),
        },
    )

    chart_df = recommendations.sort_values("Lift", ascending=True)
    fig_bar = px.bar(
        chart_df,
        x="Lift",
        y="ConsequentProductName",
        orientation="h",
        color="Confidence",
        hover_data=["Support", "Confidence"],
        labels={
            "ConsequentProductName": "Sản phẩm gợi ý",
            "Lift": "Lift",
            "Confidence": "Confidence",
        },
        title="Top sản phẩm mua kèm theo Lift",
    )
    st.plotly_chart(fig_bar, width="stretch")

st.divider()

left, right = st.columns([1.15, 1])

with left:
    st.subheader("Chất lượng các luật")
    fig_scatter = px.scatter(
        filtered_all,
        x="Support",
        y="Confidence",
        size="Lift",
        color="Lift",
        hover_name="AntecedentProductName",
        hover_data=["ConsequentProductName", "Support", "Confidence", "Lift"],
        labels={
            "Support": "Support",
            "Confidence": "Confidence",
            "Lift": "Lift",
        },
    )
    st.plotly_chart(fig_scatter, width="stretch")

with right:
    st.subheader("Cách đọc kết quả")
    st.markdown(
        """
- **Support**: tỷ lệ tổng số giỏ chứa đồng thời hai sản phẩm.
- **Confidence**: trong các giỏ có sản phẩm đầu vào, tỷ lệ cũng có sản phẩm gợi ý.
- **Lift**: mức xuất hiện cùng nhau so với xác suất thông thường của sản phẩm gợi ý.

**Ưu tiên kinh doanh:** xem đồng thời cả ba chỉ số. Không nên chỉ chọn luật có Lift cao nếu Support quá thấp.
        """
    )

st.divider()
st.subheader("Toàn bộ luật sau lọc")

all_display = filtered_all[[
    "AntecedentProductName",
    "ConsequentProductName",
    "Support",
    "Confidence",
    "Lift",
    "BusinessAction",
]].sort_values(
    ["Lift", "Confidence", "Support"],
    ascending=[False, False, False],
).rename(columns={
    "AntecedentProductName": "Sản phẩm đầu vào",
    "ConsequentProductName": "Sản phẩm gợi ý",
    "BusinessAction": "Hành động đề xuất",
})

st.dataframe(
    all_display,
    width="stretch",
    hide_index=True,
    column_config={
        "Support": st.column_config.NumberColumn(format="%.2%%"),
        "Confidence": st.column_config.NumberColumn(format="%.2%%"),
        "Lift": st.column_config.NumberColumn(format="%.2f"),
    },
)

st.caption(
    "Model chính thức: FPG_20261104_011732 | "
    "MIN_SUPPORT=0.01 | MIN_CONFIDENCE=0.20 | MIN_LIFT=1.20 | max_len=2"
)
