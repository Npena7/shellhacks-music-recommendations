import streamlit as st

from main import get_similar_artists, search_artist, get_artist_info

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

            # Display the artist's image if available
            if artist["images"]:
                st.image(artist["images"][0]["url"], width=300)
            st.link_button("View on Spotify", url=artist["external_urls"]["spotify"])
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
                            info_col = st.columns(2)
                            with info_col[0]:
                                st.metric("Listeners", f"{int(artist_info['stats']['listeners']):,}")
                            with info_col[1]:
                                st.metric("Playcount", f"{int(artist_info['stats']['playcount']):,}")
