import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
from streamlit_kpi import streamlit_kpi
import pytz
import datetime
import time



# Function to convert date to integer representation
def date_to_int(date):
    return int(date.strftime("%Y%m%d"))

# Function to convert integer representation to date
def int_to_date(int_date):
    return datetime.date(int_date // 10000, (int_date // 100) % 100, int_date % 100)


def fetchTotalDataNumber(sensor_name, start_date, end_date, sensor_id,slave_address):

    API_URL = "https://bontonfoods.aqualinkbd.com/apiV2/datatables"
    params = {
        "sensor_name": sensor_name,
        "startdate": start_date,
        "enddate": end_date,
        "sensor_id":sensor_id,
        "slave_address": slave_address,    
    }         
    response = requests.post(API_URL, data=params)
    total_data = response.json()["total"]

    return total_data


    
@st.cache_data(show_spinner=True)
def fetch__individual_data(sensor_name, start_date, end_date, sensor_id,slave_address,dataview):
      
      API_URL = "https://bontonfoods.aqualinkbd.com/apiV2/datatables"
      
      params = {
        "sensor_name": sensor_name,
        "startdate": start_date,
        "enddate": end_date,
        "sensor_id":sensor_id,
        "slave_address": slave_address,
        "page":0,
        "dataview":dataview,    
      }

      response = requests.post(API_URL, data=params)
      if response.status_code == 200:
        data = response.json()["data"]
        return data   # Slices data within the specified range 
      else:
        st.error(f"Failed to fetch data from the API. Status code: {response.status_code}")
        return None

@st.cache_data(show_spinner=False)
def fetch_both_data(start_date,end_date,slave_address_temp,slave_address_hum,dataview):
    
    API_URL = "https://bontonfoods.aqualinkbd.com/apiV2/datatables"
    params = {
        "sensor_name": "temp",
        "startdate": start_date,
        "enddate": end_date,
        "slave_address": slave_address_temp,
        "page":0,
        "dataview":dataview,    
    }

    response = requests.post(API_URL, data=params)
    if response.status_code == 200:
        temp_data = response.json()["data"]
    
    params = {
        "sensor_name": "hum",
        "startdate": start_date,
        "enddate": end_date,
        "slave_address": slave_address_hum,
        "page":0,
        "dataview":dataview,    
    }


    response1 = requests.post(API_URL,data = params)

    if response1.status_code == 200:
        hum_data = response.json()["data"]
    
    return temp_data,hum_data



def fetch_data(page,url):


    params = {
        "sensor_name": "temp",
        "startdate": '2024-05-01',
        "enddate": '2024-05-10',
        "sensor_id":151,
        "slave_address":1,
    }

    if page <= 1:
        url = "https://bontonfoods.aqualinkbd.com/apiV2/datatables"
    else:
        url = url

    response = requests.post(url,data = params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
        return None
    

    
def test_pagination():

    start = time.time()

    all_data = []
    
    current_page = 1
    total_pages = None
    url = ''
    while True:
        data = fetch_data(current_page,url)
        if data is None:
            break
        if total_pages is None:
            total_pages = data["last_page"]
        current_page += 1
        url = data['next_page_url']
        if current_page > total_pages:
            break
    
    end = time.time()
    print(end-start)
 

# Main function to create Streamlit UI
def main():

  
    st.title("Sensor Data Visualization")

    # Select sensor ID
    sensor_id = st.selectbox("Select Sensor ID", ["151","152"])

    # Select sensor type
    sensor_name = st.selectbox("Select Sensor Name", ["temp", "hum","both"])

    # Select slave address
    slave_address = st.selectbox("Select Slave Address", ["1", "2", "3","4","5","6"])

    # Date range
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
  
    total_data = fetchTotalDataNumber(sensor_name, str(start_date), str(end_date), sensor_id, slave_address)

    if(start_date == end_date):
        end_date = start_date + datetime.timedelta(days=1)
    
    start_date_int = date_to_int(start_date)
    end_date_int = date_to_int(end_date)

    start_date_slider = st.slider("Start Date", min_value=start_date_int, max_value=end_date_int, value=start_date_int)
    end_date_slider = st.slider("End Date", min_value=start_date_int, max_value=end_date_int, value=end_date_int)

    # Convert slider values back to date objects
    start_date_selected = int_to_date(start_date_slider)
    end_date_selected = int_to_date(end_date_slider)


    if sensor_name == "both":
       slave_address_temp =  st.selectbox("Select Slave Address For Temperature", ["1", "2", "3","4","5","6"])
       slave_address_hum = st.selectbox("Select Slave Address For Humidity", ["1", "2", "3","4","5","6"])

    # Fetch data button
    if st.button("Fetch Data"):
        
        if start_date and end_date:
                      
            start_date_selected = pd.to_datetime(start_date_selected).tz_localize(None).tz_localize('UTC')
            end_date_selected = pd.to_datetime(end_date_selected).tz_localize(None).tz_localize('UTC')

            if sensor_name != "both":
             data = fetch__individual_data(sensor_name, str(start_date), str(end_date), sensor_id, slave_address,total_data)
        
             if data:
        
                # Display data in a table
                st.subheader("Data Table")
                df = pd.DataFrame(data) 
                
               # Convert 'created_at' column to datetime and localize to UTC
                df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('UTC')

               

               # Filter DataFrame based on selected date range
                filtered_df = df[(df['created_at'] >= start_date_selected) & (df['created_at'] <= end_date_selected)]              

                
                st.write(len(filtered_df))
                st.write(filtered_df)
               
                df = filtered_df

                # Calculate and display statistical features
                st.subheader("Statistical Features")
                mean_value = df['value'].mean()
                max_value = df['value'].max()
                min_value = df['value'].min()
                q1 = df['value'].quantile(0.25)
                q3 = df['value'].quantile(0.75)

                mean_value = round(mean_value,2)
                max_value = round(max_value,2)
                min_value = round(min_value,2)

                st.metric("Mean:",mean_value)
                st.metric("Minimum Value:",min_value)
                st.metric("Maximum Value:",max_value)
  
                # st.markdown(f"**Mean:** <span style='color:#39FF14'>{mean_value:.2f}</span>", unsafe_allow_html=True)
                # st.markdown(f"**Highest Value:** <span style='color:#39FF14'>{max_value}</span>", unsafe_allow_html=True)
                # st.markdown(f"**Lowest Value:** <span style='color:#39FF14'>{min_value}</span>", unsafe_allow_html=True)
                # st.markdown(f"**Q1 (25th percentile):** <span style='color:#39FF14'>{q1:.2f}</span>", unsafe_allow_html=True)
                # st.markdown(f"**Q3 (75th percentile):** <span style='color:#39FF14'>{q3:.2f}</span>", unsafe_allow_html=True)

                # Plot data using Matplotlib
                st.subheader("Line Chart")
                fig, ax = plt.subplots(figsize=(10, 6))

                # Set background color
                fig.patch.set_facecolor('#262730')  # Background color
                ax.patch.set_facecolor('#262730')  # Background color

                
                ax.plot(df['created_at'], df['value'], marker='o', linestyle='-', color='#45DEA2')  # Neon green color
                ax.set_xlabel('Date', color='white')  # White color for x-axis label
                ax.set_ylabel('Sensor Value', color='white')  # White color for y-axis label
                ax.set_title('Sensor Data', color='white')  # White color for title
                plt.xticks(rotation=45, color='white')  # White color for x-axis tick labels
                plt.yticks(color='white')  # White color for y-axis tick labels
                plt.grid(True, color='white')  # White color for grid lines

                st.pyplot(fig)
               
            elif sensor_name == "both":

                 
                start_time = time.time()
             
                temp_data,hum_data = fetch_both_data(str(start_date), str(end_date) , slave_address_temp , slave_address_hum,total_data)

                temp_df = pd.DataFrame(temp_data)
                temp_df = temp_df[temp_df['sensor_name'] == "temp"] 
                hum_df = pd.DataFrame(hum_data)
                hum_df = hum_df[hum_df['sensor_name'] == "hum"] 

                temp_df['created_at'] = pd.to_datetime(temp_df['created_at']).dt.tz_convert('UTC')
                hum_df['created_at'] = pd.to_datetime(hum_df['created_at']).dt.tz_convert('UTC')

                # Filter DataFrame based on selected date range
                filtered_temp_df = temp_df[(temp_df['created_at'] >= start_date_selected) & (temp_df['created_at'] <= end_date_selected)] 
                filtered_hum_df =hum_df[hum_df['sensor_name'] == "hum"]     

                col1,col2 = st.columns(2)

                with col1:
                    st.subheader("Temperature Data")
                    st.write(filtered_temp_df)
                    st.subheader("Line_Chart")

                    st.subheader("Statistical Features")
                    mean_value = filtered_temp_df['value'].mean()
                    max_value = filtered_temp_df['value'].max()
                    min_value = filtered_temp_df['value'].min()
                 
                    mean_value = round(mean_value,2)
                    max_value = round(max_value,2)
                    min_value = round(min_value,2)

                    st.metric("Mean:",mean_value)
                    st.metric("Minimum Value:",min_value)
                    st.metric("Maximum Value:",max_value)

                    # st.markdown(f"**Mean:** <span style='color:#39FF14'>{mean_value:.2f}</span>", unsafe_allow_html=True)
                    # st.markdown(f"**Highest Value:** <span style='color:#39FF14'>{max_value}</span>", unsafe_allow_html=True)
                    # st.markdown(f"**Lowest Value:** <span style='color:#39FF14'>{min_value}</span>", unsafe_allow_html=True)
                    # st.markdown(f"**Q1 (25th percentile):** <span style='color:#39FF14'>{q1:.2f}</span>", unsafe_allow_html=True)
                    # st.markdown(f"**Q3 (75th percentile):** <span style='color:#39FF14'>{q3:.2f}</span>", unsafe_allow_html=True)

                    # Plot data using Matplotlib
                    st.subheader("Line Chart")
                    fig, ax = plt.subplots(figsize=(20, 10))

                    # Set background color
                    fig.patch.set_facecolor('#262730')  # Background color
                    ax.patch.set_facecolor('#262730')  # Background color

                
                    ax.plot(filtered_temp_df['created_at'], filtered_temp_df['value'], marker='o', linestyle='-', color='#45DEA2')  # Neon green color
                    ax.set_xlabel('Date', color='white')  # White color for x-axis label
                    ax.set_ylabel('Sensor Value', color='white')  # White color for y-axis label
                    ax.set_title('Sensor Data', color='white')  # White color for title
                    plt.xticks(rotation=45, color='white')  # White color for x-axis tick labels
                    plt.yticks(color='white')  # White color for y-axis tick labels
                    plt.grid(True, color='white')  # White color for grid lines
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("Humidity Data")
                    st.write(filtered_hum_df)
                    st.subheader("Line_Chart")

                    st.subheader("Statistical Features")
                    mean_value = filtered_hum_df['value'].mean()
                    max_value = filtered_hum_df['value'].max()
                    min_value = filtered_hum_df['value'].min()
                 
                    mean_value = round(mean_value,2)
                    max_value = round(max_value,2)
                    min_value = round(min_value,2)

                    st.metric("Mean:",mean_value)
                    st.metric("Minimum Value:",min_value)
                    st.metric("Maximum Value:",max_value)

                    # st.markdown(f"**Mean:** <span style='color:#39FF14'>{mean_value:.2f}</span>", unsafe_allow_html=True)
                    # st.markdown(f"**Highest Value:** <span style='color:#39FF14'>{max_value}</span>", unsafe_allow_html=True)
                    # st.markdown(f"**Lowest Value:** <span style='color:#39FF14'>{min_value}</span>", unsafe_allow_html=True)
                    # st.markdown(f"**Q1 (25th percentile):** <span style='color:#39FF14'>{q1:.2f}</span>", unsafe_allow_html=True)
                    # st.markdown(f"**Q3 (75th percentile):** <span style='color:#39FF14'>{q3:.2f}</span>", unsafe_allow_html=True)

                    # Plot data using Matplotlib
                    st.subheader("Line Chart")
                    fig, ax = plt.subplots(figsize=(20, 10))

                    # Set background color
                    fig.patch.set_facecolor('#262730')  # Background color
                    ax.patch.set_facecolor('#262730')  # Background color

                
                    ax.plot(filtered_hum_df['created_at'], filtered_hum_df['value'], marker='o', linestyle='-', color='#45DEA2')  # Neon green color
                    ax.set_xlabel('Date', color='white')  # White color for x-axis label
                    ax.set_ylabel('Sensor Value', color='white')  # White color for y-axis label
                    ax.set_title('Sensor Data', color='white')  # White color for title
                    plt.xticks(rotation=45, color='white')  # White color for x-axis tick labels
                    plt.yticks(color='white')  # White color for y-axis tick labels
                    plt.grid(True, color='white')  # White color for grid lines

                    st.pyplot(fig)

                    end_time = time.time()
                    st.write( end_time - start_time )
        

            


if __name__ == "__main__":
    main()