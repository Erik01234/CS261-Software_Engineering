import React from "react";
import { useParams } from "react-router-dom";
import Navbar from "./Navbar";

function SavedArticles() {
  let { headline } = useParams(); // Use article headline to fetch the article's analysis

  return (
    <div className="text-left">
      <Navbar />
      <h1 className="font-bold font-inter text-4xl pl-36 pt-8">
        Saved Articles
      </h1>
      <div className="flex items-start mt-4 pl-40 pt-8 pr-40"> {/* Changed 'items-center' to 'items-start' */}
        <img
          src="/teslanews.png"
          alt="Company Logo"
          className="w-60 h-40 mr-4"
        />{" "}
        {/* Assuming logo.svg is your logo */}
        <div className="pl-4">
          <button className="font-inika font-semibold text-2xl text-left mt-1">Tesla-beating BYD unveils $230,000 supercar and $14,000 hatchback in same week</button>{" "} {/* Added 'mt-1' class */}
          {/* Company name */}
          <div className="flex mt-1">
            <span className="font-inika text-l mr-2">
              A single line summarising the article.
            </span>{" "}
            {/* Keywords label */}
          </div>
          <div className="flex mt-4">
            <span className="text-gray-500 py-2 mr-4 relative">
              18 hours ago
            </span>
            <button className="text-gray-500 pl-4 py-2 relative mr-4">
              Summary
            </button>
            <button className="text-gray-500 pl-4 py-2 relative mr-4">
              Article Analysis
            </button>
            <button className="pl-4 py-2 relative">
            <img
              src="/bookmark_FILL0_wght400_GRAD0_opsz24 1.png"
              alt="Company Logo"
              className="w-6 h-5"
            />{" "}
            </button>
            <button className="pl-4 py-2 relative">
            <img
              src="/more_vert_FILL0_wght400_GRAD0_opsz24 1.png"
              alt="Company Logo"
              className="w-6 h-5 mr-4"
            />{" "}
            </button>
          </div>
        </div>
      </div>
      <div className="flex items-start mt-4 pl-40 pt-8 pr-40"> {/* Changed 'items-center' to 'items-start' */}
        <img
          src="/teslanews.png"
          alt="Company Logo"
          className="w-60 h-40 mr-4"
        />{" "}
        {/* Assuming logo.svg is your logo */}
        <div className="pl-4">
          <button className="font-inika font-semibold text-2xl text-left mt-1">Tesla-beating BYD unveils $230,000 supercar and $14,000 hatchback in same week</button>{" "} {/* Added 'mt-1' class */}
          {/* Company name */}
          <div className="flex mt-1">
            <span className="font-inika text-l mr-2">
              A single line summarising the article.
            </span>{" "}
            {/* Keywords label */}
          </div>
          <div className="flex mt-4">
            <span className="text-gray-500 py-2 mr-4 relative">
              18 hours ago
            </span>
            <button className="text-gray-500 pl-4 py-2 relative mr-4">
              Summary
            </button>
            <button className="text-gray-500 pl-4 py-2 relative mr-4">
              Article Analysis
            </button>
            <button className="pl-4 py-2 relative">
            <img
              src="/bookmark_FILL0_wght400_GRAD0_opsz24 1.png"
              alt="Company Logo"
              className="w-6 h-5"
            />{" "}
            </button>
            <button className="pl-4 py-2 relative">
            <img
              src="/more_vert_FILL0_wght400_GRAD0_opsz24 1.png"
              alt="Company Logo"
              className="w-6 h-5 mr-4"
            />{" "}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SavedArticles;
