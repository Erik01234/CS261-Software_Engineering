// RegisterPage.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import SimpleNavbar from "./SimpleNavbar";

function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (event: { preventDefault: () => void }) => {
    event.preventDefault();
    // Registration logic here
    console.log("Register with:", email, password, confirmPassword);
    navigate("/home");
  };

  return (
    <div>
      <SimpleNavbar />
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="absolute top-0 left-0 right-0 bottom-0 bg-gray-600 bg-opacity-50"></div>
        <div className="z-10 px-8 py-6 mt-4 text-left bg-white shadow-lg rounded-xl w-96 min-w-[500px] min-h-[400px]">
          <h3 className="text-4xl font-bold text-center">Register</h3>
          <form onSubmit={handleSubmit}>
            <div>
              <input
                type="email"
                placeholder="Email address"
                className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
            <div className="mt-4">
              <input
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm Password"
                className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <button
                type="button"
                className="text-sm text-blue-600 hover:underline"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? "Hide" : "Show"} password
              </button>
            </div>
            <button className="px-6 py-2 mt-4 w-full text-white bg-gray-700 rounded-lg hover:bg-gray-600">
              Register
            </button>
            <div className="text-center mt-4">
              <a
                href="#"
                className="text-sm text-blue-600 hover:underline"
                onClick={(e) => {
                  e.preventDefault();
                  navigate("/login"); // Make sure this path is correct for your login page
                }}
              >
                Already have an account? Log in
              </a>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
