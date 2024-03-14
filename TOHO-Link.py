import sqlite3
from plexapi.server import PlexServer
from colorama import Fore, Style, init
from configs import TOHO_config
from concurrent.futures import ThreadPoolExecutor
# Initialize Colorama for colored output
init(autoreset=True)

_configs = TOHO_config.configimport()

class TouhouMusicDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def find_matching_song(self, song_name, artist_name):
        """
        Attempts to find a matching song in the Touhou database by name and artist,
        using the correct references for songtrack_artist_id and source_track_id.
        """
        self.cursor.execute("""
            SELECT source_tracks.name
            FROM tracks
            INNER JOIN track_vs_source_index ON tracks.id = track_vs_source_index.track_id
            INNER JOIN source_tracks ON track_vs_source_index.source_track_id = source_tracks.id
            INNER JOIN songtrack_artist_index ON tracks.songtrack_artist_id = songtrack_artist_index.id
            WHERE tracks.name LIKE ? AND songtrack_artist_index.name LIKE ?
        """, ('%' + song_name + '%', '%' + artist_name + '%'))
        result = self.cursor.fetchone()
        return result[0] if result else None


    def close(self):
        """Closes the database connection."""
        self.conn.close()

class PlexMusicManager:
    def __init__(self, baseurl, token):
        self.server = PlexServer(baseurl, token)

    def get_all_music(self):
        """Retrieve all music tracks (songs) from the Plex library."""
        music_library = self.server.library.section('Music')
        return music_library.searchTracks()

    def add_track_to_matched_collection(self, track, source_track_name):
        """
        Adds a track to a collection that contains the source track name.
        If no matching collection is found, creates a new one.
        """
        matched_collections = [col for col in self.server.library.section('Music').collections() if source_track_name.lower() in col.title.lower()]
        collection_name = matched_collections[0].title if matched_collections else source_track_name
        track.addCollection(collection_name)
        print(Fore.GREEN + f"Added '{track.title}' to collection: '{collection_name}'." + Style.RESET_ALL)

def process_music_library(plex_baseurl, plex_token, db_path):
    print(Fore.BLUE + "Initializing Plex and Touhou Music Database connections..." + Style.RESET_ALL)
    plex_manager = PlexMusicManager(plex_baseurl, plex_token)
    touhou_db = TouhouMusicDB(db_path)

    try:
        print(Fore.BLUE + "Fetching all music tracks from Plex..." + Style.RESET_ALL)
        all_tracks = plex_manager.get_all_music()
        print(Fore.GREEN + f"Total tracks fetched: {len(all_tracks)}" + Style.RESET_ALL)

        for track in all_tracks:
            artist_name = track.grandparentTitle  # Assuming 'grandparentTitle' holds the artist's name
            print(Fore.CYAN + f"Processing '{track.title}' by '{artist_name}'..." + Style.RESET_ALL)
            source_song_name = touhou_db.find_matching_song(track.title, artist_name)
            
            if source_song_name:
                print(Fore.YELLOW + f"Potential match found: '{track.title}' -> '{source_song_name}'." + Style.RESET_ALL)
                plex_manager.add_track_to_matched_collection(track, source_song_name)
            else:
                print(Fore.RED + f"No source found or multiple sources found for '{track.title}'. Skipped." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
    finally:
        touhou_db.close()
        print(Fore.GREEN + "Process completed." + Style.RESET_ALL)

print(f"""
+--------------------------------------------------+
| Starting 2hu matching agent                      |
| Plex URL: {_configs.plex_baseurl}                |
| Token: [REDACTED]                                |
| Database Path: {_configs.db_path}                |
+--------------------------------------------------+  
""")

start = input("Start? (y/n): ")
if start.lower() == 'y':
    process_music_library(_configs.plex_baseurl, _configs.plex_token, _configs.db_path)
