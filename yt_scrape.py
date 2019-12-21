import pyyoutube
from youtube_transcript_api import YouTubeTranscriptApi

API_KEY = 'YourKeyHere'

def get_videos(channel_id, max_vids=50):
    if max_vids <= 0:
        max_vids = float('Inf')
    
    MAX_VIDS_PER_CALL = 50
    if max_vids < MAX_VIDS_PER_CALL:
        vids_per_call = max_vids
    else:
        vids_per_call = MAX_VIDS_PER_CALL
    
    api = pyyoutube.Api(api_key=API_KEY)
    channel_res = api.get_channel_info(channel_id=channel_id)

    playlist_id = channel_res.items[0].contentDetails.relatedPlaylists.uploads
    
    
    video_ids = []
    page_token = ''
    while page_token is not None:
        playlist_item_res = api.get_playlist_items(playlist_id=playlist_id, count=vids_per_call, page_token=page_token)
        
        video_ids += [item.contentDetails.videoId for item in playlist_item_res.items]
        if len(video_ids) >= max_vids:
            video_ids = video_ids[:max_vids]
            break
        
        page_token = playlist_item_res.nextPageToken

    return video_ids
    
def get_transcript(vid_id, language='en'):
    transcript = YouTubeTranscriptApi.get_transcript(vid_id, languages=[language])
    return ' '.join([line['text'] for line in transcript]).replace('\n', '')
    
