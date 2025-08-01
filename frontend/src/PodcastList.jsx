import React, { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import PodcastItem from "./PodcastItem";

function PodcastList() {
  const { getAccessTokenSilently } = useAuth0();
  const [podcasts, setPodcasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all"); 
  const [sortBy, setSortBy] = useState("newest"); 

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

  useEffect(() => {
    fetchPodcasts();
  }, []);

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

  const applyFilters = (list) => {
    let filtered = [...list];

    if (filter === "favorites") {
      filtered = filtered.filter((p) => p.is_favorite);
    }

    if (sortBy === "newest") {
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else if (sortBy === "oldest") {
      filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    } else if (sortBy === "short") {
      filtered.sort((a, b) => a.length - b.length);
    } else if (sortBy === "long") {
      filtered.sort((a, b) => b.length - a.length);
    }

    return filtered;
  };

  const displayedPodcasts = applyFilters(podcasts);

  return (
    <div className="w-full max-w-4xl ml-10 mt-10">
      <h2 className="text-2xl font-bold text-purple-700 mb-4">Your Podcasts</h2>

      {/* Filter Controls */}
      <div className="flex gap-4 mb-6">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded"
        >
          <option value="all">All</option>
          <option value="favorites">Favorites</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded"
        >
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="short">Shortest</option>
          <option value="long">Longest</option>
        </select>
      </div>

      {/* Podcast List */}
      {loading ? (
        <p>Loading podcasts...</p>
      ) : displayedPodcasts.length === 0 ? (
        <p className="text-gray-500">No podcasts match your filters.</p>
      ) : (
        displayedPodcasts.map((podcast) => (
          <PodcastItem
            key={podcast.podcast_id}
            podcast={podcast}
            onToggleFavorite={toggleFavorite}
          />
        ))
      )}
    </div>
  );
}

export default PodcastList;
