import { useState, useContext } from "react";
import { Button, Stack, Box, Typography } from '@mui/material'
import './forms.css';
import { LegacySlider } from './SliderForm';
import { DataContext } from "../App";


function JsonInputForm() {

  const { setInputData, setOutputData } = useContext(DataContext);


  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({ alpha: 0, D: 0, p_transf: 0 });

  const ensureArray = (val) => Array.isArray(val) ? val : [Number(val)]

  const handleFileChange = (e) => {
    const file = e.target.files[0];

    setFile(file);
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {

        const json = JSON.parse(event.target.result);
        setFormData(prev => {
          const updated = {
            ...prev, ...json,
            alpha: json.alpha != undefined ? Number(json.alpha) : prev.alpha,
            D: json.D != undefined ? Number(json.D) : prev.D,
            p_transf: json.p_transf != undefined ? Number(json.p_transf) : prev.p_transf
          };
          setInputData(updated);
          return updated;
        });

      } catch {
        setError("Invalid JSON in User-defined Parameters file.");
      }
      if (setOutputData) setOutputData(null);
    };
    reader.readAsText(file);

  };

  const handleSliderChange = (field) => (value) => {
    setFormData((prev) => {
      const updated = {
        ...prev, [field]: Number(value)
      };
      setInputData(updated);
      return updated;
    });
  };

  const handleSave = () => {
    if (!file) {
      return;
    }

    const blob = new Blob([JSON.stringify(formData, null, 2)], {
      type: "application/json",
    });

    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = file.name;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleSubmit = async (e) => {

    console.log({ alpha: formData.alpha, D: formData.D, p_transf: formData.p_transf });
    e.preventDefault();
    setError(null);

    if (!file) {
      setError("Parameters file is required.");
      return;
    }

    const payloadData = {
      ...formData,
      alpha: ensureArray(formData.alpha),
      D: ensureArray(formData.D),
      p_transf: ensureArray(formData.p_transf),
    }

    const payload = new FormData();
    payload.append("file_params", new Blob([JSON.stringify(payloadData)], { type: "application/json" }), file?.name || "system_params.json");


    try {
      const res = await fetch("/api/optimize", {
        method: "POST",
        body: payload,
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Server error");
        return;
      }

      if (setOutputData) setOutputData(data);

    }

    catch {
      setError("Network error");
    }

  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <Box display="flex" flexDirection="column" gap={1} mt={2} mb={3}>
          <Typography variant="subtitle1">Upload System Parameters:</Typography>

          <Button
            variant="contained"
            component="label"
            size="small"

            sx={{ alignSelf: 'flex-start' }}
          >
            Choose File
            <input
              type="file"
              accept=".json"
              hidden
              onChange={handleFileChange}
            />
          </Button>
        </Box>

        <LegacySlider
          text_label="Total Demand"
          min_val={0}
          max_val={100000}
          step={1}
          curr_val={formData.D}
          onChange={handleSliderChange("D")}
        />
        <LegacySlider
          text_label=" ɑ (quality vs satisfaction)"
          min_val={0}
          max_val={1}
          step={0.001}
          curr_val={formData.alpha}
          onChange={handleSliderChange("alpha")}
        />
        <LegacySlider
          text_label="Allowable patients transfers (%)"
          min_val={0}
          max_val={1}
          step={0.01}
          curr_val={formData.p_transf}
          onChange={handleSliderChange("p_transf")}
        />

        {/*localInput?.b_hl && Array.isArray(localInput.b_hl) && (
          <div className="form-row" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
            <HistogramEditor
              data={localInput.b_hl}
              onChange={(newData) =>
                setLocalInput((prev) => ({ ...prev, b_hl: newData }))
              }
            />
          </div>
        )*/}

        <Stack direction="row" spacing={2}>
          <Button variant="contained" color="primary" size="small" onClick={handleSave}>
            Save
          </Button>

          <Button variant="contained" color="primary" size="small" type="submit">
            Submit
          </Button>
        </Stack>
      </form>

      {error && <p className="error-message">Error: {error}</p>}



    </div>
  );
}

export default JsonInputForm;
