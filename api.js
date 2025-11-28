const fs = require('fs');
const path = require('path');
const express = require("express");
const { addToQueue } = require("./producer.js");
const multer = require('multer');
const cors = require('cors');

const UPLOAD_DIR = path.join(__dirname, 'uploads');
const OUTPUT_DIR = path.join(__dirname, 'output');

if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

const upload = multer({ dest: UPLOAD_DIR });
const app = express();

app.use(cors());
app.use(express.json());

// Upload and process image
app.post("/process-image", upload.single('image'), async (req, res) => {
  const uploadedPath = req.file.path;

  if (!uploadedPath) {
    return res.status(400).json({ error: "No file uploaded. Use field name 'image'." });
  }

  try {
    const jobId = await addToQueue(uploadedPath);
    return res.status(202).json({
      message: "Image uploaded and processing started.",
      jobId,
      originalName: req.file.originalname
    });
  } catch (error) {
    console.error("Error adding to queue:", error);
    return res.status(500).json({ error: "Failed to queue uploaded file" });
  }
});

// Get processed image
app.get("/result/:jobId", async (req, res) => {
  const { jobId } = req.params;

  // Check for .jpg or .png output
  let outputPath = path.join(OUTPUT_DIR, `${jobId}.jpg`);
  if (!fs.existsSync(outputPath)) {
    outputPath = path.join(OUTPUT_DIR, `${jobId}.png`);
  }

  try {
    // Simple check - if file exists and is recent, assume completed
    if (fs.existsSync(outputPath)) {
      return res.sendFile(outputPath);
    }

    // File doesn't exist yet - still processing
    return res.status(202).json({
      status: "processing",
      message: "Image is still being processed",
      jobId
    });

  } catch (error) {
    console.error("Error fetching result:", error);
    res.status(500).json({
      status: "error",
      error: "Failed to fetch result"
    });
  }
});


app.listen(PORT, () => {
  console.log(`API running on http://localhost:3000`);

});