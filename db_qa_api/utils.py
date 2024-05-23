import re, csv, os
from dotenv import load_dotenv
import pyodbc
import pandas as pd
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

def sk_execute_sql_query(sql_query):
    """
    Executes the SQL query and returns the result.

    Args:
        sql_query (str): The SQL query to execute.
        db_name (str): The name of the SQLite database.
    Returns:
        pandas.DataFrame: The result of the SQL query.
    """

    try:
        load_dotenv()
        # Connect to the SQL Server database
        conn = pyodbc.connect(
            f"""Driver={os.getenv('ODBC_DRIVER')};
               Server={os.getenv('DATABASE_SERVER')};
               Database={os.getenv('DATABASE_NAME')};
               UID={os.getenv('DATABASE_USERNAME')};
               PWD={os.getenv('DATABASE_PASSWORD')};
               Encrypt=yes;
               TrustServerCertificate=no;
               Connection Timeout=30"""
        )

        # Execute the SQL query
        result = pd.read_sql_query(sql_query, conn)
        return result
    except pyodbc.Error as e:
        print(f"Error executing SQL query: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()


def preprocess_sk_response(response):
    """
    Preprocesses the response from the API.

    Args:
        response (str): The response from the API.
    Returns:
        str: The preprocessed response.
    """

    # if response contains <summary> and not contains </summary> then add </summary> to the response at the end
    # if "<summary>" in response and "</summary>" not in response:
    #     response = response + "</summary>"

    if "<sql_query>" in response and "</sql_query>" not in response:
        response = response + "</sql_query>"

    # Preprocess the result
    match = (
        re.search(r"<sql_query>(.*?)</sql_query>", response, re.DOTALL)
    )
    if match:
        sql_query = match.group(1).strip()
    else:
        sql_query = None
    print("SQL QUERY : ",sql_query)

    return sql_query


def sk_query(question):
    # Configure Kernel
    kernel = sk.Kernel()
    load_dotenv()
    deployment, api_key, endpoint = (
        os.getenv('DEPLOYMENT_ENV'),
        os.getenv('API_KEY'),
        os.getenv('API_ENDPOINT'),
    )
    kernel.add_chat_service(
        "chat_completion", AzureChatCompletion(deployment, endpoint, api_key)
    )
    print("")
    # Load database Metas
    # with open('database-meta.yaml', 'r') as aw:
    # table_info = yaml.safe_load(aw)

    # Initialize an empty list to hold all the data
    all_data = []
    with open("data/table-cols-constraints.csv", "r", newline="") as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Append each row to the list
            all_data.append(row)

    # Import prompt-template
    with open("static/crypto_prompt.txt", "r") as skp:
        table_prompts = skp.readlines()

    db_prompts = kernel.create_semantic_function(
        "{{$input}}"
        + "\n\n\n"
        + str(table_prompts)
        + "\n\n\n Database info table \n"
        + str(all_data)
        + "\n\n\n",
        temperature=0.0
    )

    result = db_prompts(question)
    # print(
    #     "\n====================================================================\n",
    # result,
    #     "\n====================================================================",
    # )
    query = preprocess_sk_response(result.variables.input)

    df = sk_execute_sql_query(query)
    return query, df