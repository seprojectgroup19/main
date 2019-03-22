import sqlalchemy as sqla


def read_auth():
    """
    Function to read authentication file to save time for each script
    :return: Key for JCDecaux, JCDecaux contract, engine for SQL database
    """
    with open("../authentication.txt") as f:
        auth = f.read().split("\n")

    # Authentication data from file
    bikes_key = auth[0]
    contract = auth[1]
    url = auth[3]
    log = auth[4]
    pwd = auth[5]
    port = auth[6]
    db = auth[7]

    # Connect to SQL database
    eng = "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(log, pwd, url, port, db)
    engine = sqla.create_engine(eng, echo=False)
    return bikes_key, contract, engine