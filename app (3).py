import math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(page_title='Industry Conversion Command Center', page_icon='📊', layout='wide')

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.main {
    background:
      radial-gradient(circle at top left, rgba(1,105,111,.10), transparent 28%),
      radial-gradient(circle at top right, rgba(0,100,148,.10), transparent 24%),
      linear-gradient(180deg, #f7f6f2 0%, #f1f3f7 100%);
}
[data-testid="stMetricValue"] {font-size: 1.8rem; font-weight: 800;}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.card {
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(40,37,29,.08);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: 0 10px 30px rgba(30, 40, 60, 0.08);
    backdrop-filter: blur(10px);
}
.hero {
    padding: 1.2rem 1.4rem;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(1,105,111,.97), rgba(0,100,148,.88));
    color: white;
    box-shadow: 0 18px 40px rgba(1,105,111,.22);
}
.small-note {color:#5c6773; font-size:0.92rem;}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def build_data():
    np.random.seed(42)
    months = pd.date_range('2025-06-01', periods=12, freq='MS')
    month_labels = [d.strftime('%b %Y') for d in months]

    auto = pd.DataFrame({
        'month': month_labels,
        'website_visitors': [18500, 19200, 20400, 21800, 23150, 24500, 25250, 26400, 27850, 28900, 30120, 31880],
        'test_drive_bookings': [1320, 1410, 1505, 1638, 1715, 1860, 1910, 2030, 2150, 2265, 2375, 2510],
        'showroom_visits': [880, 930, 1015, 1085, 1140, 1220, 1268, 1342, 1450, 1525, 1608, 1695],
        'bookings_confirmed': [188, 205, 220, 246, 259, 284, 296, 322, 344, 368, 392, 419],
        'vehicles_delivered': [142, 154, 169, 182, 197, 212, 225, 241, 258, 277, 291, 316],
        'avg_vehicle_price': [19.2, 19.4, 19.7, 19.8, 20.1, 20.4, 20.6, 20.9, 21.0, 21.3, 21.6, 21.9],
        'marketing_spend_lakh': [16.0, 16.2, 17.0, 17.8, 18.1, 18.8, 19.3, 20.0, 20.8, 21.4, 22.2, 23.0]
    })
    auto['revenue_cr'] = auto['vehicles_delivered'] * auto['avg_vehicle_price'] / 100
    auto['lead_to_testdrive'] = auto['test_drive_bookings'] / auto['website_visitors']
    auto['testdrive_to_visit'] = auto['showroom_visits'] / auto['test_drive_bookings']
    auto['visit_to_booking'] = auto['bookings_confirmed'] / auto['showroom_visits']
    auto['booking_to_delivery'] = auto['vehicles_delivered'] / auto['bookings_confirmed']
    auto['overall_conversion'] = auto['vehicles_delivered'] / auto['website_visitors']
    auto['cpa'] = (auto['marketing_spend_lakh'] * 100000) / auto['vehicles_delivered']

    it = pd.DataFrame({
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
        'month': month_labels,
        'social_reach': [28000, 29400, 30650, 32240, 33800, 35450, 37020, 38860, 40100, 41950, 43620, 45200],
        'consultations_booked': [1560, 1650, 1715, 1838, 1942, 2015, 2148, 2280, 2355, 2482, 2598, 2724],
        'walkins': [1025, 1082, 1148, 1215, 1296, 1355, 1428, 1512, 1588, 1665, 1742, 1818],
        'package_purchases': [348, 372, 389, 418, 441, 462, 488, 521, 545, 576, 602, 634],
        'repeat_clients': [122, 131, 139, 152, 164, 173, 187, 201, 214, 228, 245, 259],
        'avg_order_value': [4.2, 4.3, 4.3, 4.4, 4.5, 4.6, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1],
        'ad_spend_lakh': [4.0, 4.1, 4.3, 4.5, 4.6, 4.8, 5.0, 5.2, 5.3, 5.5, 5.8, 6.0],
        'nps': [58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69]
    })
    hb['revenue_cr'] = hb['package_purchases'] * hb['avg_order_value'] / 100
    hb['reach_to_consult'] = hb['consultations_booked'] / hb['social_reach']
    hb['consult_to_walkin'] = hb['walkins'] / hb['consultations_booked']
    hb['walkin_to_purchase'] = hb['package_purchases'] / hb['walkins']
    hb['repeat_rate'] = hb['repeat_clients'] / hb['package_purchases']
    hb['overall_conversion'] = hb['package_purchases'] / hb['social_reach']
    hb['cpa'] = (hb['ad_spend_lakh'] * 100000) / hb['package_purchases']

    return auto, it, hb


auto, it, hb = build_data()

datasets = {
    'Automobile': auto,
    'IT Solutions': it,
    'Health & Beauty': hb,
}

metric_map = {
    'Automobile': {
        'top_label': 'Delivered vehicles',
        'top_value': 'vehicles_delivered',
        'revenue': 'revenue_cr',
        'conversion': 'overall_conversion',
        'spend_eff': 'cpa',
        'funnel': [('Website visitors', 'website_visitors'), ('Test drives', 'test_drive_bookings'), ('Showroom visits', 'showroom_visits'), ('Bookings', 'bookings_confirmed'), ('Deliveries', 'vehicles_delivered')],
        'trend_x': 'website_visitors',
        'trend_y': 'vehicles_delivered',
        'secondary': 'avg_vehicle_price',
        'secondary_label': 'Avg vehicle price (₹ lakh)',
        'color': '#01696f'
    },
    'IT Solutions': {
        'top_label': 'Clients won',
        'top_value': 'clients_closed',
        'revenue': 'revenue_cr',
        'conversion': 'overall_conversion',
        'spend_eff': 'cac',
        'funnel': [('Inbound leads', 'inbound_leads'), ('Qualified', 'qualified_leads'), ('Demos', 'solution_demos'), ('Proposals', 'proposals_sent'), ('Closed', 'clients_closed')],
        'trend_x': 'inbound_leads',
        'trend_y': 'clients_closed',
        'secondary': 'delivery_satisfaction',
        'secondary_label': 'Delivery satisfaction',
        'color': '#006494'
    },
    'Health & Beauty': {
        'top_label': 'Packages sold',
        'top_value': 'package_purchases',
        'revenue': 'revenue_cr',
        'conversion': 'overall_conversion',
        'spend_eff': 'cpa',
        'funnel': [('Social reach', 'social_reach'), ('Consultations', 'consultations_booked'), ('Walk-ins', 'walkins'), ('Purchases', 'package_purchases'), ('Repeat clients', 'repeat_clients')],
        'trend_x': 'social_reach',
        'trend_y': 'package_purchases',
        'secondary': 'nps',
        'secondary_label': 'NPS',
        'color': '#a12c7b'
    }
}

def pct(v):
    return f"{v*100:.2f}%"

def growth(series):
    return ((series.iloc[-1] - series.iloc[0]) / series.iloc[0]) * 100

st.markdown('''
<div class="hero">
    <div style="font-size:0.9rem; text-transform:uppercase; letter-spacing:.12em; opacity:.9;">Sample-data streamlit dashboard</div>
    <div style="font-size:2.1rem; font-weight:800; line-height:1.1; margin-top:.35rem;">Industry Conversion Command Center</div>
    <div style="max-width:980px; margin-top:.65rem; font-size:1rem; opacity:.92;">A multi-sector executive dashboard for Automobile, IT Solutions, and Health & Beauty with synthetic monthly performance data, full-funnel conversion metrics, revenue tracking, and campaign efficiency insights.</div>
</div>
''', unsafe_allow_html=True)

selected = st.sidebar.radio('Choose industry view', ['Overview', 'Automobile', 'IT Solutions', 'Health & Beauty'])
st.sidebar.markdown('---')
st.sidebar.caption('All numbers are sample data created for demonstration.')

def overview_page():
    summary_rows = []
    for name, df in datasets.items():
        cfg = metric_map[name]
        summary_rows.append({
            'Industry': name,
            'Primary outcome': int(df[cfg['top_value']].iloc[-1]),
            'Revenue (₹ Cr)': round(df[cfg['revenue']].sum(), 2),
            'Overall conversion': df[cfg['conversion']].iloc[-1],
            'Growth %': growth(df[cfg['top_value']]),
            'Efficiency': round(df[cfg['spend_eff']].iloc[-1], 0)
        })
    sdf = pd.DataFrame(summary_rows)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Total annual revenue', f"₹ {sdf['Revenue (₹ Cr)'].sum():.2f} Cr")
    c2.metric('Best conversion', f"{sdf.loc[sdf['Overall conversion'].idxmax(), 'Industry']} ({pct(sdf['Overall conversion'].max())})")
    c3.metric('Fastest growth', f"{sdf.loc[sdf['Growth %'].idxmax(), 'Industry']} ({sdf['Growth %'].max():.1f}%)")
    c4.metric('Industries tracked', '3')

    left, right = st.columns((1.2,1))
    with left:
        fig = px.bar(sdf, x='Industry', y='Revenue (₹ Cr)', color='Industry', text_auto='.2f',
                     color_discrete_sequence=['#01696f','#006494','#a12c7b'])
        fig.update_layout(height=370, margin=dict(l=10,r=10,t=20,b=10), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig2 = px.scatter(sdf, x='Overall conversion', y='Growth %', size='Revenue (₹ Cr)', color='Industry', text='Industry',
                          color_discrete_sequence=['#01696f','#006494','#a12c7b'])
        fig2.update_traces(textposition='top center')
        fig2.update_layout(height=370, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    show = sdf.copy()
    show['Overall conversion'] = show['Overall conversion'].map(pct)
    show['Growth %'] = show['Growth %'].map(lambda x: f"{x:.1f}%")
    st.dataframe(show, use_container_width=True, hide_index=True)


def sector_page(name):
    df = datasets[name]
    cfg = metric_map[name]
    latest = df.iloc[-1]

    st.subheader(f'{name} dashboard')
    st.caption('Executive metrics, funnel health, trend performance, and efficiency indicators from sample monthly data.')

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(cfg['top_label'], f"{int(latest[cfg['top_value']]):,}", f"{growth(df[cfg['top_value']]):.1f}% vs first month")
    m2.metric('Annual revenue', f"₹ {df[cfg['revenue']].sum():.2f} Cr")
    m3.metric('Overall conversion', pct(latest[cfg['conversion']]), f"{(latest[cfg['conversion']] - df[cfg['conversion']].iloc[0])*100:.2f} pp")
    eff_label = 'Cost per acquisition' if cfg['spend_eff'] in ['cpa','cac'] else 'Efficiency'
    m4.metric(eff_label, f"₹ {latest[cfg['spend_eff']]:,.0f}")

    f1, f2 = st.columns((1.05, 1.2))
    with f1:
        labels = [x[0] for x in cfg['funnel']]
        values = [int(latest[col]) for _, col in cfg['funnel']]
        funnel = go.Figure(go.Funnel(y=labels, x=values, textposition='inside', textinfo='value+percent initial',
                                     marker={'color': [cfg['color']]*len(values)}))
        funnel.update_layout(height=420, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(funnel, use_container_width=True)
    with f2:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df['month'], y=df[cfg['top_value']], mode='lines+markers', name=cfg['top_label'], line=dict(color=cfg['color'], width=3)), secondary_y=False)
        fig.add_trace(go.Bar(x=df['month'], y=df[cfg['revenue']], name='Revenue (₹ Cr)', marker_color='rgba(0,100,148,0.35)'), secondary_y=True)
        fig.update_layout(height=420, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation='h'))
        fig.update_yaxes(title_text=cfg['top_label'], secondary_y=False)
        fig.update_yaxes(title_text='Revenue (₹ Cr)', secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        conv_cols = [col for col in df.columns if any(key in col for key in ['to_', 'conversion', 'repeat_rate'])]
        conv_df = pd.DataFrame({'Metric': conv_cols, 'Latest value': [df[c].iloc[-1] for c in conv_cols]})
        conv_df['Latest value'] = conv_df['Latest value'].map(pct)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('### Conversion metric snapshot')
        st.dataframe(conv_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        fig3 = px.scatter(df, x=cfg['trend_x'], y=cfg['trend_y'], size=cfg['revenue'], color=cfg['secondary'],
                          hover_name='month', color_continuous_scale='Tealgrn')
        fig3.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

    display_df = df.copy()
    pct_cols = [c for c in display_df.columns if c in ['lead_to_testdrive','testdrive_to_visit','visit_to_booking','booking_to_delivery','overall_conversion','lead_to_qualified','qualified_to_demo','demo_to_proposal','proposal_to_close','reach_to_consult','consult_to_walkin','walkin_to_purchase','repeat_rate']]
    for c in pct_cols:
        if c in display_df.columns:
            display_df[c] = display_df[c].map(pct)
    st.markdown('### Monthly detail')
    st.dataframe(display_df, use_container_width=True, hide_index=True)

if selected == 'Overview':
    overview_page()
else:
    sector_page(selected)
