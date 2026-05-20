"""Streamlit arayüzü: Yol Hasar Müdahale Önceliği Sistemi."""
from __future__ import annotations

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src.fuzzy_engine import (
    OUTPUT_SETS,
    calculate_priority,
    get_universe,
    membership_table,
    run_sample_scenarios,
)


st.set_page_config(
    page_title="Yol Hasar Müdahale Önceliği Sistemi",
    page_icon="🛣️",
    layout="wide",
)


st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #586174;
        font-size: 1.02rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        border-radius: 18px;
        padding: 20px 22px;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 18px 50px rgba(15,23,42,0.16);
    }
    .metric-card h3 { margin: 0; color: #cbd5e1; font-size: 0.95rem; }
    .metric-card p { margin: 0.25rem 0 0 0; font-size: 2.25rem; font-weight: 800; }
    .small-note { color: #64748b; font-size: .9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">Yol Hasar Müdahale Önceliği Sistemi</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Mamdani bulanık çıkarım yaklaşımı ile yol hasarlarının onarım önceliğini hesaplayan karar destek arayüzü.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Giriş Değerleri")
    st.caption("Değerleri 0-100 aralığında değiştirerek sistem çıktısını anlık olarak inceleyebilirsiniz.")
    damage = st.slider("Hasar Şiddeti", 0, 100, 75, 1)
    traffic = st.slider("Yol Kullanım Yoğunluğu", 0, 100, 80, 1)
    accident = st.slider("Kaza Riski", 0, 100, 70, 1)
    calculate_clicked = st.button("Hesapla", type="primary", use_container_width=True)

result = calculate_priority(damage, traffic, accident)

score_col, class_col, rule_col = st.columns(3)
with score_col:
    st.markdown(
        f'<div class="metric-card"><h3>Durulaştırılmış Öncelik Skoru</h3><p>{result["score"]}</p></div>',
        unsafe_allow_html=True,
    )
with class_col:
    st.markdown(
        f'<div class="metric-card"><h3>Öncelik Sınıfı</h3><p>{result["class"]}</p></div>',
        unsafe_allow_html=True,
    )
with rule_col:
    st.markdown(
        f'<div class="metric-card"><h3>Aktif Kural Sayısı</h3><p>{len(result["active_rules"])}</p></div>',
        unsafe_allow_html=True,
    )

st.write("")


def plot_membership(variable: str, title: str, current_value: int | None = None):
    universe = get_universe(variable)
    curves = membership_table(variable)
    fig, ax = plt.subplots(figsize=(8, 3.1))
    for label, values in curves.items():
        ax.plot(universe, values, linewidth=2, label=label)
    if current_value is not None:
        ax.axvline(current_value, linestyle="--", linewidth=1.7, label=f"Giriş: {current_value}")
    ax.set_title(title)
    ax.set_xlabel("Değer")
    ax.set_ylabel("Üyelik Derecesi")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right")
    fig.tight_layout()
    return fig


def plot_output(result_dict):
    universe = result_dict["universe"]
    aggregated = result_dict["aggregated"]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    for label, fuzzy_set in OUTPUT_SETS.items():
        ax.plot(universe, fuzzy_set.membership(universe), linewidth=1.6, alpha=0.55, label=label)
    ax.fill_between(universe, aggregated, alpha=0.35, label="Toplulaştırılmış çıktı")
    ax.axvline(float(result_dict["score"]), linestyle="--", linewidth=2, label=f"Centroid: {result_dict['score']}")
    ax.set_title("Durulaştırma Sonucu - Ağırlık Merkezi (Centroid)")
    ax.set_xlabel("Müdahale Önceliği")
    ax.set_ylabel("Üyelik Derecesi")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left")
    fig.tight_layout()
    return fig


tab1, tab2, tab3, tab4 = st.tabs([
    "Sonuç ve Grafikler",
    "Aktif Kurallar",
    "Üyelik Dereceleri",
    "Test Senaryoları",
])

with tab1:
    st.subheader("Üyelik Fonksiyonları ve Çıktı Grafiği")
    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(plot_membership("damage", "Hasar Şiddeti Üyelik Fonksiyonları", damage))
        st.pyplot(plot_membership("traffic", "Yol Kullanım Yoğunluğu Üyelik Fonksiyonları", traffic))
    with c2:
        st.pyplot(plot_membership("accident", "Kaza Riski Üyelik Fonksiyonları", accident))
        st.pyplot(plot_output(result))
    st.info(
        "Sistem, kurallarda AND işlemi için minimum operatörünü, kural çıktılarının birleşimi için maksimum operatörünü ve durulaştırma için centroid yöntemini kullanır."
    )

with tab2:
    st.subheader("Aktif Kural Listesi")
    if result["active_rules"]:
        active_df = pd.DataFrame(
            [
                {
                    "Aktivasyon": round(float(item["activation"]), 3),
                    "Çıktı": item["output"],
                    "Kural": item["label"],
                    "Yorum": item["explanation"],
                }
                for item in result["active_rules"]
            ]
        )
        st.dataframe(active_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Bu giriş değerleri için aktif kural oluşmadı. Giriş aralıklarını kontrol edin.")

    with st.expander("Tüm Kural Tabanını Göster"):
        all_df = pd.DataFrame(
            [
                {
                    "Aktivasyon": round(float(item["activation"]), 3),
                    "Çıktı": item["output"],
                    "Kural": item["label"],
                }
                for item in result["rule_evaluations"]
            ]
        )
        st.dataframe(all_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Bulanıklaştırma Sonuçları")
    membership_rows = []
    variable_names = {
        "damage": "Hasar Şiddeti",
        "traffic": "Yol Kullanım Yoğunluğu",
        "accident": "Kaza Riski",
    }
    for variable, memberships in result["memberships"].items():
        for label, degree in memberships.items():
            membership_rows.append(
                {
                    "Değişken": variable_names[variable],
                    "Dilsel Küme": label,
                    "Üyelik Derecesi": round(float(degree), 3),
                }
            )
    st.dataframe(pd.DataFrame(membership_rows), use_container_width=True, hide_index=True)
    st.caption("Üyelik dereceleri, keskin girişlerin her dilsel kümeye hangi oranda ait olduğunu gösterir.")

with tab4:
    st.subheader("Örnek Test Senaryoları")
    sample_df = pd.DataFrame(run_sample_scenarios())
    st.dataframe(sample_df, use_container_width=True, hide_index=True)
    st.bar_chart(sample_df.set_index("Senaryo")[["Öncelik Skoru"]])
    st.markdown(
        '<p class="small-note">Test senaryoları, sistemin düşük, orta, yüksek ve kritik durumlara verdiği tepkilerin tutarlılığını göstermek için eklenmiştir.</p>',
        unsafe_allow_html=True,
    )
