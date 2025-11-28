const fs = require('fs');
const path = require('path');
const express = require("express");
const { addToQueue } = require("./producer.js");
const multer  = require('multer');

const UPLOAD_DIR = path.join(__dirname, 'uploads');

// make sure uploads dir exists
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const upload = multer({ dest: UPLOAD_DIR });

const app = express();
app.use(express.json());


app.post("/process-image", async (req, res) => {

  const imgPath = req.body?.imgPath;

  if (!imgPath) {
    return res.status(400).json({ error: "imgPath is required in JSON body" });
  }

  try {
    const jobId = await addToQueue(imgPath);
    return res.status(202).json({
      message: "Image path received and processing started.",
      jobId,
      filePath: imgPath
    });
  } catch (error) {
    console.error("Error adding to queue:", error);
    return res.status(500).json({ error: "Failed to queue" });
  }
});




app.listen(3000, () => {
  console.log("API running on http://localhost:3000");
});
