import React, { useState } from "react";
import axios from "axios";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";

const EmojiSlider = ({ value, onChange, emojis }) => {
  return (
    <div style={{ display: "flex", alignItems: "center" }}>
      <span>{emojis[0]}</span>
      <Slider
        min={0}
        max={100}
        value={value}
        onChange={onChange}
        trackStyle={{ backgroundColor: "#4caf50" }}
        handleStyle={{ borderColor: "#4caf50", height: 20, width: 20 }}
        railStyle={{ backgroundColor: "#ddd" }}
      />
      <span>{emojis[emojis.length - 1]}</span>
    </div>
  );
};

function App() {
  const [moodData, setMoodData] = useState({
    happiness: 50,
    anxiety: 50,
    energy: 50,
    stress: 50,
    activity: "",
    notes: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:5000/api/add-mood-entry", moodData);
      alert("Mood entry added successfully!");
      console.log(response.data);
    } catch (error) {
      console.error("Error adding mood entry:", error);
      alert("Failed to add mood entry.");
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>MindSage Mood Tracker</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "20px" }}>
          <label>Happiness:</label>
          <EmojiSlider
            value={moodData.happiness}
            onChange={(value) => setMoodData({ ...moodData, happiness: value })}
            emojis={["😢", "😐", "😊"]}
          />
        </div>
        <div style={{ marginBottom: "20px" }}>
          <label>Anxiety:</label>
          <EmojiSlider
            value={moodData.anxiety}
            onChange={(value) => setMoodData({ ...moodData, anxiety: value })}
            emojis={["😌", "😐", "😰"]}
          />
        </div>
        <div style={{ marginBottom: "20px" }}>
          <label>Energy:</label>
          <EmojiSlider
            value={moodData.energy}
            onChange={(value) => setMoodData({ ...moodData, energy: value })}
            emojis={["😴", "😐", "⚡️"]}
          />
        </div>
        <div style={{ marginBottom: "20px" }}>
          <label>Stress:</label>
          <EmojiSlider
            value={moodData.stress}
            onChange={(value) => setMoodData({ ...moodData, stress: value })}
            emojis={["😎", "😐", "🤯"]}
          />
        </div>
        <div style={{ marginBottom: "10px" }}>
          <label>Activity:</label>
          <input
            type="text"
            value={moodData.activity}
            onChange={(e) => setMoodData({ ...moodData, activity: e.target.value })}
          />
        </div>
        <div style={{ marginBottom: "10px" }}>
          <label>Notes:</label>
          <textarea
            value={moodData.notes}
            onChange={(e) => setMoodData({ ...moodData, notes: e.target.value })}
          />
        </div>
        <button type="submit">Submit Mood Entry</button>
      </form>
    </div>
  );
}

export default App;