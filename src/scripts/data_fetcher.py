from model.channel import Channel, load_channels_data, save_new_channels_data
from model.video import Video, load_videos_data, save_new_videos_data
import model.youtube_api as ytAPI
from model.comparisons import ComparisonFile, ComparisonLine


def _list_user_missing_video_data(target_user: str, input_dir: str, vid_to_ignore: set[str]):
	missing_vids: set[str] = set()

	def check_add_missing_vid(ldata: ComparisonLine):
		if ldata.user == target_user: # Only interessed into videos compared by me
			if not (ldata.vid1 in vid_to_ignore):
				missing_vids.add(ldata.vid1)
			if not (ldata.vid2 in vid_to_ignore):
				missing_vids.add(ldata.vid2)

	ComparisonFile(input_dir).foreach(check_add_missing_vid)

	return list(missing_vids)

def _fetch_missing_data(CHANNELS, VIDEOS, missing_vids):
	#
	# Requesting missing data
	#
	youtube = ytAPI.get_connection()
	data = []

	try:
		for i in range(0, len(missing_vids), ytAPI.INCREMENT):
			print(f"Fetching {i}/{len(missing_vids)}...")
			request = youtube.videos().list(
				part="id,snippet", # Information to get
				id= ','.join(missing_vids[i:i+ytAPI.INCREMENT]) # vid to get
			)
			data.extend(request.execute()['items'])
	except:
		print('Fetch failed.')
		pass

	#
	# Parsing youtube data output
	#
	newchannels = {}
	newvideos = {}
	for vdata in data:
		vid = vdata['id']
		vsnippet = vdata['snippet']

		cid = vsnippet['channelId']
		if not (cid in CHANNELS):
			newchannels[cid] = Channel(cid, vsnippet['channelTitle'], vsnippet.get('defaultAudioLanguage', vsnippet.get('defaultLanguage', '??')))
			CHANNELS[cid] = newchannels[cid]

		newvideos[vid] = Video(CHANNELS.get(cid, newchannels.get(cid)), vid, vsnippet['title'])
		VIDEOS[vid] = newvideos[vid]

	# Writing new data to cache
	save_new_channels_data(newchannels)
	save_new_videos_data(newvideos)

def fetch_by_user(input_dir: str, target_user: str) -> dict[str, Video]:
	# Load all cached data
	print('Loading channels data...')
	CHANNELS = load_channels_data() # {cid: Channel}
	print(len(CHANNELS), 'channels loaded from cache.')

	print('Loading video data...')
	VIDEOS = load_videos_data(CHANNELS) # {vid: Video}
	print(len(VIDEOS), 'videos loaded from cache.')

	# Find missing video ids
	print('Finding missing video data...')
	missing_vids = _list_user_missing_video_data(target_user, input_dir, VIDEOS.keys())
	if missing_vids:
		print('Found', len(missing_vids), 'video missing: Fetching...')
		_fetch_missing_data(CHANNELS, VIDEOS, missing_vids)

	print(len(VIDEOS), 'videos and', len(CHANNELS), 'channels listed')

	# Output
	return VIDEOS

def fetch_list(vid_list: list[str], onlyCached=False) -> dict[str, Video]:
	# Load all cached data
	CHANNELS = load_channels_data() # {cid: Channel}
	print('Loaded', len(CHANNELS), 'channels from cache.')

	VIDEOS = load_videos_data(CHANNELS) # {vid: Video}
	print('Loaded', len(VIDEOS), 'videos from cache.')

	# Find missing video ids
	missing_vids = [vid for vid in vid_list if vid not in VIDEOS]
	if not onlyCached and missing_vids:
		print('Found', len(missing_vids), 'video missing: Fetching...')
		_fetch_missing_data(CHANNELS, VIDEOS, missing_vids)
		print(len(VIDEOS), 'videos and', len(CHANNELS), 'channels listed')

	return VIDEOS
