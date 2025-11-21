activity = []
ip_counts = {}  # Dictionary to store IP addresses and their occurrence counts

def addActivity(data){
    global activity
    activity.append(data)
}

def getActivity(data){
    global activity
    return data
}