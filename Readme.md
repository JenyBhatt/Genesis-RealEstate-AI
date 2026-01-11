#Genesis-RealEstate-AI

Overview :
*metadata dataset is being used which is obtained by web scraping magicbricks site for houses in bangalore. Web scraping forms a dataset which is cleaned 
using pandas and combined with the rented house dataset to obtain a brief analysis of average rent rate of the particular area. This is ultimately calculated
using formulas and compared with the buy rate of each property over a tenure of 20yrs, on the basis of which, a buy-rent decision is made and added furthur to
the dataset. An AI chatbot is integrated which examines the dataset to provide appropriate responses.

UI(frontend) : 
Streamlit is being used for website UI. 

Hybrid RAG implementation :
FAISS is being used as a functional element to perform vector embeddings(for semantic search) which is added as a new column (statement) in metadata.csv
    * **Pandas:** Handles all hard math (EMI, ROI) to ensure zero calculation errors.
    * **GPT-4o:** Acts as the 'Financial Advisor' synthesizing the data into human-readable advice and query analysis.
GPT 4-o is used for the categorization of query mood to make the process more efficient. How-
ever, we are not using it for calculation purposes; for that, we completely rely on pandas and
dataset calculations.

The Backend uses FASTAPI and UVICORN with two API endpoints :/filter and /chat.
    * **/filter : for the structured table view
    * **/chat   : for AI conversations

Matplotlib is used to print the wealth projection graph over 20 years.


#Preview for the website : 

<img width="1912" height="910" alt="Screenshot 2026-01-10 183316" src="https://github.com/user-attachments/assets/aec5f2eb-a110-4ba4-9047-aa620ac76993" />

#Obtain EMI and Loan calculation using Mortgage calculator using AI chatbot 

<img width="378" height="812" alt="Screenshot 2026-01-10 183330" src="https://github.com/user-attachments/assets/b19a2feb-f371-4c02-a7e9-16c6932041b0" />

#AI Chatbot preview

<img width="1920" height="1080" alt="Screenshot (278)" src="https://github.com/user-attachments/assets/c344d20f-2e4c-4376-b937-0afcb5676166" />


#Graphical data with explanatory analysis

<img width="1885" height="916" alt="Screenshot 2026-01-10 183958" src="https://github.com/user-attachments/assets/81695850-690e-4e40-8649-6e039e2a18b3" />




