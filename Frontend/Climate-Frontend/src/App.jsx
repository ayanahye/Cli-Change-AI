import React, { useEffect, useState } from "react";
import './App.css';
import Data from './data.json';
import Data2 from './data2.json';

function App() {
  const [headlines, setHeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState("");
  const [weekSummaries, setWeekSummaries] = useState("");
  const [AIWeekSummary, setAIWeekSummary] = useState("");

  useEffect(() => {
    const fetchHeadlines = async () => {
      try {
        //const res = await fetch("http://127.0.0.1:8000/api/headlines/");
        /*
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        */
        //const data = await res.json();
        const data = Data;
        setHeadlines(data.data);  
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
          articles: headlines,
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

  const handleSeePrev = async () => {
    // make a req backend that gets whole week of summaries
    try {
      //const res = await fetch("http://127.0.0.1:8000/api/get_week_news/")
      /*
      if (!res.ok) {
        throw new Error("Network response was not ok");
      }
      */
      //const data = await res.json();
      const data = Data2;
      setWeekSummaries(data);
    } catch (err) {
      setError(err.message);
    }
  }

  const handleWeekSummarize = async () => {
    try {
      if (weekSummaries == "") {
        try {
          //const res = await fetch("http://127.0.0.1:8000/api/get_week_news/")
          /*
          if (!res.ok) {
            throw new Error("Network response was not ok");
          }
          */
          //const data = await res.json();
          const data = Data2;
          setWeekSummaries(data);
        } catch (err) {
          setError(err.message);
        }
      }
      console.log(weekSummaries)
      const res = await fetch("http://127.0.0.1:8000/api/chat-completion-week/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          articles: weekSummaries,
        }),
      });

      if (!res.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await res.json();
      print(data)
      setAIWeekSummary(data.response);  
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="App">
      <h1>Latest News</h1>
      
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

      <button onClick={handleSummarize} className="summarize-button">Summarize News</button>

      {summary && (
        <div className="summary-section">
          <h2>AI Summary</h2>
          <p>{summary}</p>
        </div>
      )}
      <button onClick={handleSeePrev} className="summarize-button">See This Week's News</button>
      {weekSummaries && weekSummaries.length > 0 && (
      <div className="previous">
        <ul>
          {weekSummaries.map((summary, index) => (
            <li key={index}>
              <h3>{summary.title}</h3>
              <p>{summary.description}</p>
              <a href={summary.url} target="_blank" rel="noopener noreferrer">Read more</a>
            </li>
          ))}
          </ul>
        </div>
        )}
        <button onClick={handleWeekSummarize} className="summarize-button">Summarize This Weeks News</button>
        {AIWeekSummary && (
          <div className="summary-section">
            <h2>AI Summary</h2>
            <p>{AIWeekSummary}</p>
          </div>
        )}
    </div>
  );
}

export default App;
