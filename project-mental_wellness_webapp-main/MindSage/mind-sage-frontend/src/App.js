import React, { useState } from "react";

function App() {
  const [journalEntry, setJournalEntry] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const analyzeJournal = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: journalEntry }),
      });
      console.log("Response received:", res);
      
      const data = await res.json();
      console.log("API Response Data:", data);
      setResponse(data);
    } catch (error) {
      console.error("Error analyzing journal:", error);
    }
    setLoading(false);
  };
  
  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "auto" }}>
      <h2>Mental Well-being Journal</h2>
      <textarea
        value={journalEntry}
        onChange={(e) => setJournalEntry(e.target.value)}
        placeholder="Write about your day..."
        rows={5}
        style={{ width: "100%", padding: "10px", fontSize: "16px" }}
      />
      <button onClick={analyzeJournal} disabled={loading} style={{ marginTop: "10px" }}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>
      
      {response && (
        <div style={{ marginTop: "20px" }}>
          <h3>Analysis Results:</h3>
          <p><strong>Dominant Emotion:</strong> {response.dominant_emotion}</p>
          <p><strong>Recommended Activity:</strong> {response.activity_suggestion}</p>
          <p><strong>Insights:</strong> {response.insights}</p>
          {response.suicide_risk && (
            <p style={{ color: "red", fontWeight: "bold" }}>⚠️ Urgent: Seek Support!</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;