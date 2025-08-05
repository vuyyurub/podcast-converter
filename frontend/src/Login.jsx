import React, { useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";

function Login() {
  const { loginWithRedirect, isAuthenticated } = useAuth0();

  useEffect(() => {
    if (!isAuthenticated) {
      loginWithRedirect();
    }
  }, [loginWithRedirect, isAuthenticated]);

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-purple-400 via-pink-300 to-yellow-200">
      <p className="text-white text-lg">Redirecting to login...</p>
    </div>
  );
}

export default Login;