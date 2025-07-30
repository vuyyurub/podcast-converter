// src/Home.jsx
import React, { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

function Home() {
  const { getAccessTokenSilently } = useAuth0();
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [inputMode, setInputMode] = useState("url");
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAudioUrl("");

    try {
      const token = await getAccessTokenSilently();
      const res = await fetch("http://localhost:8000/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          url: inputMode === "url" ? url : null,
          text: inputMode === "text" ? text : null,
        }),
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
    <div className="bg-white bg-opacity-90 shadow-2xl rounded-2xl p-10 w-[600px] text-center">
      <h1 className="text-5xl font-extrabold text-purple-700 mb-8">Article to Podcast</h1>

      <div className="flex justify-center mb-6">
        <button
          onClick={() => setInputMode("url")}
          className={`px-4 py-2 rounded-l-xl font-medium border ${
            inputMode === "url"
              ? "bg-purple-600 text-white"
              : "bg-white text-purple-600 border-purple-300"
          }`}
        >
          URL
        </button>
        <button
          onClick={() => setInputMode("text")}
          className={`px-4 py-2 rounded-r-xl font-medium border ${
            inputMode === "text"
              ? "bg-purple-600 text-white"
              : "bg-white text-purple-600 border-purple-300"
          }`}
        >
          Text
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {inputMode === "url" ? (
          <input
            type="url"
            placeholder="Paste article URL..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full border-2 border-purple-400 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-4 focus:ring-purple-300"
            required
          />
        ) : (
          <textarea
            placeholder="Paste article text..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="w-full border-2 border-purple-400 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-4 focus:ring-purple-300"
            rows="6"
            required
          />
        )}

        <button
          type="submit"
          className="w-full bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-white font-bold py-3 px-6 rounded-xl text-lg transition"
          disabled={loading}
        >
          {loading ? "Generating..." : "Convert to Podcast"}
        </button>
      </form>

      {audioUrl && (
        <div className="mt-10">
          <h2 className="text-2xl font-semibold text-green-700 mb-4">Your Podcast:</h2>
          <audio controls className="w-full">
            <source src={audioUrl} type="audio/mp3" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
}

export default Home;
