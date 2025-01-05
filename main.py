import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SLACK_TOKEN = os.getenv('ACCESS_TOKEN')
HEADERS = {'Authorization': f'Bearer {SLACK_TOKEN}'}

BASE_DIR = os.getcwd()
CHANNELS_DIR = os.path.join(BASE_DIR, "channels")
CHANNEL_MESSAGES_DIR = os.path.join(BASE_DIR, "channel_messages")
THREADS_DIR = os.path.join(BASE_DIR, "threads")
USERS_DIR = os.path.join(BASE_DIR, "users")
CHANNEL_MEMBERS_DIR = os.path.join(BASE_DIR, "channel_members")
CHECKPOINT_FILE = os.path.join(BASE_DIR, "checkpoint.json")

def ensure_directory(path):
    os.makedirs(path, exist_ok=True)

def generate_filename(directory, timestamp):
    base_filename = f"{timestamp}.json"
    filepath = os.path.join(directory, base_filename)
    counter = 1
    
    while os.path.exists(filepath):
        base_filename = f"{timestamp}_{counter}.json"
        filepath = os.path.join(directory, base_filename)
        counter += 1

    return filepath
        
def save_to_file(directory, data):
    ensure_directory(directory)
    timestamp = int(datetime.now().timestamp() * 1000) 
    filepath = generate_filename(directory, timestamp)
    
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as file:
            return json.load(file)
    return {"processed_messages": {}}

def update_checkpoint(channel_id, timestamp):
    checkpoint = load_checkpoint()
    checkpoint["processed_messages"][channel_id] = timestamp
    with open(CHECKPOINT_FILE, "w") as file:
        json.dump(checkpoint, file, indent=4)

def fetch_channels():
    url = 'https://slack.com/api/conversations.list'
    params = {'limit': 1000, 'types': 'public_channel,private_channel'}
    response = requests.get(url, headers=HEADERS, params=params).json()
    if response['ok']:
        save_to_file(CHANNELS_DIR, response['channels'])
        return response['channels']
    else:
        print(f"Error fetching channels: {response['error']}")
        return []

def fetch_channel_messages(channel_id):
    checkpoint = load_checkpoint()
    last_timestamp = checkpoint["processed_messages"].get(channel_id, None)

    url = 'https://slack.com/api/conversations.history'
    params = {'channel': channel_id, 'limit': 100}
    if last_timestamp:
        params['oldest'] = last_timestamp

    messages = []

    while True:
        response = requests.get(url, headers=HEADERS, params=params).json()
        if response['ok']:
            messages.extend(response['messages'])
            if 'response_metadata' in response and 'next_cursor' in response['response_metadata']:
                params['cursor'] = response['response_metadata']['next_cursor']
            else:
                break
        else:
            print(f"Error fetching messages for channel {channel_id}: {response['error']}")
            break

    if messages:
        update_checkpoint(channel_id, messages[0]['ts'])

    return messages

def fetch_thread_replies(channel_id, thread_ts):
    url = 'https://slack.com/api/conversations.replies'
    params = {'channel': channel_id, 'ts': thread_ts}
    response = requests.get(url, headers=HEADERS, params=params).json()

    if response['ok']:
        return response['messages']
    else:
        print(f"Error fetching thread replies: {response['error']}")
        return []

def fetch_users():
    url = 'https://slack.com/api/users.list'
    response = requests.get(url, headers=HEADERS).json()
    if response['ok']:
        save_to_file(USERS_DIR, response['members'])
    else:
        print(f"Error fetching users: {response['error']}")

def fetch_channel_members(channel_id):
    url = 'https://slack.com/api/conversations.members'
    params = {'channel': channel_id}
    response = requests.get(url, headers=HEADERS, params=params).json()

    if response['ok']:
        members = response['members']
        res = [{'member_id': member, 'channel_id': channel_id} for member in members]
        return res
    else:
        print(f"Error fetching members for channel {channel_id}: {response['error']}")
        return []

def main():
    ensure_directory(CHANNELS_DIR)
    ensure_directory(CHANNEL_MESSAGES_DIR)
    ensure_directory(THREADS_DIR)
    ensure_directory(USERS_DIR)
    ensure_directory(CHANNEL_MEMBERS_DIR)

    channels = fetch_channels()
    all_messages = []
    all_members = []
    all_threads = []
    for channel in channels:
        messages = fetch_channel_messages(channel['id'])
        for message in messages:
            message["channel_id"] = channel['id']
            all_messages.append(message) 
            
        members = fetch_channel_members(channel['id'])
        for member in members:
            all_members.append(member)

        for message in messages:
            if 'thread_ts' in message:
                threads = fetch_thread_replies(channel['id'], message['thread_ts'])
                for thread in threads:
                    all_threads.append(thread) 

    fetch_users()
    save_to_file(CHANNEL_MESSAGES_DIR, all_messages)
    save_to_file(CHANNEL_MEMBERS_DIR, all_members)
    save_to_file(THREADS_DIR, all_threads)
    
    
if __name__ == "__main__":
    main()
