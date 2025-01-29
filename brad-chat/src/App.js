import React, { useEffect, useState } from 'react';
import ChatContainer from './components/ChatContainer';
import './App.css';

import "highlight.js/styles/github.css";
import hljs from "highlight.js";

function App() {
  const [messages, setMessages] = useState([]);
  const [videoSrc, setVideoSrc] = useState("https://www.youtube.com/embed/nF59F_igAsE"); // Default video link
  const [ragDatabase, setRagDatabase] = useState('Wikipedia');  // Default RAG choice
  const [availableDatabases, setAvailableDatabases] = useState([]);  // Hold available databases

  useEffect(() => {
    hljs.highlightAll();
  }, [messages]);

  // Fetch available databases from the Flask API when the component loads
  useEffect(() => {
    const fetchDatabases = async () => {
      try {
        const response = await fetch('/api/databases/available');
        if (response.ok) {
          const data = await response.json();
          console.log(`data.databases: ${data.databases}`);
          setAvailableDatabases(data.databases);
          setRagDatabase(data.databases[0]);  // Set the first available DB as default
        } else {
          console.error('Failed to fetch databases');
        }
      } catch (error) {
        console.error('Error fetching databases:', error);
      }
    };

    fetchDatabases();
  }, []);  // Run this effect only once when the component mounts


  const handleRagChange = async (event) => {
    const selectedDatabase = event.target.value;
    console.log(`Setting RAG database to: ${selectedDatabase}`);

    try {
      const response = await fetch('/api/video/databases/set', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ database: selectedDatabase })  // Send selected DB in the request body
      });
      console.log(`Database response: `, response);
      if (response.ok) {
        const data = await response.json();
        console.log(`Database set successfully:`, data.message);
        setRagDatabase(selectedDatabase);  // Update the current selection
      } else {
        const errorData = await response.json();
        console.error('Error setting database:', errorData.message);
      }
    } catch (error) {
      console.error('Error during database request:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2>DCMB Seminar RAG by BRAD {String.fromCodePoint('0x1f916')}</h2>
      </header>
      <div className="main-content">
        {/* YouTube Video on the right */}
        <div className="video-container">
          <iframe
            src={videoSrc} // Dynamically update the video source
            title="YouTube video"
            allowFullScreen
          ></iframe>
          {/* Settings Panel */}
          <div className="database-options">
            <h3>Settings</h3>
            <div className="setting-option-choose-db">
              <label htmlFor="rag-database"><b>Choose Database:</b></label>
              <select id="rag-database" value={ragDatabase} onChange={handleRagChange}>
                {availableDatabases.map((db, index) => (
                  <option key={index} value={db}>{db}</option>
                ))}
              </select>
            </div>
            <label className="playback-speed">
              Video Database:  
              <select>
                <option>DCMB Seminar Series</option>
                <option>Three Blue One Brown</option>
              </select>
            </label>
          </div>
        </div>
        {/* Chat Container on the left */}
        <ChatContainer
          messages={messages}
          setMessages={setMessages}
          setVideoSrc={setVideoSrc} // Pass the videoSrc setter to ChatContainer
        />
      </div>
    </div>
  );
}

export default App;
