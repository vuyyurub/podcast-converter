import React from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Login from "./Login";
import Home from "./Home";
import PodcastPage from "./PodcastPage";

function App() {
  const { isAuthenticated, isLoading, logout } = useAuth0();

  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <Login />;

  return (
    <Router>
      <div className="relative h-screen w-screen bg-gradient-to-br from-purple-400 via-pink-300 to-yellow-200">
        <nav className="absolute top-0 w-full flex justify-between items-center p-5 bg-white bg-opacity-60 backdrop-blur-sm shadow-md z-50">
          <div className="flex gap-6">
            <Link
              to="/"
              className="text-purple-700 font-bold hover:underline text-lg"
            >
              Convert
            </Link>
            <Link
              to="/podcasts"
              className="text-purple-700 font-bold hover:underline text-lg"
            >
              My Podcasts
            </Link>
          </div>
          <button
            onClick={() =>
              logout({
                returnTo: "https://www.podifynews.com/login", 
              })
            }
            className="bg-red-500 text-white px-4 py-2 rounded shadow"
          >
            Log Out
          </button>
        </nav>

        <div className="flex items-center justify-center h-full pt-20">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/podcasts" element={<PodcastPage />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
