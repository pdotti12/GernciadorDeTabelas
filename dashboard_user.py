import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# Create tabs for Upload and Filters
tab1, tab2 = st.tabs(["Upload Files", "Filters and Analysis"])

# Let the user upload multiple CSV files on the first tab
with tab1:
    uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type="csv")

# Check if files were uploaded
if uploaded_files:
    df_list = []
    table_names = []

    # Process each uploaded file
    for file in uploaded_files:
        df_list.append(pd.read_csv(file))
        table_names.append(file.name)

    # Move to the Filters tab if files were uploaded
    with tab2:
        selected_table = st.selectbox("Choose a table", table_names)

        # Load the selected table
        df = df_list[table_names.index(selected_table)]
        st.write(f"## Table: {selected_table} Analysis")

        # Sidebar filters
        st.sidebar.header("Filters")

        # Filter C0_missing < threshold
        if 'C0_missing' in df.columns:
            threshold = st.sidebar.number_input("C0_missing <= threshold", min_value=0.0, max_value=1.0, step=0.05, value=0.2)
            filtered_df = df[df['C0_missing'] <= threshold]
        else:
            filtered_df = df.copy()

        # "p value" filter using number_input with 0.01 step
        p_threshold = st.sidebar.number_input("Select Threshold for p value", min_value=0.0, max_value=1.0, step=0.01, value=0.05)

        # "Maximum missing data" filter using number_input with 0.01 step
        miss_threshold = st.sidebar.number_input("Maximum missing data", min_value=0.0, max_value=1.0, step=0.01, value=0.1)

        # Filter Category (if available)
        if 'Category' in df.columns:
            categories = st.sidebar.multiselect("Filter by Category", options=df['Category'].unique(), default=df['Category'].unique())
            filtered_df = filtered_df[filtered_df['Category'].isin(categories)]

        # Apply additional filtering based on p_threshold and miss_threshold
        ANCOVA_cols = filtered_df.filter(regex='ANCOVA').columns.to_list()
        miss_cols = filtered_df.filter(regex='missing').columns.to_list()

        # Filter based on p_threshold and miss_threshold
        filtered_df = filtered_df[
            (filtered_df[ANCOVA_cols] < p_threshold).all(axis=1) &  # All ANCOVA (p-value) columns must be below the threshold
            (filtered_df[miss_cols] <= miss_threshold).all(axis=1)   # All missing columns must be below the missing threshold
        ]

        # Display filtered data
        st.write("### Filtered Data")
        st.dataframe(filtered_df)

        # Display the complete table below
        st.write("### Complete Table (Unfiltered)")
        st.dataframe(df)
else:
    with tab2:
        st.warning("Please upload one or more CSV files in the 'Upload Files' tab.")
