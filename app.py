import streamlit as st

from main import (
    get_artist_info,
    get_similar_artists,
    get_similar_tracks,
    get_track_info,
    search_artist,
    search_track,
)


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


st.title("Music Discovery")
# let the user choose whether to search for an artist or a song
search_type = st.radio("Search for", ["Artist", "Song"], horizontal=True)
# ask the user for an artist's or song's name
if search_type == "Artist":
    name = st.text_input("Enter an artist's name:").strip()
else:
    name = st.text_input("Enter a song's name:").strip()


if st.button("Search"):
    if not name:
        st.warning(f"Please enter a {search_type.lower()}'s name.")
    elif search_type == "Artist":
        # Search for the artist using the Spotify API
        with st.spinner("Searching for artist..."):
            artist = search_artist(name)
        if not artist:
            st.error(f"No artist found for {name}.")
        else:
            st.divider()
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
                                    recommendation_data["images"][0]["url"], width=150
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
                            if (
                                recommendation_data
                                and recommendation_data["external_urls"]
                            ):
                                st.link_button(
                                    "View on Spotify",
                                    url=recommendation_data["external_urls"]["spotify"],
                                )
    else:
        # Search for the song using the Spotify API
        with st.spinner("Searching for song..."):
            track = search_track(name)
        if not track:
            st.error(f"No song found for {name}.")
        else:
            # Last.fm needs the song and its main artist to find the right track
            main_artist = track["artists"][0]["name"]
            artist_names = []
            for track_artist in track["artists"]:
                artist_names.append(track_artist["name"])

            st.divider()
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
                                    width=150,
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
                            if (
                                recommendation_data
                                and recommendation_data["external_urls"]
                            ):
                                st.link_button(
                                    "View on Spotify",
                                    url=recommendation_data["external_urls"]["spotify"],
                                )
