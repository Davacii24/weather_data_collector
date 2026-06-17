import datetime
import pandas as pd
from astral import LocationInfo
from astral.sun import sun
from OWM_database import get_connection
import streamlit as st
import plotly.graph_objects as go

# ── setup ───────────────────────────────────────────────────
conn = get_connection()
city = LocationInfo("Prague", "Czech Republic", "Europe/Prague", 50.0755, 14.4378)
today = datetime.date.today()
s = sun(city.observer, date=today, tzinfo=city.tzinfo)
yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
last_month = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

STATION_COORDS = {
    "Praha-Ruzyne":  {"lat": 50.1003, "lon": 14.2556},
    "Praha-Karlov":  {"lat": 50.0704, "lon": 14.4282},
    "Praha-Libus":   {"lat": 50.0077, "lon": 14.4467},
    "Praha-Kbely":   {"lat": 50.1232, "lon": 14.5380},
}

STATION_STYLE = {
    "Praha-Karlov": {"color": "#E24B4A", "label": "Karlov (city center)"},
    "Praha-Ruzyne": {"color": "#378ADD", "label": "Ruzyně (west)"},
    "Praha-Libus":  {"color": "#1D9E75", "label": "Libuš (south)"},
    "Praha-Kbely":  {"color": "#BA7517", "label": "Kbely (northeast)"},
}


def hex_to_rgba(hex_color, alpha=0.1):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── queries ─────────────────────────────────────────────────
query = """
    SELECT * FROM minute
    WHERE (station, date) IN (
        SELECT station, MAX(date)
        FROM minute
        WHERE data_richness = 'LARGE'
        GROUP BY station
    )
"""

query_2 = f"""
    SELECT * FROM minute
    WHERE data_richness = 'LARGE'
    AND date >= '{yesterday}'
"""

query_3 = f"""
    SELECT * FROM daily
    WHERE data_richness = 'LARGE'
    AND date >= '{last_month}'
    ORDER BY date ASC
"""

# ── load data ───────────────────────────────────────────────
df = (pd.read_sql_query(query, conn)
      .assign(date=lambda x: pd.to_datetime(x['date'])
              .dt.tz_localize("UTC")
              .dt.tz_convert("Europe/Prague")
              .dt.tz_localize(None)))

df_30 = (pd.read_sql_query(query_2, conn)
         .assign(date=lambda x: pd.to_datetime(x['date'])
                 .dt.tz_localize("UTC")
                 .dt.tz_convert("Europe/Prague")
                 .dt.tz_localize(None)))

df_month = pd.read_sql_query(query_3, conn)

# ── FIX: convert temperature columns to numeric ────────────
for col in ["temp_min", "temp_avg", "temp_max"]:
    df_month[col] = pd.to_numeric(df_month[col], errors="coerce")

# ── deltas ──────────────────────────────────────────────────
target_time = df["date"].max() - pd.Timedelta(minutes=30)
target_time = target_time.round("10min")
df_prev = df_30[df_30["date"] == target_time].set_index("station")["temperature"]
deltas = df.set_index("station")["temperature"] - df_prev

print("Latest time:", df["date"].max())
print("Target time:", target_time)
print("Matching rows:", len(df_30[df_30["date"] == target_time]))

# ── header ──────────────────────────────────────────────────
st.header("Prague weather overview", text_alignment="center")

_, date_range, sunrise, noon, sunset, _ = st.columns([1, 1, 1, 1, 1, 1], gap="small")
with date_range:
    st.markdown(f":material/date_range: {today.strftime('%Y-%m-%d')}")
with sunrise:
    st.markdown(f":material/Wb_Twilight: {s['dawn'].strftime('%H:%M')}")
with noon:
    st.markdown(f":material/Wb_Sunny: {s['noon'].strftime('%H:%M')}")
with sunset:
    st.markdown(f":material/wb_twilight: {s['sunset'].strftime('%H:%M')}")

st.markdown('<hr style="border: 1px solid red; margin-top: 0;">', unsafe_allow_html=True)

# ── temperature cards ───────────────────────────────────────
col1, col2, col3, col4 = st.columns(4, border=True, width="stretch", vertical_alignment="center")

with col1:
    st.metric(label="City Center / Karlov",
              value=f"{df[df['station'] == 'Praha-Karlov']['temperature'].values[0]}°C",
              delta=f"{round(deltas['Praha-Karlov'], 2)}°C")
with col2:
    st.metric(label="West / Ruzyně",
              value=f"{df[df['station'] == 'Praha-Ruzyne']['temperature'].values[0]}°C",
              delta=f"{round(deltas['Praha-Ruzyne'], 2)}°C")
with col3:
    st.metric(label="South / Libuš",
              value=f"{df[df['station'] == 'Praha-Libus']['temperature'].values[0]}°C",
              delta=f"{round(deltas['Praha-Libus'], 2)}°C")
with col4:
    st.metric(label="Northeast / Kbely",
              value=f"{df[df['station'] == 'Praha-Kbely']['temperature'].values[0]}°C",
              delta=f"{round(deltas['Praha-Kbely'], 2)}°C")

# ── precipitation chart ─────────────────────────────────────
fig = go.Figure()

for station, style in STATION_STYLE.items():
    sdf = df_month[df_month["station"] == station].sort_values("date")
    c = style["color"]

    fig.add_trace(go.Scatter(
        x=sdf["date"], y=sdf["temp_min"],
        mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=sdf["date"], y=sdf["temp_max"],
        mode="lines", line=dict(width=0),
        fill="tonexty",
        fillcolor=hex_to_rgba(c, 0.10),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=sdf["date"], y=sdf["temp_avg"],
        mode="lines",
        line=dict(color=c, width=2, shape="spline"),
        name=style["label"],
    ))

fig.update_layout(
    template="simple_white",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
    height=450,
    font=dict(family="Inter, sans-serif", size=13),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="left", x=0,
        font=dict(size=12),
    ),
    margin=dict(l=50, r=30, t=50, b=50),
    xaxis=dict(
        showgrid=False,
        tickformat="%d %b",
        dtick="D5",
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0.06)",
        gridwidth=0.5,
        ticksuffix="°",
        title="",
    ),
)

with st.container(border=True):
    st.markdown("#### :material/thermostat: Temperature overview")
    st.caption("Daily average with min–max band · past 30 days")
    st.plotly_chart(fig, use_container_width=True)


# ── precipitation chart ─────────────────────────────────────
df_month["precipitation"] = pd.to_numeric(df_month["precipitation"], errors="coerce")

fig_rain = go.Figure()

for station, style in STATION_STYLE.items():
    sdf = df_month[df_month["station"] == station].sort_values("date")
    fig_rain.add_trace(go.Bar(
        x=sdf["date"],
        y=sdf["precipitation"],
        name=style["label"],
        marker_color=hex_to_rgba(style["color"], 0.7),
        marker_line=dict(color=style["color"], width=0.5),
    ))

fig_rain.update_layout(
    template="simple_white",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    barmode="group",
    hovermode="x unified",
    height=400,
    font=dict(family="Inter, sans-serif", size=13),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="left", x=0,
        font=dict(size=12),
    ),
    margin=dict(l=50, r=30, t=50, b=50),
    xaxis=dict(
        showgrid=False,
        tickformat="%d %b",
        dtick="D5",
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0.06)",
        gridwidth=0.5,
        ticksuffix=" mm",
        title="",
    ),
)

with st.container(border=True):
    st.markdown("#### :material/water_drop: Precipitation")
    st.caption("Daily rainfall by station · past 30 days")
    st.plotly_chart(fig_rain, use_container_width=True)