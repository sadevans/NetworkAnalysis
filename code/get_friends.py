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
        # "fields": "first_name,last_name,id,sex,bdate,country,city,photo_id,\
        #     status,can_post,can_see_all_posts,can_write_private_message,contacts,\
        #     domain,education,has_mobile,timezone,last_seen, nickname,online,relation, universities, education",
        "fields": [
                "first_name",
                "last_name",
                "id",
                "sex",
                "bdate",
                "country",
                "city",
                "photo_id",
                "status",
                "can_post",
                "can_see_all_posts",
                "can_write_private_message",
                "contacts",
                "domain",
                "education",
                "has_mobile",
                "timezone",
                "last_seen",
                "nickname",
                "online",
                "relation",
                "universities",
                "education",
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

    # print(data)
    friends = data.get("response", {}).get("items", [])
    # print(friends)
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
            "education": friend.get("education"),

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
    Create a NetworkX graph from processed friends data with comprehensive node attributes.

    Args:
        processed_friends (List[Dict[str, Any]]): List of friends with their friends' IDs.

    Returns:
        nx.Graph: A graph representing the social network.
    """
    G = nx.Graph()

    for friend in processed_friends:
        friend_id = str(friend.get('id'))
        friend_name = f"{friend.get('first_name', 'Unknown')} {friend.get('last_name', 'Unknown')}"
        
        node_attributes = {
            'name': friend_name,
            'first_name': friend.get('first_name'),
            'last_name': friend.get('last_name'),
            'id': friend_id,
            
            'sex': friend.get('sex'),
            'bdate': friend.get('bdate'),
            
            'country': friend.get('country', {}).get('title') if isinstance(friend.get('country'), dict) else friend.get('country'),
            'city': friend.get('city', {}).get('title') if isinstance(friend.get('city'), dict) else friend.get('city'),
            
            'friends_count': friend.get('friends_count', 0),
            'friends_ids': friend.get('friends_ids', []),
            
            'domain': friend.get('domain'),
            'online': friend.get('online'),
            'last_seen': friend.get('last_seen', {}).get('time') if isinstance(friend.get('last_seen'), dict) else friend.get('last_seen'),
            
            'can_post': friend.get('can_post'),
            'can_write_private_message': friend.get('can_write_private_message'),
            'relation': friend.get('relation'),
            
            'education': friend.get('education'),
            'universities': [univ.get('name') for univ in friend.get('universities', [])] if friend.get('universities') else None,

            'education': friend.get('education'),

        }

        node_attributes = {k: v for k, v in node_attributes.items() if v is not None}
        
        G.add_node(friend_id, **node_attributes)

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


def create_graph_from_json(json_file_path: str) -> nx.Graph:
    """
    Create a NetworkX graph from a JSON file with friends data.

    Args:
        json_file_path (str): Path to the JSON file containing friends data.

    Returns:
        nx.Graph: A graph representing the social network.
    """
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        friends_data = json.load(file)

    # Create a new graph
    G = nx.Graph()

    # Add nodes with attributes
    for friend in friends_data:
        # Convert ID to string to ensure consistency
        friend_id = str(friend.get('id'))
        friend_name = f"{friend.get('first_name', 'Unknown')} {friend.get('last_name', 'Unknown')}"

        
        # Prepare node attributes
        node_attributes = {
            'vk_id': friend_id,
            'name': friend_name,
            'first_name': friend.get('first_name'),
            'last_name': friend.get('last_name'),
        }

        # Add all non-None attributes
        for key, value in friend.items():
            if key != 'friends_ids' and value is not None:
                if key == 'sex':
                    value = 'female' if value == 1 else 'male' if value == 2 else 'unknown'
                node_attributes[key] = value

        # Add node to the graph
        G.add_node(friend_id, **node_attributes)
        # G.add_node(friend_name, **node_attributes)


    # Add edges based on mutual friends
    for friend in friends_data:
        friend_id = str(friend.get('id'))
        friends_ids = friend.get('friends_ids', [])


        for other_friend_id in friends_ids:
            # Ensure both nodes exist in the graph before adding an edge
            if G.has_node(friend_id) and G.has_node(other_friend_id):
                G.add_edge(friend_id, other_friend_id)

    return G

def main() -> None:
    access_token = os.getenv('ACCESS_TOKEN')
    if not access_token:
        print("Authorization failed, token not received.")
        return

    user_id = os.getenv('USER_ID')
    # processed_friends = fetch_friends_of_each_friend(user_id, access_token)

    # if processed_friends:
    #     save_to_json(processed_friends, './data/friends_of_friends_new.json')
    #     print("Saved friends of friends to 'friends_of_friends_new.json'")
    # else:
    #     print("No data to save.")


    graph = create_graph_from_json('./data/friends_of_friends_new_updated.json')
    save_graph(graph, './data/friends_network_new_updated.gml')

    # try:
    #     friends_network = create_friends_network_graph(processed_friends)
    #     save_graph(friends_network, './data/friends_network.gml')
    #     print(f"Total nodes: {friends_network.number_of_nodes()}")
    #     print(f"Total edges: {friends_network.number_of_edges()}")
    # except Exception as e:
    #     print(f"Error creating network graph: {e}")


if __name__ == "__main__":
    main()
