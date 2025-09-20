
# Streamlit dashboard kód létrehozása
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Oldal konfiguráció
st.set_page_config(
    page_title="Budapest Lakáspiac Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Címsor és leírás
st.title("🏠 Budapest Lakáspiac Dashboard")
st.markdown("---")

# Adatok betöltése
@st.cache_data
def load_data():
    # Itt a feltöltött CSV fájlt kell beolvasni
    df = pd.read_csv(budapest_lakaspiac_osszefuzve.csv)
    
    # Oszlopnevek tisztítása
    df.columns = df.columns.str.strip()
    
    # Numerikus oszlopok konvertálása
    numeric_cols = ['Családi ház átlagár, ezer Ft/m²', 'Családi ház átlagár darab',
                   'Többlakásos társasház átlagár, ezer Ft/m²', 'Többlakásos társasház darab',
                   'Lakótelepi panel átlagár, ezer Ft/m²', 'Lakótelepi panel darab',
                   'Lakások összesen átlagár, ezer Ft/m²', 'Lakások összesen darab',
                   'Lakások összesen relatív szórás, %', 'Év', 'Kerület']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

# Adatok betöltése
df = load_data()

# Sidebar szűrők
st.sidebar.header("🔍 Szűrők")

# Év szűrő
years = sorted(df['Év'].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Válassz évet:",
    years,
    default=years[-3:] if len(years) >= 3 else years
)

# Kerület szűrő
districts = sorted(df['Kerület'].dropna().unique())
selected_districts = st.sidebar.multiselect(
    "Válassz kerületet:",
    districts,
    default=districts[:5] if len(districts) >= 5 else districts
)

# Adatok szűrése
filtered_df = df[
    (df['Év'].isin(selected_years)) & 
    (df['Kerület'].isin(selected_districts))
]

# Főbb metrikák
st.header("📊 Főbb Mutatók")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_price = filtered_df['Lakások összesen átlagár, ezer Ft/m²'].mean()
    st.metric(
        "Átlagos lakásár",
        f"{avg_price:.0f} eFt/m²" if not pd.isna(avg_price) else "N/A"
    )

with col2:
    total_transactions = filtered_df['Lakások összesen darab'].sum()
    st.metric(
        "Összes tranzakció",
        f"{total_transactions:.0f}" if not pd.isna(total_transactions) else "N/A"
    )

with col3:
    avg_volatility = filtered_df['Lakások összesen relatív szórás, %'].mean()
    st.metric(
        "Átlagos volatilitás",
        f"{avg_volatility:.1f}%" if not pd.isna(avg_volatility) else "N/A"
    )

with col4:
    districts_count = len(selected_districts)
    st.metric(
        "Vizsgált kerületek",
        f"{districts_count}"
    )

st.markdown("---")

# Térképes megjelenítés
st.header("🗺️ Térképes Ábrázolás")

# Kerületek szerint aggregált adatok
district_summary = filtered_df.groupby('Kerület').agg({
    'Lakások összesen átlagár, ezer Ft/m²': 'mean',
    'Lakások összesen darab': 'sum',
    'Lakások összesen relatív szórás, %': 'mean'
}).reset_index()

# Budapest kerületek koordinátái (közelítő értékek)
district_coords = {
    1: (47.4979, 19.0402),   # I. kerület
    2: (47.5138, 19.0267),   # II. kerület
    3: (47.5428, 19.0408),   # III. kerület
    4: (47.5615, 19.0892),   # IV. kerület
    5: (47.4969, 19.0514),   # V. kerület
    6: (47.5030, 19.0651),   # VI. kerület
    7: (47.4969, 19.0651),   # VII. kerület
    8: (47.4875, 19.0651),   # VIII. kerület
    9: (47.4875, 19.0514),   # IX. kerület
    10: (47.4781, 19.0651),  # X. kerület
    11: (47.4781, 19.0402),  # XI. kerület
    12: (47.5030, 19.0267),  # XII. kerület
    13: (47.5138, 19.0651),  # XIII. kerület
    14: (47.5245, 19.1026),  # XIV. kerület
    15: (47.4687, 19.1163),  # XV. kerület
    16: (47.5138, 19.1026),  # XVI. kerület
    17: (47.4781, 19.1300),  # XVII. kerület
    18: (47.4406, 19.1163),  # XVIII. kerület
    19: (47.4312, 19.0892),  # XIX. kerület
    20: (47.4312, 19.1026),  # XX. kerület
    21: (47.4406, 19.1437),  # XXI. kerület
    22: (47.4125, 19.0267),  # XXII. kerület
    23: (47.3937, 19.0651)   # XXIII. kerület
}

# Koordináták hozzáadása
district_summary['lat'] = district_summary['Kerület'].map(lambda x: district_coords.get(x, (47.5, 19.05))[0])
district_summary['lon'] = district_summary['Kerület'].map(lambda x: district_coords.get(x, (47.5, 19.05))[1])

# Térkép létrehozása
if not district_summary.empty:
    fig_map = px.scatter_mapbox(
        district_summary,
        lat='lat',
        lon='lon',
        size='Lakások összesen darab',
        color='Lakások összesen átlagár, ezer Ft/m²',
        hover_name='Kerület',
        hover_data={
            'Lakások összesen átlagár, ezer Ft/m²': ':.0f',
            'Lakások összesen darab': ':.0f',
            'Lakások összesen relatív szórás, %': ':.1f',
            'lat': False,
            'lon': False
        },
        color_continuous_scale='Viridis',
        size_max=30,
        zoom=10,
        mapbox_style='open-street-map',
        title='Lakásárak kerületenként'
    )
    
    fig_map.update_layout(
        height=600,
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Nincs megjeleníthető adat a kiválasztott szűrőkkel.")

st.markdown("---")

# Grafikonok
st.header("📈 Részletes Elemzések")

col1, col2 = st.columns(2)

with col1:
    # Árak alakulása időben
    st.subheader("Árak alakulása időben")
    
    time_series = filtered_df.groupby(['Év', 'Kerület'])['Lakások összesen átlagár, ezer Ft/m²'].mean().reset_index()
    
    if not time_series.empty:
        fig_time = px.line(
            time_series,
            x='Év',
            y='Lakások összesen átlagár, ezer Ft/m²',
            color='Kerület',
            title='Lakásárak változása kerületenként'
        )
        fig_time.update_layout(height=400)
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.warning("Nincs idősor adat.")

with col2:
    # Kerületek összehasonlítása
    st.subheader("Kerületek összehasonlítása")
    
    district_avg = filtered_df.groupby('Kerület')['Lakások összesen átlagár, ezer Ft/m²'].mean().reset_index()
    district_avg = district_avg.sort_values('Lakások összesen átlagár, ezer Ft/m²', ascending=True)
    
    if not district_avg.empty:
        fig_bar = px.bar(
            district_avg,
            x='Lakások összesen átlagár, ezer Ft/m²',
            y='Kerület',
            orientation='h',
            title='Átlagos lakásárak kerületenként'
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Nincs kerületi adat.")

# Lakástípusok összehasonlítása
st.subheader("Lakástípusok összehasonlítása")

property_types = ['Családi ház átlagár, ezer Ft/m²', 
                 'Többlakásos társasház átlagár, ezer Ft/m²', 
                 'Lakótelepi panel átlagár, ezer Ft/m²']

property_data = []
for prop_type in property_types:
    if prop_type in filtered_df.columns:
        avg_price = filtered_df[prop_type].mean()
        if not pd.isna(avg_price):
            property_data.append({
                'Típus': prop_type.replace(' átlagár, ezer Ft/m²', ''),
                'Átlagár': avg_price
            })

if property_data:
    prop_df = pd.DataFrame(property_data)
    fig_prop = px.bar(
        prop_df,
        x='Típus',
        y='Átlagár',
        title='Átlagárak lakástípusonként'
    )
    fig_prop.update_layout(height=400)
    st.plotly_chart(fig_prop, use_container_width=True)

# Volatilitás elemzés
st.subheader("Piaci Volatilitás")

col1, col2 = st.columns(2)

with col1:
    # Volatilitás hisztogram
    volatility_data = filtered_df['Lakások összesen relatív szórás, %'].dropna()
    if not volatility_data.empty:
        fig_hist = px.histogram(
            volatility_data,
            nbins=20,
            title='Volatilitás eloszlása'
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    # Volatilitás vs ár
    scatter_data = filtered_df[['Lakások összesen átlagár, ezer Ft/m²', 
                               'Lakások összesen relatív szórás, %']].dropna()
    if not scatter_data.empty:
        fig_scatter = px.scatter(
            scatter_data,
            x='Lakások összesen átlagár, ezer Ft/m²',
            y='Lakások összesen relatív szórás, %',
            title='Ár vs Volatilitás'
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

# Adattábla
st.header("📋 Részletes Adatok")

# Összesített adatok megjelenítése
summary_table = filtered_df.groupby(['Kerület', 'Év']).agg({
    'Lakások összesen átlagár, ezer Ft/m²': 'mean',
    'Lakások összesen darab': 'sum',
    'Lakások összesen relatív szórás, %': 'mean'
}).round(2).reset_index()

st.dataframe(summary_table, use_container_width=True)

# Letöltési lehetőség
csv = summary_table.to_csv(index=False)
st.download_button(
    label="📥 Adatok letöltése CSV-ben",
    data=csv,
    file_name='budapest_lakaspiac_summary.csv',
    mime='text/csv'
)

# Lábjegyzet
st.markdown("---")
st.markdown("*Dashboard készítve Streamlit segítségével | Adatok: Budapest lakáspiaci adatbázis*")


# Fájl mentése
with open('budapest_lakaspiac_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(dashboard_code)

print("✅ Streamlit dashboard sikeresen létrehozva: budapest_lakaspiac_dashboard.py")
print("\n🚀 Futtatáshoz használd a következő parancsot:")
print("streamlit run budapest_lakaspiac_dashboard.py")
