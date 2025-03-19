import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Journaling.css";

const JournalPage = () => {
  const [journalEntry, setJournalEntry] = useState("");
  const [journalHistory, setJournalHistory] = useState([]);
  const [response, setResponse] = useState(null);
  const userId = "user-123";  // Replace with actual user ID

  useEffect(() => {
    // Fetch previous journal entries
    axios.get(`http://127.0.0.1:5000/get-journals/${userId}`)
      .then(res => setJournalHistory(res.data))
      .catch(err => console.error("Error fetching journals:", err));
  }, []);

  const handleJournalSubmit = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/add-journal", {
        id: userId,
        content: journalEntry
      });

      setResponse(res.data);
      setJournalHistory([...journalHistory, { content: journalEntry, ...res.data }]);
      setJournalEntry("");
    } catch (error) {
      console.error("Error submitting journal:", error);
    }
  };

  return (
    <div className="journal-container">
      <h2>Journal Your Thoughts</h2>
      <textarea 
        value={journalEntry}
        onChange={(e) => setJournalEntry(e.target.value)}
        placeholder="Write here..."
      />
      <button onClick={handleJournalSubmit}>Submit</button>

      {response && (
        <div className="response-section">
          <h3>Summary:</h3>
          <p>{response.summary}</p>
          <h3>Emotion Analysis:</h3>
          <p><strong>Dominant Emotion:</strong> {response.dominant_emotion}</p>
          <p><strong>Suggested Activity:</strong> {response.activity_suggestion}</p>
          <h3>Insights:</h3>
          <p>{response.insights}</p>
        </div>
      )}

      <h3>Past Entries:</h3>
      {journalHistory.map((entry, index) => (
        <div key={index} className="journal-entry">
          <p>{entry.content}</p>
          <p><strong>Emotion:</strong> {entry.dominant_emotion}</p>
        </div>
      ))}
    </div>
  );
};

export default JournalPage;
