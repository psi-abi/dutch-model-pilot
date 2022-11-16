import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import urllib.request
import json
import os
import ssl
import ast
import string
import random
from io import BytesIO
import xlsxwriter



############################################################
####################-PAGE SETUP-####################
############################################################

st.set_page_config(
    layout="wide", 
    page_title="Dutch-reverse Auction Pilot", 
    page_icon=":star:"
    )

st.sidebar.markdown("# Dutch-Reverse Auction Pilot")
st.sidebar.markdown("This tool provides recommendendations for Dutch-Reverse auctions.")
st.sidebar.markdown("Feed the User Inputs, and then select YES in the 'Submit Inputs' section. The recommendations will be generated in a few seconds. You can change any recommendation.")
st.sidebar.markdown("You can download the rule recommendations by clicking the 'Export data' button.")

link = '[Feedback](https://forms.office.com/r/sitNFfzSDJ)'
st.sidebar.markdown(link, unsafe_allow_html=True)
st.sidebar.markdown("")

############################################################



############################################################
####################-USER INPUTS-####################
############################################################

st.markdown("### User Inputs")
st.markdown("")



# @st.cache
def convert_df(df):
    # return df.to_csv(index=False).encode('utf-8')
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Rules')
    workbook = writer.book
    worksheet = writer.sheets['Rules']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    
    return processed_data



@st.cache
def getOutput(data):
    
    def allowSelfSignedHttps(allowed):
        # bypass the server certificate verification on client side
        if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
            ssl._create_default_https_context = ssl._create_unverified_context

    allowSelfSignedHttps(True)

    body = str.encode(json.dumps(data))

    url = 'http://8881f677-b6d8-4d43-b99c-5709f371e832.westeurope.azurecontainer.io/score'
    api_key = '2oujYRZIWlQdYd0eUZjUFJzp5Uo4FhQV' # Replace this with the API key for the web service

    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()

    except urllib.error.HTTPError as error:
        pass
    
    return result

####################

col1, col2, col3 = st.columns([1, 1, 1])



with col1:
    
    auction_name = st.text_input(
        label="Auction Name", 
        value=""
        )

    st.markdown("")

    baselinespend_usd = st.number_input("Baseline Spend", 1, 10**7)
    
    st.markdown("")
    
    commodity = st.selectbox(
        "Commodity", 
        ['CAPEX', 'Simple Packages', 'Logistics', 'RAU', 'Commercial', 'Packaging'], 
        index=0)
    
    
    
with col2:

    zone = st.selectbox(
        "Zone", 
        ['APAC', 'AFR', 'EUR', 'MAZ', 'NAZ', 'SAZ'], 
        index=0)

    st.markdown("")

    bestbid_usd = st.number_input("BFQ Spend", 1, 10**7)
    
    st.markdown("")
    
    invited_suppliers = st.slider("Invited Suppliers", 1, 20)

    

with col3:

    currency = st.selectbox("Currency", 
                            [
                                'AED','ARS','AUD','BOB','BRL','BWP','CAD','CHF','CLP','CNY','COP','CZK','DKK','DOP','ETB','EUR','GBP',
                                'GHC','GTQ','HKD','HNL','HUF','ILS','INR','JPY','KES','KRW','LSL','MUR','MWK','MXN','MYR','MZN','NAD',
                                'NGN','NOK','NZD','PEN','PLN','PYG','RUB','SDP','SEK','SGD','SZL','TRY','TZS','UAH','UGX','USD','UYU',
                                'VND','ZAR','ZMK'
                            ])    

    st.markdown("")

    auction_historic_total = st.number_input("Historical Spend", 1, 10**7)
    
    st.markdown("")

    submit_button = st.radio(label='Submit Inputs', options=['NO', 'YES'])
        


####################

data = {
    'auction_name'                   : auction_name,
    'date'                           : str(datetime.now()),
    'zone'                           : zone,
    'currency'                       : currency,
    'commodity'                      : commodity,
    'invited_suppliers'              : invited_suppliers,
    'baselinespend_local'            : baselinespend_usd,
    'bfq_local'                      : bestbid_usd,
    'auction_historic_total_local'   : auction_historic_total
}

name = ''

############################################################



############################################################
####################-ACI ENDPOINT-####################
############################################################

if submit_button == 'YES':
    
#     try:
        
    st.write("")
    st.markdown("### Auction Edge Recommendations")
    st.markdown("")
    # st.write("")

    ####################

    result = getOutput(data)        

    s = json.loads(result)
    x = ast.literal_eval(s)
    ae_rec = {}

    for i in range(len(x['index'])):
        ae_rec[x['index'][i]] = x['data'][i][0]

    
    if name == '':
        name = ae_rec['auction_name']
    
    ####################

    rule_cat = [
        'Show bid graph to all participants',
        'Show participant responses to other participants',
        'Hide countdown clock from participants',
    ]


    final_rec = {}



    col0, col1, col2 = st.columns([1,1,1])

    with col0:
        recc = st.selectbox(
            rule_cat[0],
            [ae_rec[rule_cat[0]], [i for i in ['Yes', 'No'] if i not in [ae_rec[rule_cat[0]]]][0]],
            index=0,
        )
        final_rec[rule_cat[0]] = recc

    with col1:
        recc = st.selectbox(
            rule_cat[1],
            [ae_rec[rule_cat[1]], [i for i in ['Yes', 'No'] if i not in [ae_rec[rule_cat[1]]]][0]],
            index=0,
        )
        final_rec[rule_cat[1]] = recc

    with col2:
        recc = st.selectbox(
            rule_cat[2],
            [ae_rec[rule_cat[2]], [i for i in ['Yes', 'No'] if i not in [ae_rec[rule_cat[2]]]][0]],
            index=0,
        )
        final_rec[rule_cat[2]] = recc

    st.write("")

    ####################

    col0, col1, col2 = st.columns([1,1,1])

    with col0:
        recc_runtime = st.number_input(
            label='Running time for the first lot (in Minutes)',
            min_value=0,
            max_value=1000,
            value=ae_rec['Running time for the first lot'],
            step = 5
        )
        final_rec['Running time for the first lot'] = str(recc_runtime) + ' Minutes'

    with col1:
        recc_lottime = st.number_input(
            label='Time between lot closing (in Minutes)',
            min_value=0,
            max_value=1000,
            value=ae_rec['Time between lot closing'],
            step = 5
        )
        final_rec['Time between lot closing'] = str(recc_lottime) + ' Minutes'

    with col2:
        recc_bidtime = st.number_input(
            label='Bid adjustment interval (in Seconds)',
            min_value=0,
            max_value=300,
            value=ae_rec['Bid adjustment interval'],
            step = 5
        )
        final_rec['Bid adjustment interval'] = str(recc_bidtime) + ' Seconds'

    st.write("")


    col0, col1, col2 = st.columns([1,1,1])

    with col0:
        recc_bidamount = st.number_input(
            label='Adjust bid amount by (in ' + currency + ')',
            min_value=0,
            max_value=10**7,
            value=ae_rec['Adjust bid amount by'],
        )
        final_rec['Adjust bid amount by (in ' + currency + ')'] = recc_bidamount

    with col1:
        recc_iniamount = st.number_input(
            label='Auction Starting Price (in ' + currency + ')',
            min_value=0,
            max_value=10**7,
            value=ae_rec['auction_initial_total'],
        )
        final_rec['Auction Starting Price (in ' + currency + ')'] = recc_iniamount

    with col2:
        recc = st.selectbox(
            'Allow participants to select bidding currency',
            ['No', 'Yes'],
            index=0,
        )
        final_rec['Allow participants to select bidding currency'] = recc

    st.write("")



    col0, col1, col2 = st.columns([1,1,1])

    with col0:
        recc = st.selectbox(
            'Require participant to give a reason for declining to bid',
            ['No', 'Yes'],
            index=0,
        )
        final_rec['Require participant to give a reason for declining to bid'] = recc

    with col1:
        recc = st.selectbox(
            'Hide the number of bidders by using the same participant alias',
            ['No', 'Yes'],
            index=0,
        )
        final_rec['Hide the number of bidders by using the same participant alias'] = recc

    with col2:
        st.write("")
        st.write("")
        recc = st.selectbox(
            'Enable approval for team grading',
            ['No', 'Yes'],
            index=0,
        )
        final_rec['Enable approval for team grading'] = recc

#     except:
#         st.error("Please check your inputs")
#         st.stop()


    ### Default values
    final_rec['Default Grading Method'] = 'Select'
    final_rec['Adjust bid amount by'] = 'Nominal amount'


    df = pd.DataFrame(final_rec.values(), index=final_rec.keys(), columns=['Value'])
    df = df.reset_index(drop=False).rename(columns={'index' : 'ID'}).astype('str')
    
    df_xlsx = convert_df(df)
        
    st.download_button(
        label="Export data",
        data=df_xlsx,
        file_name = name + '.xlsx',
        )

    st.sidebar.markdown(f"## Please use auction name '{name}' while conducting the auction on Ariba")
