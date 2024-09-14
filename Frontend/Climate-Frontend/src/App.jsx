import React, { useEffect, useState } from "react";
import './App.css';

function App() {
  const [headlines, setHeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState("");

  useEffect(() => {
    const fetchHeadlines = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/headlines/");
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await res.json();
        setHeadlines(data.general);  
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHeadlines();
  }, []);

  const handleSummarize = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat-completion/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          headlines: headlines.map(headline => headline.description),  
        }),
      });

      if (!res.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await res.json();
      setSummary(data.response);  
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="App">
      <h1>Latest Headlines</h1>
      
      {loading && <p>Loading headlines...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <div className="headline-list">
        {headlines.map((headline) => (
          <div key={headline.uuid} className="headline-card">
            <img src={headline.image_url} alt={headline.title} className="headline-image" />
            <h3>{headline.title}</h3>
            <p>{headline.description}</p>
            <a href={headline.url} target="_blank" rel="noopener noreferrer">Read more</a>
          </div>
        ))}
      </div>

      <button onClick={handleSummarize} className="summarize-button">Summarize Headlines</button>

      {summary && (
        <div className="summary-section">
          <h2>Summary</h2>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}

export default App;
