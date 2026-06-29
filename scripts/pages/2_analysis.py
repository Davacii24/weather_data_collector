import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

PLOTS = Path(__file__).resolve().parent.parent.parent / "plots"

@st.cache_data(ttl=3600)
def load_data():
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    daily_avg = pd.read_csv(data_dir / "daily_avg_historical.csv", parse_dates=['date'])
    extremes = pd.read_csv(data_dir / "extremes_by_period.csv", index_col=0)
    return daily_avg, extremes

daily_avg, extremes = load_data()

st.header("Weather data analysis", text_alignment="center")
st.markdown('<hr style="border: 1px solid red; margin-top: 0;">', unsafe_allow_html=True)

if st.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

with st.container(border=True):
    st.markdown("#### Average temperature trend 1775–2026")
    st.caption("Data source: ČHMÚ daily · 10-year rolling average across all stations")

    temp_series = daily_avg.set_index('date')['temp_avg']
    for w in [3650, 1825, 365]:
        rolling_10y = temp_series.rolling(w, min_periods=w // 2).mean().dropna()
        if len(rolling_10y) > 10:
            break

    annual_avg = daily_avg.set_index('date')['temp_avg'].resample('YE').mean().dropna()
    x_years = annual_avg.index.year.values.astype(float)
    z_annual = np.polyfit(x_years, annual_avg.values, 1)
    total_change = z_annual[0] * (x_years[-1] - x_years[0])
    sign = "+" if total_change > 0 else ""

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rolling_10y.index, y=rolling_10y.values,
        mode='lines', line=dict(color='steelblue', width=2),
        name='10-year rolling average',
    ))
    fig.add_trace(go.Scatter(
        x=annual_avg.index, y=np.poly1d(z_annual)(x_years),
        mode='lines', line=dict(color='red', width=2, dash='dash'),
        name=f'Linear trend ({sign}{total_change:.1f}°C over {int(x_years[-1] - x_years[0])} years)',
    ))
    fig.update_layout(
        template="simple_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13),
        height=450,
        hovermode="x unified",
        margin=dict(l=50, r=30, t=30, b=50),
        yaxis=dict(title="Temperature (°C)", ticksuffix="°",
                   gridcolor="rgba(0,0,0,0.06)", gridwidth=0.5),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="left", x=0, font=dict(size=12)),
    )
    st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.markdown("#### Extreme temperature days by period (1775–2026)")
    st.caption("Data source: ČHMÚ daily · hot days (>30°C) and cold days (<0°C), averaged per year")

    periods = extremes.index.tolist()
    period_labels = [f"{p}–{p+19}" for p in periods]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=period_labels,
        y=extremes['hot'].tolist(),
        name='Hot days (>30°C)',
        marker_color='rgba(226,75,74,0.7)',
    ))
    fig.add_trace(go.Bar(
        x=period_labels,
        y=extremes['cold'].tolist(),
        name='Cold days (<0°C)',
        marker_color='rgba(55,138,221,0.7)',
    ))
    fig.update_layout(
        template="simple_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13),
        height=450,
        barmode='group',
        hovermode="x unified",
        margin=dict(l=50, r=30, t=40, b=80),
        yaxis=dict(title="Avg days per year",
                   gridcolor="rgba(0,0,0,0.06)", gridwidth=0.5),
        xaxis=dict(showgrid=False, tickangle=-45),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="left", x=0, font=dict(size=12)),
    )
    st.plotly_chart(fig, use_container_width=True)


with st.container(border=True):
    st.markdown("#### Temperature records")
    col_hot, col_cold = st.columns(2)

    top_hot = (daily_avg.nlargest(10, 'temp_avg')[['date', 'temp_avg']]
               .assign(date=lambda x: x['date'].dt.strftime('%Y-%m-%d'))
               .rename(columns={'date': 'Date', 'temp_avg': 'Temp (°C)'}))

    top_cold = (daily_avg.nsmallest(10, 'temp_avg')[['date', 'temp_avg']]
                .assign(date=lambda x: x['date'].dt.strftime('%Y-%m-%d'))
                .rename(columns={'date': 'Date', 'temp_avg': 'Temp (°C)'}))

    with col_hot:
        st.caption("Top 10 hottest days")
        st.dataframe(top_hot, hide_index=True, use_container_width=True)

    with col_cold:
        st.caption("Top 10 coldest days")
        st.dataframe(top_cold, hide_index=True, use_container_width=True)


st.subheader("Temperature analysis")

with st.container(border=True):
    st.markdown("#### Temperature distribution across periods")
    st.caption("Data source: ČHMÚ daily · Period: 1775–2026 · Variables: temp_avg")
    st.image(str(PLOTS / "Temperature_Distribution_Across_Periods.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        The temperature mean presents a U-shape, corresponding with the Little Ice Age (1800–1840).
        The minimum temperature was −23.4°C in the 1775–1800 period. From 2000 onwards, the minimum
        sits at −9.26°C, which is shockingly warmer in winter. The 75th percentile shows summer
        temperatures aren't that different across periods. Global warming shows much more effect in
        increasing winter temperature than in summer.
        """)

with st.container(border=True):
    st.markdown("#### Cross-validation: OWM vs Open-Meteo temperature")
    st.caption("Data source: owm_weather, open_meteo_hourly · Period: 2026-05-13 to 2026-06-04")
    st.image(str(PLOTS / "Cross_validation.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        The OLS slope is close to 1 (0.992) with R² of 0.9447. The OWM intercept of 1.46°C shows
        a systematic difference. OWM uses physical weather stations while Open-Meteo uses the ERA5
        reanalysis model, so OWM reads consistently warmer by approximately 1.46°C.
        """)


st.subheader("Air quality analysis")

with st.container(border=True):
    st.markdown("#### Air quality, Prague May–June 2026")
    st.caption("Data source: owm_pollution · Variables: aqi, pm2_5")
    st.image(str(PLOTS / "air_quality.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        Red dots (worse quality) cluster around the end of May, mostly during afternoon time.
        Green and yellow dots dominate, showing acceptable air visibility. Daytime business hours
        show more serious air quality problems, while during night-time the air gets clearer.
        """)

with st.container(border=True):
    st.markdown("#### Average AQI by hour of day, Prague May–June 2026")
    st.caption("Data source: owm_pollution · Variables: aqi")
    st.image(str(PLOTS / "aqi_by_hour.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        The bar chart presents a bell-shape. The worst air pollution happens during daytime, and
        the lowest before sunrise. The most serious AQI is at 2pm with 2.6, corresponding
        to human activity patterns.
        """)

with st.container(border=True):
    st.markdown("#### Pollutant composition, Prague May–June 2026")
    st.caption("Data source: owm_pollution · Variables: no2, o3, so2, pm2_5, pm10")
    st.image(str(PLOTS / "pollutant_composition.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        O₃ composes 89.1% of observed pollutants, followed by PM10 (4.17%) and NO₂ (3.02%).
        O₃ (ozone) naturally forms when sunlight reacts with NOx from cars. This means May–June
        Prague has major sunlight, and it does not necessarily indicate dangerous air. PM2.5 is
        the most harmful among the five, and SO₂ from industrial emission is considerably low.
        """)

with st.container(border=True):
    st.markdown("#### Pollutant breakdown (excluding O₃)")
    st.caption("Data source: owm_pollution · Variables: no2, so2, pm2_5, pm10")
    st.image(str(PLOTS / "pollutant_breakdown.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        Without O₃ dominating, PM10 leads at 3.10 μg/m³, followed by NO₂ and PM2.5. Low SO₂
        means there is no heavily polluting industry in the city. The high PM10 represents
        construction work generating dust particles in Prague.
        """)


st.subheader("Soil and solar analysis")

with st.container(border=True):
    st.markdown("#### Solar radiation sorted by season")
    st.caption("Data source: Open-Meteo hourly · Period: 1940–2026 · Variables: shortwave_radiation")
    st.image(str(PLOTS / "solar_radiation_seasonal.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        A symmetric bell-shape with peak radiation at hours 11–12 in each season. Prague at 50°N
        explains the 4-hour difference in daytime between summer (4am–7pm) and winter (6am–5pm).
        Peak radiation reaches 571 W/m² in summer and 211 W/m² in winter.
        """)

with st.container(border=True):
    st.markdown("#### Air vs soil temperature by month, Prague")
    st.caption("Data source: Open-Meteo hourly · Period: 1940–2026")
    st.image(str(PLOTS / "air_soil_temp.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        Air temperature and soil above 28cm track closely. Soil at 28–100cm moves more mildly.
        In autumn and winter, deep soil (28–100cm) is warmer than air, widening the gap by 4°C in
        December. Deeper soil buffers better against surface temperature fluctuations.
        """)

with st.container(border=True):
    st.markdown("#### Soil moisture seasonal pattern")
    st.caption("Data source: Open-Meteo daily · Period: 1940–2026")
    st.image(str(PLOTS / "soil_pattern.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        Surface soil (0–7cm) has higher moisture across all months with a narrower range
        (0.284–0.364 m³/m³). Deeper layers show wider variation of roughly 0.10 difference.
        Snow melt and rain keep surface moisture high. Summer evaporation reduces it, but
        rain compensates.
        """)


st.subheader("Correlation and cross-analysis")

with st.container(border=True):
    st.markdown("#### Correlation heatmap, weather variables in Prague")
    st.caption("Data source: Open-Meteo hourly · Period: 1940–2026")
    st.image(str(PLOTS / "correlation_heatmap.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        The strongest relationship is soil temperature 0–7cm and air temperature (r = 0.97).
        Humidity has a negative relationship to shortwave radiation. Precipitation and wind speed
        show no clear correlation to other variables. The negative relationship between radiation
        and humidity matches real-world experience.
        """)

with st.container(border=True):
    st.markdown("#### Monthly temperature vs precipitation, Prague (1775–2026)")
    st.caption("Data source: ČHMÚ daily · Variables: temp_avg, precipitation")
    st.image(str(PLOTS / "temp_precipitation.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        Both variables follow seasonal patterns, but the precipitation peak is in June (2.28 mm)
        while temperature peaks in July (19.43°C). Despite appearing to move together, the
        correlation is near-zero (0.06). Shared seasonality does not equal direct causation.
        """)

with st.container(border=True):
    st.markdown("#### Annual average sunshine hours, Prague (1920–2026)")
    st.caption("Data source: ČHMÚ daily · Variables: sunshine_hours")
    st.image(str(PLOTS / "sunshine_hour.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        Surprisingly, the trend shows decreasing sunlight hours (coefficient −0.002, R² = 0.02).
        Since temperatures are rising, other factors may trap heat in the atmosphere. Air
        pollutants like PM2.5, O₃, greenhouse gases, and CO₂ may contribute to heat retention
        despite reduced sunshine.
        """)

with st.container(border=True):
    st.markdown("#### Humidity throughout 250 years")
    st.caption("Data source: ČHMÚ synoptic · Variables: vapour_pressure")
    st.image(str(PLOTS / "humidity_250.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        Vapour pressure peaks in July at approximately 14.24 hPa and hits a winter minimum of
        roughly 4.8 hPa in January. Note that this measures vapour pressure (hPa), not relative
        humidity (%). Warmer air holds more water molecules, so vapour pressure rises in summer.
        However, relative humidity actually decreases because warmer air has greater moisture capacity.
        """)

with st.container(border=True):
    st.markdown("#### Solar radiation cross-validation: ČHMÚ vs Open-Meteo")
    st.caption("Data source: ČHMÚ hourly, Open-Meteo hourly")
    st.image(str(PLOTS / "solar_radiation_cross.png"), use_container_width=True)
    with st.expander("Observation & key findings"):
        st.write("""
        Both sources show nearly identical daily radiation curves peaking at hours 11–12.
        ČHMÚ reaches approximately 421 W/m², while Open-Meteo is slightly lower at roughly
        400 W/m². The small peak-hour difference is likely due to measurement vs model
        methodology. This validates Open-Meteo's ERA5 model as a reliable source for solar
        radiation data in Prague.
        """)