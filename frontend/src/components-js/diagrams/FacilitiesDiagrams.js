import { PieChart, Pie, ResponsiveContainer, Tooltip } from 'recharts';
import { Card, Typography, Grid, Table, TableHead, TableBody, TableRow, TableContainer, TableCell } from '@mui/material';
import { DataContext } from '../../App';
import { useContext, useMemo } from "react";

const GROUP_COLORS = [
  "#6388b4", "#f1c480ff", ' #ef6f6a', "#8cc2ca",
  "#55ad89", "#e4e093ff", "#bb7693", "#baa094",
  "#a9b5ae", "#767676", "#31a1b3", "#8175aa", "#f7f2ccff", "#9be0a2ff"
];


export default function Dashboard() {
  const { inputData } = useContext(DataContext);

  const casemix = inputData?.dashboard_stats.case_mix ?? [];



  const groupData = useMemo(() => {
    const acc = {};
    for (const row of casemix) {
      if (!acc[row.group_id]) { acc[row.group_id] = { group_id: row.group_id, ratio: 0 } };
      acc[row.group_id].ratio += row.ratio;
    }
    return [...Object.values(acc)]
  }, [casemix]);


  const casemixFiltered = useMemo(() => {
    const sorted = groupData.sort((a, b) => b.ratio - a.ratio)
    const topGroups = [... new Set(sorted.slice(0, 10).map(d => d.group_id))]
    const casemix_top = casemix.filter(d => topGroups.includes(d.group_id))
    let casemix_other = casemix.filter(d => !topGroups.includes(d.group_id))
    casemix_other = casemix_other.map((e) => ({
      "group_id": "Other", "region_id": e.region_id,
      "ratio": casemix_other.filter((e2) => e2.region_id == e.region_id).reduce((sum, e) => sum + e.ratio, 0)
    }))
    casemix_other = casemix_other.filter((v, i, self) => i === self.findIndex((t) => (t.region_id == v.region_id)))
    return casemix_other.length > 0 ? [...Object.values(casemix_top), ...Object.values(casemix_other)] :
      [...Object.values(casemix_top)]
  }, [casemix]);


  const groupColorMap = useMemo(() => {
    const ids = [...new Set(casemixFiltered.map(d => d.group_id))];
    return Object.fromEntries(ids.map((id, i) => [id, GROUP_COLORS[i % GROUP_COLORS.length]]));
  }, [casemix]);

  const filteredGoupData = useMemo(() => {
    const acc = {};
    for (const row of casemixFiltered) {
      if (!acc[row.group_id]) { acc[row.group_id] = { group_id: row.group_id, fill: groupColorMap[row.group_id], ratio: 0 } };
      acc[row.group_id].ratio += row.ratio;
    }
    return [...Object.values(acc)]
  }, [casemixFiltered])

  const regionData = useMemo(() => {
    const grouped = Object.groupBy(casemixFiltered, d => d.group_id);
    return Object.entries(grouped).flatMap(([groupId, rows]) => {
      const sorted = [...rows].sort((a, b) => b.ratio - a.ratio);
      const topValues = sorted.slice(0, 4);
      const otherValue = sorted.slice(4).reduce((sum, r) => sum + r.ratio, 0);
      const color = groupColorMap[groupId];

      const result = topValues.map((d, i) => ({
        name: `${groupId}-${d.region_id}`,
        value: d.ratio,
        group_id: groupId,
        region_id: d.region_id,
        fill: `${color}`,
      }));

      if (otherValue > 0) {
        result.push({
          name: `${groupId}-Other`,
          value: otherValue,
          group_id: groupId,
          region_id: 'Other',
          fill: `${color}`,
        });
      }

      return result;
    });
  }, [casemix, groupColorMap]);

  return (
    <Grid container spacing={5}>
      <Grid>
        <Card sx={{ m: 5, width: "100%" }} >
          <Typography align="left" sx={{ m: 1, fontSize: 12 }}  > Instance Dashboard</Typography>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: "bold" }}> Property</TableCell>
                <TableCell sx={{ fontWeight: "bold" }}> Value</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(inputData.dashboard_stats)
                .filter(([_, value]) => typeof value == "number")
                .map(([key, value]) => (
                  <TableRow key={key}>
                    <TableCell>
                      {key.replace(/_/g, " ")}
                    </TableCell>
                    <TableCell>
                      {value}
                    </TableCell>
                  </TableRow>))}
            </TableBody>
          </Table>
        </Card>
      </Grid>
      <Grid sx={{ width: 400 }}>
        <Card sx={{ m: 5, width: "100%" }} >
          <Typography align="left" sx={{ m: 1, fontSize: 12 }}  >Case Mix Distribution</Typography>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={filteredGoupData}
                dataKey="ratio"
                nameKey="group_id"
                cx="50%"
                cy="50%"
                outerRadius={80}
              />
              <Pie
                data={regionData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={90}
                outerRadius={140}
              />
              <Tooltip
                formatter={(value, name) => [value.toFixed(3), name]}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </Grid>
    </Grid >
  );
}