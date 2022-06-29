import requests
import json

# This code is a sample of how to migrate a Wingman call to Gong.
# Note that, in this current state - it is not a loop.
# To make this "production" - simply turn this into a function
# and loop through it for each call in Wingman.

#Put your key and secret here
k=
s=

baseuri='https://api.gong.io/v2/calls'
usersUri='https://api.gong.io/v2/users'

# Get all the Gong users
gongUsers = requests.request("GET", usersUri, auth=(k,s))

# Store the list of Gong users to map from Wingman
gongUsers = gongUsers.json()['users']

######### Replace this code with Wingman API Call ########

# Your code should return a JSON object with a URL to download
# Set f = the Wingman json response

# Your code will also need to download the Wingman call via the link, Eg; 
# video = requests.get(response['call']['video_url'], stream=True)

# with open("tempvideolocation.mp4","wb") as v:
#   for chunk in video.iter_content(chunk_sie = 1024*1024):
#       if chunk:
#           v.write(chunk)

#This example was built from a response saved to a json file.
f = open("/Downloads/response (11).json") 
f = f.read()
f = json.loads(f)
# ########################################################

# Create the Gong call object
gongCall = {}
gongCall['actualStart'] = f['call']['time']
gongCall['clientUniqueId'] = f['call']['id'] +'v2'
gongCall['direction'] = 'Conference'
gongCall['callProviderCode'] = 'zoom'
gongCall['duration'] = f['call']['metrics']['call_duration']

# Add the internal Wingman users to the parties array
parties = []
primaryUser = ''

for u in f['call']['users']:
    user = {}
    user['emailAddress'] = u['userEmail']
    user['partyId'] = str(u['personId'])
    user['name'] = None
    
    for g in gongUsers:
        
        if u['userEmail'] == g['emailAddress']:
            user['userId'] = g['id']
            user['name'] = g['firstName'] + ' ' + g['lastName']
            # Set the organizer as the primary user for Gong
            if u['isOrganizer']:
                primaryUser = g['id']
    
    parties.append(user)

# Sometimes the call organizer is not on the call - when this is the case, set the first internal user to primary user
if len(primaryUser) < 1:
    primaryUser = parties[0]['userId']

# Add the external participants to the parties array
for p in f['call']['externalParticipants']:
    user = {}
    user['emailAddress'] = p['email'] if 'email' in p.keys() else None
    user['partyId'] = str(p['personId'])
    user['name'] = p['name'] if 'name' in p.keys() else None
    parties.append(user)

# Add the parties and primary user to the Gong object
gongCall['parties'] = parties
gongCall['primaryUser'] = primaryUser

# Construct the speaker timeline
speakersTimeline = {}
speakersTimeline['precise'] = True

# Format the speech segments how Gong wants them
speechSegments = []

for t in f['call']['transcript']:
    seg = {}
    partyIds = []
    seg['fromTime'] = round(t['start'] * 1000)
    partyIds.append(str(t['personId']) if t['personId'] != None else '0')
    seg['partyIds'] = partyIds
    seg['toTime'] = round(t['end'] * 1000)
    speechSegments.append(seg)

speakersTimeline['speechSegments'] = speechSegments

# Add speakersTimeline to the Gong call object
gongCall['speakersTimeline'] = speakersTimeline

# Set the call title
gongCall['title'] = f['call']['title']

# Create the call in Gong
x = requests.post(baseuri, json=gongCall, auth=(k,s))

# Grab the call ID of the new call
newId = x.json()['callId']


# Construct new URL with the returned call Id
mediaUrl = 'https://api.gong.io/v2/calls/'+newId+'/media'

# Replace this location with wherever you are downloading the Wingman Call from the top section
files=[('mediaFile',('call.mp4',open("your-download-location-here.mp4",'rb'),'application/octet-stream'))]

# Add the call media to the call
y = requests.put(mediaUrl, files=files, auth=(k,s))
