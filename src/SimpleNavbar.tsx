import React, { useState } from "react";
import { Link, useParams } from "react-router-dom";

function SimpleNavbar() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Toggle dropdown visibility
  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);
  return (
    <nav className="w-full bg-nav-bar-grey p-4 flex items-center justify-between sticky top-0 z-10">
      <div className="flex space-x-4">
        <span className="text-white text-4xl font-bold">CoRNIA</span>
      </div>
    </nav>
  );
}

export default SimpleNavbar;
