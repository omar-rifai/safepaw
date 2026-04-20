import { Button } from '@mui/material'
import { useState } from 'react';
import { styled } from '@mui/material/styles';
import './forms.css';




const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});


function JsonInputForm() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    const jsonData= JSON.parse(text)

    const response = await fetch("/api/optimize",{
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(jsonData)
    })

    const result = await response.json();
    console.log(result)
  };

  return (
    <div>
      <Button
        component="label"
        role={undefined}
        variant="contained"
        tabIndex={-1}
      >
        Upload files
        <VisuallyHiddenInput
          type="file"
          onChange={handleUpload}
          multiple
        />
      </Button>
    </div>
  );
}

export default JsonInputForm;
