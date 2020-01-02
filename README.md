## Sync-Watch
A Docker for rclone that adjusts bandwidth limit to accomodate for remote plex stream quality of service. 

## Usage

```
docker create \
	--name syncwatch \
	-e SERVER_URL=https://192.168.1.5:32400/ \
	-e SERVER_TOKEN={Put your Plex Token Here} \
	-e SERVER_NAME={Put your server name here} \
	-e BW_MAX={Maximum Bandwidth in KBs}
	-e BW_FLOOR={Lowest BW setting in KBs}
	-e BW_FACTOR={Factor to multiply plex stream by to get amount BW is reduced}
	-v <where you want your config>:/config \
	-e TZ="US/Eastern" \
	-v /volume1:/volume1 \ 
	-v /volume2:/volume2 \
	vertigo235/syncwatch
```

## Starting a transfer

```
docker exec -it syncwatch rclone copy --rc -v /volume1/Media "Remote:Media"
```

You must enable remote control with the --rc flag. 

## Syncwatch script
Alternatively you could just run the syncwatch.py script on your machine to monitor rclone sessions there if you don't want to run the docker. 

It's located in the syncwatch folder...