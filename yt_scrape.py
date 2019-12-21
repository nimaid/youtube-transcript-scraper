import pyyoutube
from youtube_transcript_api import YouTubeTranscriptApi

API_KEY = 'YourKeyHere'

def get_channel_videos(channel_id, max_videos=50):
    if max_videos <= 0:
        max_videos = float('Inf')
    
    MAX_VIDS_PER_CALL = 50
    if max_videos < MAX_VIDS_PER_CALL:
        vids_per_call = max_videos
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
        num_videos = len(video_ids)
        
        num_videos_left = max_videos - num_videos
        if num_videos_left < MAX_VIDS_PER_CALL:
            vids_per_call = num_videos_left
        
        if len(video_ids) >= max_videos:
            break
        
        page_token = playlist_item_res.nextPageToken

    return video_ids
    
def get_transcript(vid_id, language='en'):
    transcript = YouTubeTranscriptApi.get_transcript(vid_id, languages=[language])
    return ' '.join([line['text'] for line in transcript]).replace('\n', '')
    
def get_channel_transcripts(channel_id, max_videos=50, language='en'):
    videos = get_channel_videos(channel_id=channel_id, max_videos=max_videos)
    
    video_transcripts = []
    for video in videos:
        transcript = get_transcript(video, language=language)
        video_transcripts.append(transcript)
    
    return video_transcripts
