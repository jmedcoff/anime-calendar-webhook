# Anime Calendar Webhook
This project is a Python script that searches for posts in the subreddit r/AnimeCalendar and sends a randomly selected image for the current day or video link to specified webhook endpoints. The script is designed to run daily and can be scheduled using cron or a similar scheduler.

## Dependencies
The script requires the following Python packages:

- `requests`
- `inflect`
- `pyyaml`

## What it does, in a nutshell
The script searches for posts in the subreddit r/AnimeCalendar that match the current date formatted as "Month DayOrdinal" (e.g., "September 10th").
It filters the posts to prefer images or imgur links. If no images are found, it includes videos.
A randomly selected media link (image or video) is sent to the provided webhook endpoints, configured in a YAML file (webhook_endpoints.yaml).

## Cautions
This was a quick project to get my feet wet with both the discord webhooks API and working with discord embed objects. Unfortunately, exactly the combination of posting embeds using webhooks is either not fully implemented or intentionally gimped by discord. Thus, the code to select images/videos is rife with edge case catching. Perhaps a good opportunity for some refactoring.

I think I've caught most of the edge cases by now, but after this has been running daily for a month and a half, I still rarely see something new I need to fix for.

## Configuration
Create a `webhook_endpoints.yaml` file in the same directory as the script with the following structure:

```
webhooks:
  - name: "Endpoint for Discord Channel 1"
    url: "https://discord.com/api/webhooks/1234567890/abcdefg"
  - name: "Endpoint for Discord Channel 2"
    url: "https://discord.com/api/webhooks/0987654321/hijklmn"
```

My target deployment is my home server, where the script is scheduled with a simple cron job. The script logs to console, so you can catch a log file if you want.

```
0 8 * * * /usr/bin/python3 /path/to/script.py >> /path/to/log.txt
```