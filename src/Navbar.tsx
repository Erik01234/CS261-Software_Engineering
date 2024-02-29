import React, { useState } from "react";
import { Link, useParams } from "react-router-dom";

function Navbar() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Toggle dropdown visibility
  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);
  return (
    <nav className="w-full bg-nav-bar-grey p-4 flex items-center justify-between sticky top-0 z-10">
      <div className="flex space-x-4">
        <span className="text-white text-4xl font-bold">CoRNIA</span>
        <button className="flex items-center text-white">
          <Link to="/home" className="flex items-center text-white">
            Home
            <img
              src={"/homeicon.png"}
              alt="Home"
              className="h-10 w-10 rounded-full ml-2"
              style={{ objectFit: "contain", padding: "8px" }}
            />
          </Link>
        </button>
        <button className="flex items-center text-white">
          Discover
          <img
            src={"/discovericon.png"}
            alt="Discover"
            className="h-10 w-10 rounded-full ml-2"
            style={{ objectFit: "contain", padding: "8px" }}
          />
        </button>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex">
          <button>
            <img
              src={"/filtericon.png"}
              alt="Filter"
              className="h-10 w-10 rounded-full ml-2"
              style={{ objectFit: "contain", padding: "8px" }}
            />
          </button>
          <input
            className="p-2 w-full max-w-md rounded mx-auto block"
            type="search"
            placeholder="Search"
          />
        </div>

        <div className="relative">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center text-white"
          >
            Profile
            <img
              src={"/profile.png"}
              alt="Profile"
              className="h-10 w-10 rounded-full ml-2"
            />
          </button>
          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 py-2 w-48 bg-white rounded-md shadow-xl z-20">
              <Link
                to="/savedarticles"
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Saved articles
              </Link>
              <Link
                to="/followedcompanies"
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Followed companies
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
