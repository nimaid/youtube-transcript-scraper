import pyyoutube
import youtube_transcript_api

def get_channel_videos(channel_id, api_key, max_videos=50):
    if max_videos <= 0:
        max_videos = float('Inf')
    
    MAX_VIDS_PER_CALL = 50
    if max_videos < MAX_VIDS_PER_CALL:
        vids_per_call = max_videos
    else:
        vids_per_call = MAX_VIDS_PER_CALL
    
    api = pyyoutube.Api(api_key=api_key)
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
    
def get_transcript(vid_id, language='en', type_override=None):
    transcript_object = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(vid_id, languages=(language,), type_override=type_override)
    transcript_text = ' '.join([line['text'] for line in transcript_object]).replace('\n', ' ')
    return transcript_text
    
def get_channel_transcripts(channel_id, api_key, max_videos=50, language='en', type_override=None):
    videos = get_channel_videos(channel_id=channel_id, api_key=api_key, max_videos=max_videos)
    transcripts, temp = youtube_transcript_api.YouTubeTranscriptApi.get_transcripts(videos, languages=(language,), continue_after_error=True, type_override=type_override)
    transcript_objects = [transcripts[id] for id in transcripts.keys()]
    transcript_texts = [' '.join([line['text'] for line in t]).replace('\n', ' ') for t in transcript_objects]
    return transcript_texts
