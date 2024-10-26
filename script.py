import os
import requests
import random
import logging
import datetime
import inflect
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def webhook_post(webhook_endpoint, content, media_type):
    """
    Sends a POST request to a specified webhook endpoint with the given content.

    Args:
        webhook_endpoint (str): The URL of the webhook endpoint.
        content (str): The content to be sent in the POST request.
        content_type (str): The type of content ('image' or 'video').

    Returns:
        requests.Response: The response object resulting from the POST request.
    """
    if "redd.it" in content:
        media_type = "video"
    
    if media_type == "image":
        payload = {
            "embeds": [
                {
                    'image': {"url": content}
                }
            ]
        }
    elif media_type == "video":
        payload = {
            "content": content
        }
    else:
        raise ValueError("Invalid content_type. Must be 'image' or 'video'.")

    response = requests.post(webhook_endpoint, json=payload)
    return response

def get_random_image_from_reddit(search_term):
    """
    Searches for posts in the subreddit r/AnimeCalendar that match the given search term,
    filters the posts to prefer images or imgur links, and if none are found, includes videos.
    Returns a randomly selected media link and its type.

    Args:
        search_term (str): The search term to use for finding relevant posts.

    Returns:
        tuple: A tuple containing the direct link to a randomly selected media post and a string
               indicating the type ('image' or 'video'), or (None, None) if no media posts are found.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://www.reddit.com/r/AnimeCalendar/search.json?q={search_term}&restrict_sr=on&sort=relevance&t=all"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch data from Reddit. Status code: {response.status_code}")
        return None, None
    
    posts = response.json().get('data', {}).get('children', [])
    
    # Filter for image posts
    image_posts = [
        post['data']['url'] for post in posts
        if post['data']['url'].endswith(('.jpg', '.jpeg', '.png')) or 'imgur.com' in post['data']['url']
    ]
    
    # If no image posts are found, filter for video posts
    if not image_posts:
        video_posts = [
            post['data']['url'] for post in posts
            if post['data']['url'].endswith(('.mp4', '.webm'))
        ]
        if not video_posts:
            logging.error("No image or video posts found matching the search criteria.")
            return None, None
        selected_post = random.choice(video_posts)
        media_type = 'video'
    else:
        selected_post = random.choice(image_posts)
        media_type = 'video' if selected_post.endswith(('.gifv')) else 'image'
    
    # If the selected post is an imgur link, convert it to a direct image link
    if 'imgur.com' in selected_post and not selected_post.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        selected_post += '.jpg'

    logging.debug(f"Found media type {media_type}: {selected_post}")
    
    return selected_post, media_type

def get_formatted_current_date():
    """
    Returns the current date formatted as "Month DayOrdinal".

    The function retrieves the current date, extracts the month and day,
    converts the day to its ordinal form (e.g., 1 to 1st, 2 to 2nd), and
    formats the date as "Month DayOrdinal" (e.g., "September 10th").

    Returns:
        str: The current date formatted as "Month DayOrdinal".
    """
    p = inflect.engine()
    now = datetime.datetime.now()
    month = now.strftime("%B")
    day = now.day
    day_ordinal = p.ordinal(day)
    formatted_date = f"{month} {day_ordinal}"
    return formatted_date

def main():
    """
    Main function to search for a random image post from the subreddit r/AnimeCalendar
    and send it to specified webhook endpoints if found.
    """
        # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'webhook_endpoints.yaml')
    
    # Read the webhook endpoints from webhook_endpoints.yaml
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            webhook_endpoints = [(entry['name'], entry['url']) for entry in config['webhooks']]
    except FileNotFoundError:
        logging.error("webhook_endpoints.yaml file not found.")
        return
    except Exception as e:
        logging.error(f"An error occurred while reading webhook_endpoints.yaml: {e}")
        return

    search_term = get_formatted_current_date()
    image_link, media_type = get_random_image_from_reddit(search_term)
    
    if image_link:
        for name, webhook_endpoint in webhook_endpoints:
            response = webhook_post(webhook_endpoint, image_link, media_type)
            
            if response.ok:
                logging.info(f"Successfully posted {media_type} link to webhook: {name} ({webhook_endpoint})")
                logging.debug(f"Media was: {image_link}")
            else:
                logging.error(f"Failed to post {media_type} link to webhook: {name} ({webhook_endpoint}). Status code: {response.status_code}")
    else:
        logging.error("No image or video link found to post to webhook.")

if __name__ == "__main__":
    main()