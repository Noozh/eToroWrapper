import json

def parse_wallet(wallet):
    """
    Gather some key data about an active

    :param wallet: Raw data of user's wallet gathered from Web IDE
    :type wallet: string

    :return: Well formatted dict
    :rtype: dict
    """
    output = {}
    wallet = wallet.split("\n")
    output["available"] = wallet[0]
    output["invested"] = wallet[2]
    output["profit"] = wallet[4]
    output["total"] = wallet[6]
    return output

def str_clean(str, charlist):
    """
    Delete from a provided string a specific list of characters

    :param str: String to clean
    :type str: string
    :param charlist: List of target characters
    :type list: list

    :return: Well formatted string
    :rtype: string
    """
    for char in charlist:
        str = str.replace(char, "")
    return str

def parse_portfolio(portfolio):
    """
    Clean and format provided portfolio info and put them in a dict format

    :param portfolio: Raw data of user's portfolio gathered from Web IDE
    :type portfolio: string

    :return: Well formatted dict
    :rtype: dict
    """
    output = []
    portfolio = str_clean(portfolio, ["[","]","'",'"'])
    portfolio = portfolio.split(", ")
    for input in portfolio:
        output_row = {}
        input = input.replace("\\n","\n").split("\n")
        input[3] = input[3].split(" ")
        output_row["active"] = input[0]
        output_row["available_amount"] = input[1]
        output_row["average_buy_price"] = input[3][0]
        output_row["invested"] = input[3][1]
        output_row["G/P($)"] = input[3][2]
        output_row["G/P(%)"] = input[3][3]
        output_row["current_value"] = input[3][4]
        output.append(output_row)
    return output

def active_portfolio_format(portfolio):
    """
    Order provided active portfolio info and put them in a dict format

    :param portfolio: Raw data of user's portfolio gathered from Web IDE
    :type portfolio: string

    :return: Well formatted dict
    :rtype: dict
    """
    output = []
    i = 0
    try:
        while True:
            output.append(portfolio[i])
            i+=1
    except IndexError:
        return output

def parse_active_portfolio(portfolio):
    """
    Clean and format provided active portfolio info and put them in a dict format

    :param portfolio: Raw data of user's portfolio gathered from Web IDE
    :type portfolio: string

    :return: Well formatted dict
    :rtype: dict
    """
    output = []
    portfolio = str_clean(portfolio, ["[","]","'",'"'])
    portfolio = portfolio.split(", ")
    portfolio = active_portfolio_format(portfolio)
    id = 0
    for input in portfolio:
        output_row = {}
        input = input.replace("\\n","\n").split("\n")
        input[2] = input[2].split(" ")
        output_row["id"] = id
        output_row["type"] = input[0]
        output_row["opening_date"] = input[1]
        output_row["invested"] = input[2][0]
        output_row["amount"] = input[2][1]
        output_row["opening_value"] = input[2][2]
        output_row["current_value"] = input[2][3]
        output_row["G/P($)"] = input[2][6]
        #output_row["G/P(%)"] = input[2][7]
        output.append(output_row)
        id += 1
    return output
