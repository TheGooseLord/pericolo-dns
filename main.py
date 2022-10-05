import os
import re
import socket
import requests
import json
from dotenv import load_dotenv
import discord

load_dotenv()

intents = discord.Intents.default()
#intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

def update_dns(ip, port):
    recordA = pbConfig.copy()
    recordA.update({"content": ip, "ttl": "30" })

    endpointA = recordA["endpoint"] + '/dns/editByNameType/' + os.getenv("DOMAIN") + "/A/" + os.getenv("SUBDOMAIN")

    recordSRV = pbConfig.copy()
    recordSRV.update({ "content": "0 " + port + " " + os.getenv("SUBDOMAIN") + "." + os.getenv("DOMAIN"), "ttl": "30" })
    
    endpointSRV = recordSRV["endpoint"] + '/dns/editByNameType/' + os.getenv("DOMAIN") + "/SRV/_minecraft._tcp." + os.getenv("SUBDOMAIN")

    # print(recordA)
    # print(recordSRV)
    # print(endpointA)
    # print(endpointSRV)

    resultA = json.loads(requests.post(endpointA, data = json.dumps(recordA)).text)
    print("A   - " + resultA["status"])

    resultSRV = json.loads(requests.post(endpointSRV, data = json.dumps(recordSRV)).text)
    print("SRV - " + resultSRV["status"])

    # print(resultA)
    # print(resultSRV)

    
    return


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.display_name == str(os.getenv('NGROK_PROVIDER')):
        ip_port = re.search(r"is `*([^\n\r ]*)", message.content).group(1)[:-1]

        for i in range(len(ip_port) - 1, 0, -1):
            if ip_port[i] == ":":
                port = ip_port[i+1:]
                colon = i
                break

            if i == 0:
                await message.channel.send("Error: IP formatted incorrectly")
                return

        host = ip_port[:i]
        ip = socket.gethostbyname(host)

        await message.channel.send("The new IP is: " + ip + ":" + port + " (" + host + ")\nThe DNS server is being updated...")

        update_dns(ip, port)

        await message.channel.send("Done! To update the IP automatically in your client, use `mc.geese.dev`")

    return


pbConfig = json.loads('{ "endpoint":"https://api-ipv4.porkbun.com/api/json/v3", "apikey": "%s", "secretapikey": "%s" }' % (os.getenv('PORKBUN_API'), os.getenv('PORKBUN_SECRET')))


client.run(os.getenv('DISCORD_TOKEN'))

