// producer.js
const { Queue } = require("bullmq");

const connection = { host: "localhost", port: 6379 }; 
const anotationQueue = new Queue("anotation-queue", { connection });

async function addToQueue(imgPath) {
  const job = await anotationQueue.add("process image", { imgPath });
  console.log("Job added:", job.id, "imgPath:", imgPath);
  return job.id;
}

module.exports = { addToQueue };
