import { List, ListItem, ListItemText } from "@mui/material";
import React, { useState, useRef } from "react";
import styles from "./Input.module.css";

export default function RecordInput({ logData }) {
  return (
    <>
      <div className={styles.container}>
        <h1>Лог</h1>
        <List dense={3}>
          {logData.map((item, index) => (
            <div key={index}>{item}</div>
          ))}
        </List>
      </div>
    </>
  );
}
