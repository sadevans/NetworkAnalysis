import os
import json
import requests
import webbrowser
import networkx as nx
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
dotenv_path = '../.env'
load_dotenv()

APP_ID = os.getenv('APP_ID')
REDIRECT_URI = 'https://oauth.vk.com/blank.html'
OAUTH_URL = (
    f'https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&'
    f'redirect_uri={REDIRECT_URI}&scope=friends,status,offline&response_type=token&'
    f'revoke=1&v=5.199'
)


def get_access_token() -> str:
    """
    Opens a web browser for user authentication and retrieves an access token.

    Returns:
        str: The VK API access token provided by the user.
    """
    print("Opening browser for authorization...")
    webbrowser.open(OAUTH_URL)
    return input("Enter your access_token copied from the URL after authorization: ")


def fetch_friends(user_id: str, access_token: str) -> List[Dict[str, Any]]:
    """
    Fetches a list of friends for the given VK user ID using the provided access token.

    Args:
        user_id (str): VK user ID.
        access_token (str): VK API access token.

    Returns:
        List[Dict[str, Any]]: A list of friends' data.
    """
    url = "https://api.vk.com/method/friends.get"
    params = {
        "user_id": user_id,
        "order": "name",
        "count": 5000,
        "offset": 0,
        "fields": [
            "first_name", "last_name", "id", "sex", "bdate", "country", 
            "city", "photo_id", "status", "can_post", "can_see_all_posts", 
            "can_write_private_message", "contacts", "domain", "education", 
            "has_mobile", "timezone", "last_seen", "nickname", "online", 
            "relation", "universities"
        ],
        "access_token": access_token,
        "v": "5.199"
    }
    response = requests.get(url, params=params)
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error decoding JSON. Check the request.")
        return []

    if 'error' in data:
        error = data['error']
        print(f"API Error: {error.get('error_msg', 'Unknown error')}")
        return []

    friends = data.get("response", {}).get("items", [])
    return [
        {
            "first_name": friend.get("first_name"),
            "last_name": friend.get("last_name"),
            "id": friend.get("id"),
            "sex": friend.get("sex"),
            "bdate": friend.get("bdate"),
            "country": friend.get("country"),
            "city": friend.get("city"),
            "photo_id": friend.get("photo_id"),
            "status": friend.get("status"),
            "can_post": friend.get("can_post"),
            "can_see_all_posts": friend.get("can_see_all_posts"),
            "can_write_private_message": friend.get("can_write_private_message"),
            "contacts": friend.get("contacts"),
            "domain": friend.get("domain"),
            "education": friend.get("education"),
            "has_mobile": friend.get("has_mobile"),
            "timezone": friend.get("timezone"),
            "last_seen": friend.get("last_seen"),
            "nickname": friend.get("nickname"),
            "online": friend.get("online"),
            "relation": friend.get("relation"),
            "universities": friend.get("universities"),
        }
        for friend in friends
    ]


def fetch_friends_of_each_friend(user_id: str, access_token: str, delay: float = 0.5) -> List[Dict[str, Any]]:
    """
    Fetches the friends of each friend of the user.

    Args:
        user_id (str): VK user ID.
        access_token (str): VK API access token.
        delay (float): Delay in seconds between API requests to avoid hitting rate limits.

    Returns:
        List[Dict[str, Any]]: A list of friends with their friends' IDs added.
    """
    print("Fetching your friends...")
    friends = fetch_friends(user_id, access_token)
    if not friends:
        print("You have no friends or an error occurred.")
        return []

    processed_friends = []

    for friend in friends:
        friend_id = str(friend.get("id"))
        friend_name = f"{friend.get('first_name', 'Unknown')} {friend.get('last_name', 'Unknown')}"
        print(f"Fetching friends of {friend_name} (ID: {friend_id})...")

        try:
            friends_of_friend = fetch_friends(friend_id, access_token)
            processed_friend = friend.copy()
            processed_friend['friends_ids'] = [str(f.get('id')) for f in friends_of_friend]
            processed_friend['friends_count'] = len(processed_friend['friends_ids'])
            processed_friends.append(processed_friend)
        except Exception as e:
            print(f"Error fetching friends of {friend_name} (ID: {friend_id}): {e}")
            continue

        time.sleep(delay)

    return processed_friends


def create_friends_network_graph(processed_friends: List[Dict[str, Any]]) -> nx.Graph:
    """
    Create a NetworkX graph from processed friends data.

    Args:
        processed_friends (List[Dict[str, Any]]): List of friends with their friends' IDs.

    Returns:
        nx.Graph: A graph representing the social network.
    """
    G = nx.Graph()

    for friend in processed_friends:
        friend_id = str(friend.get('id'))
        friend_name = f"{friend.get('first_name', 'Unknown')} {friend.get('last_name', 'Unknown')}"
        G.add_node(
            friend_id, 
            name=friend_name, 
            first_name=friend.get('first_name'), 
            last_name=friend.get('last_name')
        )

    for i, friend1 in enumerate(processed_friends):
        for friend2 in processed_friends[i + 1:]:
            friend1_id = str(friend1.get('id'))
            friend2_id = str(friend2.get('id'))

            if (friend2_id in friend1.get('friends_ids', []) and 
                friend1_id in friend2.get('friends_ids', [])):
                G.add_edge(friend1_id, friend2_id)

    return G


def save_to_json(data: Any, filename: str) -> None:
    """
    Saves data to a JSON file.

    Args:
        data (Any): Data to save.
        filename (str): Name of the file.
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def save_graph(graph: nx.Graph, filename: str) -> None:
    """
    Saves a graph to a GraphML file.

    Args:
        graph (nx.Graph): The graph to save.
        filename (str): File path to save the graph.
    """
    nx.write_gml(graph, filename)
    print(f"Graph saved to {filename}")


def main() -> None:
    access_token = os.getenv('ACCESS_TOKEN')
    if not access_token:
        print("Authorization failed, token not received.")
        return

    user_id = os.getenv('USER_ID')
    processed_friends = fetch_friends_of_each_friend(user_id, access_token)

    if processed_friends:
        save_to_json(processed_friends, './data/friends_of_friends.json')
        print("Saved friends of friends to 'friends_of_friends.json'")
    else:
        print("No data to save.")

    try:
        friends_network = create_friends_network_graph(processed_friends)
        save_graph(friends_network, './data/friends_network.gml')
        print(f"Total nodes: {friends_network.number_of_nodes()}")
        print(f"Total edges: {friends_network.number_of_edges()}")
    except Exception as e:
        print(f"Error creating network graph: {e}")


if __name__ == "__main__":
    main()
