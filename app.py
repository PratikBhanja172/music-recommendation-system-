import pickle
import warnings
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Suppress all warnings (including deprecation)
warnings.filterwarnings("ignore")

# Spotify credentials
CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"

# Spotify client setup
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load data
try:
    music = pickle.load(open('df.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    st.success("Data loaded successfully.")
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# Get album cover from Spotify
def get_song_album_cover_url(song_name, artist_name):
    query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=query, type="track")
    if results and results["tracks"]["items"]:
        return results["tracks"]["items"][0]["album"]["images"][0]["url"]
    return "https://i.postimg.cc/0QNxYz4V/social.png"  # fallback image

# Recommendation logic
def recommend(song):
    if song not in music['song'].values:
        return [], []
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    names, posters = [], []
    for i in distances[1:6]:
        name = music.iloc[i[0]].song
        artist = music.iloc[i[0]].artist
        names.append(name)
        posters.append(get_song_album_cover_url(name, artist))
    return names, posters

# Streamlit UI
st.markdown("<h1 style='text-align: center;'>Music Recommender System</h1>", unsafe_allow_html=True)

# Dropdown and Button
if 'song' in music.columns and not music['song'].isnull().all():
    music_list = music['song'].dropna().unique()
    selected_song = st.selectbox("Select a song to get recommendations:", music_list)

    if st.button("Show Recommendation"):
        names, posters = recommend(selected_song)
        if names:
            st.markdown("Recommended Songs:")
            cols = st.columns(len(names))
            for i in range(len(names)):
                with cols[i]:
                    st.image(posters[i], use_container_width=True)
                    st.caption(names[i])
        else:
            st.warning("No recommendations found. Try a different song.")
else:
    st.error("No songs found in the dataset.")
