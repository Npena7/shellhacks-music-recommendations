import streamlit as st
import streamlit.components.v1 as components

from main import (
    get_artist_info,
    get_similar_artists,
    get_similar_tracks,
    get_track_info,
    search_artist,
    search_track,
)

# browser tab title and icon, and use the full page width so the cards have more room
st.set_page_config(page_title="Sonar", page_icon="🎵", layout="wide")

# tooltip for Last.fm stats so viewers don't mistake them for Spotify streams
LASTFM_STATS_HELP = (
    "From Last.fm, counting people who track their listening with Last.fm. "
    "These are not Spotify stream counts."
)


# shorten large numbers for display, e.g. 4423629 -> "4.4M"
def format_number(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# convert a song's length from milliseconds to minutes:seconds, e.g. 225000 -> "3:45"
def format_duration(ms):
    total_seconds = ms // 1000
    return f"{total_seconds // 60}:{total_seconds % 60:02d}"


# show a recommendation's match score as a bar, then its listeners and plays as a small caption
def show_recommendation_stats(match, listeners=None, playcount=None):
    st.progress(match, text=f"{match:.0%} match")
    if listeners is None:
        st.caption("Stats unavailable")
    else:
        st.caption(
            f":material/person: {format_number(listeners)} listeners  \n"
            f":material/play_arrow: {format_number(playcount)} plays"
        )


#  make a recommendation the new search and add it to the trail
def explore(search_type, name, artist=None):
    item = {"type": search_type, "name": name, "artist": artist}
    st.session_state.trail.append(item)
    st.session_state.current = item
    st.session_state.scroll_to_top = True


#  go back to an earlier step and drop everything after it
def jump_to(index):
    st.session_state.trail = st.session_state.trail[: index + 1]
    st.session_state.current = st.session_state.trail[index]
    st.session_state.scroll_to_top = True


# Streamlit keeps the scroll position on reruns, so after exploring from the bottom
# of the page, scroll back up so the new artist/song profile is visible
def scroll_to_top():
    # a changing number makes Streamlit treat it as new HTML, so the script runs every time
    st.session_state.scroll_count = st.session_state.get("scroll_count", 0) + 1
    st.html(
        f"<script>/* {st.session_state.scroll_count} */"
        "document.querySelector('[data-testid=\"stMain\"]')"
        ".scrollTo({top: 0});</script>",
        unsafe_allow_javascript=True,
    )


# show the path the user has explored
def show_trail():
    trail = st.session_state.trail
    if len(trail) < 2:
        return
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        for i, item in enumerate(trail):
            if i > 0:
                st.markdown("→")
            # the last step is where the user is now, so it isn't clickable
            st.button(
                item["name"],
                key=f"trail_{i}",
                type="tertiary",
                on_click=jump_to,
                args=(i,),
                disabled=i == len(trail) - 1,
            )


st.title("Sonar")
st.caption("Ping an artist or song to discover what's nearby.")

# keep the search controls in the left half so the input doesn't stretch across the wide page
search_col, _ = st.columns(2)
with search_col:
    # let the user choose whether to search for an artist or a song
    search_type = st.radio("Search for", ["Artist", "Song"], horizontal=True)
    # ask the user for an artist's or song's name
    if search_type == "Artist":
        name = st.text_input("Enter an artist's name:").strip()
    else:
        name = st.text_input("Enter a song's name:").strip()
    search_clicked = st.button("Search")

# session_state keeps values between reruns (every button click reruns the whole script),
# so the results stay on screen after clicking Explore or a breadcrumb
if "current" not in st.session_state:
    st.session_state.current = None
    st.session_state.trail = []

if search_clicked:
    if not name:
        st.warning(f"Please enter a {search_type.lower()}'s name.")
        st.session_state.current = None
    else:
        # a typed search starts a new trail
        st.session_state.current = {"type": search_type, "name": name, "artist": None}
        st.session_state.trail = []

current = st.session_state.current
if st.session_state.pop("scroll_to_top", False):
    scroll_to_top()
if current:
    if current["type"] == "Artist":
        # Search for the artist using the Spotify API
        with st.spinner("Searching for artist..."):
            artist = search_artist(current["name"])
        if not artist:
            st.error(f"No artist found for {current['name']}.")
        else:
            # a typed search starts the trail with the artist Spotify found
            if not st.session_state.trail:
                st.session_state.trail.append(
                    {"type": "Artist", "name": artist["name"], "artist": None}
                )
            st.divider()
            show_trail()
            with st.spinner("Loading artist info..."):
                main_info, info_error = get_artist_info(artist["name"])

            left, right = st.columns([1, 2])
            # Left column: the artist's image (if available) and Spotify link
            with left:
                if artist["images"]:
                    st.image(artist["images"][0]["url"], width="stretch")
                st.link_button(
                    "View on Spotify", url=artist["external_urls"]["spotify"]
                )

            # Right column: name, Last.fm stats, tags, and bio
            with right:
                st.header(artist["name"])
                if info_error:
                    st.warning("Stats unavailable")
                else:
                    listeners = int(main_info["stats"]["listeners"])
                    playcount = int(main_info["stats"]["playcount"])
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(
                            "Last.fm listeners",
                            format_number(listeners),
                            help=LASTFM_STATS_HELP,
                        )
                    with c2:
                        st.metric(
                            "Last.fm plays",
                            format_number(playcount),
                            help=LASTFM_STATS_HELP,
                        )

                    tags = []
                    for tag in main_info["tags"]["tag"]:
                        tags.append(tag["name"])
                    if tags:
                        st.write(f"**Tags:** {', '.join(tags)}")

                    bio = main_info["bio"]["summary"].split("<a href")[0].strip()
                    if bio:
                        st.write(bio + "...")

                    st.link_button("Read more on Last.fm", main_info["url"])

                # Spotify's embedded player with the artist's top 10 songs
                # (30-second previews, or full songs if logged in to Spotify in the browser)
                components.iframe(
                    f"https://open.spotify.com/embed/artist/{artist['id']}",
                    height=352,
                )

            with st.spinner("Finding similar artists..."):
                # Find similar artists using the Last.fm API
                similar, error = get_similar_artists(artist["name"])
                if error:
                    st.error(f"Error: {error}")
                elif not similar:
                    st.info(f"No similar artists found for {artist['name']}.")
                else:
                    st.subheader(f"Similar artists to {artist['name']}:")
                    st.caption("Recommendations, match scores, and stats from Last.fm")
                    cols = st.columns(len(similar))
                    # Display similar artists with their images and Spotify links (if available)
                    for i, sim_artist in enumerate(similar):
                        recommendation_data = search_artist(sim_artist["name"])
                        with cols[i]:
                            if recommendation_data and recommendation_data["images"]:
                                st.image(
                                    recommendation_data["images"][0]["url"], width="stretch"
                                )
                            st.write(f"**{sim_artist['name']}**")
                            artist_info, error = get_artist_info(sim_artist["name"])
                            if error:
                                show_recommendation_stats(float(sim_artist["match"]))
                            else:
                                show_recommendation_stats(
                                    float(sim_artist["match"]),
                                    int(artist_info["stats"]["listeners"]),
                                    int(artist_info["stats"]["playcount"]),
                                )
                            st.button(
                                "Explore",
                                key=f"explore_{i}",
                                type="primary",
                                icon=":material/travel_explore:",
                                on_click=explore,
                                args=("Artist", sim_artist["name"]),
                            )
                            if (
                                recommendation_data
                                and recommendation_data["external_urls"]
                            ):
                                st.link_button(
                                    "View on Spotify",
                                    url=recommendation_data["external_urls"]["spotify"],
                                )
    else:
        # Search for the song using the Spotify API (explored songs also know their artist)
        with st.spinner("Searching for song..."):
            track = search_track(current["name"], current["artist"])
        if not track:
            st.error(f"No song found for {current['name']}.")
        else:
            # Last.fm needs the song and its main artist to find the right track
            main_artist = track["artists"][0]["name"]
            artist_names = []
            for track_artist in track["artists"]:
                artist_names.append(track_artist["name"])

            # a typed search starts the trail with the song Spotify found
            if not st.session_state.trail:
                st.session_state.trail.append(
                    {"type": "Song", "name": track["name"], "artist": main_artist}
                )
            st.divider()
            show_trail()
            with st.spinner("Loading song info..."):
                main_info, info_error = get_track_info(track["name"], main_artist)

            left, right = st.columns([1, 2])
            # Left column: the album cover (if available) and Spotify link
            with left:
                if track["album"]["images"]:
                    st.image(track["album"]["images"][0]["url"], width="stretch")
                st.link_button("View on Spotify", url=track["external_urls"]["spotify"])

            # Right column: song details, Last.fm stats, tags, and wiki summary
            with right:
                st.header(track["name"])
                st.write(f"**Artist:** {', '.join(artist_names)}")
                st.write(f"**Album:** {track['album']['name']}")
                st.write(f"**Duration:** {format_duration(track['duration_ms'])}")
                # compact Spotify player for this song
                components.iframe(
                    f"https://open.spotify.com/embed/track/{track['id']}",
                    height=152,
                )
                if info_error:
                    st.warning("Stats unavailable")
                else:
                    listeners = int(main_info["listeners"])
                    playcount = int(main_info["playcount"])
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(
                            "Last.fm listeners",
                            format_number(listeners),
                            help=LASTFM_STATS_HELP,
                        )
                    with c2:
                        st.metric(
                            "Last.fm plays",
                            format_number(playcount),
                            help=LASTFM_STATS_HELP,
                        )

                    tags = []
                    for tag in main_info["toptags"]["tag"]:
                        tags.append(tag["name"])
                    if tags:
                        st.write(f"**Tags:** {', '.join(tags)}")

                    # not every song has a wiki, so check before using it
                    if "wiki" in main_info:
                        summary = (
                            main_info["wiki"]["summary"].split("<a href")[0].strip()
                        )
                        if summary:
                            st.write(summary + "...")

                    st.link_button("Read more on Last.fm", main_info["url"])

            with st.spinner("Finding similar songs..."):
                # Find similar songs using the Last.fm API
                similar, error = get_similar_tracks(track["name"], main_artist)
                if error:
                    st.error(f"Error: {error}")
                elif not similar:
                    st.info(f"No similar songs found for {track['name']}.")
                else:
                    st.subheader(f"Similar songs to {track['name']}:")
                    st.caption("Recommendations, match scores, and stats from Last.fm")
                    cols = st.columns(len(similar))
                    # Display similar songs with their album covers and Spotify links (if available)
                    for i, sim_track in enumerate(similar):
                        sim_artist = sim_track["artist"]["name"]
                        recommendation_data = search_track(
                            sim_track["name"], sim_artist
                        )
                        with cols[i]:
                            if (
                                recommendation_data
                                and recommendation_data["album"]["images"]
                            ):
                                st.image(
                                    recommendation_data["album"]["images"][0]["url"],
                                    width="stretch",
                                )
                            st.write(f"**{sim_track['name']}**")
                            st.write(sim_artist)
                            track_info, error = get_track_info(
                                sim_track["name"], sim_artist
                            )
                            if error:
                                show_recommendation_stats(float(sim_track["match"]))
                            else:
                                show_recommendation_stats(
                                    float(sim_track["match"]),
                                    int(track_info["listeners"]),
                                    int(track_info["playcount"]),
                                )
                            st.button(
                                "Explore",
                                key=f"explore_{i}",
                                type="primary",
                                icon=":material/travel_explore:",
                                on_click=explore,
                                args=("Song", sim_track["name"], sim_artist),
                            )
                            if (
                                recommendation_data
                                and recommendation_data["external_urls"]
                            ):
                                st.link_button(
                                    "View on Spotify",
                                    url=recommendation_data["external_urls"]["spotify"],
                                )
