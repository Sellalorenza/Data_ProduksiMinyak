from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

PRODUKSI = 'data/produksi_minyak_mentah.csv'
NEGARA = 'data/kode_negara_lengkap.json'

st.set_page_config(layout="wide")

@st.cache
def baca_data():
    df = pd.read_csv(PRODUKSI)
    country = pd.read_json(NEGARA)
    data = df.join(country.set_index('alpha-3'),on='kode_negara')[['kode_negara', 'tahun', 'produksi','name','region','sub-region']].pivot(index=['name','kode_negara','region','sub-region'],columns='tahun',values='produksi').reset_index()
    data = data[~data['name'].isnull()]
    data = pd.melt(data,id_vars=data.columns[:4],value_vars=data.columns[4:],value_name='produksi').sort_values(by=['name','tahun']).reset_index(drop=True)
    data['produksi'] = data['produksi'].fillna(0)
    data['produksi'] = data['produksi'].astype(float)
    data['name'] = data['name'].astype(str)
    return data

data = baca_data()

negara = st.sidebar.selectbox(
    "Pilih Negara",
    sorted(data['name'].unique().tolist()),
)

tahun = st.sidebar.selectbox(
    'Pilih Tahun', 
    sorted(data['tahun'].unique().tolist())
)


st.title(f'Dashboard Produksi Minyak {negara}')

ts_chart = data[data['name']==negara][['tahun','produksi']]
ts_chart['tahun'] = pd.to_datetime(ts_chart['tahun'], format='%Y')
ts_chart = ts_chart.set_index('tahun')
ts_chart = ts_chart.fillna(0)

st.header(f"Laju Produksi Minyak {negara} tahun {min(ts_chart.reset_index()['tahun'].dt.year)} - {max(ts_chart.reset_index()['tahun'].dt.year)}")
st.area_chart(ts_chart)

st.header("Data Produksi Minyak")

col1, col2 = st.columns(2)

pie_thn = list(sorted(data[data['tahun']==tahun].sort_values('produksi',ascending=False).head(5)['name'].values.tolist() + [negara]))
pie1 = data[(data['tahun']==tahun) & (data['name'].isin(pie_thn))][['name','produksi']].sort_values('produksi',ascending=False).set_index('name')

with col1:
    labels = pie1.index.values.tolist()
    sizes = pie1.values.reshape(1,-1)[0].tolist()
    explode = tuple([0.1 if n == negara else 0 for n in labels])
    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax.axis('equal')
    st.header(f'Produksi Minyak {negara} dan 5 Negara Tertinggi {tahun}')
    st.pyplot(fig)

pie_all = list(sorted(data.groupby('name')['produksi'].sum().sort_values(ascending=False).head(5).reset_index()['name'].values.tolist() + [negara]))
pie2 = data[data['name'].isin(pie_all)].groupby('name')['produksi'].sum()

with col2:
    labels = pie2.index.values.tolist()
    sizes = pie2.values.reshape(1,-1)[0].tolist()
    explode = tuple([0.1 if n == negara else 0 for n in labels])
    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax.axis('equal')
    st.header(f'Produksi Minyak {negara} dan 5 Negara Tertinggi Kumulatif')
    st.pyplot(fig)

col3,col4 = st.columns(2)

top_thn = data[data['tahun']==tahun].sort_values('produksi',ascending=False).drop('tahun',axis=1).iloc[0]

with col3:
    st.subheader(f"Negara dengan Produksi Tertinggi {tahun}")
    st.components.v1.html(
        f'''
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <div class="card">
            <p style="margin-bottom:0"><b>Negara : </b>{top_thn['name']}</p>
            <p style="margin-bottom:0"><b>Kode Negara : </b>{top_thn['kode_negara']}</p>
            <p style="margin-bottom:0"><b>Region : </b>{top_thn['region']}</p>
            <p style="margin-bottom:0"><b>Sub-Region : </b>{top_thn['sub-region']}</p>
            <p style="margin-bottom:0"><b>Produksi : </b>{top_thn['produksi']}</p>
        </div>
        '''
    )

top = data.groupby(['name','kode_negara','region','sub-region'])['produksi'].sum().sort_values(ascending=False).reset_index().iloc[0]

with col4:
    st.subheader(f"Negara dengan Produksi Tertinggi Tahun {min(ts_chart.reset_index()['tahun'].dt.year)} - {max(ts_chart.reset_index()['tahun'].dt.year)}")
    st.components.v1.html(
        f'''
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <div class="card">
            <p style="margin-bottom:0"><b>Negara : </b>{top['name']}</p>
            <p style="margin-bottom:0"><b>Kode Negara : </b>{top['kode_negara']}</p>
            <p style="margin-bottom:0"><b>Region : </b>{top['region']}</p>
            <p style="margin-bottom:0"><b>Sub-Region : </b>{top['sub-region']}</p>
            <p style="margin-bottom:0"><b>Produksi : </b>{top['produksi']}</p>
        </div>
        '''
    )

col5,col6 = st.columns(2)

lowest_tahun = data[(data['tahun']==tahun) & (data['produksi']>0)].sort_values('produksi').drop('tahun',axis=1).iloc[0]

with col5:
    st.subheader(f"Negara dengan Produksi Terrendah {tahun}")
    st.components.v1.html(
        f'''
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <div class="card">
            <p style="margin-bottom:0"><b>Negara : </b>{lowest_tahun['name']}</p>
            <p style="margin-bottom:0"><b>Kode Negara : </b>{lowest_tahun['kode_negara']}</p>
            <p style="margin-bottom:0"><b>Region : </b>{lowest_tahun['region']}</p>
            <p style="margin-bottom:0"><b>Sub-Region : </b>{lowest_tahun['sub-region']}</p>
            <p style="margin-bottom:0"><b>Produksi : </b>{lowest_tahun['produksi']}</p>
        </div>
        '''
    )

lowest = data.groupby(['name','kode_negara','region','sub-region'])['produksi'].sum().reset_index()
lowest = lowest[lowest['produksi']>0].sort_values(by='produksi').iloc[0]

with col6:
    st.subheader(f"Negara dengan Produksi Terrendah Tahun {min(ts_chart.reset_index()['tahun'].dt.year)} - {max(ts_chart.reset_index()['tahun'].dt.year)}")
    st.components.v1.html(
        f'''
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <div class="card">
            <p style="margin-bottom:0"><b>Negara : </b>{lowest['name']}</p>
            <p style="margin-bottom:0"><b>Kode Negara : </b>{lowest['kode_negara']}</p>
            <p style="margin-bottom:0"><b>Region : </b>{lowest['region']}</p>
            <p style="margin-bottom:0"><b>Sub-Region : </b>{lowest['sub-region']}</p>
            <p style="margin-bottom:0"><b>Produksi : </b>{lowest['produksi']}</p>
        </div>
        '''
    )

col7, col8 = st.columns(2)

nol_thn = data[(data['tahun']==tahun) & (data['produksi']==0)].reset_index(drop=True).drop(['tahun','produksi'],axis=1)

with col7:
    st.header(f'Negara Bukan Penghasil Minyak Tahun {tahun}')
    st.dataframe(nol_thn)

nol = data.groupby(['name','kode_negara','region','sub-region'])['produksi'].sum().reset_index()
nol = nol[nol['produksi']==0].reset_index(drop=True).drop('produksi',axis=1)

with col8:
    st.header('Negara Bukan Penghasil Minyak')
    st.dataframe(nol)