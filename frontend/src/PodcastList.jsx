import React, { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import PodcastItem from "./PodcastItem";

function PodcastList() {
  const { getAccessTokenSilently } = useAuth0();
  const [podcasts, setPodcasts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPodcasts = async () => {
    try {
      const token = await getAccessTokenSilently();
      const res = await fetch("http://localhost:8000/api/podcasts", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      setPodcasts(data.podcasts || []);
    } catch (err) {
      console.error("Failed to load podcasts", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async (podcastId) => {
    try {
      const token = await getAccessTokenSilently();
      await fetch(`http://localhost:8000/api/podcasts/${podcastId}/favorite`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      fetchPodcasts(); // Refresh list
    } catch (err) {
      console.error("Failed to toggle favorite", err);
    }
  };

  useEffect(() => {
    fetchPodcasts();
  }, []);

  const favorites = podcasts.filter((p) => p.is_favorite);
  const others = podcasts.filter((p) => !p.is_favorite);

  return (
  <div className="mt-10 w-full max-w-2xl ml-10">
    <h2 className="text-2xl font-bold text-purple-700 mb-4">Your Podcasts</h2>

    {loading ? (
      <p>Loading podcasts...</p>
    ) : podcasts.length === 0 ? (
      <p className="text-gray-500">You haven’t generated any podcasts yet.</p>
    ) : (
      <>
        {favorites.length > 0 && (
          <>
            <h3 className="text-lg font-semibold text-yellow-500 mb-2">★ Favorites</h3>
            {favorites.map((podcast) => (
              <PodcastItem
                key={podcast.podcast_id}
                podcast={podcast}
                onToggleFavorite={toggleFavorite}
              />
            ))}
          </>
        )}

        {others.length > 0 && (
          <>
            {others.map((podcast) => (
              <PodcastItem
                key={podcast.podcast_id}
                podcast={podcast}
                onToggleFavorite={toggleFavorite}
              />
            ))}
          </>
        )}
      </>
    )}
  </div>
);

}

export default PodcastList;
