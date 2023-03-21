from pathlib import Path
from model.channel import Channel

FILE_LOCATION = 'data/cache/video_info.tsv'

class Video:
	def __init__(self, channel: Channel, vid: str, title: str):
		self.channel = channel
		self.id = vid
		self.title = title

	def __str__(self):
		return f"[{self.id}] {self.channel.name}: {self.title}"

def load_videos_data(channels: dict[str, Channel]):
	all_vids: dict[str, Video] = dict() # {vid: Video}

	# channel_id \t video_id \t video_name
	try:
		file = open(FILE_LOCATION, 'r', encoding='utf-8')
	except:
		return all_vids

	while True:
		line = file.readline()
		# if line is empty, end of file is reached
		if not line:
			break

		ldata = line.strip().split('\t')
		all_vids[ldata[1]] = Video(channels[ldata[0]], ldata[1], ldata[2])
	file.close()
	return all_vids

def save_new_videos_data(videos: dict[str, Video]):
	# channel_id \t video_id \t title

	Path(FILE_LOCATION).parent.mkdir(parents=True, exist_ok=True)
	file = open(FILE_LOCATION, 'a+', encoding='utf-8')

	ordered = list(videos.values())
	ordered.sort(key=lambda c: (c.channel.lang, c.channel.id, c.id))

	for video in ordered:
		file.write(f"{video.channel.id}\t{video.id}\t{video.title}\n")
		print('New video data saved:', video)
	file.close()
