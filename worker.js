// worker.js
const { Worker } = require("bullmq");
const { spawn } = require("child_process");

const path = require("path");

const connection = { host: "localhost", port: 6379 };

const worker = new Worker("anotation-queue", async (job) => {
  console.log(`Processing job: ${job.id}`);
  const imgPath = job.data.imgPath;
  const jobid = job.id;
  console.log(imgPath)
  return await runPython(imgPath, jobid);
}, { connection });

function runPython(imgPath, jobid) {
  return new Promise((resolve, reject) => {
   
    pythonPath = path.join(__dirname, "venv", "Scripts", "python.exe");
   
    console.log(`Using Python from: ${pythonPath}`);
    
    const python = spawn(pythonPath, ["detect.py", imgPath, jobid], { 
      stdio: ["ignore", "pipe", "pipe"],
      cwd: __dirname 
    });

    let stdout = "";
    let stderr = "";

    python.stdout.on("data", (d) => { stdout += d.toString(); });
    python.stderr.on("data", (d) => { stderr += d.toString(); });

    python.on("error", (err) => {
      console.error("Failed to start python process:", err);
      console.error(`Make sure venv exists at: ${pythonPath}`);
      reject(err);
    });

    python.on("close", (code) => {
      if (code === 0) {
        console.log("Python finished:", stdout.trim());
        resolve(stdout.trim());
      } else {
        console.error("Python exited with code", code);
        console.error("stderr:", stderr);
        reject(new Error(`Python exited with code ${code}`));
      }
    });
  });
}

// Graceful shutdown
worker.on("completed", (job) => {
  console.log(`Job ${job.id} completed successfully`);
});

worker.on("failed", (job, err) => {
  console.error(`Job ${job?.id} failed:`, err.message);
});

;