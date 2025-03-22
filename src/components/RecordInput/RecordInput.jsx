import { IconButton, TextField } from "@mui/material";
import React, { useState, useRef } from "react";
import styles from "./Input.module.css";
import MicIcon from "@mui/icons-material/Mic";
import RecordRTC from "recordrtc";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

export default function RecordInput() {
  const [recordValue, setRecordValue] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const recorderRef = useRef(null);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorderRef.current = new RecordRTC(stream, {
      type: "audio",
      mimeType: "audio/wav", // Формат WAV
      recorderType: RecordRTC.StereoAudioRecorder,
      desiredSamplesPerSecond: 44100,
      numberOfAudioChannels: 1,
      timeSlice: 1000,
      ondataavailable: (blob) => {
        setAudioBlob(blob); // Сохраняем WAV-файл
      },
    });

    recorderRef.current.startRecording();
    setIsRecording(true);
  };

  const stopRecording = async () => {
    recorderRef.current.stopRecording(() => {
      setIsRecording(false);
      const blob = recorderRef.current.getBlob();
      setAudioBlob(blob); // Сохраняем WAV-файл
    });
  };

  const uploadAudio = async () => {
    if (!audioBlob) return;

    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav"); // Используем WAV-файл

    try {
      const response = await fetch("http://192.168.4.213:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        console.log("File uploaded successfully");
      } else {
        console.error("Failed to upload file");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  const handleToggleRecording = () => {
    if (recordValue) {
      setRecordValue(false);
      stopRecording();
    } else {
      setRecordValue(true);
      startRecording();
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
          <IconButton
            onClick={handleToggleRecording}
            aria-label="delete"
            size="large"
          >
            <MicIcon color="primary" fontSize="inherit" />
          </IconButton>
          <IconButton disabled={!audioBlob} onClick={uploadAudio}>
            <CloudUploadIcon fontSize="inherit"></CloudUploadIcon>
          </IconButton>
        </div>
        <div style={{ color: isRecording ? "#ff0000" : "#00ff00" }}>
          {isRecording ? "Запись идёт" : "Запись не идёт"}
        </div>
      </div>
    </>
  );
}
