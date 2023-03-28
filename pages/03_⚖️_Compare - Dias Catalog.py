# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 23:15:51 2022

@author: Anderson Almeida
"""


import numpy as np
import pandas as pd 
from astropy import units as u
from astropy.coordinates import SkyCoord
from scipy.optimize import curve_fit 
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from oc_tools_padova_edr3 import *
import matplotlib.pyplot as plt



st.set_page_config(page_title="Compare Dias Catalog",layout='wide', page_icon='⚖️')

st.markdown(
    """
    <style>
    body {
        background-color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

###############################################################################
# CATALOG DIAS
###############################################################################
# read isochrones
mod_grid, age_grid, z_grid = load_mod_grid()
filters = ['Gmag','G_BPmag','G_RPmag']
refMag = 'Gmag' 

# fundamental parameters
cluster_our = np.genfromtxt('data/log-results-eDR3.txt', delimiter=';', names = True, 
                        dtype=None, encoding=None, autostrip=True)

list_cluster_ours = cluster_our['name']

cluster_our_name = st.sidebar.selectbox("Select open cluster:", list(list_cluster_ours))

  
file = 'data/membership_data_edr3/{}_data_stars.npy'.format(cluster_our_name)
members_ship = np.load(file, allow_pickle=True)

# select fundamental parameters cluster_our	
ind = np.where(cluster_our['name'] == cluster_our_name)

RA_our = cluster_our['RA_ICRS'][ind]
DEC_our = cluster_our['DE_ICRS'][ind]
age_our = cluster_our['age'][ind]
e_age_our = cluster_our['e_age'][ind]
dist_our = (cluster_our['dist']/1000)[ind]
e_dist_our = (cluster_our['e_dist']/1000)[ind]
FeH_our = cluster_our['FeH'][ind]
e_FeH_our = cluster_our['e_FeH'][ind]
Av_our = cluster_our['Av'][ind]
e_Av_our = cluster_our['e_Av'][ind]

st.sidebar.subheader("Our Fundamental parameters:")
st.sidebar.subheader("$log(age) = {} \pm {}$".format(age_our[0], e_age_our[0]))
st.sidebar.subheader("$Dist. = {} \pm {}~(kpc)$".format(dist_our[0],e_dist_our[0]))
st.sidebar.subheader("$Av. = {} \pm {}~(mag)$".format(Av_our[0],e_Av_our[0]))
st.sidebar.subheader("$FeH = {} \pm {}$".format(FeH_our[0],e_FeH_our[0]))


###############################################################################
# CATALOG EMILY HUNT
###############################################################################

#load clusters
clustersEmily = pd.read_parquet('data/parquet/clusters.parquet')

#select only open clusters
mask_oc = clustersEmily['kind'] == 'o'
clustersEmily = clustersEmily[mask_oc]

#aply filter
clustersEmily = clustersEmily[clustersEmily['name'] == cluster_our_name]

###############################################################################

#load members
members_ship_Emily = pd.read_parquet('data/parquet/members.parquet')

#aply filter name
members_ship_Emily = members_ship_Emily[members_ship_Emily['name'] == cluster_our_name]

RA = clustersEmily['ra']
DEC = clustersEmily['dec']
age = clustersEmily['log_age_84'].iloc[0]
dist = (clustersEmily['distance_84']/1000).iloc[0]
Av = clustersEmily['a_v_84'].iloc[0]

# bar with fundamental parameters
st.sidebar.subheader("Hunt Fundamental parameters:")
st.sidebar.subheader("$log(age) = {}$".format(np.around(age,decimals=3)))
st.sidebar.subheader("$Dist. = {}~(kpc)$".format(np.around(dist,decimals=3)))
st.sidebar.subheader("$Av. = {}~(mag)$".format(np.around(Av,decimals=3)))

#Graphics
###############################################################################
# CMD Emily
grid_iso = get_iso_from_grid(age,(10.**0)*0.0152,filters,refMag, nointerp=False)
fit_iso = make_obs_iso(filters, grid_iso, dist, Av, gaia_ext = True) 

cor_obs_emily = members_ship_Emily['phot_bp_mean_mag']-members_ship_Emily['phot_rp_mean_mag']
absMag_obs_emily = members_ship_Emily['phot_g_mean_mag']

cmd_scatter_emily = pd.DataFrame({'G_BPmag - G_RPmag': cor_obs_emily, 'Gmag': absMag_obs_emily})

cmd_iso_emily = pd.DataFrame({'G_BPmag - G_RPmag': fit_iso['G_BPmag']-fit_iso['G_RPmag'], 
                        'Gmag': fit_iso['Gmag']})

cmd_scatter_emily = px.scatter(cmd_scatter_emily, x = 'G_BPmag - G_RPmag', y = 'Gmag', opacity=0.3)

cmd_emily_iso = px.line(cmd_iso_emily, x = 'G_BPmag - G_RPmag', y = 'Gmag', color_discrete_sequence=['red'])

fig_CMD_emily = go.Figure(data = cmd_scatter_emily.data + cmd_emily_iso.data).update_layout(coloraxis=cmd_scatter_emily.layout.coloraxis)
fig_CMD_emily.update_layout(xaxis_title= 'G_BP - G_RP (mag)',
                  yaxis_title="G (mag)",
                  coloraxis_colorbar=dict(title="M☉"),
                  yaxis_range=[20,5])

#CMD Wilton Dias
grid_iso = get_iso_from_grid(age,(10.**FeH_our)*0.0152,filters,refMag, nointerp=False)
fit_iso = make_obs_iso(filters, grid_iso, dist, Av, gaia_ext = True) 
cor_obs = members_ship['BPmag']-members_ship['RPmag']
absMag_obs = members_ship['Gmag']

cmd_scatter_dias = pd.DataFrame({'G_BPmag - G_RPmag': cor_obs, 'Gmag': absMag_obs})

cmd_iso = pd.DataFrame({'G_BPmag - G_RPmag': fit_iso['G_BPmag']-fit_iso['G_RPmag'], 
                        'Gmag': fit_iso['Gmag']})

CMD_scatter_dias = px.scatter(cmd_scatter_dias, x = 'G_BPmag - G_RPmag', y = 'Gmag', opacity=0.3)

CMD_iso_dias = px.line(cmd_iso, x = 'G_BPmag - G_RPmag', y = 'Gmag', color_discrete_sequence=['red'])

fig_CMD_dias = go.Figure(data = CMD_scatter_dias.data + CMD_iso_dias.data).update_layout(coloraxis=CMD_scatter_dias.layout.coloraxis)
fig_CMD_dias.update_layout(xaxis_title= 'G_BP - G_RP (mag)',
                  yaxis_title="G (mag)",
                  coloraxis_colorbar=dict(title="M☉"),
                  yaxis_range=[20,5])

###############################################################################	
x = ['log(age)', 'Dist. (kpc)', 'Av.(mag)']
x1 = [1,2,3]
y1 = [age_our, dist_our, Av_our]
y2 = [age, dist, Av]

# criar subplots individuais
fig_parameters_our, axs = plt.subplots(nrows=1, ncols=3)

# definir a largura das barras
bar_width = 0.35

for i in range(3):

    pos = np.arange(len(x1)) + bar_width
    
    axs[i].bar(x1[i], y1[i], bar_width, alpha=0.5)
    axs[i].bar(x1[i]+ bar_width, y2[i], bar_width, alpha=0.5)
    axs[i].set_xlabel(x[i])
    axs[i].set_xticks([])
    
fig_parameters_our.legend(['Our', 'Hunt'])
fig_parameters_our.tight_layout()

###############################################################################	
# clusters in common
cluster01 = np.genfromtxt('data/log-results-eDR3.txt', delimiter=';', names = True, 
                        dtype=None, encoding=None, autostrip=True)

cluster02 = pd.read_parquet('data/parquet/clusters.parquet')
cluster02 = cluster02.to_records()
ab = np.intersect1d(cluster01['name'],cluster02['name'])

#common ind
ind_commom = np.where(np.in1d(cluster02['name'], ab))[0]
cluster02 = cluster02[ind_commom]

#dist
dist_dt = pd.DataFrame({'dist': cluster01['dist'], 'distance_84': cluster02['distance_84']})
scatter_dist = px.scatter(dist_dt, x='Our', y='Hunt', opacity=0.3)
fig_dist = go.Figure(data=scatter_dist)
# fig_dist.update_layout(aspectratio=dict(x=1, y=1))

#age
age_dt = pd.DataFrame({'age': cluster01['age'], 'log_age_84': cluster02['log_age_84']})
scatter_age = px.scatter(age_dt, x='Our', y='Hunt', opacity=0.3)
fig_age = go.Figure(data=scatter_age)
# fig_age.update_layout(aspectratio=dict(x=1, y=1))

#av
age_dt = pd.DataFrame({'Av': cluster01['Av'], 'a_v_84': cluster02['a_v_84']})
scatter_av = px.scatter(age_dt, x='Our', y='Hunt')
fig_av = go.Figure(data=scatter_av)
# fig_av.update_layout(aspectratio=dict(x=1, y=1))



container1 = st.container()
col1, col2, col3  = st.columns(3)

with container1:
    with col1:
        st.caption("CMD Hunt")
        st.plotly_chart(fig_CMD_emily, use_container_width=True)

    with col2:
        st.caption("CMD our")
        st.plotly_chart(fig_CMD_dias, use_container_width=True)
        
    with col3:
        st.caption("Comparison of fundamental parameters")
        st.pyplot(fig_parameters_our)

container2 = st.container()
col4, col5, col6  = st.columns(3)

with container2:
    with col1:
        st.caption("Distance catalog")
        st.plotly_chart(fig_dist, use_container_width=True)

    with col2:
        st.caption("Age catalog")
        st.plotly_chart(fig_age, use_container_width=True)
        
    with col3:
        st.caption("Av catalog")
        st.plotly_chart(fig_av, use_container_width=True)





























