import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";

const Journaling = ({ journalText, setJournalText }) => {
    const [journals, setJournals] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    
    const userId = localStorage.getItem("user_id"); // Retrieve user ID
    
    //  Fetch journal entries (Memoized to prevent redundant API calls)
    const fetchJournals = useCallback(async () => {
        if (!userId) return;
        setLoading(true);
        setError(null);
        
        try {
            const response = await axios.get(`http://localhost:5000/get-journals/${userId}`);
            setJournals(response.data || []);
        } catch (err) {
            setError("Failed to load journals. Please try again.");
            console.error("Error fetching journals:", err);
        } finally {
            setLoading(false);
        }
    }, [userId]);
    
    useEffect(() => {
        fetchJournals();
    }, [fetchJournals]);
    
    //  Handle Journal Submission
    const handleSubmit = async () => {
        if (!userId) {
            alert("User ID missing! Please log in again.");
            return;
        }
        if (!journalText.trim()) {
            alert("Please enter text before saving.");
            return;
        }
        
        setLoading(true);
        try {
            const response = await axios.post("http://localhost:5000/add-journal", {
                id: userId,
                content: journalText,
            });
            
            if (response.status === 200) {
                alert("Journal saved successfully!");
                setJournalText(""); //  Clear input after saving
                fetchJournals(); //  Refresh journal list
            }
        } catch (error) {
            console.error("Error saving journal:", error);
            alert("Failed to save journal. Try again.");
        } finally {
            setLoading(false);
        }
    };
    
    //  New function to analyze journal text
    const handleAnalyzeJournal = async () => {
        if (!journalText.trim()) {
            alert("Please enter text to analyze.");
            return;
        }
        
        setAnalyzing(true);
        setAnalysis(null);
        
        try {
            const response = await axios.post("http://localhost:5000/analyze", {
                text: journalText
            });
            
            if (response.status === 200) {
                setAnalysis(response.data);
            }
        } catch (error) {
            console.error("Error analyzing journal:", error);
            alert("Failed to analyze journal. Try again.");
        } finally {
            setAnalyzing(false);
        }
    };
    
    // Get emotion color for visualization
    const getEmotionColor = (emotion) => {
        const colors = {
            joy: "#FFD700",          // Gold
            sadness: "#4682B4",      // Steel Blue
            anger: "#FF4500",        // Orange Red
            fear: "#800080",         // Purple
            disgust: "#006400",      // Dark Green
            surprise: "#FF69B4",     // Hot Pink
            neutral: "#808080",      // Grey
            stress: "#8B0000",       // Dark Red
            overwhelmed: "#483D8B"   // Dark Slate Blue
        };
        
        return colors[emotion] || "#808080";
    };
    
    return (
        <div>
            <textarea
                value={journalText}
                onChange={(e) => setJournalText(e.target.value)}
                placeholder="Write your journal here..."
                rows={5}
                style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
            />
            
            <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
                <button onClick={handleSubmit} disabled={loading}>
                    {loading ? "Saving..." : "Save Journal"}
                </button>
                <button 
                    onClick={handleAnalyzeJournal} 
                    disabled={analyzing || !journalText.trim()}
                    style={{ backgroundColor: "#4CAF50", color: "white" }}
                >
                    {analyzing ? "Analyzing..." : "Analyze Journal"}
                </button>
            </div>
            
            {/* Display Analysis Results */}
            {analysis && (
                <div className="analysis-results" style={{ 
                    marginBottom: "20px", 
                    padding: "15px", 
                    backgroundColor: "#f8f9fa", 
                    borderRadius: "5px",
                    border: "1px solid #ddd" 
                }}>
                    <h4>Journal Analysis</h4>
                    
                    {/* Dominant Emotion */}
                    <div style={{ marginBottom: "15px" }}>
                        <h5>Primary Emotion</h5>
                        <div style={{ 
                            display: "flex", 
                            alignItems: "center", 
                            gap: "10px" 
                        }}>
                            <div style={{
                                width: "20px",
                                height: "20px",
                                backgroundColor: getEmotionColor(analysis.dominant_emotion),
                                borderRadius: "50%"
                            }}></div>
                            <span style={{ textTransform: "capitalize" }}>
                                {analysis.dominant_emotion}
                            </span>
                        </div>
                    </div>
                    
                    {/* Suggestions */}
                    <div style={{ marginBottom: "15px" }}>
                        <h5>Suggestion</h5>
                        <p>{analysis.activity_suggestion}</p>
                    </div>
                    
                    {/* Insights */}
                    <div>
                        <h5>Insights</h5>
                        <p>
                            {analysis.insights || 
                             (analysis.emotions && Object.keys(analysis.emotions).length > 0 ? 
                              "Processing your emotional patterns..." : 
                              "Insights will be generated once more journal entries are analyzed.")}
                        </p>
                    </div>
                    
                    {/* Suicide Risk Alert - Only show if risk detected */}
                    {analysis.suicide_risk && (
                        <div style={{ 
                            marginTop: "15px",
                            padding: "10px 15px",
                            backgroundColor: "#FFCCCB",
                            borderLeft: "4px solid #FF0000",
                            borderRadius: "3px"
                        }}>
                            <h5 style={{ color: "#FF0000", margin: "0 0 5px 0" }}>Important</h5>
                            <p style={{ margin: 0 }}>
                                We've detected content that suggests you might be going through a difficult time. 
                                If you're feeling suicidal or need immediate support, please contact a mental health 
                                professional or call the National Suicide Prevention Lifeline at 988.
                            </p>
                        </div>
                    )}
                </div>
            )}
            
            {/* Error Message */}
            {error && <p style={{ color: "red" }}>{error}</p>}
            
            {/* Journals List */}
            <h3>Your Journals</h3>
            {loading ? <p>Loading journals...</p> : (
                <ul>
                    {journals.map((journal, index) => (
                        <li key={index} style={{ marginBottom: "10px" }}>
                            <strong>{new Date(journal.date).toLocaleDateString()}</strong>: {journal.content}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Journaling;