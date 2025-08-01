import React from "react";
import PodcastList from "./PodcastList";

function PodcastPage() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-purple-400 via-pink-300 to-yellow-200 pt-10 px-6">
      <PodcastList />
    </div>
  );
}

export default PodcastPage;
