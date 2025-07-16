import React, { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAudioUrl("");

    try {
      const res = await fetch("http://localhost:8000/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      const data = await res.json();
      setAudioUrl(data.audio_url);
    } catch (err) {
      console.error("Error generating podcast:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-purple-400 via-pink-300 to-yellow-200 flex items-center justify-center">
      <div className="bg-white bg-opacity-90 shadow-2xl rounded-2xl p-10 w-[600px] text-center">
        <h1 className="text-5xl font-extrabold text-purple-700 mb-8">
          Article to Podcast
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <input
            type="url"
            placeholder="Paste article URL..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full border-2 border-purple-400 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-4 focus:ring-purple-300"
            required
          />

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-white font-bold py-3 px-6 rounded-xl text-lg transition"
            disabled={loading}
          >
            {loading ? "Generating..." : "Convert to Podcast 🎧"}
          </button>
        </form>

        {audioUrl && (
          <div className="mt-10">
            <h2 className="text-2xl font-semibold text-green-700 mb-4">
              Your Podcast:
            </h2>
            <audio controls className="w-full">
              <source src={audioUrl} type="audio/mp3" />
              Your browser does not support the audio element.
            </audio>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
