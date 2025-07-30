import React from "react";

function PodcastItem({ podcast, onToggleFavorite }) {
  return (
    <div className="bg-white rounded-xl p-4 shadow mb-4">
      <h3 className="font-bold text-lg text-purple-700 mb-2">
        {podcast.title || "Untitled Podcast"}
      </h3>
      <audio controls className="w-full mb-2">
        <source src={podcast.audio_url} type="audio/mp3" />
      </audio>
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">{new Date(podcast.created_at).toLocaleString()}</p>
        <button
          onClick={() => onToggleFavorite(podcast.podcast_id)}
          className={`text-sm font-semibold px-4 py-1 rounded ${
            podcast.is_favorite ? "bg-yellow-400 text-white" : "bg-gray-200 text-gray-700"
          }`}
        >
          {podcast.is_favorite ? "★ Favorite" : "☆ Favorite"}
        </button>
      </div>
    </div>
  );
}

export default PodcastItem;
