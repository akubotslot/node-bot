const { TelegramClient } = require("telegram");
const { StringSession } = require("telegram/sessions");
const readline = require("readline");

const apiId = 23892173; // Ganti dengan API ID kamu
const apiHash = "5b6a63e81e214ded98b1f67758612183"; // Ganti dengan API Hash kamu
const stringSession = new StringSession(""); // Isi ini nanti dengan nilai dari session.save()

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// Nomor telepon yang sudah ditentukan
const phoneNumber = "6285776941350"; // Ganti dengan nomor yang ingin digunakan

(async () => {
  console.log("Loading interactive example...");
  const client = new TelegramClient(stringSession, apiId, apiHash, {
    connectionRetries: 5,
  });
  await client.start({
    phoneNumber: async () => {
      console.log(`Using phone number: ${phoneNumber}`);
      return phoneNumber; // Langsung menggunakan nomor yang sudah ditentukan
    },
    password: async () =>
      new Promise((resolve) =>
        rl.question("Please enter your password: ", resolve)
      ),
    phoneCode: async () =>
      new Promise((resolve) =>
        rl.question("Please enter the code you received: ", resolve)
      ),
    onError: (err) => console.log(err),
  });
  console.log("You should now be connected.");
  console.log(client.session.save()); // Simpan string ini untuk menghindari login lagi
  await client.sendMessage("me", { message: "Hello!" });
})();