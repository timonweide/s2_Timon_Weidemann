import streamlit as st
import pandas as pd
from news_llm_functions import get_gdelt_params, get_gdelt_articles, get_summary, generate_pdf

def main():
    
    # Initialize Streamlit app
    st.title("🌍 World News Summarizer")
    st.write("Ask a question about a current or historic world event. For example: 'What happened in Barcelona in 2020?'")
    st.write("Your query can include a specific action (e.g., 'football' or 'protest'), region (e.g., 'Spain' or 'Barcelona') and timespan (e.g. 'last year' or 'February to April 2023').")
    st.write("The app will summarize and recommend news articles related to your query using the GDELT API and the cohere LLM model.")
    st.divider()
    
    # Get user input
    user_prompt = st.text_input("Enter your question:")
    submitted = st.button("🗞️ Get News Summary")
    success = False
    
    # Proceed when button is clicked
    if user_prompt or submitted:
        
        # Create status tracking
        with st.status("⏳ Processing your request..."):

            # Check if user input is empty
            if not user_prompt:
                st.info("⚠️ Please enter a question to proceed.")
            else:

                # Use the LLM-based function to extract query, startdate, and enddate
                st.write("⚙️ Transforming query...")
                gdelt_params = get_gdelt_params(user_prompt)

                # Check if the response is valid
                if not isinstance(gdelt_params, dict):
                    st.error(f"⚠️ Error transforming query. Response: {gdelt_params}")
                else:
                
                    # Query the GDELT API using the parameters
                    st.write("📥 Fetching articles...")
                    gdelt_articles = get_gdelt_articles(gdelt_params)
                    
                    # Check if the response is valid
                    if not isinstance(gdelt_articles, dict):
                        st.error(f"⚠️ Error fetching articles. Response: {gdelt_articles}")
                    else:
                        
                        # Use the LLM-based function to generate a summary and recommendations based on the articles
                        st.write("📝 Generating summary...")
                        summary = get_summary(user_prompt, gdelt_articles)

                        # Check if the response is valid
                        if not isinstance(summary, str):
                            st.error(f"⚠️ Error generating summary. Response: {summary}")
                        else:
                            success = "✅ Summary generated successfully!"
                            st.success(success)

        # Check if request was successful
        if success:

            # Create tabs to order output
            tab1, tab2, tab3 = st.tabs(["Summary", "Articles", "Parameters"])

            # Create summary output tab
            with tab1:
                st.subheader("📃 Summary")
                st.write(summary)

                # Add download button for summary
                pdf_bytes = generate_pdf(user_prompt, summary)
                st.download_button(
                    label="📁 Download Summary as PDF",
                    data=pdf_bytes,
                    file_name="news_summary.pdf",
                    mime="application/pdf"
                )
            
            # Create articles output tab
            with tab2:
                st.subheader("📰 Articles")
                st.write("Here are the articles used to generate the summary.")
                
                # Display articles in table format
                st.divider()
                st.write("Dataframe")
                st.dataframe(pd.json_normalize(gdelt_articles, record_path='articles'))

                # Display articles in JSON format
                st.divider()
                st.write("JSON")
                st.json(gdelt_articles)

            # Create parameters output tab
            with tab3:
                st.subheader("🛠️ Parameters")
                st.write("Here are the parameters used to query the GDELT API.")

                # Display parameters in table format
                st.divider()
                st.write("Dataframe")
                st.dataframe(pd.json_normalize(gdelt_params))

                # Display parameters in JSON format
                st.divider()
                st.write("JSON")
                st.json(gdelt_params)

# Launch the Streamlit app
if __name__ == "__main__":
    main()
