import React from "react";
import { useAuth0 } from "@auth0/auth0-react";

function Login() {
  const { loginWithRedirect, isAuthenticated } = useAuth0();
  if (!isAuthenticated && !window.location.search.includes("code=")) {
    loginWithRedirect({
      authorizationParams: {
        redirect_uri: "https://www.podifynews.com"
      }
    });
    return null; 
  }

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-purple-400 via-pink-300 to-yellow-200">
      <button 
        onClick={() => loginWithRedirect()}
        className="bg-white px-6 py-3 rounded-lg shadow-lg text-purple-600 font-bold"
      >
        Click to Login
      </button>
    </div>
  );
}

export default Login;