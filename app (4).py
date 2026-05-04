import io
import zipfile
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(page_title='Industry Conversion Command Center v2', page_icon='📈', layout='wide')

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.main {
    background:
      radial-gradient(circle at top left, rgba(1,105,111,.10), transparent 28%),
      radial-gradient(circle at top right, rgba(0,100,148,.10), transparent 24%),
      linear-gradient(180deg, #f7f6f2 0%, #eef3f5 100%);
}
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
[data-testid="stMetricValue"] {font-size: 1.75rem; font-weight: 800;}
.card {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(40,37,29,.08);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: 0 12px 32px rgba(30,40,60,.08);
    backdrop-filter: blur(8px);
}
.hero {
    padding: 1.2rem 1.4rem;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(1,105,111,.97), rgba(0,100,148,.88));
    color: white;
    box-shadow: 0 18px 40px rgba(1,105,111,.22);
}
.small-note {color:#5c6773; font-size:0.92rem;}
.download-box {
    background: rgba(255,255,255,.82);
    border: 1px solid rgba(40,37,29,.08);
    border-radius: 16px;
    padding: .85rem 1rem;
}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def build_data():
    months = pd.date_range('2025-06-01', periods=12, freq='MS')
    month_labels = [d.strftime('%b %Y') for d in months]

    auto = pd.DataFrame({
        'date': months,
        'month': month_labels,
        'website_visitors': [18500, 19200, 20400, 21800, 23150, 24500, 25250, 26400, 27850, 28900, 30120, 31880],
        'test_drive_bookings': [1320, 1410, 1505, 1638, 1715, 1860, 1910, 2030, 2150, 2265, 2375, 2510],
        'showroom_visits': [880, 930, 1015, 1085, 1140, 1220, 1268, 1342, 1450, 1525, 1608, 1695],
        'bookings_confirmed': [188, 205, 220, 246, 259, 284, 296, 322, 344, 368, 392, 419],
        'vehicles_delivered': [142, 154, 169, 182, 197, 212, 225, 241, 258, 277, 291, 316],
        'avg_vehicle_price_lakh': [19.2, 19.4, 19.7, 19.8, 20.1, 20.4, 20.6, 20.9, 21.0, 21.3, 21.6, 21.9],
        'marketing_spend_lakh': [16.0, 16.2, 17.0, 17.8, 18.1, 18.8, 19.3, 20.0, 20.8, 21.4, 22.2, 23.0]
    })
    auto['revenue_cr'] = auto['vehicles_delivered'] * auto['avg_vehicle_price_lakh'] / 100
    auto['lead_to_testdrive'] = auto['test_drive_bookings'] / auto['website_visitors']
    auto['testdrive_to_visit'] = auto['showroom_visits'] / auto['test_drive_bookings']
    auto['visit_to_booking'] = auto['bookings_confirmed'] / auto['showroom_visits']
    auto['booking_to_delivery'] = auto['vehicles_delivered'] / auto['bookings_confirmed']
    auto['overall_conversion'] = auto['vehicles_delivered'] / auto['website_visitors']
    auto['cpa'] = (auto['marketing_spend_lakh'] * 100000) / auto['vehicles_delivered']

    it = pd.DataFrame({
        'date': months,
        'month': month_labels,
        'inbound_leads': [420, 438, 452, 471, 495, 510, 524, 548, 562, 590, 615, 640],
        'qualified_leads': [218, 226, 239, 251, 266, 281, 293, 308, 321, 338, 352, 369],
        'solution_demos': [122, 128, 136, 144, 152, 161, 167, 176, 182, 194, 202, 214],
        'proposals_sent': [71, 75, 82, 86, 91, 98, 103, 111, 115, 122, 129, 136],
        'clients_closed': [22, 24, 25, 28, 30, 31, 34, 36, 38, 41, 44, 47],
        'avg_contract_lakh': [8.2, 8.3, 8.5, 8.4, 8.7, 8.9, 9.1, 9.0, 9.3, 9.5, 9.8, 10.1],
        'delivery_satisfaction': [4.1, 4.2, 4.2, 4.3, 4.3, 4.4, 4.4, 4.5, 4.5, 4.6, 4.6, 4.7],
        'campaign_spend_lakh': [6.1, 6.2, 6.4, 6.6, 6.8, 7.0, 7.1, 7.4, 7.6, 7.9, 8.2, 8.5]
    })
    it['revenue_cr'] = it['clients_closed'] * it['avg_contract_lakh'] / 100
    it['lead_to_qualified'] = it['qualified_leads'] / it['inbound_leads']
    it['qualified_to_demo'] = it['solution_demos'] / it['qualified_leads']
    it['demo_to_proposal'] = it['proposals_sent'] / it['solution_demos']
    it['proposal_to_close'] = it['clients_closed'] / it['proposals_sent']
    it['overall_conversion'] = it['clients_closed'] / it['inbound_leads']
    it['cac'] = (it['campaign_spend_lakh'] * 100000) / it['clients_closed']

    hb = pd.DataFrame({
        'date': months,
        'month': month_labels,
        'social_reach': [28000, 29400, 30650, 32240, 33800, 35450, 37020, 38860, 40100, 41950, 43620, 45200],
        'consultations_booked': [1560, 1650, 1715, 1838, 1942, 2015, 2148, 2280, 2355, 2482, 2598, 2724],
        'walkins': [1025, 1082, 1148, 1215, 1296, 1355, 1428, 1512, 1588, 1665, 1742, 1818],
        'package_purchases': [348, 372, 389, 418, 441, 462, 488, 521, 545, 576, 602, 634],
        'repeat_clients': [122, 131, 139, 152, 164, 173, 187, 201, 214, 228, 245, 259],
        'avg_order_value_lakh': [4.2, 4.3, 4.3, 4.4, 4.5, 4.6, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1],
        'ad_spend_lakh': [4.0, 4.1, 4.3, 4.5, 4.6, 4.8, 5.0, 5.2, 5.3, 5.5, 5.8, 6.0],
        'nps': [58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69]
    })
    hb['revenue_cr'] = hb['package_purchases'] * hb['avg_order_value_lakh'] / 100
    hb['reach_to_consult'] = hb['consultations_booked'] / hb['social_reach']
    hb['consult_to_walkin'] = hb['walkins'] / hb['consultations_booked']
    hb['walkin_to_purchase'] = hb['package_purchases'] / hb['walkins']
    hb['repeat_rate'] = hb['repeat_clients'] / hb['package_purchases']
    hb['overall_conversion'] = hb['package_purchases'] / hb['social_reach']
    hb['cpa'] = (hb['ad_spend_lakh'] * 100000) / hb['package_purchases']
    return auto, it, hb


def pct(v):
    return f"{v*100:.2f}%"


def growth(series):
    if len(series) < 2 or series.iloc[0] == 0:
        return 0.0
    return ((series.iloc[-1] - series.iloc[0]) / series.iloc[0]) * 100


def df_to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8')


def make_zip(file_map):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, data in file_map.items():
            zf.writestr(name, data)
    return buf.getvalue()


auto, it, hb = build_data()
datasets = {'Automobile': auto, 'IT Solutions': it, 'Health & Beauty': hb}



portfolio_notes = {
    'Automobile': ['Gap-aligned highlights: visitor-to-delivery funnel, marketing efficiency, and monthly revenue momentum.', 'Positive options included: date filtering, direct CSV export, and portfolio-ready KPI storytelling.'],
    'IT Solutions': ['Gap-aligned highlights: lead qualification quality, demo-to-proposal movement, and close-rate visibility.', 'Positive options included: executive overview, drilldown trends, and exportable filtered data.'],
    'Health & Beauty': ['Gap-aligned highlights: reach-to-consult conversion, walk-in monetization, and repeat-client retention.', 'Positive options included: NPS tracking, presentation-friendly charts, and portfolio-specific downloads.']
}

metric_map = {
    'Automobile': {
        'top_label': 'Delivered vehicles', 'top_value': 'vehicles_delivered', 'revenue': 'revenue_cr', 'conversion': 'overall_conversion', 'eff': 'cpa',
        'funnel': [('Website visitors', 'website_visitors'), ('Test drives', 'test_drive_bookings'), ('Showroom visits', 'showroom_visits'), ('Bookings', 'bookings_confirmed'), ('Deliveries', 'vehicles_delivered')],
        'scatter_x': 'website_visitors', 'scatter_y': 'vehicles_delivered', 'scatter_color': 'avg_vehicle_price_lakh', 'color': '#01696f'
    },
    'IT Solutions': {
        'top_label': 'Clients won', 'top_value': 'clients_closed', 'revenue': 'revenue_cr', 'conversion': 'overall_conversion', 'eff': 'cac',
        'funnel': [('Inbound leads', 'inbound_leads'), ('Qualified', 'qualified_leads'), ('Demos', 'solution_demos'), ('Proposals', 'proposals_sent'), ('Closed', 'clients_closed')],
        'scatter_x': 'inbound_leads', 'scatter_y': 'clients_closed', 'scatter_color': 'delivery_satisfaction', 'color': '#006494'
    },
    'Health & Beauty': {
        'top_label': 'Packages sold', 'top_value': 'package_purchases', 'revenue': 'revenue_cr', 'conversion': 'overall_conversion', 'eff': 'cpa',
        'funnel': [('Social reach', 'social_reach'), ('Consultations', 'consultations_booked'), ('Walk-ins', 'walkins'), ('Purchases', 'package_purchases'), ('Repeat clients', 'repeat_clients')],
        'scatter_x': 'social_reach', 'scatter_y': 'package_purchases', 'scatter_color': 'nps', 'color': '#a12c7b'
    }
}

st.markdown('''
<div class="hero">
    <div style="font-size:0.88rem; text-transform:uppercase; letter-spacing:.12em; opacity:.9;">Enhanced portfolio version</div>
    <div style="font-size:2.05rem; font-weight:800; line-height:1.1; margin-top:.35rem;">Industry Conversion Command Center v2</div>
    <div style="max-width:980px; margin-top:.65rem; font-size:1rem; opacity:.92;">Interactive Streamlit dashboard with sample portfolio data, date-range filtering, industry-specific conversion funnels, and downloadable CSV exports for executive reporting.</div>
</div>
''', unsafe_allow_html=True)

st.sidebar.header('Controls')
page = st.sidebar.radio('View', ['Overview', 'Automobile', 'IT Solutions', 'Health & Beauty'])
all_dates = auto['date']
start_date, end_date = st.sidebar.date_input('Date range', value=(all_dates.min().date(), all_dates.max().date()), min_value=all_dates.min().date(), max_value=all_dates.max().date())
if isinstance(start_date, tuple) or isinstance(end_date, tuple):
    pass
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)
if start_date > end_date:
    start_date, end_date = end_date, start_date
st.sidebar.caption('All values use synthetic sample data for portfolio/demo use.')

filtered = {name: df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy() for name, df in datasets.items()}

all_zip = make_zip({f"{name.lower().replace(' & ','_').replace(' ','_')}_filtered.csv": df_to_csv_bytes(df) for name, df in filtered.items()})
raw_zip = make_zip({f"{name.lower().replace(' & ','_').replace(' ','_')}_full.csv": df_to_csv_bytes(df) for name, df in datasets.items()})

cA, cB = st.columns((1,1))
with cA:
    st.download_button('Download filtered CSV bundle (.zip)', data=all_zip, file_name='industry_portfolios_filtered_csv.zip', mime='application/zip', use_container_width=True)
with cB:
    st.download_button('Download full sample CSV bundle (.zip)', data=raw_zip, file_name='industry_portfolios_full_csv.zip', mime='application/zip', use_container_width=True)


def render_export_panel(name, df):
    st.markdown('<div class="download-box">', unsafe_allow_html=True)
    st.markdown(f'**Download {name} filtered data**')
    st.download_button(f'Download {name} CSV', data=df_to_csv_bytes(df), file_name=f"{name.lower().replace(' & ','_').replace(' ','_')}_filtered.csv", mime='text/csv', key=f'{name}_download')
    st.markdown('</div>', unsafe_allow_html=True)


def format_display_df(df):
    display_df = df.copy()
    pct_cols = [c for c in display_df.columns if c in ['lead_to_testdrive','testdrive_to_visit','visit_to_booking','booking_to_delivery','overall_conversion','lead_to_qualified','qualified_to_demo','demo_to_proposal','proposal_to_close','reach_to_consult','consult_to_walkin','walkin_to_purchase','repeat_rate']]
    for c in pct_cols:
        if c in display_df.columns:
            display_df[c] = display_df[c].map(pct)
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    return display_df


def overview_page():
    rows = []
    for name, df in filtered.items():
        if df.empty:
            continue
        cfg = metric_map[name]
        rows.append({
            'Industry': name,
            'Primary outcome': int(df[cfg['top_value']].sum()),
            'Revenue (₹ Cr)': round(df[cfg['revenue']].sum(), 2),
            'Overall conversion': df[cfg['conversion']].iloc[-1],
            'Growth %': growth(df[cfg['top_value']]),
            'Efficiency cost': round(df[cfg['eff']].iloc[-1], 0)
        })
    sdf = pd.DataFrame(rows)
    if sdf.empty:
        st.warning('No data available for the selected date range.')
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric('Filtered revenue', f"₹ {sdf['Revenue (₹ Cr)'].sum():.2f} Cr")
    k2.metric('Top conversion portfolio', f"{sdf.loc[sdf['Overall conversion'].idxmax(), 'Industry']}")
    k3.metric('Top growth portfolio', f"{sdf.loc[sdf['Growth %'].idxmax(), 'Industry']}")
    k4.metric('Date span', f"{len(auto[(auto['date'] >= start_date) & (auto['date'] <= end_date)])} months")

    l, r = st.columns((1.15,1))
    with l:
        fig = px.bar(sdf, x='Industry', y='Revenue (₹ Cr)', color='Industry', text_auto='.2f', color_discrete_sequence=['#01696f','#006494','#a12c7b'])
        fig.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with r:
        fig2 = px.scatter(sdf, x='Overall conversion', y='Growth %', size='Revenue (₹ Cr)', color='Industry', text='Industry', color_discrete_sequence=['#01696f','#006494','#a12c7b'])
        fig2.update_traces(textposition='top center')
        fig2.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    show = sdf.copy()
    show['Overall conversion'] = show['Overall conversion'].map(pct)
    show['Growth %'] = show['Growth %'].map(lambda x: f"{x:.1f}%")
    st.dataframe(show, use_container_width=True, hide_index=True)


def sector_page(name):
    df = filtered[name]
    if df.empty:
        st.warning('No rows available for this portfolio in the selected date range.')
        return
    cfg = metric_map[name]
    latest = df.iloc[-1]

    top1, top2 = st.columns((3,1))
    with top1:
        st.subheader(f'{name} portfolio dashboard')
        st.caption('Filtered view with conversion tracking, trend analysis, and export-ready data.')
        note1, note2 = portfolio_notes[name]
        st.info(note1)
        st.success(note2)
    with top2:
        render_export_panel(name, format_display_df(df))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(cfg['top_label'], f"{int(df[cfg['top_value']].sum()):,}")
    m2.metric('Revenue in range', f"₹ {df[cfg['revenue']].sum():.2f} Cr")
    m3.metric('Latest conversion', pct(latest[cfg['conversion']]), f"{growth(df[cfg['conversion']])*1:.1f}% trend")
    m4.metric('Latest efficiency cost', f"₹ {latest[cfg['eff']]:,.0f}")

    f1, f2 = st.columns((1.0, 1.25))
    with f1:
        labels = [x[0] for x in cfg['funnel']]
        values = [int(latest[col]) for _, col in cfg['funnel']]
        funnel = go.Figure(go.Funnel(y=labels, x=values, textposition='inside', textinfo='value+percent initial', marker={'color': [cfg['color']]*len(values)}))
        funnel.update_layout(height=410, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(funnel, use_container_width=True)
    with f2:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df['month'], y=df[cfg['top_value']], mode='lines+markers', name=cfg['top_label'], line=dict(color=cfg['color'], width=3)), secondary_y=False)
        fig.add_trace(go.Bar(x=df['month'], y=df[cfg['revenue']], name='Revenue (₹ Cr)', marker_color='rgba(0,100,148,0.30)'), secondary_y=True)
        fig.update_layout(height=410, margin=dict(l=10,r=10,t=10,b=10), legend=dict(orientation='h'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_yaxes(title_text=cfg['top_label'], secondary_y=False)
        fig.update_yaxes(title_text='Revenue (₹ Cr)', secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        conv_cols = [col for col in df.columns if any(key in col for key in ['to_', 'conversion', 'repeat_rate'])]
        conv_df = pd.DataFrame({'Metric': conv_cols, 'Latest value': [df[c].iloc[-1] for c in conv_cols]})
        conv_df['Latest value'] = conv_df['Latest value'].map(pct)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('### Conversion metrics')
        st.dataframe(conv_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        fig3 = px.scatter(df, x=cfg['scatter_x'], y=cfg['scatter_y'], size=cfg['revenue'], color=cfg['scatter_color'], hover_name='month', color_continuous_scale='Tealgrn')
        fig3.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('### Portfolio monthly data')
    st.dataframe(format_display_df(df), use_container_width=True, hide_index=True)

if page == 'Overview':
    overview_page()
else:
    sector_page(page)
