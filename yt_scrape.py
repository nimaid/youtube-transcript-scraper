import pyyoutube
import youtube_transcript_api

def get_channel_videos(channel_id, api_key, max_videos=50, page_token=''):
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
    while page_token is not None:
        # TODO: handle pyyoutube.error.PyYouTubeException by returning IDs and page token
        playlist_item_res = api.get_playlist_items(playlist_id=playlist_id, count=vids_per_call, page_token=page_token)
        
        page_token = playlist_item_res.nextPageToken
        
        video_ids += [item.contentDetails.videoId for item in playlist_item_res.items]
        num_videos = len(video_ids)
        
        num_videos_left = max_videos - num_videos
        if num_videos_left < MAX_VIDS_PER_CALL:
            vids_per_call = num_videos_left
        
        if len(video_ids) >= max_videos:
            break

    return {'video_ids': video_ids, 'next_page_token': page_token}
    
def get_transcript(video_id, language='en', type_override=None):
    transcript_object = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id, languages=(language,), type_override=type_override)
    transcript_text = ' '.join([line['text'] for line in transcript_object]).replace('\n', ' ')
    return transcript_text
    
def get_transcripts(video_ids, language='en', type_override=None):
    transcripts, temp = youtube_transcript_api.YouTubeTranscriptApi.get_transcripts(video_ids, languages=(language,), continue_after_error=True, type_override=type_override)
    transcript_objects = [transcripts[id] for id in transcripts.keys()]
    transcript_texts = [' '.join([line['text'] for line in t]).replace('\n', ' ') for t in transcript_objects]
    return transcript_texts

def get_channel_transcripts(channel_id, api_key, max_videos=50, page_token='', language='en', type_override=None):
    videos = get_channel_videos(channel_id=channel_id, api_key=api_key, max_videos=max_videos, page_token=page_token)
    transcripts = get_transcripts(videos['video_ids'], language=language, type_override=type_override)
    return {'video_transcripts': transcripts, 'next_page_token': videos['next_page_token']}
