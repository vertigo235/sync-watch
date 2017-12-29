## Sync-Watch
A Docker for rclone that suspends transfers when there are remote Plex Streams

## Usage

'''
docker create \
	--name syncwatch \
	-e SERVER_URL=https://192.168.1.5:32400/ \
	-e SERVER_TOKEN={Put your Plex Token Here} \
	-e SERVER_NAME={Put your server name here} \
	-v <where you want your config>:/config \
	-e TZ="US/Eastern" \
	-v /volume1:/volume1 \ 
	-v /volume2:/volume2 \
	vertigo235/syncwatch
'''

## Starting a transfer

docker exec -it syncwatch rclone copy -v /volume1/Media "Remote:Media"

## Syncwatch script
Alternatively you could just run the syncwatch.py script on your machine to monitor rclone sessions there if you don't want to run the docker. 

It's located in the syncwatch folder...