import React, { useEffect, useState } from "react";
import './App.css';

function App() {
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/chat-completion/");
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await res.json();
        setResponse(data.response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="App">
      <h1>AI Response</h1>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {!loading && response && <p>{response}</p>}
    </div>
  );
}

export default App;
