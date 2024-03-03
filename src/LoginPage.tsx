import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import SimpleNavbar from "./SimpleNavbar";

function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (event: { preventDefault: () => void }) => {
    event.preventDefault();
    // Login logic
    console.log("Login with:", username, password);
    navigate("/home");
  };

  return (
    <div>
      <SimpleNavbar />
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="absolute top-0 left-0 right-0 bottom-0 bg-gray-600 bg-opacity-50"></div>
        <div className="z-10 px-8 py-6 mt-4 text-left bg-white shadow-lg rounded-xl w-96 min-w-[500px] min-h-[400px]">
          <h3 className="text-4xl font-bold text-center">Log in</h3>
          <form onSubmit={handleSubmit}>
            <div className="mt-4">
              <div>
                <input
                  type="text"
                  placeholder="Email address"
                  id="email"
                  className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="mt-4">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Password"
                  className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="text-sm text-blue-600 hover:underline"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? "Hide" : "Show"} password
                </button>
              </div>
              <div className="flex items-baseline justify-between">
                <button className="w-full px-6 py-2 mt-4 text-white bg-gray-700 rounded-lg hover:bg-gray-600">
                  Login
                </button>
              </div>
              <div className="border-b border-gray-400 my-4"></div>
              <div className="flex justify-between">
                <a
                  href="#"
                  className="text-sm text-blue-600 hover:underline"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate("/forgotpassword");
                  }}
                >
                  Forgot Password
                </a>
                <a
                  href="#"
                  className="text-sm text-blue-600 hover:underline"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate("/register");
                  }}
                >
                  Create account
                </a>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
