# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 12:22:52 2023

@author: whill
"""
import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import altair as alt
import datetime as datetime
from snowflake.snowpark.context import get_active_session
st.set_page_config(layout="wide")
session = get_active_session()
series_df = session.sql("""select distinct(VARIABLE_NAME) as Date_List FROM CPIVSFEDFUNDS""")
queried_series_df=series_df.to_pandas()
formatted_series = [str(value[0]) for value in queried_series_df.values]
series_select = st.multiselect('Select Series for Chart', formatted_series,formatted_series[0])


# title and instruction
st.title("Cybersyn Inflation Data Analysis")


date1 = st.text_input("Enter start date:", value="2018-01-01", max_chars=30, key="date1")
date2 = st.text_input("Enter end date:", value="2023-07-31", max_chars=30, key="date2")

if st.button("View Charts for Dates"):
    if date1 and date2:
        series_select_str = ", ".join([f"'{series}'" for series in series_select])
        df_cpi = session.sql(f"""SELECT * From CPIVSFEDFUNDS where Date >= '{date1}' and Date <= '{date2}' and VARIABLE_NAME in ({series_select_str})""")
        queried_df_cpi=df_cpi.to_pandas()
        condition_list = [((queried_df_cpi['VARIABLE_NAME'] == 'CPI: All items, Not seasonally adjusted, Monthly'),'CPI: All items, Not seasonally adjusted, Monthly'),
                          ((queried_df_cpi['VARIABLE_NAME'] == 'CPI: All items less shelter, Not seasonally adjusted, Monthly'),'CPI: All items less shelter, Not seasonally adjusted, Monthly'),
                          ((queried_df_cpi['VARIABLE_NAME'] == 'CPI: All items less food and energy, Not seasonally adjusted, Monthly'),'CPI: All items less food and energy, Not seasonally adjusted, Monthly'),
                          ((queried_df_cpi['VARIABLE_NAME'] == 'Personal Consumption Expenditures: Chain-type Price Index, Seasonally adjusted, Monthly, Index 2012=100'),'Personal Consumption Expenditures: Chain-type Price Index, Seasonally adjusted, Monthly, Index 2012=100')]
        if len(queried_df_cpi['VARIABLE_NAME'].unique()) > 1  or 'Federal Funds Effective Rate' not in queried_df_cpi['VARIABLE_NAME'].unique():
            for condition in condition_list:
                
                queried_df_cpi.loc[condition[0], 'VALUE'] = np.round(queried_df_cpi.loc[condition[0], 'VALUE'].pct_change(12),3)
                queried_df_cpi.loc[condition[0],'VARIABLE_NAME'] = f"""{condition[1]}, Percent Change YoY"""
                queried_df_cpi.dropna(inplace=True)
        reshaped_df =  queried_df_cpi.melt(id_vars=['VARIABLE_NAME', 'DATE'], value_vars=['VALUE'], var_name='Column', value_name='Value')
        fig2 = px.line(reshaped_df, x='DATE', y='Value', color='VARIABLE_NAME',
                      labels={'DATE': '<b>Fiscal Date Ending</b>', 'Value': '<b>Value</b>'},render_mode='svg')
        fig2.update_layout(legend=dict(
            yanchor="bottom",
            y=-1,
            xanchor="center",
            x=0.5))
        fig2.update_layout(yaxis_tickformat='.2%')
        st.plotly_chart(fig2, use_container_width=True)
        