import React, { useState, useEffect } from "react";
import { Box, TextField, IconButton, Paper } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import axios from "axios";
import { MuiMarkdown, getOverrides } from "mui-markdown";

const ChatUI = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [currentMessage, setCurrentMessage] = useState("");

  const handleSend = () => {
    if (input.trim()) {
      setMessages([...messages, { content: input, role: "user" }]);
      setCurrentMessage(input);
      setInput("");
    }
  };

  useEffect(() => {
    if (!currentMessage) return;

    const fetchResponse = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/predict?text=${currentMessage}`
        );
        setMessages((prevMessages) => [
          ...prevMessages,
          { content: response.data.content, role: "assistant" },
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
        height: "80vh",
        display: "flex",
        flexDirection: "column",
        borderRadius: 3,
        boxShadow: 5,
        p: 2,
        bgcolor: "rgba(255, 255, 255, 0.15)", // Semi-transparent white
        backdropFilter: "blur(15px)", // Frosted glass effect
        border: "1px solid rgba(255, 255, 255, 0.2)",
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
              p: 1.5,
              bgcolor: msg.role === "user" ? "#0066B2" : "#99E2F7",
              color: "white",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              borderRadius: "12px",
              maxWidth: "75%",
            }}
          >
            <MuiMarkdown
              overrides={{
                ...getOverrides({}), // This will keep the other default overrides.
                h1: {
                  component: "p",
                  props: {
                    style: { color: "red" },
                  },
                },
              }}
            >
              {msg.content}
            </MuiMarkdown>
          </Paper>
        ))}
      </Box>

      {/* Input Field & Send Button */}
      <Box sx={{ display: "flex", gap: 1, alignItems: "center", mt: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          sx={{
            bgcolor: "rgba(255, 255, 255, 0.8)",
            borderRadius: "8px",
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSend();
            }
          }}
        />
        <IconButton
          sx={{
            bgcolor: "#0099CC",
            color: "#fff",
            "&:hover": { bgcolor: "#0066B2" },
          }}
          onClick={handleSend}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default ChatUI;
