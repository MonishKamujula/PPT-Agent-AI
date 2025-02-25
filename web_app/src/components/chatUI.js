import React, { useState, useEffect } from "react";
import { Box, TextField, IconButton, Typography, Paper } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import "axios";
import axios from "axios";

const ChatUI = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  
  const [currentMessage, setcurrentMessage] = useState("");
  const handleSend = () => {
    if (input.trim()) {
      console.log("Send button clicked...");
      setMessages([...messages, { content: input, role: "user" }]);
      setcurrentMessage(input);
      console.log("Current message:", currentMessage);
      setInput("");
    }
  };

  useEffect(() => {
    if (!currentMessage) return; // Prevent API call if input is empty

    const fetchResponse = async () => {
      try {
        console.log("Calling API ...");
        const response = await axios.get(`http://127.0.0.1:5000/predict?text=${currentMessage}`);
        setMessages((prevMessages) => [
          ...prevMessages,
          { content: response.data.content, role: "assistant" }
        ]);
      } catch (error) {
        console.error("Error fetching response:", error);
      }
    };

    fetchResponse();
  }, [currentMessage]);

  return (
    <Box
      sx={{
        width: "40%",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        borderRadius: 2,
        boxShadow: 3,
        p: 2,
        bgcolor: "#f5f5f5",
      }}
    >
      {/* Messages Container */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 1,
          p: 1,
        }}
      >
        {messages.map((msg, index) => (
  <Paper
    key={index}
    sx={{
      p: 1,
      bgcolor: msg.role === "user" ? "#1976d2" : "#e0e0e0",
      color: msg.role === "user" ? "#fff" : "#000",
      alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
    }}
  >
    <Typography>{msg.content}</Typography>
  </Paper>
))}
      </Box>

      {/* Input Field & Send Button */}
      <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <IconButton color="primary" onClick={handleSend}>
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default ChatUI;
