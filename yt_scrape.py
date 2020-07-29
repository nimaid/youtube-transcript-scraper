#!/usr/bin/env python3

import argparse
import pyyoutube as _pyt
import youtube_transcript_api as _yta
import re as _re

def get_channel_videos(channel_id, api_key, max_videos=50, page_token=''):
    if max_videos <= 0:
        max_videos = float('Inf')

    if max_videos >= 5000:
        print('Warning: The YouTube API limits the number of requests to about 7000 videos a day.')
        if max_videos < float('Inf'):
            num_vids = max_videos
        else:
            num_vids = 'all'
        print('You are trying to get', num_vids, 'videos, so you may hit your quota. It resets at midnight pacific time.')

    MAX_VIDS_PER_CALL = 50
    if max_videos < MAX_VIDS_PER_CALL:
        vids_per_call = max_videos
    else:
        vids_per_call = MAX_VIDS_PER_CALL

    api = _pyt.Api(api_key=api_key)
    channel_res = api.get_channel_info(channel_id=channel_id)

    playlist_id = channel_res.items[0].contentDetails.relatedPlaylists.uploads

    videos = {'video_ids': [], 'next_page_token': page_token}

    while videos['next_page_token'] is not None:
        try:
            playlist_item_res = api.get_playlist_items(playlist_id=playlist_id, count=vids_per_call, page_token=videos['next_page_token'])
        except _pyt.error.PyYouTubeException as e:
            num_videos = len(videos['video_ids'])
            if num_videos > 0:
                print('YouTube Error:', str(e))
                print('Cannot get any more video ID\'s, but already got', num_videos)
                return videos
            else:
                raise e
        videos['next_page_token'] = playlist_item_res.nextPageToken

        videos['video_ids'] += [item.contentDetails.videoId for item in playlist_item_res.items]
        num_videos = len(videos['video_ids'])

        num_videos_left = max_videos - num_videos
        if num_videos_left < MAX_VIDS_PER_CALL:
            vids_per_call = num_videos_left

        if num_videos >= max_videos:
            break

    return videos

def get_transcript(video_id, language='en', type_override=None):
    transcript_object = _yta.YouTubeTranscriptApi.get_transcript(video_id, languages=(language,), type_override=type_override)
    transcript_text = ' '.join([line['text'] for line in transcript_object]).replace('\n', ' ')
    return transcript_text

def get_transcripts(video_ids, language='en', type_override=None):
    transcripts, temp = _yta.YouTubeTranscriptApi.get_transcripts(video_ids, languages=(language,), continue_after_error=True, type_override=type_override)
    transcript_objects = [transcripts[id] for id in transcripts.keys()]
    transcript_texts = [' '.join([line['text'] for line in t]).replace('\n', ' ') for t in transcript_objects]
    return transcript_texts

def get_channel_transcripts(channel_id, api_key, max_videos=0, page_token='', language='en', type_override=None):
    videos = get_channel_videos(channel_id=channel_id, api_key=api_key, max_videos=max_videos, page_token=page_token)
    transcripts = get_transcripts(videos['video_ids'], language=language, type_override=type_override)
    return {'video_transcripts': transcripts, 'next_page_token': videos['next_page_token']}

def save_transcripts_to_file(transcripts, filename):
    npt = transcripts['next_page_token']
    if npt not in [None, '']:
        filename = npt + '_' + filename
    with open(filename, 'w') as f:
        text = '\n'.join(transcripts['video_transcripts'])
        text = text.replace('’', '\'')
        text = text.replace('—', ' - ')
        text = text.encode('ascii', 'ignore').decode('utf-8')
        text = _re.sub(' +', ' ', text)
        f.write(text)

def save_channel_transcripts(channel_id, api_key, filename, max_videos=0, page_token='', language='en', type_override=None):
    transcripts = get_channel_transcripts(channel_id, api_key, max_videos=max_videos, page_token=page_token, language=language, type_override=type_override)
    save_transcripts_to_file(transcripts, filename)
    
 if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    # channel_id, api_key, filename, max_videos=0, language='en', type_override=None
    ap.add_argument("-c", "--channel", type=str, required=True,
        help="ID of the channel to scrape transcripts from")
    ap.add_argument("-n", "--num_videos", type=int, required=False,
        help="maximum number of videos to get transcripts for (all if not supplied)")
    ap.add_argument("-p", "--page_token", type=str, required=False,
        help="page token used to start somewhere other than the most recent videos")
    ap.add_argument("-l", "--language", type=str, required=False, choices=["en"], default="en"
        help="language code (default is [en]glish)")
    ap.add_argument("-t", "--type", type=str, required=False, choices=["automatic", "manual"], default=None,
        help="force either automatic or manual transcripts only")
        
        
    args = vars(ap.parse_args())