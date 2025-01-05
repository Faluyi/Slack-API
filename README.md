# **Slack API Data Fetcher**

This Python project fetches and organizes data from a Slack workspace, including channel information, messages, threads, users, and channel members. The project supports checkpointing for efficient data fetching and prevents re-fetching already processed messages.

---

## **Features**

- Fetch and save:
  - **Channel information** (public and private channels)
  - **Channel messages** (with checkpointing for previously fetched messages)
  - **Thread replies**
  - **Users list**
  - **Channel members**
- Organizes fetched data into respective directories:
  - `channels/`
  - `channel_messages/`
  - `threads/`
  - `users/`
  - `channel_members/`
- Each file is saved as a JSON file with a timestamp-based filename (e.g., `2025_01_03_173539.json`).

---

## **Requirements**

- Python 3.7 or higher
- A Slack workspace with appropriate permissions for the token
- Slack OAuth token with the following scopes:
  - `channels:read`
  - `groups:read`
  - `channels:history`
  - `groups:history`
  - `users:read`
  - `conversations:read`
  - `conversations:history`
  - `conversations:members`

---

## **Setup Instructions**

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd slack-api-fetcher
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file**:
   - Add your Slack OAuth token in a `.env` file:
     ```
     ACCESS_TOKEN=your-slack-oauth-token
     ```

4. **Run the script**:
   ```bash
   python main.py
   ```

---

## **Directory Structure**

After execution, the fetched data will be organized as follows:

```
project/
├── channels/         # JSON files containing channel information
├── channel_messages/ # JSON files containing channel messages
├── threads/          # A single JSON file for all thread replies
├── users/            # JSON files containing user information
├── channel_members/  # JSON files containing channel members
├── checkpoint.json   # Tracks the last fetched message timestamp per channel
└── main.py  # Main script
```

---

## **Functionality**

### **1. Fetch Channels**
- Fetches details of all public and private channels.
- Saves the data in the `channels/` directory.

### **2. Fetch Messages**
- Fetches historical messages for each channel.
- Checkpointing ensures that only new messages are fetched on subsequent runs.
- Saves data in the `channel_messages/` directory.

### **3. Fetch Threads**
- Fetches all thread replies for messages that have threads.
- Saves data in a single file in the `threads/` directory.

### **4. Fetch Users**
- Fetches all users in the workspace.
- Saves data in the `users/` directory.

### **5. Fetch Channel Members**
- Fetches members for each channel.
- Saves data in the `channel_members/` directory.

---

## **Checkpointing**

- Checkpoints are stored in `checkpoint.json`.
- Tracks the latest fetched message timestamp (`ts`) for each channel.
- Ensures efficient re-runs by fetching only new messages.

---

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for details.
