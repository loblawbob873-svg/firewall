## DDOS Protection System

![image](image6.png)

## Features
* Live Reporting 
* Automatic Blocking
* Customizable 
* Send Alerts to NTFY
* Web Interface for Reporting

## Requirements
* Python
* NFT Firewall

### Setup Configurations in ```config.py```
* Configure ```LOG_FILE``` to point to your NGINX access file. I recommend having NGINX store it in TMPFS
* Adjust ```TIME_FRAME``` and ```IP_OCCURENCE_THRESHOLD``` to your needs 
* ```SUBNET_BLOCKS``` in config. Any subnet here will automatically be blocked
* Configure the NFTables Firewall. See sample file at the bottom of this ```README.md```

### Block Lists and Allowed lists
* ```tier_one.py``` - An array of Traffic to allow and not block. Remove/Comment out a line to have it rate limited to ```IP_OCCURENCE_THRESHOLD```
* ```ip_blocks.py``` - Terms/Bots/Crawlers/etc to automatically block

## Installing the required libraries and Running  Python Firewall
```
python -m venv venv
. venv/bin/activate
pip install requests logging psutil httpx fastapi asyncio uvicorn
```

### Run the app in the foreground
```
python firewall.py --print
```

### Run the app in the background
```
python firewall.py
```

### A web interface will automatically start on ```http://0.0.0.0:6767```


### NTFY Notifications for Mobile or Desktop
Modify ```config.py``` and change this to your desired NTFY server/Topic:
```
NTFY_URL = "https://push.poster.place/logs"
```

### Sample NFT firewall

Save it as ```/etc/firewall.nft``` and load it with ```nft -f /etc/firewall.nft```
```
table ip filter {
	set http_ratelimit {
		type ipv4_addr
		size 65535
		flags dynamic,timeout
		timeout 1s
		elements = { }
	}

	chain input {
		type filter hook input priority filter; policy drop;
		udp sport 68 udp dport 67 ip saddr 0.0.0.0 ip daddr 255.255.255.255 accept
		ct state new tcp dport 443 update @http_ratelimit { ip saddr limit rate 50/second burst 1 packets } accept
		ct state new tcp dport 80 update @http_ratelimit { ip saddr limit rate 25/second burst 1 packets } accept
		iif "lo" accept
		ct state established accept
		icmp type echo-request accept
		ip saddr 192.168.0.0/24 accept
	}

	chain forward {
		type filter hook forward priority filter; policy accept;
		ct status dnat accept
		accept
	}

	chain output {
		type filter hook output priority filter; policy accept;
		accept
	}
}
table ip nat {
	chain prerouting {
		type nat hook prerouting priority dstnat; policy accept;
	}

	chain postrouting {
		type nat hook postrouting priority srcnat; policy accept;
		masquerade
	}
}
table ip6 filter {
	chain input {
		type filter hook input priority filter; policy drop;
	}

	chain forward {
		type filter hook forward priority filter; policy accept;
	}

	chain output {
		type filter hook output priority filter; policy accept;
	}
}
table ip6 nat {
	chain prerouting {
		type nat hook prerouting priority dstnat; policy accept;
	}

	chain postrouting {
		type nat hook postrouting priority srcnat; policy accept;
		masquerade
	}
}

```