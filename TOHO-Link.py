import sqlite3

from plexapi.server import PlexServer
from colorama import Fore, Style
from configs import TOHO_config

_configs = TOHO_config.configimport()
class TouhouMusicDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def find_source_song(self, song_name):
        self.cursor.execute("SELECT id FROM tracks WHERE name LIKE ?", ('%' + song_name + '%',))
        track_id_result = self.cursor.fetchone()
        if not track_id_result:
            print(Fore.RED + "Song not found in Touhou DB." + Style.RESET_ALL)
            return None
        track_id = track_id_result[0]
        self.cursor.execute("SELECT source_track_id FROM track_vs_source_index WHERE track_id = ?", (track_id,))
        source_track_id_result = self.cursor.fetchone()
        if not source_track_id_result:
            print(Fore.YELLOW + "Source song not found for track in Touhou DB." + Style.RESET_ALL)
            return None
        source_track_id = source_track_id_result[0]
        self.cursor.execute("SELECT name FROM source_tracks WHERE id = ?", (source_track_id,))
        source_track_name_result = self.cursor.fetchone()
        if source_track_name_result:
            return source_track_name_result[0]
        else:
            print(Fore.RED + "Error retrieving source song from Touhou DB." + Style.RESET_ALL)
            return None

    def close(self):
        self.conn.close()


class PlexMusicManager:
    def __init__(self, baseurl, token):
        self.server = PlexServer(baseurl, token)

    def get_all_music(self):
        """Retrieve all music tracks (songs) from the Plex library."""
        music_library = self.server.library.section('Music')
        return music_library.searchTracks()

    def add_track_to_collection(self, track, collection_name):
        """Add a specific track to a collection, creating the collection if it doesn't exist."""
        if track:
            track.addCollection(collection_name)
            print(Fore.GREEN + f"Added '{track.title}' to collection: '{collection_name}'." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Track not found, cannot add to collection." + Style.RESET_ALL)


from colorama import init

# Initialize colorama
init(autoreset=True)

# Example integration function (you'll fill in the specifics)
def process_music_library(plex_baseurl, plex_token, db_path):
    print(Fore.BLUE + "Initializing Plex and Touhou Music Database connections..." + Style.RESET_ALL)
    plex_manager = PlexMusicManager(plex_baseurl, plex_token)
    touhou_db = TouhouMusicDB(db_path)

    try:
        print(Fore.BLUE + "Fetching all music tracks from Plex..." + Style.RESET_ALL)
        all_tracks = plex_manager.get_all_music()
        print(Fore.GREEN + f"Total tracks fetched: {len(all_tracks)}" + Style.RESET_ALL)

        for track in all_tracks:
            print(Fore.CYAN + f"Processing '{track.title}'..." + Style.RESET_ALL)
            source_song_name = touhou_db.find_source_song(track.title)
            if source_song_name:
                print(Fore.YELLOW + f"Potential match found: '{track.title}' -> '{source_song_name}'." + Style.RESET_ALL)
                #confirm = input(Fore.YELLOW + f"Add '{track.title}' to collection named '{source_song_name}'? (y/n): " + Style.RESET_ALL)
                #if confirm.lower() == 'y':
                plex_manager.add_track_to_collection(track, source_song_name)
                print(Fore.GREEN + f"Successfully added '{track.title}' to '{source_song_name}' collection." + Style.RESET_ALL)
                #else:
                 #   print(Fore.MAGENTA + f"Skipped adding '{track.title}' to any collection." + Style.RESET_ALL)
            else:
                print(Fore.RED + f"No source found or multiple sources found for '{track.title}'. Skipped." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
    finally:
        print(Fore.BLUE + "Closing database connection..." + Style.RESET_ALL)
        touhou_db.close()
        print(Fore.GREEN + "Process completed." + Style.RESET_ALL)


print(f"""
+--------------------------------------------------+
+Starting 2hu matching agent      
+{_configs.plex_baseurl}
+{_configs.plex_token}
+{_configs.db_path}      
+--------------------------------------------------+  """)
start=input("Starty?")
if start:
    process_music_library(_configs.plex_baseurl,_configs.plex_token,_configs.db_path)
