// static/script.js

let recognition = null;
let aiController = null; // For aborting fetch
let speakingUtterance = null;
let stopped = false;

function speak(text) {
  if (stopped) return;
  // Detect language of the text for correct pronunciation
  let lang = 'en-US';
  if (/\p{Script=Latin}/u.test(text) && /[çğıöşüÇĞİÖŞÜ]/.test(text)) {
    lang = 'tr-TR'; // Turkish special chars detected
  } else if (/\p{Script=Latin}/u.test(text) && /[äöüßÄÖÜ]/.test(text)) {
    lang = 'de-DE'; // German special chars detected
  } else if (/\p{Script=Latin}/u.test(text) && /[éèêçàùâîôûëïüœæ]/i.test(text)) {
    lang = 'fr-FR'; // French special chars detected
  }
  speakingUtterance = new SpeechSynthesisUtterance(text);
  speakingUtterance.lang = lang;
  speakingUtterance.pitch = 1;
  speakingUtterance.rate = 1;
  speakingUtterance.volume = 1;
  speechSynthesis.speak(speakingUtterance);
}

function stopAll() {
  stopped = true;
  // Stop voice recognition
  if (recognition) {
    recognition.onend = null;
    recognition.onerror = null;
    recognition.stop();
    recognition = null;
  }
  // Abort AI fetch
  if (aiController) {
    aiController.abort();
    aiController = null;
  }
  // Stop speech synthesis
  if (window.speechSynthesis && window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
  }
  document.getElementById('stopBtn').disabled = true;
  document.getElementById('loader').style.display = 'none';
}

function searchOnGoogle(query) {
  const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
  window.open(url, '_blank');
}

function startRecognition() {
  stopAll(); // Ensure everything is stopped before starting
  stopped = false;
  // Default to English
  const lang = "en-US";
  recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = lang;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  const loader = document.getElementById("loader");
  loader.style.display = "block";

  document.getElementById('stopBtn').disabled = false;

  recognition.start();

  recognition.onstart = () => {
    console.log("Voice recognition started...");
  };

  recognition.onresult = (event) => {
    if (stopped) return;
    const transcript = event.results[0][0].transcript;
    document.getElementById("userText").textContent = transcript;

    aiController = new AbortController();
    fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: transcript }),
      signal: aiController.signal
    })
    .then(response => response.json())
    .then(data => {
      if (stopped) return;
      loader.style.display = "none";
      document.getElementById('stopBtn').disabled = true;
      if (data.response) {
        document.getElementById("responseText").textContent = data.response;
        speak(data.response);
        // Open Google Images immediately if requested
        if (data.open_images && data.query) {
          setTimeout(() => {
            window.open(`https://www.google.com/search?tbm=isch&q=${encodeURIComponent(data.query)}`, '_blank');
          }, 100); // slight delay to ensure popup is not blocked
        }
      } else {
        document.getElementById("responseText").textContent = "Error: " + data.error;
      }
    })
    .catch(error => {
      if (stopped) return;
      loader.style.display = "none";
      document.getElementById('stopBtn').disabled = true;
      if (error.name === 'AbortError') {
        document.getElementById("responseText").textContent = "Stopped.";
      } else {
        document.getElementById("responseText").textContent = "Request failed.";
        console.error("Error:", error);
      }
    });
  };

  recognition.onerror = (event) => {
    if (stopped) return;
    loader.style.display = "none";
    document.getElementById('stopBtn').disabled = true;
    alert("Speech recognition error: " + event.error);
  };

  recognition.onend = () => {
    if (stopped) return;
    document.getElementById('stopBtn').disabled = true;
  };
}

function stopRecognition() {
  stopAll();
}

function sendChat() {
  stopAll();
  stopped = false;
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;
  document.getElementById('userText').textContent = message;
  document.getElementById('loader').style.display = 'block';
  document.getElementById('responseText').textContent = '';
  aiController = new AbortController();
  fetch('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: message }),
    signal: aiController.signal
  })
    .then(response => response.json())
    .then(data => {
      if (stopped) return;
      document.getElementById('loader').style.display = 'none';
      if (data.response) {
        document.getElementById('responseText').textContent = data.response;
        speak(data.response);
        // Open Google Images immediately if requested
        if (data.open_images && data.query) {
          setTimeout(() => {
            window.open(`https://www.google.com/search?tbm=isch&q=${encodeURIComponent(data.query)}`, '_blank');
          }, 100);
        }
      } else {
        document.getElementById('responseText').textContent = 'Error: ' + data.error;
      }
    })
    .catch(error => {
      if (stopped) return;
      document.getElementById('loader').style.display = 'none';
      if (error.name === 'AbortError') {
        document.getElementById('responseText').textContent = 'Stopped.';
      } else {
        document.getElementById('responseText').textContent = 'Request failed.';
        console.error('Error:', error);
      }
    });
  input.value = '';
}

document.getElementById('chatInput').addEventListener('keydown', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    sendChat();
  }
});
