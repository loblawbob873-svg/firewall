activity = []
html = []
ip_counts = {}  # Dictionary to store IP addresses and their occurrence counts


def addIPCOUNTS(data):
    global ip_counts
    ip_counts.append(data)

def clearIPCOUNTS(data):
    global ip_counts
    ip_counts = []
    
def getIPCOUNTS(data):
    global ip_counts
    return ip_counts

def addActivity(data):
    global activity
    activity.append(data)

def getActivity():
    global activity
    return activity

def clearDB():
    global activity
    activity = []
    
def getHTML():
    global html
    return html

def clearHTML():
    global html
    html = []

def addHTML(data):
    global html
    html.append(data)