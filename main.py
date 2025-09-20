import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import folium
from streamlit_folium import st_folium

# Oldal konfiguráció
st.set_page_config(
    page_title="Budapest Lakáspiac Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Adatok betöltése
@st.cache_data
def load_data():
    df = pd.read_csv('budapest_lakaspiac_osszefuzve.csv')
    return df

# Főcím
st.title("🏠 Budapest Lakáspiac Elemzés Dashboard")
st.markdown("---")

# Adatok betöltése
try:
    df = load_data()
    
    # Sidebar szűrők
    st.sidebar.header("Szűrők")
    
    # Év szűrő
    years = sorted(df['Év'].unique())
    selected_year = st.sidebar.selectbox("Válassz évet:", years, index=len(years)-1)
    
    # Kerület szűrő
    districts = sorted(df['Kerület'].unique())
    selected_districts = st.sidebar.multiselect("Válassz kerületeket:", districts, default=districts[:5])
    
    # Ingatlan típus szűrő
    property_types = ['Családi ház', 'Többlakásos társasház', 'Lakótelepi panel', 'Lakások összesen']
    selected_property_type = st.sidebar.selectbox("Ingatlan típus:", property_types, index=3)
    
    # Adatok szűrése
    filtered_df = df[
        (df['Év'] == selected_year) & 
        (df['Kerület'].isin(selected_districts))
    ].copy()
    
    # Ár oszlop kiválasztása
    price_column = f"{selected_property_type} átlagár, ezer Ft/m²"
    count_column = f"{selected_property_type} darab"
    
    # Főbb metrikák
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_price = filtered_df[price_column].mean()
        st.metric("Átlagár", f"{avg_price:.0f} eFt/m²" if not np.isnan(avg_price) else "N/A")
    
    with col2:
        max_price = filtered_df[price_column].max()
        st.metric("Legmagasabb ár", f"{max_price:.0f} eFt/m²" if not np.isnan(max_price) else "N/A")
    
    with col3:
        min_price = filtered_df[price_column].min()
        st.metric("Legalacsonyabb ár", f"{min_price:.0f} eFt/m²" if not np.isnan(min_price) else "N/A")
    
    with col4:
        total_properties = filtered_df[count_column].sum()
        st.metric("Összes ingatlan", f"{total_properties:.0f}" if not np.isnan(total_properties) else "N/A")
    
    # Tabs létrehozása
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Áttekintés", "📈 Trendek", "🗺️ Kerületek", "🏘️ Utcák"])
    
    with tab1:
        st.header("Áttekintés")
        
        # Kerületek szerinti árak
        district_data = filtered_df.groupby('Kerület')[price_column].mean().reset_index()
        district_data = district_data.dropna()
        
        if not district_data.empty:
            fig_bar = px.bar(
                district_data, 
                x='Kerület', 
                y=price_column,
                title=f"{selected_property_type} átlagárak kerületenként ({selected_year})",
                labels={price_column: 'Átlagár (eFt/m²)', 'Kerület': 'Kerület'}
            )
            fig_bar.update_layout(height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Top 10 legdrágább utca
        top_streets = filtered_df.nlargest(10, price_column)[['Az ingatlan helye', price_column, 'Kerület']]
        top_streets = top_streets.dropna()
        
        if not top_streets.empty:
            st.subheader("Top 10 legdrágább utca")
            st.dataframe(top_streets, use_container_width=True)
    
    with tab2:
        st.header("Időbeli trendek")
        
        # Évenkénti átlagárak
        yearly_trends = df.groupby('Év')[price_column].mean().reset_index()
        yearly_trends = yearly_trends.dropna()
        
        if not yearly_trends.empty:
            fig_line = px.line(
                yearly_trends, 
                x='Év', 
                y=price_column,
                title=f"{selected_property_type} átlagár alakulása",
                labels={price_column: 'Átlagár (eFt/m²)', 'Év': 'Év'}
            )
            fig_line.update_layout(height=500)
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Kerületenkénti trendek
        if len(selected_districts) > 1:
            district_trends = df[df['Kerület'].isin(selected_districts)].groupby(['Év', 'Kerület'])[price_column].mean().reset_index()
            district_trends = district_trends.dropna()
            
            if not district_trends.empty:
                fig_multi_line = px.line(
                    district_trends, 
                    x='Év', 
                    y=price_column,
                    color='Kerület',
                    title=f"{selected_property_type} átlagár alakulása kerületenként",
                    labels={price_column: 'Átlagár (eFt/m²)', 'Év': 'Év'}
                )
                fig_multi_line.update_layout(height=500)
                st.plotly_chart(fig_multi_line, use_container_width=True)
    
    with tab3:
        st.header("Kerületek elemzése")
        
        # Kerületek összehasonlítása
        district_comparison = df[df['Év'] == selected_year].groupby('Kerület').agg({
            price_column: 'mean',
            count_column: 'sum'
        }).reset_index()
        district_comparison = district_comparison.dropna()
        
        if not district_comparison.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_scatter = px.scatter(
                    district_comparison,
                    x=count_column,
                    y=price_column,
                    size=count_column,
                    hover_data=['Kerület'],
                    title="Ár vs. Mennyiség kerületenként",
                    labels={price_column: 'Átlagár (eFt/m²)', count_column: 'Ingatlanok száma'}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                fig_pie = px.pie(
                    district_comparison,
                    values=count_column,
                    names='Kerület',
                    title="Ingatlanok megoszlása kerületenként"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab4:
        st.header("Utcák elemzése")
        
        # Utcák listája a kiválasztott kerületekben
        street_data = filtered_df[['Az ingatlan helye', price_column, count_column, 'Kerület']].copy()
        street_data = street_data.dropna()
        
        if not street_data.empty:
            # Keresés az utcák között
            search_term = st.text_input("Keresés utca neve alapján:")
            
            if search_term:
                street_data = street_data[street_data['Az ingatlan helye'].str.contains(search_term, case=False, na=False)]
            
            # Rendezési opciók
            sort_option = st.selectbox("Rendezés:", ["Ár szerint (csökkenő)", "Ár szerint (növekvő)", "Név szerint"])
            
            if sort_option == "Ár szerint (csökkenő)":
                street_data = street_data.sort_values(price_column, ascending=False)
            elif sort_option == "Ár szerint (növekvő)":
                street_data = street_data.sort_values(price_column, ascending=True)
            else:
                street_data = street_data.sort_values('Az ingatlan helye')
            
            st.dataframe(street_data, use_container_width=True)
            
            # Statisztikák
            st.subheader("Statisztikák")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Utcák száma", len(street_data))
            with col2:
                st.metric("Átlagár", f"{street_data[price_column].mean():.0f} eFt/m²")
            with col3:
                st.metric("Medián ár", f"{street_data[price_column].median():.0f} eFt/m²")

except FileNotFoundError:
    st.error("A 'budapest_lakaspiac_osszefuzve.csv' fájl nem található. Kérlek, győződj meg róla, hogy a fájl a megfelelő helyen van.")
except Exception as e:
    st.error(f"Hiba történt az adatok betöltése során: {str(e)}")

# Footer
st.markdown("---")
st.markdown("📊 Budapest Lakáspiac Dashboard | Adatok forrása: budapest_lakaspiac_osszefuzve.csv")
