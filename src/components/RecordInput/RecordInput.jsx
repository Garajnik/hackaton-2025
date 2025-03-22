import { IconButton, TextField } from "@mui/material";
import React, { useState, useRef } from "react";
import styles from "./Input.module.css";
import MicIcon from "@mui/icons-material/Mic";
import RecordRTC from "recordrtc";
import { Mp3Encoder } from "lamejs";

export default function RecordInput() {
  const [recordValue, setRecordValue] = useState(false);
  const [inputText, setInputText] = useState("Запись не идёт");
  const [color, setColor] = useState("#ff0000");

  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const recorderRef = useRef(null);

  const startRecording = () => {
    if (recordValue) {
      setRecordValue(false);
      setColor("#ff0000");
    } else {
      setRecordValue(true);
      setColor("#00ff00");
    }
  };

  return (
    <>
      <div className={styles.container}>
        <h1>Голосовой ввод</h1>
        <div className={styles.inputContainer}>
          <TextField
            id="outlined-basic"
            label="Ваш запрос"
            variant="outlined"
          ></TextField>
          <IconButton onClick={startRecording} aria-label="delete" size="large">
            <MicIcon color="primary" fontSize="inherit" />
          </IconButton>
        </div>
        <div style={{ color }}>{inputText}</div>
      </div>
    </>
  );
}
