import React from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "./Navbar";

function HomePage() {
  const feedEntries = [
    {
      headline: "Microsoft topples Apple to become global market cap leader",
      source: "finance.yahoo.com",
      time: "18 hours ago",
      icon: "/microsoftnews.png",
      logo: "/microsoftIcon.png",
      company: "Microsoft",
    },
    {
      headline: "OpenAI's Breakthrough in Generative AI",
      source: "techcrunch.com",
      time: "1 week ago",
      icon: "/openAInews.png",
      logo: "/openAIIcon.png",
      company: "OpenAI",
    },
    {
      headline: "OpenAI's Breakthrough in Generative AI",
      source: "techcrunch.com",
      time: "1 week ago",
      icon: "/openAInews.png",
      logo: "/openAIIcon.png",
      company: "OpenAI",
    },
    {
      headline: "Microsoft topples Apple to become global market cap leader",
      source: "finance.yahoo.com",
      time: "18 hours ago",
      icon: "/microsoftnews.png",
      logo: "/microsoftIcon.png",
      company: "Microsoft",
    },
    {
      headline: "Tesla Electric Vehicles Surge in Popularity",
      source: "theverge.com",
      time: "2 days ago",
      icon: "/teslanews.png",
      logo: "/teslaIcon.png",
      company: "Tesla",
    },
    {
      headline: "OpenAI's Breakthrough in Generative AI",
      source: "techcrunch.com",
      time: "1 week ago",
      icon: "/openAInews.png",
      logo: "/openAIIcon.png",
      company: "OpenAI",
    },
    {
      headline: "Microsoft topples Apple to become global market cap leader",
      source: "finance.yahoo.com",
      time: "18 hours ago",
      icon: "/microsoftnews.png",
      logo: "/microsoftIcon.png",
      company: "Microsoft",
    },
    {
      headline: "Tesla Electric Vehicles Surge in Popularity",
      source: "theverge.com",
      time: "2 days ago",
      icon: "/teslanews.png",
      logo: "/teslaIcon.png",
      company: "Tesla",
    },
    {
      headline: "Tesla Electric Vehicles Surge in Popularity",
      source: "theverge.com",
      time: "2 days ago",
      icon: "/teslanews.png",
      logo: "/teslaIcon.png",
      company: "Tesla",
    },

    // ...add more entries as needed
  ];

  const navigate = useNavigate(); // Correctly instantiate the useNavigate hook here

  // Function to determine the class based on index
  const getItemClass = (index: number): string => {
    switch (index % 5) {
      case 0:
        return "row-span-2 col-span-2"; // Larger item
      case 1:
      case 2:
        return "row-span-1 col-span-1"; // Regular items
      default:
        return "row-span-1 col-span-2"; // Wider item
    }
  };

  // Function to handle navigation to the "About" page
  const handleNavigateAbout = (company: string, icon: string) => {
    navigate(`/about/${company.replace(/\s+/g, "-").toLowerCase()}`, {
      state: { logoUrl: icon }, // Pass the logo URL in the state
    });
  };

  return (
    <div>
      <Navbar />
      <div className="bg-feed-grey p-8 mt-8 mb-8 shadow-lg mx-auto w-full md:w-11/12 lg:w-5/6 xl:w-3/4 overflow-hidden">
        <div className="grid grid-cols-3 gap-4">
          {feedEntries.map((entry, index) => (
            <div
              key={index}
              className={`flex flex-col items-center text-center ${getItemClass(
                index
              )}`}
            >
              <h3 className="font-bold mb-2">{entry.headline}</h3>
              <img
                src={entry.icon}
                alt="Company Icon"
                className={"w-full h-auto mb-2"}
              />
              <span className="text-gray-600">({entry.source})</span>
              <div className="text-gray-500 text-sm mt-2">
                {entry.time} | <button className="mx-1">Save</button> |
                <button className="mx-1">
                  <Link
                    to={`/analysis/${entry.headline
                      .replace(/\s+/g, "-")
                      .toLowerCase()}`}
                  >
                    Article Analysis
                  </Link>
                </button>{" "}
                |
                <button
                  className="mx-1"
                  onClick={() => handleNavigateAbout(entry.company, entry.logo)}
                >
                  About {entry.company}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default HomePage;
