import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt



# Define your usernames and passwords
USERS = {
    "admin": "mckeil",
    "tyler": "mckeil",
    "michael": "mckeil",
    "marcus": "mckeil",
    # Add more users as needed
}


# Function to check if the username and password are correct
def check_password():
    def password_entered():
        if st.session_state["username"] in USERS and st.session_state["password"] == USERS[
            st.session_state["username"]]:
            st.session_state["authenticated"] = True
            del st.session_state["username"]
            del st.session_state["password"]
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)

        if st.session_state["authenticated"] == False:
            st.error("Invalid username or password")
        return False
    else:
        return True


# Main function to run the app
def main():
    if check_password():
        st.title("Welcome to the Streamlit App")
        st.write("You are successfully logged in.")

        # Load the Actual and Budget data from the provided CSV files
        actual_data = pd.read_csv("./Actual.csv")
        budget_data = pd.read_csv("./Budget.csv")

        # Convert date columns to datetime
        actual_data['Last Discharge Port Depart'] = pd.to_datetime(actual_data['Last Discharge Port Depart'])
        actual_data['Discharge Port Depart'] = pd.to_datetime(actual_data['Discharge Port Depart'])
        budget_data['Last Discharge Port Depart'] = pd.to_datetime(budget_data['Last Discharge Port Depart'])
        budget_data['Discharge Port Depart'] = pd.to_datetime(budget_data['Discharge Port Depart'])

        # Streamlit app
        st.title('Actual vs Budget Data Analysis')

        # Date selectors
        start_date = st.date_input('Start Date', value=datetime(2024, 1, 1))
        end_date = st.date_input('End Date', value=datetime(2024, 12, 31))

        # Convert Streamlit date inputs to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Define the filtering and computation logic
        def filter_and_compute_time(data):
            conditions = [
                ((start_date < data['Last Discharge Port Depart']) &
                 (data['Last Discharge Port Depart'] < data['Discharge Port Depart']) &
                 (data['Discharge Port Depart'] < end_date)),
                ((start_date < data['Last Discharge Port Depart']) &
                 (data['Last Discharge Port Depart'] < end_date) &
                 (end_date < data['Discharge Port Depart'])),
                ((data['Last Discharge Port Depart'] < start_date) &
                 (start_date < data['Discharge Port Depart']) &
                 (data['Discharge Port Depart'] < end_date)),
                ((data['Last Discharge Port Depart'] < start_date) &
                 (start_date < end_date) &
                 (end_date < data['Discharge Port Depart']))
            ]

            choices = [
                (data['Discharge Port Depart'] - data['Last Discharge Port Depart']),
                (end_date - data['Last Discharge Port Depart']),
                (data['Discharge Port Depart'] - start_date),
                (end_date - start_date)
            ]

            data['Recognized Time'] = pd.to_timedelta(0)  # Initialize the Time column
            for condition, choice in zip(conditions, choices):
                data.loc[condition, 'Recognized Time'] = choice

            # Convert Time to days with 2 decimal precision
            data['Recognized Time'] = data['Recognized Time'].dt.total_seconds() / (24 * 3600)

            # Calculate Actual Revenue
            data['Total Time'] = data['Total Time'].astype(float)
            data['Total Revenue'] = data['Total Revenue'].astype(float)
            data['Recognized Revenue'] = data.apply(
                lambda row: row['Total Revenue'] * (row['Recognized Time'] / row['Total Time']) if row[
                                                                                                       'Total Time'] != 0 else 0,
                axis=1)
            data['Recognized Revenue'] = data['Recognized Revenue'].round(2)
            data['Recognized Time'] = data['Recognized Time'].round(2)
            data['Total Revenue'] = data['Total Revenue'].round(2)
            return data[
                conditions[0] | conditions[1] | conditions[2] | conditions[3]
                ]

        def daily_revenue(data, start_date, end_date):
            conditions = [
                ((start_date < data['Last Discharge Port Depart']) &
                 (data['Last Discharge Port Depart'] < data['Discharge Port Depart']) &
                 (data['Discharge Port Depart'] < end_date)),
                ((start_date < data['Last Discharge Port Depart']) &
                 (data['Last Discharge Port Depart'] < end_date) &
                 (end_date < data['Discharge Port Depart'])),
                ((data['Last Discharge Port Depart'] < start_date) &
                 (start_date < data['Discharge Port Depart']) &
                 (data['Discharge Port Depart'] < end_date)),
                ((data['Last Discharge Port Depart'] < start_date) &
                 (start_date < end_date) &
                 (end_date < data['Discharge Port Depart']))
            ]

            choices = [
                (data['Discharge Port Depart'] - data['Last Discharge Port Depart']),
                (end_date - data['Last Discharge Port Depart']),
                (data['Discharge Port Depart'] - start_date),
                (end_date - start_date)
            ]

            data['Recognized Time'] = pd.to_timedelta(0)  # Initialize the Time column
            for condition, choice in zip(conditions, choices):
                data.loc[condition, 'Recognized Time'] = choice

            # Convert Time to days with 2 decimal precision
            data['Recognized Time'] = data['Recognized Time'].dt.total_seconds() / (24 * 3600)

            # Calculate Actual Revenue
            data['Total Time'] = data['Total Time'].astype(float)
            data['Total Revenue'] = data['Total Revenue'].astype(float)
            data['Recognized Revenue'] = data.apply(
                lambda row: row['Total Revenue'] * (row['Recognized Time'] / row['Total Time']) if row[
                                                                                                       'Total Time'] != 0 else 0,
                axis=1)
            data['Recognized Revenue'] = data['Recognized Revenue'].round(2)
            data['Recognized Time'] = data['Recognized Time'].round(2)
            data['Total Revenue'] = data['Total Revenue'].round(2)
            return data[
                conditions[0] | conditions[1] | conditions[2] | conditions[3]
                ]

        # Filter and compute time and actual revenue for Actual and Budget data
        filtered_actual_data = filter_and_compute_time(actual_data)
        filtered_actual_data = filtered_actual_data.rename(
            columns={'Discharge Port Depart': 'End Date', 'Last Discharge Port Depart': 'Start Date',
                     'Total Time': 'Total Trip Time'})
        filtered_budget_data = filter_and_compute_time(budget_data)
        filtered_budget_data = filtered_budget_data.rename(
            columns={'Discharge Port Depart': 'End Date', 'Last Discharge Port Depart': 'Start Date',
                     'Total Time': 'Total Trip Time'})

        # Group by Type and Vessel and calculate the total actual and budget revenue
        summary_actual = filtered_actual_data.groupby(['Type', 'Vessel']).agg(
            {'Recognized Revenue': 'sum'}).reset_index()
        summary_budget = filtered_budget_data.groupby(['Type', 'Vessel']).agg(
            {'Recognized Revenue': 'sum'}).reset_index()

        # **************************************************************************************
        # Initialize an empty list to store the dates
        date_list = []

        # Initialize current_date with start_date
        current_date = start_date

        # Loop from start_date to end_date
        while current_date < end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)  # Increment the current date by one day

        # Create a DataFrame from the date list
        actual_daily_df = pd.DataFrame(date_list, columns=['Start Day'])
        budget_daily_df = pd.DataFrame(date_list, columns=['Start Day'])

        # Create a new column 'Next Day' which is 'Start Date' + 1 day
        actual_daily_df['End Day'] = actual_daily_df['Start Day'] + timedelta(days=1)
        budget_daily_df['End Day'] = budget_daily_df['Start Day'] + timedelta(days=1)

        for index, row in actual_daily_df.iterrows():
            start_day = pd.to_datetime(row['Start Day'], format='%Y-%m-%d %H:%M:%S')
            end_day = pd.to_datetime(row['End Day'], format='%Y-%m-%d %H:%M:%S')
            temp_df = daily_revenue(actual_data, start_day, end_day)
            print(temp_df)
            summary = temp_df['Recognized Revenue'].sum()
            actual_daily_df.at[index, 'Recognized Daily Revenue'] = summary
        for index, row in budget_daily_df.iterrows():
            start_day = pd.to_datetime(row['Start Day'], format='%Y-%m-%d')
            end_day = pd.to_datetime(row['End Day'], format='%Y-%m-%d')
            temp_df = daily_revenue(budget_data, start_day, end_day)
            summary = temp_df.groupby(['Type']).agg(
                {'Recognized Revenue': 'sum'}).reset_index()
            budget_daily_df.at[index, 'Recognized Daily Revenue'] = sum(summary['Recognized Revenue'])

        summary = pd.merge(actual_daily_df, budget_daily_df, on=['Start Day', 'End Day'], how='inner',
                           suffixes=(' (Actual)', ' (Budget)'))
        summary['Variance'] = summary['Recognized Daily Revenue (Actual)'] - summary['Recognized Daily Revenue (Budget)']
        summary['Start Day'] = summary['Start Day'].dt.date
        summary['End Day'] = summary['End Day'].dt.date
        st.write(summary)
        plt.figure(figsize=(10, 6))
        plt.plot(summary['Start Day'], summary['Variance'], marker='o', linestyle='-', color='b')
        plt.title('Variance over Start Day')
        plt.xlabel('Start Day')
        plt.ylabel('Variance')
        plt.grid(True)
        st.pyplot(plt)

        # **************************************************************************************


        # Merge the actual and budget summaries
        summary = pd.merge(summary_actual, summary_budget, on=['Type', 'Vessel'], how='outer',
                           suffixes=(' (Actual)', ' (Budget)'))
        summary['Variance'] = summary['Recognized Revenue (Actual)'] - summary['Recognized Revenue (Budget)']

        # Calculate the totals
        total_actual = summary['Recognized Revenue (Actual)'].sum()
        total_budget = summary['Recognized Revenue (Budget)'].sum()
        total_variance = total_actual - total_budget

        # Create a DataFrame for the total row
        total_row = pd.DataFrame({
            'Type': ['Total'],
            'Vessel': [''],
            'Recognized Revenue (Actual)': [total_actual],
            'Recognized Revenue (Budget)': [total_budget],
            'Variance': [total_variance]
        })

        # Concatenate the total row to the summary DataFrame
        summary = pd.concat([summary, total_row], ignore_index=True)

        # Display the summarized results
        st.subheader('Summarized Results by Type and Vessel')
        st.write(summary)

        # Display the filtered and computed data
        st.subheader('Filtered and Computed Actual Data')
        st.write(filtered_actual_data[
                     ['Type', 'Vessel', 'Trip No', 'Start Date', 'End Date', 'Recognized Time', 'Trip Details',
                      'Total Load Quantity', 'Total Trip Time', 'Recognized Revenue', 'Total Revenue']
                 ])

        st.subheader('Filtered and Computed Budget Data')
        st.write(filtered_budget_data[
                     ['Type', 'Vessel', 'Trip No', 'Start Date', 'End Date', 'Recognized Time', 'Trip Details',
                      'Total Load Quantity', 'Total Trip Time', 'Recognized Revenue', 'Total Revenue']
                 ])

        # New section for summarizing daily dry bulk and liquid bulk
        st.subheader('Daily Summary of Dry Bulk and Liquid Bulk')



if __name__ == "__main__":
    main()
