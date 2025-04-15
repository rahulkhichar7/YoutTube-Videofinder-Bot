from googleapiclient.discovery import build
from datetime import datetime, timedelta
import google.generativeai as genai
import isodate

def search_youtube(query, max_results=20):
    print("searching for youtube query .....")
    youtube = build('youtube', 'v3', developerKey="AIzaSyCct2Ad2WJe_dDp24YiQ_nneZqFhZDykoA")
    
    # apply day range filter (uploaded latestly in last 14 days)
    published_after = (datetime.utcnow() - timedelta(days=14)).isoformat("T") + "Z"

    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=30,  # Get more to filter later (as max is 20)
        publishedAfter=published_after
    )
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response['items']]
    print("video ids has fatched ")

    # fatch video details
    details = youtube.videos().list(
        part="snippet,contentDetails",
        id=','.join(video_ids)
    ).execute()

    filtered_videos = []
    for item in details['items']:
        duration = item['contentDetails']['duration']
        minutes = parse_duration(duration)

        # apply time range filter
        if 4 <= minutes <= 20: 
            filtered_videos.append({
                "title": item['snippet']['title'],
                "videoId": item['id'],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "publishedAt": item['snippet']['publishedAt'],
                "duration_mins": minutes
            })
    print("Filtered items")
    for i in filtered_videos:
        print(i['title'])

    return filtered_videos[:max_results]

def parse_duration(iso_duration):
    duration = isodate.parse_duration(iso_duration)
    return int(duration.total_seconds() // 60)




genai.configure(api_key="AIzaSyCeNitC_JA3d_xloj39sXFlyY1YiH6W0dI")
model = genai.GenerativeModel("gemini-1.5-flash")

def find_best_video(videos, query):
    # put a prompt for out search
    prompt = f"""You are a video recommendation AI. Based on the query: "{query}", pick the most relevant video from the list below. Only return the URL of the most suitable one.

Videos:
{format_videos(videos)}
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def format_videos(videos):
    return "\n".join([
        f"Title: {v['title']}\nURL: {v['url']}\nPublished: {v['publishedAt']}\nDuration: {v['duration_mins']} mins\n"
        for v in videos
    ])

def youtube_video_finder(query):
    videos = search_youtube(query)
    if not videos:
        return "No videos found."

    best_video_url = find_best_video(videos, query)
    return f"Best video for: '{query}'\n is  {best_video_url}"


query = input("Enter query: ")
print(youtube_video_finder(query))
