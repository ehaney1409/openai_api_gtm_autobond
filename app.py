# Load libraries
import pandas as pd
from pandas.io.json import json_normalize 
import numpy as np
import requests
import urllib.request
import json
from datetime import datetime
import datetime as dt
import streamlit as st
import openai
from bs4 import BeautifulSoup
import json
    

finaldf = pd.DataFrame()
st.title("Sprout Social GTM with Open AI")
st.markdown('---')
st.markdown('###### This app aims to enrich a **SELL TO** list of prospect companies and provide unique messaging based on the **SELL FROM** company information. Just follow the steps/prompts below. It''s easy!')
st.markdown('---')
st.title("Steps")
st.markdown('#### Step 1: Set and Generate SELL FROM info')
st.markdown('#### Step 2: Upload SELL TO List')
st.markdown('#### Step 3: Process with OpenAI')
st.markdown('#### Step 4: Download Enriched CSV')
st.markdown('---')

st.title("Prompts")
st.markdown('## Step 1: Set and Generate SELL FROM info')

st.markdown('#### :rotating_light: you must put in your own API KEY for this app to work :rotating_light:')
openai_key = st.text_input('Enter your OpenAI API Key Here')
sell_from = st.text_input('Input the company domain you want to SELL FROM ... i.e company.com')

with st.form("step_1"):
   
   st.markdown('##### :sparkle: Once you provide the data points above, click SUBMIT to preview the SELL FROM values')

   # Every form must have a submit button.
   submitted1 = st.form_submit_button("Submit")
   if submitted1:
        sell_from = 'https://' + sell_from
        #selling site
        #set URL to be enriched
        URL1 = sell_from
        #get content 
        page = requests.get(URL1)
        #transform content 
        soup = BeautifulSoup(page.content, "html.parser")
        #clean content
        souper = soup.text
        souperx = souper.replace("\n", "")
        #set prompt input from clean content
        selling_values = souperx[:1000]
        st.write(selling_values)


st.markdown('---')
st.markdown('## Step 2: Upload SELL TO List')

st.markdown('##### :rotating_light:  Your file should be a ONE column CSV file with DOMAIN as the column name and COMPANY.COM as the website format :rotating_light: ')

uploaded_file = st.file_uploader("Upload Here")
if uploaded_file is not None:
#process and format csv 
    testdf = pd.read_csv(uploaded_file)
    testdf['DOMAIN'] = 'https://' + testdf['DOMAIN'].astype(str)
    testlist = testdf.DOMAIN.values.tolist()
    st.write(testlist)

if 'selling_values' not in st.session_state:
    st.session_state.selling_values = None

st.markdown('---')
st.markdown('## Step 3: Process with OpenAI')

with st.form("step_3"):
   st.markdown('##### :rotating_light:  Click SUBMIT and allow the process to run completely before pressing DOWNLOAD DATA AS CSV :rotating_light: ')

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
        listx = testlist

        finaldf = pd.DataFrame()

        sell_from = 'https://' + sell_from
        #selling site
        #set URL to be enriched
        URLx = sell_from
        #get content 
        page = requests.get(URLx)
        #transform content 
        soup = BeautifulSoup(page.content, "html.parser")
        #clean content
        souper = soup.text
        souperx = souper.replace("\n", "")
        #set prompt input from clean content
        selling_values = souperx[:1000]

        for i in listx:
            try:
                #set URL to be enriched
                URL1 = i
                #get content 
                page = requests.get(URL1, timeout=10)
                #transform content 
                soup = BeautifulSoup(page.content, "html.parser")
                #clean content
                souper = soup.text
                souperx = souper.replace("\n", "")
                #set prompt input from clean content
                prompt_input = souperx[:1000]
                #build prompt
                prompt = f"""
                This is the content of the prospect company website {prompt_input}
                This is the prospect company website {URL1}
                This is the selling company's product offering: {selling_values}
                In a JSON format:
                - Give me the value proposition of the prospect company. In less than 50 words. In English. Casual Tone. Format is: "[Company Name] helps [target audience] [achieve desired outcome] and [additional benefit]"
                - Guess the target audience of each prospect company.(Classify and choose 1 from this list: [Sales Teams, Marketing Teams, Product Teams, HR teams, Customer Service Teams, Consumers, Data Teams, DevOps Teams, Programmers, Finance Teams])
                
                - Tell me where this company's headquarters is located. Format is: "City, State/Province"
                
                - Give me the industry of the prospect company. (Classify using this industry list: [Energy, Materials, Industrials, Consumer Goods, Health Care, Wellness & Fitness, Finance, Software, Communication, Entertainment, Utilities, Agriculture, Arts, Construction, Education, Legal, Manufacturing, Public Administration, Advertisements, Real Estate, Recreation & Travel, Retail, Transportation & Logistics])
                
                - Give me the market segment of the prospect company. (Classify using this industry list: [SMB, Mid-Market, Enterprise])
                - Tell me if the prospect company is B2B or B2C.
                - Include the original prospect company website mentioned above.
                format should be:
                {{"value_proposition": value_proposition,
                "target_audience": target_audience, 
                "headquarters": headquarters, 
                "industry": industry,
                "market_segment": market_segment,
                "business_model": business_model,
                "website": website}}
                JSON:
                """
                #authenticate openai
                openai.api_key = openai_key
                # Set up the model
                model_engine = "text-davinci-003"
                # Generate a response
                completion = openai.Completion.create(
                    engine=model_engine,
                    prompt=prompt,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                #access response text
                response = completion.choices[0].text
                #transform to json/dict
                json_object = json.loads(response, strict=False)
                #append to main df
                finaldf = finaldf.append(json_object, ignore_index=True)
                #print confirm
                st.write(i + " is done!")
            except Exception as e:
                #st.write(e)
                st.write(i + " has failed :(")
                continue
    


def convert_df_to_csv(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv().encode('utf-8')

st.markdown('---')
st.markdown('## Step 4: Download Enriched CSV')


st.download_button(
  label="Download data as CSV",
  data=convert_df_to_csv(finaldf),
  file_name='dmOpenAIgtm.csv',
  mime='text/csv'
)
