import os

def get_mysql_uri():
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = 33060 if host == "localhost" else 3306
    password = os.environ.get("MYSQL_PASSWORD", "abc123")
    user, db_name = "root", "allocation"
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"

def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else 80
    return f"http://{host}:{port}"
