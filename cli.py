from commands import get_cpu_usage
from commands import get_block_count

def buildCLI(activity,timestamp):
    print("\t\t🔥 Python Firewall 🔥")
    print (f"{get_cpu_usage()}\tBlocked IP's: {get_block_count().strip()} ✅")
    print ("-------------------------------------------------------------------------------------------------")
    print (f"\t\t\t⚠️ Unfiltered and Blocked Traffic as of: {timestamp}\n")
    
    for line in activity:
        print(line)
        