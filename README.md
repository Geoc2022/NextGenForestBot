# NextGenForestBot

This is the code for the NextGenForestBot on twitter (https://twitter.com/NextGenForestB1/status/1286073084362010624?s=20).
Keys have been removed.

# How to use the bot: @NextGenForestB1

Bot which helps find parks/trails:

@ bot and use the functions bellow

Park functions: name(), act(), area(), link(), nearby(), weather()

Trails functions: name(), len(), nearby(), weather()

# Example:
@NextGenForestB1
Atlanta, GA nearby(5) #park

## nearby() aka nearbys()
### finds nearby parks/trails with a given location

for parks:
	
	nearbyparks(5)
	nearbypark(5)
	nearby(-5) #parks
	nearbys(5) #parks

for trails:

	nearbytrails(5)
	nearbytrail(-5)
	nearby(5) #trails
	nearbys(5) #trails

(negative numbers give the reverse)

## weather()
### Adds detailed weather

#### weather(0)
	{placetitle} - {Status} {Weather Emoji}  ({Details})
	Temperature: {Temperature temp}
	    max: {Temperature temp_max}
	    min: {Temperature temp_min}
	    feels like: {Temperature feels_like}
	Wind: {Wind[0]}, {Wind[1]}
	UV Exposure: {(UV Exposure).title()}


#### weather(1)
	{placetitle} - {Status} {Weather Emoji}  ({Details})

## name() aka title()
### finds parks/trails with the same name

name(abc): abc, abcd, or aabc
name(^a): all trails/parks which start with ‘a’ (uses regex: http://regexr.com)

## act() aka activity()
### finds parks which have the activities listed

act(swim, bike): all parks which have swimming or biking

## area() aka size()
### finds parks which have the size specified (km2)

area(5): parks 5km2
area(5-10): parks 5km2 - 10km2
area(>5) or area(5<): parks >5km2
area(<5) or area(5>): parks <5km2
(specify other units using: acres, mi2, y2, hectare (ha))

## len() aka length()
### finds trails which have the length (km) specified

len(5): parks 5km
len(5-10): parks 5km - 10km
len(>5) or area(5<): parks >5km
len(<5) or area(5>): parks <5km
(specify other units using: mi (kilometer), y (yard), f (feet))

## link()
### get links to common resources

link(info)
link(map)
link(cal)
link(permit)
link(conditions)
