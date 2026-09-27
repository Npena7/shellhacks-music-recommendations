import streamlit as st

from main import search_artist, get_similar_artists

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
                for sim_artist in similar:
                    st.write(sim_artist["name"])
