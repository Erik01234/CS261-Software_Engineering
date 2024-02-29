import React from "react";
import { useParams } from "react-router-dom";
import Navbar from "./Navbar";

function ArticleAnalysis() {
  let { headline } = useParams(); // Use article headline to fetch the article's analysis

  return (
    <div>
      <Navbar />
      <h1>Article Analysis: {headline}</h1>
      <p>This article bla bla bla</p>
    </div>
  );
}

export default ArticleAnalysis;
