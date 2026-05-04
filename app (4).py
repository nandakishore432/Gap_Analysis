import io
import zipfile
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Business Gap Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.stApp {
    background:
        radial-gradient(circle at top left, rgba(99,102,241,.12), transparent 25%),
        radial-gradient(circle at top right, rgba(34,211,238,.10), transparent 24%),
        linear-gradient(180deg, #0b1020 0%, #111827 45%, #f8fafc 45%, #f8fafc 100%);
}
.main .block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px;}
.hero-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 58%, #312e81 100%);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 22px;
    padding: 1.4rem 1.5rem;
    color: white;
    box-shadow: 0 18px 40px rgba(15,23,42,.30);
    margin-bottom: 1rem;
}
.mini-card {
    background: rgba(255,255,255,.9);
    border: 1px solid rgba(15,23,42,.06);
    border-radius: 16px;
    padding: .9rem 1rem;
    box-shadow: 0 8px 24px rgba(15,23,42,.06);
}
.section-title {color:#0f172a; font-weight:800; font-size:1.15rem; margin-bottom:.35rem;}
.small-muted {color:#475569; font-size:.92rem;}
.badge {display:inline-block; padding:.28rem .55rem; border-radius:999px; background:#e2e8f0; color:#0f172a; font-size:.78rem; font-weight:700;}
[data-testid="stMetricValue"] {font-size: 1.7rem; font-weight: 800;}
</style>
""", unsafe_allow_html=True)

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DATE_MAP = pd.date_range('2025-01-01', periods=12, freq='MS')
DOMAINS = {
    "Automobile": {
        "color": "#6366f1",
        "rgba_full": "rgba(99,102,241,1)",
        "rgba_mid": "rgba(99,102,241,0.75)",
        "rgba_low": "rgba(99,102,241,0.45)",
        "icon": "🚗",
        "lead_label": "Leads",
        "channels": ["Organic Search","Paid Ads","Referral","Social Media","Direct"],
        "conv_name": "Vehicle Deliveries",
        "headline": "From showroom discovery to vehicle delivery conversion"
    },
    "IT Solutions": {
        "color": "#22d3ee",
        "rgba_full": "rgba(34,211,238,1)",
        "rgba_mid": "rgba(34,211,238,0.75)",
        "rgba_low": "rgba(34,211,238,0.45)",
        "icon": "💻",
        "lead_label": "Bookings",
        "channels": ["Organic Search","Paid Ads","Email","Social Media","Events"],
        "conv_name": "Closed Clients",
        "headline": "Lead qualification and proposal closure intelligence"
    },
    "Health & Beauty": {
        "color": "#f472b6",
        "rgba_full": "rgba(244,114,182,1)",
        "rgba_mid": "rgba(244,114,182,0.75)",
        "rgba_low": "rgba(244,114,182,0.45)",
        "icon": "💄",
        "lead_label": "Bookings",
        "channels": ["Organic Search","Influencer","Referral","Social Media","Paid Ads"],
        "conv_name": "Package Purchases",
        "headline": "Audience reach, bookings, purchases, and repeat behavior"
    },
}

np.random.seed(42)

def gen_monthly(base_vis, lead_pct, conv_pct, trend=1.02):
    vis, leads, convs = [], [], []
    v = base_vis
    for _ in MONTHS:
        v = int(v * trend * np.random.uniform(0.96, 1.05))
        l = int(v * lead_pct * np.random.uniform(0.93, 1.07))
        c = int(l * conv_pct * np.random.uniform(0.90, 1.10))
        vis.append(v); leads.append(l); convs.append(c)
    return vis, leads, convs

RAW = {
    "Automobile": gen_monthly(12000, 0.18, 0.35, 1.018),
    "IT Solutions": gen_monthly(9500, 0.22, 0.42, 1.025),
    "Health & Beauty": gen_monthly(15000, 0.14, 0.28, 1.030),
}

DFS = {}
MONTHLY = {}
for domain, (vis, leads, convs) in RAW.items():
    meta = DOMAINS[domain]
    ll = meta["lead_label"]
    rows = []
    monthly_rows = []
    for i, m in enumerate(MONTHS):
        split = np.random.dirichlet(np.ones(5))
        month_spend = round((vis[i] / 1000) * np.random.uniform(0.55, 0.9), 2)
        avg_value = round(np.random.uniform(3.5, 22.5), 2)
        revenue = round(convs[i] * avg_value / 100, 2)
        monthly_rows.append({
            'Date': DATE_MAP[i], 'Month': m, 'Visitors': vis[i], ll: leads[i], 'Conversions': convs[i],
            'Marketing Spend (Lakh)': month_spend, 'Avg Value (Lakh)': avg_value, 'Revenue (Cr)': revenue
        })
        for j, ch in enumerate(meta["channels"]):
            v_ch = int(vis[i] * split[j])
            l_ch = int(leads[i] * split[j] * np.random.uniform(0.85, 1.15))
            c_ch = int(convs[i] * split[j] * np.random.uniform(0.80, 1.20))
            spend_ch = round(month_spend * split[j] * np.random.uniform(0.9, 1.1), 2)
            rows.append({"Date": DATE_MAP[i], "Month": m, "Channel": ch, "Visitors": v_ch, ll: l_ch, "Conversions": c_ch, "Spend (Lakh)": spend_ch})
    df = pd.DataFrame(rows)
    df["Month"] = pd.Categorical(df["Month"], categories=MONTHS, ordered=True)
    DFS[domain] = df

    grp = pd.DataFrame(monthly_rows)
    grp["Month"] = pd.Categorical(grp["Month"], categories=MONTHS, ordered=True)
    grp["Leads"] = grp[ll]
    grp["Lead Rate"] = grp["Leads"] / grp["Visitors"]
    grp["Conv Rate"] = grp["Conversions"] / grp["Leads"]
    grp["Overall CR"] = grp["Conversions"] / grp["Visitors"]
    grp["CPA"] = (grp["Marketing Spend (Lakh)"] * 100000) / grp["Conversions"]
    MONTHLY[domain] = grp

TOTALS = {}
for d in DOMAINS:
    g = MONTHLY[d]
    tv, tl, tc = g["Visitors"].sum(), g["Leads"].sum(), g["Conversions"].sum()
    TOTALS[d] = {
        "visitors": tv,
        "leads": tl,
        "convs": tc,
        "lead_rate": tl / tv,
        "conv_rate": tc / tl,
        "overall_cr": tc / tv,
        "revenue": g["Revenue (Cr)"].sum(),
    }

BEST_DOMAIN = max(DOMAINS, key=lambda d: TOTALS[d]["overall_cr"])
LOWEST_LEADS = min(DOMAINS, key=lambda d: TOTALS[d]["lead_rate"])
DOMAIN_LIST = list(DOMAINS.keys())

def to_csv_bytes(df):
    x = df.copy()
    for c in x.columns:
        if pd.api.types.is_datetime64_any_dtype(x[c]):
            x[c] = x[c].dt.strftime('%Y-%m-%d')
    return x.to_csv(index=False).encode('utf-8')

def make_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()

with st.sidebar:
    st.markdown("## 🎛️ Dashboard Filters")
    sel_domains = st.multiselect("Select Portfolio", DOMAIN_LIST, default=DOMAIN_LIST)
    sel_months = st.multiselect("Filter by Month", MONTHS, default=MONTHS)
    if not sel_months:
        sel_months = MONTHS
    min_d, max_d = DATE_MAP.min().date(), DATE_MAP.max().date()
    start_date, end_date = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    st.markdown("---")
    st.markdown("### 📌 Quick Snapshot")
    for d, meta in DOMAINS.items():
        t = TOTALS[d]
        st.markdown(f"{meta['icon']} **{d}**  \nVisitors: `{t['visitors']:,}` | CR: `{t['overall_cr']:.1%}`")
    st.markdown("---")
    st.caption("Dashboard v3.0 · Reference-aligned analytics + exports")

filtered_monthly = {}
filtered_channels = {}
for d in DOMAIN_LIST:
    m = MONTHLY[d]
    c = DFS[d]
    filtered_monthly[d] = m[(m['Month'].astype(str).isin(sel_months)) & (m['Date'] >= start_date) & (m['Date'] <= end_date)].copy()
    filtered_channels[d] = c[(c['Month'].astype(str).isin(sel_months)) & (c['Date'] >= start_date) & (c['Date'] <= end_date)].copy()

zip_filtered = make_zip({
    **{f"{d.lower().replace(' & ','_').replace(' ','_')}_monthly_filtered.csv": to_csv_bytes(filtered_monthly[d]) for d in DOMAIN_LIST},
    **{f"{d.lower().replace(' & ','_').replace(' ','_')}_channel_filtered.csv": to_csv_bytes(filtered_channels[d]) for d in DOMAIN_LIST},
})

st.markdown("""
<div class='hero-box'>
    <div style='font-size:.85rem; letter-spacing:.12em; text-transform:uppercase; opacity:.82;'>Decision-Making Intelligence</div>
    <div style='font-size:2.1rem; font-weight:800; line-height:1.1; margin-top:.35rem;'>Business Gap Analysis Dashboard</div>
    <div style='margin-top:.55rem; max-width:1000px; font-size:1rem; opacity:.9;'>Automobile · IT Solutions · Health & Beauty — updated from the uploaded reference structure with month filters, date-range analysis, channel-level performance, KPI storytelling, and downloadable CSV exports.</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
summary_domains = sel_domains if sel_domains else DOMAIN_LIST
sum_vis = sum(filtered_monthly[d]['Visitors'].sum() for d in summary_domains)
sum_leads = sum(filtered_monthly[d]['Leads'].sum() for d in summary_domains)
sum_convs = sum(filtered_monthly[d]['Conversions'].sum() for d in summary_domains)
cr = (sum_convs / sum_vis) if sum_vis else 0
c1.metric("Total Visitors", f"{sum_vis:,}")
c2.metric("Total Leads/Bookings", f"{sum_leads:,}")
c3.metric("Total Conversions", f"{sum_convs:,}")
c4.metric("Overall Conversion Rate", f"{cr:.2%}")

x1, x2, x3 = st.columns([1.2,1.1,1.1])
with x1:
    st.markdown("<div class='mini-card'><div class='section-title'>Executive Signals</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='badge'>Best converter: {BEST_DOMAIN}</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-muted' style='margin-top:.6rem;'>Highest full-period overall conversion comes from <b>{BEST_DOMAIN}</b>, while <b>{LOWEST_LEADS}</b> shows the lowest lead-generation rate and may need top-of-funnel optimization.</div></div>", unsafe_allow_html=True)
with x2:
    st.download_button("Download filtered CSV bundle (.zip)", data=zip_filtered, file_name="gap_analysis_filtered_exports.zip", mime="application/zip", use_container_width=True)
with x3:
    files = {f"{d.lower().replace(' & ','_').replace(' ','_')}_monthly_full.csv": to_csv_bytes(MONTHLY[d]) for d in DOMAIN_LIST}
    files.update({f"{d.lower().replace(' & ','_').replace(' ','_')}_channel_full.csv": to_csv_bytes(DFS[d]) for d in DOMAIN_LIST})
    st.download_button("Download full sample CSV bundle (.zip)", data=make_zip(files), file_name="gap_analysis_full_exports.zip", mime="application/zip", use_container_width=True)

st.markdown("### Portfolio Overview")
overview_rows = []
for d in summary_domains:
    g = filtered_monthly[d]
    if g.empty:
        continue
    overview_rows.append({
        'Domain': d,
        'Visitors': int(g['Visitors'].sum()),
        'Leads/Bookings': int(g['Leads'].sum()),
        'Conversions': int(g['Conversions'].sum()),
        'Revenue (Cr)': round(g['Revenue (Cr)'].sum(), 2),
        'Lead Rate': g['Leads'].sum() / g['Visitors'].sum(),
        'Conv Rate': g['Conversions'].sum() / g['Leads'].sum(),
        'Overall CR': g['Conversions'].sum() / g['Visitors'].sum(),
    })
overview_df = pd.DataFrame(overview_rows)
if not overview_df.empty:
    left, right = st.columns((1.12,1))
    with left:
        fig = px.bar(overview_df, x='Domain', y='Conversions', color='Domain', text_auto=True,
                     color_discrete_map={d: DOMAINS[d]['color'] for d in DOMAIN_LIST})
        fig.update_layout(height=360, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig2 = px.scatter(overview_df, x='Lead Rate', y='Overall CR', size='Revenue (Cr)', color='Domain', text='Domain',
                          color_discrete_map={d: DOMAINS[d]['color'] for d in DOMAIN_LIST})
        fig2.update_traces(textposition='top center')
        fig2.update_layout(height=360, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)
    show = overview_df.copy()
    for c in ['Lead Rate','Conv Rate','Overall CR']:
        show[c] = show[c].map(lambda x: f"{x:.2%}")
    st.dataframe(show, use_container_width=True, hide_index=True)

st.markdown("### Domain Drilldowns")
tabs = st.tabs(summary_domains if summary_domains else DOMAIN_LIST)
for tab, domain in zip(tabs, summary_domains if summary_domains else DOMAIN_LIST):
    with tab:
        meta = DOMAINS[domain]
        g = filtered_monthly[domain]
        cdf = filtered_channels[domain]
        if g.empty:
            st.warning("No data available for this selection.")
            continue
        st.markdown(f"#### {meta['icon']} {domain}")
        st.caption(meta['headline'])

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Visitors", f"{int(g['Visitors'].sum()):,}")
        m2.metric(meta['lead_label'], f"{int(g['Leads'].sum()):,}")
        m3.metric(meta['conv_name'], f"{int(g['Conversions'].sum()):,}")
        m4.metric("Revenue", f"₹ {g['Revenue (Cr)'].sum():.2f} Cr")
        m5.metric("Overall CR", f"{(g['Conversions'].sum()/g['Visitors'].sum()):.2%}")

        col1, col2 = st.columns((1.05,1.2))
        with col1:
            funnel = go.Figure(go.Funnel(
                y=['Visitors', meta['lead_label'], meta['conv_name']],
                x=[int(g['Visitors'].sum()), int(g['Leads'].sum()), int(g['Conversions'].sum())],
                textposition='inside', textinfo='value+percent initial',
                marker={'color':[meta['rgba_full'], meta['rgba_mid'], meta['rgba_low']]}
            ))
            funnel.update_layout(height=380, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(funnel, use_container_width=True)
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=g['Month'].astype(str), y=g['Visitors'], mode='lines+markers', name='Visitors', line=dict(color=meta['rgba_full'], width=3)))
            fig.add_trace(go.Scatter(x=g['Month'].astype(str), y=g['Leads'], mode='lines+markers', name=meta['lead_label'], line=dict(color=meta['rgba_mid'], width=3)))
            fig.add_trace(go.Bar(x=g['Month'].astype(str), y=g['Conversions'], name='Conversions', marker_color=meta['rgba_low']))
            fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10), legend=dict(orientation='h'))
            st.plotly_chart(fig, use_container_width=True)

        r1, r2 = st.columns(2)
        with r1:
            by_channel = cdf.groupby('Channel', as_index=False)[['Visitors', 'Conversions']].sum()
            by_channel['Overall CR'] = by_channel['Conversions'] / by_channel['Visitors']
            figc = px.bar(by_channel, x='Channel', y='Conversions', color='Channel', text_auto=True)
            figc.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
            st.plotly_chart(figc, use_container_width=True)
        with r2:
            rate_df = g[['Month','Lead Rate','Conv Rate','Overall CR']].melt(id_vars='Month', var_name='Metric', value_name='Rate')
            figr = px.line(rate_df, x='Month', y='Rate', color='Metric', markers=True)
            figr.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(figr, use_container_width=True)

        d1, d2 = st.columns((1,1))
        with d1:
            st.download_button(f"Download {domain} monthly CSV", data=to_csv_bytes(g), file_name=f"{domain.lower().replace(' & ','_').replace(' ','_')}_monthly_filtered.csv", mime='text/csv', key=f'{domain}_monthly')
        with d2:
            st.download_button(f"Download {domain} channel CSV", data=to_csv_bytes(cdf), file_name=f"{domain.lower().replace(' & ','_').replace(' ','_')}_channel_filtered.csv", mime='text/csv', key=f'{domain}_channel')

        table_df = g.copy()
        for c in ['Lead Rate','Conv Rate','Overall CR']:
            table_df[c] = table_df[c].map(lambda x: f"{x:.2%}")
        table_df['Date'] = table_df['Date'].dt.strftime('%Y-%m-%d')
        st.markdown("##### Monthly table")
        st.dataframe(table_df, use_container_width=True, hide_index=True)
        channel_table = cdf.copy()
        channel_table['Date'] = channel_table['Date'].dt.strftime('%Y-%m-%d')
        st.markdown("##### Channel table")
        st.dataframe(channel_table, use_container_width=True, hide_index=True)
