import React from "react";
import { useParams } from "react-router-dom";
import Navbar from "./Navbar";

function FollowedCompanies() {
  let { headline } = useParams(); // Use article headline to fetch the article's analysis

  return (
    <div className="text-left">
      <Navbar />
      <h1 className="font-bold font-inter text-4xl pl-36 pt-8">
        Followed Companies
      </h1>
      <div className="flex items-center mt-4 pl-40 pt-8 pr-40">
        <img
          src="/teslaIcon.png"
          alt="Company Logo"
          className="w-12 h-12 mr-4"
        />{" "}
        {/* Assuming logo.svg is your logo */}
        <div className="pl-4">
          <button className="font-inika font-semibold text-2xl">Tesla</button>{" "}
          {/* Company name */}
          <div className="flex mt-1">
            <span className="font-inika text-l text-gray-500 mr-2">
              Keywords:
            </span>{" "}
            {/* Keywords label */}
            <div className="flex">
              <button className="bg-gray-200 text-gray-700 rounded-full px-2 py-1 mr-2">
                automotive
              </button>{" "}
              {/* First keyword */}
              <button className="bg-gray-200 text-gray-700 rounded-full px-2 py-1">
                energy
              </button>{" "}
              {/* Second keyword */}
            </div>
          </div>
        </div>
        <button className="ml-auto bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-full">
          Unfollow
        </button>{" "}
        {/* Unfollow button */}
      </div>
      <hr className="border-t border-gray-400 mt-4 ml-40 mr-40" /> {/* Line */}
      <div className="flex items-center mt-4 pl-40 pt-8 pr-40">
        <img
          src="/teslaIcon.png"
          alt="Company Logo"
          className="w-12 h-12 mr-4"
        />{" "}
        {/* Assuming logo.svg is your logo */}
        <div className="pl-4">
          <button className="font-inika font-semibold text-2xl">Tesla</button>{" "}
          {/* Company name */}
          <div className="flex mt-1">
            <span className="font-inika text-l text-gray-500 mr-2">
              Keywords:
            </span>{" "}
            {/* Keywords label */}
            <div className="flex">
              <button className="bg-gray-200 text-gray-700 rounded-full px-2 py-1 mr-2">
                automotive
              </button>{" "}
              {/* First keyword */}
              <button className="bg-gray-200 text-gray-700 rounded-full px-2 py-1">
                energy
              </button>{" "}
              {/* Second keyword */}
            </div>
          </div>
        </div>
        <button className="ml-auto bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-full">
          Unfollow
        </button>{" "}
        {/* Unfollow button */}
      </div>
      <hr className="border-t border-gray-400 mt-4 ml-40 mr-40" /> {/* Line */}
    </div>
  );
}

export default FollowedCompanies;
