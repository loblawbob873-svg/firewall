activity = []
html = []
   
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