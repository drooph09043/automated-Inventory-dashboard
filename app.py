import pandas as pd
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
import plotly.graph_objects as go
from decimal import Decimal, ROUND_HALF_UP
import webbrowser
import socket
from waitress import serve
import dash_auth
from datetime import datetime, timedelta
import io
from dash.dependencies import Input, Output



# 👥 Define username-password pairs
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'password123',
    'dhruv': 'test@123',
    'dhanashri': '123'
}



# Function to process and return all required data
def load_and_process_data():
    tesog_csv = r'C:\Users\gargd\Downloads\pipeline\txt_to_csv\TESOG INV.csv'
    df_tesog = pd.read_csv(tesog_csv)

# Clean columns
    df_tesog['Material'] = df_tesog['Material'].astype(str).str.strip()
    df_tesog['Material Description'] = df_tesog['Material Description'].astype(str).str.lower().str.strip()
    df_tesog['Purch. Gro'] = df_tesog['Purch. Gro'].astype(str).str.strip()  # 🆕 Clean this column too
    df_tesog['Inv Value'] = df_tesog['Inv Value'].astype(str).str.replace(',', '').str.strip()
    df_tesog['Inv Value'] = pd.to_numeric(df_tesog['Inv Value'], errors='coerce')
    df_tesog.to_csv(tesog_csv, index=False)

# Define materials to exclude
    excluded_materials = ['1337245-3', '1337352-1', '9-1393087-2']

# Filter data
    df_tesog_filtered = df_tesog[
        (~df_tesog['Material'].isin(excluded_materials)) &
        (~df_tesog['Material Description'].str.contains('sensor', na=False)) &
        (df_tesog['Purch. Gro'] != 'AND')  # 🆕 This excludes rows where Purch. Gro is 'AND'
    ]

# Sum inventory value
    total_tesog = round(df_tesog_filtered['Inv Value'].sum() / 1000, 2)
#########################################################################################
    mudc_csv = r'C:\Users\gargd\Downloads\pipeline\txt_to_csv\MUDC Inv.csv'
    df_mudc = pd.read_csv(mudc_csv)
    df_mudc.iloc[:, 0] = df_mudc.iloc[:, 0].str.strip()
    df_mudc = df_mudc[~df_mudc.iloc[:, 0].str.startswith('Material', na=False)]
    df_mudc['Profit Cen'] = df_mudc['Profit Cen'].astype(str).str.strip()
    df_mudc['Inv Value'] = df_mudc['Inv Value'].astype(str).str.replace(',', '').str.strip()
    df_mudc['Inv Value'] = pd.to_numeric(df_mudc['Inv Value'], errors='coerce')
    df_mudc.to_csv(mudc_csv, index=False)
    df_mudc_filtered = df_mudc[df_mudc['Profit Cen'] == '101']
    total_mudc = round(df_mudc_filtered['Inv Value'].sum() / 83.472 / 1000, 2)

#########################################################################################
    h41_csv = r'C:\Users\gargd\Downloads\pipeline\txt_to_csv\H41 Scrap.csv'

    df_h41 = pd.read_csv(h41_csv)
    df_h41['Storage Lo'] = df_h41['Storage Lo'].astype(str).str.strip()
    df_h41['Storage Lo'] = df_h41['Storage Lo'].replace('nan', '')
    total_shirwal = round(df_h41[(df_h41['Storage Lo'] != 'PE04') & df_h41['Storage Lo'].isin(['PE01', 'PE03'])]['Inv Value'].sum() / 83.472 / 1000, 2)
# Group 2: PERT or blank, excluding PE04 : No storage Location
    nostg = round(df_h41[(df_h41['Storage Lo'] != 'PE04') & df_h41['Storage Lo'].isin(['PERT', ''])]['Inv Value'].sum() / 83.472 / 1000, 2)
##########################################################################################
    h41_no_scrap_csv = r'C:\Users\gargd\Downloads\pipeline\txt_to_csv\H41 no Scrap.csv'

    df_final = pd.read_csv(h41_no_scrap_csv)

    total_fg = round(df_final[df_final['mat type'] == 'FG']['Total Valu'].sum() / 83.472 / 1000, 2)
    total_rm = round(df_final[df_final['mat type'] == 'RM']['Total Valu'].sum() / 83.472 / 1000, 2)
    total_sfg = round(df_final[df_final['mat type'] == 'SFG']['Total Valu'].sum() / 83.472 / 1000, 2)
    scrap = float(Decimal(total_shirwal - (total_fg + total_rm + total_sfg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    p1_total = round(df_final[df_final['Plant_y'] == 'P1']['Total Valu'].sum() / 83.472 / 1000, 2)
    p2_total = round(df_final[df_final['Plant_y'] == 'P2']['Total Valu'].sum() / 83.472 / 1000, 2)
    p1_rm_total = round(df_final[(df_final['Plant_y'] == 'P1') & (df_final['mat type'] == 'RM')]['Total Valu'].sum() / 83.472 / 1000, 2)
    p1_fg_total = round(df_final[(df_final['Plant_y'] == 'P1') & (df_final['mat type'] == 'FG')]['Total Valu'].sum() / 83.472 / 1000, 2)
    p1_sfg_total = round(df_final[(df_final['Plant_y'] == 'P1') & (df_final['mat type'] == 'SFG')]['Total Valu'].sum() / 83.472 / 1000, 2)
    p2_rm_total = round(df_final[(df_final['Plant_y'] == 'P2') & (df_final['mat type'] == 'RM')]['Total Valu'].sum() / 83.472 / 1000, 2)
    p2_fg_total = round(df_final[(df_final['Plant_y'] == 'P2') & (df_final['mat type'] == 'FG')]['Total Valu'].sum() / 83.472 / 1000, 2)
    p2_sfg_total = round(df_final[(df_final['Plant_y'] == 'P2') & (df_final['mat type'] == 'SFG')]['Total Valu'].sum() / 83.472 / 1000, 2)
    grand_total = total_shirwal + total_tesog + total_mudc
    perc_shirwal = (total_shirwal / grand_total) * 100
    perc_tesog = (total_tesog / grand_total) * 100
    perc_mudc = float(total_mudc / grand_total) * 100
    return {
        "scrap" : total_shirwal-(total_fg+total_rm+total_sfg),
        "total_shirwal": total_shirwal,
        "total_tesog": total_tesog,
        "total_mudc": total_mudc,
        "perc_shirwal": perc_shirwal,
        "perc_tesog": perc_tesog,
        "perc_mudc": perc_mudc,
	    "total_fg" : total_fg,
	    "total_rm" : total_rm,
	    "total_sfg" : total_sfg,
        "p1_total": p1_total,
        "p2_total": p2_total,
        "p1_rm_total": p1_rm_total,
        "p2_rm_total": p2_rm_total,
        "p1_fg_total": p1_fg_total,
        "p2_fg_total": p2_fg_total,
        "p1_sfg_total": p1_sfg_total,
        "p2_sfg_total": p2_sfg_total,
	    "nostg": nostg
    }

app = Dash(__name__)
server = app.server
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
app.title = "Inventory Dashboard"
# Layout
app.layout = html.Div([
    dcc.Interval(id="interval-refresh", interval= 10 * 1000, n_intervals=0),

    html.H1("Inventory Dashboard", style={"textAlign": "center"}),


    html.Div(id="scorecards", style={
        "display": "flex",
        "justifyContent": "space-between",
        "flexWrap": "wrap",
        "marginBottom": "30px"
    }),

    
    
    html.Div([
    html.Div([
        dcc.Graph(id="bar-graph", style={"height": "100%", "width": "100%"})
    ], style={
        "flex": "1",
        "padding": "15px",
        "minWidth": "400px",
        "boxSizing": "border-box",
        "border": "2px solid #ccc",
        "borderRadius": "0px",
        "backgroundColor": "#f9f9f9",
        "marginTop": "-30px"  # 👈 Move bar chart upward
    }),

    html.Div([
        dcc.Graph(id="sunburst-chart", style={"height": "100%", "width": "100%"})
    ], style={
        "flex": "1",
        "padding": "15px",
        "minWidth": "400px",
        "boxSizing": "border-box",
        "border": "2px solid #ccc",
        "borderRadius": "0px",
        "backgroundColor": "#f9f9f9",
        "marginTop": "-30px"  # 👈 Move sunburst chart upward
    }),
    
    html.Button("Download Material Summary", id="download-summary-btn"),
    dcc.Download(id="download-summary")

    
], style={
    "display": "flex",
    "flexDirection": "row",
    "justifyContent": "space-between",
    "alignItems": "stre"
})




 

])

@app.callback(
    Output("scorecards", "children"),
    Input("interval-refresh", "n_intervals")
)
def update_scorecards(n):
    data = load_and_process_data()
    print(f"📦 Interval triggered at: {datetime.now()}, n_intervals={n}")
    print("📊 KPI chart data:", data)
    return html.Div([
    html.Div([
        html.H4("SHIRWAL TOTAL(K$)", style={"marginBottom": "10px", "marginTop": "-5px"}),
        html.H2(f"{data['total_shirwal']:.2f} ({data['perc_shirwal']:.1f}%)", style={"color": "#636EFA", "margin": 0})
    ], style={
        "border": "2px solid #ccc",
        "padding": "15px",
        "borderRadius": "0px",  
        "textAlign": "left",
        "backgroundColor": "#f9f9f9",
        "flex": "1",
        "minWidth": "200px"
    }),

    html.Div([
        html.H4("TESOG TOTAL(K$)", style={"marginBottom": "10px", "marginTop": "-5px"}),
        html.H2(f"{data['total_tesog']:.2f} ({data['perc_tesog']:.1f}%)", style={"color":"#636EFA", "margin": 0})
    ], style={
        "border": "2px solid #ccc",
        "padding": "15px",
        "borderRadius": "0px",
        "textAlign": "left",
        "backgroundColor": "#f9f9f9",
        "flex": "1",
        "minWidth": "200px"
    }),

    html.Div([
        html.H4("MUDC TOTAL(K$)", style={"marginBottom": "10px", "marginTop": "-5px"}),
        html.H2(f"{data['total_mudc']:.2f} ({data['perc_mudc']:.4f}%)", style={"color": "#636EFA", "margin": 0})
    ], style={
        "border": "2px solid #ccc",
        "padding": "15px",
        "borderRadius": "0px",
        "textAlign": "left",
        "backgroundColor": "#f9f9f9",
        "flex": "1",
        "minWidth": "200px"
    }),
    html.Div([
        html.H4("TE TOTAL(K$)", style={"marginBottom": "10px", "marginTop": "-5px"}),
        html.H2(f"{(data['total_shirwal'] + data['total_mudc'] + data['total_tesog']):.2f} ", style={"color": "#636EFA", "margin": 0})
    ], style={
        "border": "2px solid #ccc",
        "padding": "15px",
        "borderRadius": "0px",  
        "textAlign": "left",
        "backgroundColor": "#f9f9f9",
        "flex": "1",
        "minWidth": "200px"
    }),
], style={
    "display": "flex",
    "justifyContent": "space-between",
    "flexWrap": "nowrap",  # prevents wrapping
    "width": "100%",
    "boxSizing": "border-box",
    "columnGap": "0px"  # no gap between cards
})



@app.callback(
    Output("bar-graph", "figure"),
    Input("interval-refresh", "n_intervals")
)
def update_bar_graph(n):
    data = load_and_process_data()
    print(f"📦 Interval triggered at: {datetime.now()}, n_intervals={n}")
    print("📊 Bar chart data:", data)

    values = [
        data["total_rm"],
        data["total_sfg"],
        data["scrap"],
        data["nostg"],
        data["total_fg"]
    ]


    fig = px.bar(
        x=["RM","SFG", "PE03", "No Storage","FG"],
        y=values,
        labels={"x": "Material Type", "y": "Value"},
        color_discrete_sequence=["#636EFA"],
        title="Inventory SHIRWAL (K$)",
        text=[f"{v:.2f}" for v in values]
    )

    fig.update_traces(
        textposition='auto',  # 👈 Position text outside the bar
        cliponaxis=False         # 👈 Allow text to overflow if needed
    )

    fig.update_layout(
        yaxis=dict(title='Value (K$)'),
        xaxis=dict(title='Material Type'),
        margin=dict(t=50, b=50),
        height=400
    )

    return fig




@app.callback(
    Output("sunburst-chart", "figure"),
    Input("interval-refresh", "n_intervals")
)
def update_sunburst_chart(n):
    data = load_and_process_data()
    print(f"📦 Interval triggered at: {datetime.now()}, n_intervals={n}")
    print("📊 pie chart data:", data)
    
    # Create a DataFrame for Plotly Express
    df = pd.DataFrame({
        'Category': ['P1 Total'] * 3 + ['P2 Total'] * 3,
        'Subcategory': ['P1 RM', 'P1 FG', 'P1 SFG', 'P2 RM', 'P2 FG', 'P2 SFG'],
        'Value': [
            float(data.get('p1_rm_total', 0)),
            float(data.get('p1_fg_total', 0)),
            float(data.get('p1_sfg_total', 0)),
            float(data.get('p2_rm_total', 0)),
            float(data.get('p2_fg_total', 0)),
            float(data.get('p2_sfg_total', 0))
        ]
    })

    # Create the sunburst chart
    fig = px.sunburst(
        df,
        path=['Category', 'Subcategory'],
        values='Value',
        title='Plant 1 and Plant 2 Inventory Breakdown(K$)'
    )

    # Update to show percentages
    fig.update_traces(
    textinfo='label+percent root+value',
    insidetextorientation='auto',
    outsidetextfont=dict(size=12, color='black'),
    textfont=dict(size=12),
    hovertemplate='<b>%{label}</b><br>Value: %{value:.2f}<br>Percent: %{percentRoot:.2%}<extra></extra>'
    
    )   


    fig.update_layout(
        margin=dict(t=50, l=0, r=0, b=50),
        height=500
    )

    return fig





@app.callback(
    Output("download-summary", "data"),
    Input("download-summary-btn", "n_clicks"),
    prevent_initial_call=True
)
def generate_summary_excel(n_clicks):
    # Load the CSV file
    h41_no_scrap_csv = r'C:\Users\gargd\Downloads\pipeline\txt_to_csv\H41 no Scrap.csv'
    df = pd.read_csv(h41_no_scrap_csv, dtype=str)

    # Clean and convert relevant columns
    df['Material'] = df['Material'].apply(lambda x: x.strip().lower() if pd.notnull(x) else x)
    df['Storage Lo'] = df['Storage Lo'].apply(lambda x: x.strip().lower() if pd.notnull(x) else x)
    df['Total stock'] = pd.to_numeric(df['Total stock'].str.replace(',', ''), errors='coerce')

    # Filter out rows where Storage Lo is 'null'
    df_filtered = df[df['Storage Lo'] != 'null']

    # Group by Material and Storage Lo, summing Total stock
    grouped = df_filtered.groupby(['Material', 'Storage Lo'])['Total stock'].sum().reset_index()

    # Pivot to get 'shop' and 'main' columns
    pivot_df = grouped.pivot(index='Material', columns='Storage Lo', values='Total stock').fillna(0)

    # Ensure both 'shop' and 'main' columns exist
    for col in ['shop', 'main']:
        if col not in pivot_df.columns:
            pivot_df[col] = 0

    # Add total column
    pivot_df['total'] = pivot_df['shop'] + pivot_df['main']

    # Reset index to make 'Material' a column
    summary_df = pivot_df.reset_index()

    # Write to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        summary_df.to_excel(writer, index=False, sheet_name='Summary')
    output.seek(0)

    return dcc.send_bytes(output.read(), filename="material_summary.xlsx")



if __name__ == "__main__":
    host_ip = socket.gethostbyname(socket.gethostname())
    url = f"http://{host_ip}:8050"
    print(f"🔐 Dashboard secured at: {url}")
    webbrowser.open(url)
    serve(app.server, host=host_ip, port=8050)
    