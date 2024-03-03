import React, { useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import Navbar from "./Navbar";

function AboutCompany() {
  let { companyId } = useParams();
  const location = useLocation();
  const [isFollowed, setIsFollowed] = useState(false); // State to track follow status

  const { logoUrl } = location.state || {};

  const keyWords = [
    "Artificial Intelligence",
    "Machine Learning",
    "Data Science",
  ];

  // Example list of similar companies
  const similarCompanies = [
    { name: "Microsoft", logo: "/microsofticon.png" },
    { name: "OpenAI", logo: "/openaiicon.png" },
    { name: "Tesla", logo: "/teslaicon.png" },
    { name: "Microsoft", logo: "/microsofticon.png" },
    { name: "OpenAI", logo: "/openaiicon.png" },
    { name: "Tesla", logo: "/teslaicon.png" },
    // Add more companies as needed
  ];

  // Example executives list
  const keyExecutives = [
    "John Doe - CEO",
    "Jane Smith - CTO",
    "Richard Roe - CFO",
    // Add more executives as needed
  ];

  const newsEntries = [
    {
      title: "AI Revolution in Tech",
      summary: "Exploring how AI is changing the landscape of technology.",
      imageUrl: "/news-image-1.png",
    },
    {
      title: "Breakthrough in Machine Learning",
      summary:
        "A new algorithm has set the stage for advances in machine learning.",
      imageUrl: "/news-image-2.png",
    },
    {
      title: "AI Revolution in Tech",
      summary: "Exploring how AI is changing the landscape of technology.",
      imageUrl: "/news-image-1.png",
    },
    // Add more news entries as needed
  ];

  const capitalizeFirstLetter = (string: string | undefined) => {
    return string ? string.charAt(0).toUpperCase() + string.slice(1) : "";
  };

  const companyName = capitalizeFirstLetter(companyId);

  // Function to toggle follow status
  const toggleFollow = () => {
    setIsFollowed(!isFollowed);
  };

  return (
    <div>
      <Navbar />
      <div className="flex justify-center mt-8">
        <div className="flex space-x-4 max-w-7xl w-full px-4">
          <div className="flex-1 bg-gray-200 p-4 rounded-lg flex flex-col">
            <div className="flex-grow">
              <div className="flex justify-between items-center">
                {logoUrl && (
                  <img
                    src={logoUrl}
                    alt="Company Icon"
                    className="mr-4 h-20 w-20"
                  />
                )}
                <div>
                  <h1 className="text-3xl font-semibold">{companyName}</h1>
                  <p className="mt-2">Artificial Intelligence Company</p>
                </div>
                <button onClick={toggleFollow}>
                  <img
                    src={isFollowed ? "/Unfollow.png" : "/Follow.png"}
                    alt={isFollowed ? "Unfollow" : "Follow"}
                    className="h-9 w-21"
                  />
                </button>
              </div>
              <p className="text-sm pt-8">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam
                consequat quis sem in molestie. In eget turpis cursus, cursus
                ligula ac, lobortis sapien. Sed porta velit a dictum fringilla.
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam
                cursus neque in porttitor vestibulum. Nulla finibus neque sed
                orci laoreet, ac tincidunt arcu vestibulum. Nulla vitae ipsum
                varius, rutrum magna vitae, condimentum quam. Pellentesque a
                pharetra arcu. Quisque luctus, orci pellentesque dictum blandit,
                libero justo fringilla risus, eget ultrices nunc nisi a sem.
              </p>
              {/* Stock Trends and Related News Headings */}
              <div className="flex justify-between items-start pt-8">
                <div className="w-1/2">
                  <h2 className="text-lg text-left font-semibold">
                    Stock Trends
                  </h2>
                  <img
                    src={"/stocktrends.png"}
                    alt="Stock Trends"
                    className="mt-2 h-60 w-80"
                  />
                  {/* Key Executives Section */}
                  <div className="pt-4">
                    <h2 className="text-lg text-left font-semibold">
                      Key Executives
                    </h2>
                    <ul className="list-disc pl-5">
                      {keyExecutives.map((executive, index) => (
                        <li className="text-left" key={index}>
                          {executive}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                <div className="w-1/2">
                  <h2 className="text-lg text-left font-semibold">
                    Related News
                  </h2>
                  {newsEntries.map((entry, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-start my-4"
                    >
                      <img
                        src={entry.imageUrl}
                        alt="News"
                        className="ml-4 w-24 h-24 object-cover"
                      />
                      <div className="flex-1">
                        <h3 className="font-bold text-left pl-2">
                          {entry.title}
                        </h3>
                        <p className="text-left pl-2">{entry.summary}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="w-1/4 bg-gray-200 p-4 rounded-lg">
            <h2 className="text-lg font-semibold">Similar Companies</h2>
            <div>
              {similarCompanies.map((company, index) => (
                <div key={index} className="flex items-center my-6">
                  <img
                    src={company.logo}
                    alt={`${company.name} Logo`}
                    className="h-10 w-10 mr-4"
                  />
                  <span className="font-bold">{company.name}</span>
                </div>
              ))}
            </div>
            <h2 className="text-lg font-semibold">Keywords</h2>
            <div>
              {keyWords.map((keyword, index) => (
                <div key={index} className="flex items-center my-2">
                  <span className="bg-gray-400 text-sm px-4 py-1 rounded-full">
                    {keyword}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AboutCompany;
