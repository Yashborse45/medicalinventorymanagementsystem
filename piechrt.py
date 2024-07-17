import streamlit as st
import pandas as pd
import plotly.express as px
import io

def main():
    st.title("Medical Inventory Worldwide Sales")

    """
    **Data Preparation**
    """

    # No need to install pandas as it's likely already installed with Streamlit
    data = """
    Sr.NO,user_id,Med_name,Expiry_date,Quantity,Amount
    1,3,Vicks,2024-05-02,15,19.99
    2,3,Candida,2023-11-21,20,64
    3,3,Paracetamol,2023-04-14,33,92
    4,3,Miconazole 3,2023-09-02,10,28
    ... (rest of the data omitted for brevity) ...
    50,3,Propanol Hydrochloride,2023-09-10,12,61
    """


    df = pd.read_csv(io.StringIO(data))

    """
    **Pie Chart for Total Sales by Medicine**
    """

    pie_chart = px.pie(df, names='Med_name', values='Quantity', title='Total Sales by Medicine',
                       color_discrete_sequence=px.colors.sequential.Plasma)  # Add color customization

    # Display the pie chart
    st.plotly_chart(pie_chart)

if __name__ == "__main__":
    main()
