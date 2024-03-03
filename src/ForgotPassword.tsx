import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import SimpleNavbar from "./SimpleNavbar";

type Step = "request" | "verify" | "change";

function ForgotPassword() {
  const [step, setStep] = useState<Step>("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const navigate = useNavigate();

  const handleRequestReset = (event: React.FormEvent) => {
    event.preventDefault();
    // TODO: Implement request reset logic
    console.log("Requesting reset for:", email);
    setStep("verify");
  };

  const handleVerifyCode = (event: React.FormEvent) => {
    event.preventDefault();
    // TODO: Implement verify code logic
    console.log("Verifying code:", code);
    setStep("change");
  };

  const handleChangePassword = (event: React.FormEvent) => {
    event.preventDefault();
    // TODO: Implement change password logic
    console.log("Changing password to:", newPassword);
    navigate("/"); // Redirect to login page after password change
  };

  return (
    <div>
      <SimpleNavbar />
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="z-10 px-8 py-6 text-left bg-white shadow-lg rounded-xl">
          {step === "request" && (
            <form onSubmit={handleRequestReset}>
              <h3 className="text-2xl font-bold">Forgot Password</h3>
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full px-4 py-2 mt-2 border rounded-md"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <button
                type="submit"
                className="btn-primary w-full px-6 py-2 mt-4 text-white bg-gray-700 rounded-lg hover:bg-gray-600"
              >
                Request Reset
              </button>
            </form>
          )}
          {step === "verify" && (
            <form onSubmit={handleVerifyCode}>
              <h3 className="text-2xl font-bold">Verify Code</h3>
              <input
                type="text"
                placeholder="Enter code sent to your email"
                className="w-full px-4 py-2 mt-2 border rounded-md"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
              />
              <button
                type="submit"
                className="btn-primary w-full px-6 py-2 mt-4 text-white bg-gray-700 rounded-lg hover:bg-gray-600"
              >
                Verify
              </button>
            </form>
          )}
          {step === "change" && (
            <form onSubmit={handleChangePassword}>
              <h3 className="text-2xl font-bold">Change Your Password</h3>
              <input
                type="password"
                placeholder="Enter new password"
                className="w-full px-4 py-2 mt-2 border rounded-md"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
              <button
                type="submit"
                className="btn-primary w-full px-6 py-2 mt-4 text-white bg-gray-700 rounded-lg hover:bg-gray-600"
              >
                Change Password
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
