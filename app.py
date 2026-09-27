import streamlit as st

from main import get_similar_artists, search_artist, get_artist_info


# shorten large numbers for display, e.g. 4423629 -> "4.4M"
def format_number(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


st.title("Music Discovery")
# ask the user for an artist's name
name = st.text_input("Enter an artist's name:").strip()


if st.button("Search"):
    if not name:
        st.warning("Please enter an artist's name.")
    else:
        # Search for the artist using the Spotify API
        artist = search_artist(name)
        if not artist:
            st.error(f"No artist found for {name}.")
        else:
            st.success(f"Showing results for {artist['name']}")
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
                        st.metric("Listeners", format_number(listeners))
                    with c2:
                        st.metric("Plays", format_number(playcount))

                    tags = []
                    for tag in main_info["tags"]["tag"]:
                        tags.append(tag["name"])
                    if tags:
                        st.write(f"**Tags:** {', '.join(tags)}")

                    bio = main_info["bio"]["summary"].split("<a href")[0].strip()
                    if bio:
                        st.write(bio + "...")

                    st.link_button("Read more on Last.fm", main_info["url"])

            # Find similar artists using the Last.fm API
            similar, error = get_similar_artists(artist["name"])
            if error:
                st.error(f"Error: {error}")
            elif not similar:
                st.info(f"No similar artists found for {artist['name']}.")
            else:
                st.subheader(f"Similar artists to {artist['name']}:")
                cols = st.columns(len(similar))
                # Display similar artists with their images and Spotify links (if available)
                for i, sim_artist in enumerate(similar):
                    recommendation_data = search_artist(sim_artist["name"])
                    with cols[i]:
                        if recommendation_data and recommendation_data["images"]:
                            st.image(recommendation_data["images"][0]["url"], width=150)
                        st.write(sim_artist["name"])
                        if recommendation_data and recommendation_data["external_urls"]:
                            st.link_button(
                                "View on Spotify",
                                url=recommendation_data["external_urls"]["spotify"],
                            )
                        artist_info, error = get_artist_info(sim_artist["name"])
                        if error:
                            st.warning(f"Error fetching artist info: {error}")
                        else:
                            with st.expander("Stats"):
                                st.metric(
                                    "Listeners",
                                    f"{int(artist_info['stats']['listeners']):,}",
                                )
                                st.metric(
                                    "Playcount",
                                    f"{int(artist_info['stats']['playcount']):,}",
                                )
