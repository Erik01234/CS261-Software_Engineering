import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import "./App.css";
import AboutCompany from "./AboutCompany";
import ArticleAnalysis from "./ArticleAnalysis";
import FollowedCompanies from "./FollowedCompanies";
import SavedArticles from "./SavedArticles";
import LoginPage from "./LoginPage";
import HomePage from "./Homepage";
import Navbar from "./Navbar";
import RegisterPage from "./RegisterPage";
import ForgotPassword from "./ForgotPassword";

function App() {
  return (
    <Router>
      <div className="App bg-white flex flex-col min-h-screen">
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/about/:companyId" element={<AboutCompany />} />
          <Route path="/analysis/:headline" element={<ArticleAnalysis />} />
          <Route path="/followedcompanies" element={<FollowedCompanies />} />
          <Route path="/savedarticles" element={<SavedArticles />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgotpassword" element={<ForgotPassword />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
