import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { Box, Button, ButtonGroup } from "@mui/material";
import xlsx from "json-as-xlsx";
import { mkConfig, generateCsv, download } from "export-to-csv";
import io from "socket.io-client";
import React, { useState, useEffect, useRef } from "react";

//Setting for Excel exporter
let settings = {
  fileName: "MySpreadsheet", // Name of the resulting spreadsheet
  extraLength: 3, // A bigger number means that columns will be wider
  writeMode: "writeFile", // The available parameters are 'WriteFile' and 'write'. This setting is optional. Useful in such cases https://docs.sheetjs.com/docs/solutions/output#example-remote-file
  writeOptions: {}, // Style options from https://docs.sheetjs.com/docs/api/write-options
  RTL: false, // Display the columns from right-to-left (the default value is false)
};

let data = [
  {
    startTime: "13:40",
    endTime: "17:47",
    stall: "1320",
    stage: "Бурение",
    comment: "Без замечаний",
  },
];

export default function ReportTable() {
  const [tableData, setTableData] = useState(data);
  const [inputValue, setInputValue] = useState("");
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io("ws://localhost:8000");
    setSocket(newSocket);

    newSocket.on("connect", () => {
      console.log("Connected to server");
    });

    newSocket.on("json_data", (data) => {
      console.log(data);
      try {
        const message = JSON.parse(data);
        setTableData((prev) => [...prev, message]);
      } catch (error) {
        console.error("Ошибка при парсинге JSON:", error);
      }
    });

    newSocket.on("log", (data) => {
      console.log(data);
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected from server");
    });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const handleExcelExport = () => {
    let table = [
      {
        sheet: "Отчёт",
        columns: [
          { label: "Время начала", value: "startTime" },
          { label: "Время конца", value: (row) => row.endTime },
          { label: "Забой", value: (row) => row.stall },
          { label: "Этап", value: (row) => row.stage },
          { label: "Комментарий", value: (row) => row.comment },
        ],
        content: tableData,
      },
    ];
    xlsx(table, settings);
  };

  // Экспорт в CSV
  const csvConfig = mkConfig({ useKeysAsHeaders: true });

  const handleCSVExport = () => {
    const csv = generateCsv(csvConfig)(data);
    download(csvConfig)(csv);
  };

  return (
    <>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Время начала</TableCell>
              <TableCell align="right">Время окончания</TableCell>
              <TableCell align="right">Забой</TableCell>
              <TableCell align="right">Этап</TableCell>
              <TableCell align="right">Комментарий</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tableData.map((row) => (
              <TableRow
                key={row.startTime}
                sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {row.startTime}
                </TableCell>
                <TableCell align="right">{row.endTime}</TableCell>
                <TableCell align="right">{row.stall}</TableCell>
                <TableCell align="right">{row.stage}</TableCell>
                <TableCell align="right">{row.comment}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box>
        <h1>Скачать в формате: </h1>
        <ButtonGroup variant="contained" aria-label="Basic button group">
          <Button color="success" onClick={handleExcelExport}>
            Excel
          </Button>
          <Button onClick={handleCSVExport}>CSV</Button>
        </ButtonGroup>
      </Box>
    </>
  );
}
