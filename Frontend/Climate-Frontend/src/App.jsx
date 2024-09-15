import React, { useEffect, useState } from "react";
import './App.css';
import Modal from 'react-modal';

Modal.setAppElement('#root');

function App() {
  const [headlines, setHeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState("");
  const [weekSummaries, setWeekSummaries] = useState("");
  const [AIWeekSummary, setAIWeekSummary] = useState("");
  const [tapped, setTapped] = useState(false);

  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [email, setEmail] = useState(""); 

  const [unsubscribeEmail, setUnsubscribeEmail] = useState("");
  const [unsubscribeModalIsOpen, setUnsubscribeModalIsOpen] = useState(false);

  useEffect(() => {
    const fetchHeadlines = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/headlines/");
        
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        
        const data = await res.json();
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
    try {
      setTapped(true);
      const res = await fetch("http://127.0.0.1:8000/api/get_week_news/");
      if (!res.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await res.json();
      setWeekSummaries(data.summaries);
    } catch (err) {
      setError(err.message);
    }
  }

  const handleWeekSummarize = async () => {
    try {
      if (weekSummaries.length === 0) {
        console.log("weekSummaries is empty. Fetching data...");
        await handleSeePrev(); 
      }
        
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
      if (data.success) {
        setAIWeekSummary(data.response);
      } else {
        setError(data.error || "Failed to summarize");
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const openModal = () => {
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
  };

  const handleNewsletterSignup = async (e) => {
    e.preventDefault();
    if (email) {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/subscribe/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        });

        const data = await res.json();
        if (data.success) {
          alert(`Thank you! Daily climate news summary will be sent to: ${email}`);
          setEmail("");
          closeModal();
        } else {
          alert(data.message || "Subscription failed.");
        }
      } catch (error) {
        alert("An error occurred. Please try again.");
      }
    } else {
      alert("Please enter a valid email.");
    }
  };

  const handleLike = async (uuid) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/like-article/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ uuid }),
      });

      if (!res.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await res.json();
      if (data.success) {
        setHeadlines(prevHeadlines => 
          prevHeadlines.map(headline => 
            headline.uuid === data.uuid
              ? { ...headline, likes: data.likes, liked: data.liked }
              : headline
          )
        );
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUnsubscribe = async (e) => {
    e.preventDefault();
    if (unsubscribeEmail) {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/unsubscribe/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email: unsubscribeEmail }),
        });

        const data = await res.json();
        if (data.success) {
          alert(data.message);
          setUnsubscribeEmail("");
          closeUnsubscribeModal();
        } else {
          alert(data.message || "Unsubscription failed.");
        }
      } catch (error) {
        alert("An error occurred. Please try again.");
      }
    } else {
      alert("Please enter a valid email.");
    }
  };

  const openUnsubscribeModal = () => {
    setUnsubscribeModalIsOpen(true);
  };

  const closeUnsubscribeModal = () => {
    setUnsubscribeModalIsOpen(false);
  };

  return (
    <div className="App">
      <div className="cont">
        <header className="header">
          <h1>Cli-Change AI</h1>
          <nav>
            <button onClick={openModal} className="nav-button">Subscribe</button>
            <button onClick={openUnsubscribeModal} className="nav-button">Unsubscribe</button>
          </nav>
        </header>

        {loading && <p>Loading headlines...</p>}
        {error && <p className="error">{error}</p>}

        <div className="headline-grid">
          {headlines.map((headline) => (
            <div key={headline.uuid} className="headline-card">
              <img src={headline.image_url} alt={headline.title} className="headline-image" />
              <div className="headline-content">
                <h3>{headline.title || "No title available"}</h3>
                <p>{headline.description || "No description available"}</p>
                <div className="headline-actions">
                  <button 
                    onClick={() => handleLike(headline.uuid)} 
                    className={`action-button ${headline.liked ? 'liked' : ''}`}
                  >
                    {headline.liked ? 'Unlike' : 'Like'} ({headline.likes})
                  </button>
                  <a href={headline.url} target="_blank" rel="noopener noreferrer" className="cust-link">Read more</a>
                </div>
              </div>
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
        {weekSummaries.length > 0 && tapped && (
          <div className="previous-news">
            <ul>
              {weekSummaries.map((summary, index) => (
                <li key={index}>
                  <h3>{summary.title}</h3>
                  <p>{summary.description}</p>
                  <p><strong>Date:</strong> {summary.date}</p>
                  <a href={summary.url} target="_blank" rel="noopener noreferrer">Read more</a>
                </li>
              ))}
            </ul>
          </div>
        )}
        <button onClick={handleWeekSummarize} className="summarize-button">Summarize This Week's News</button>
        {AIWeekSummary && (
          <div className="summary-section">
            <h2>AI Weekly Summary</h2>
            <p>{AIWeekSummary}</p>
          </div>
        )}
        <Modal
          isOpen={modalIsOpen}
          onRequestClose={closeModal}
          contentLabel="Newsletter Signup"
          className="Modal"
          overlayClassName="Overlay"
        >
          <h2>Sign up for Daily News Summary</h2>
          <form onSubmit={handleNewsletterSignup}>
            <label>
              Email:
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </label>
            <button type="submit" className="submit-button">Subscribe</button>
            <button type="button" onClick={closeModal} className="cancel-button">Cancel</button>
          </form>
        </Modal>

        <Modal
          isOpen={unsubscribeModalIsOpen}
          onRequestClose={closeUnsubscribeModal}
          contentLabel="Unsubscribe"
          className="Modal"
          overlayClassName="Overlay"
        >
          <h2>Unsubscribe from Daily News Summary</h2>
          <form onSubmit={handleUnsubscribe}>
            <label>
              Email:
              <input
                type="email"
                value={unsubscribeEmail}
                onChange={(e) => setUnsubscribeEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </label>
            <button type="submit" className="submit-button">Unsubscribe</button>
            <button type="button" onClick={closeUnsubscribeModal} className="cancel-button">Cancel</button>
          </form>
        </Modal>
      </div>
    </div>
  );
}

export default App;