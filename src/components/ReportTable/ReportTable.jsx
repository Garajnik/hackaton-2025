import * as React from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { Box, Button, ButtonGroup } from "@mui/material";

function createData(startTime, endTime, stall, stage, comment) {
  return { startTime, endTime, stall, stage, comment };
}

const rows = [
  createData("Frozen yoghurt", 159, 6.0, 24, 4.0),
  createData("Ice cream sandwich", 237, 9.0, 37, 4.3),
  createData("Eclair", 262, 16.0, 24, 6.0),
  createData("Cupcake", 305, 3.7, 67, 4.3),
  createData("Gingerbread", 356, 16.0, 49, 3.9),
];

export default function ReportTable() {
  return (
    <>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Время начала</TableCell>
              <TableCell align="right">Время окончания</TableCell>
              <TableCell align="right">Запой</TableCell>
              <TableCell align="right">Этап</TableCell>
              <TableCell align="right">Комментарий</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
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
          <Button color="success">Excel</Button>
          <Button>CSV</Button>
        </ButtonGroup>
      </Box>
    </>
  );
}
