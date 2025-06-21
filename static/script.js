// static/script.js

let recognition = null;

function speak(text) {
  // Detect language of the text for correct pronunciation
  let lang = 'en-US';
  if (/\p{Script=Latin}/u.test(text) && /[çğıöşüÇĞİÖŞÜ]/.test(text)) {
    lang = 'tr-TR'; // Turkish special chars detected
  } else if (/\p{Script=Latin}/u.test(text) && /[äöüßÄÖÜ]/.test(text)) {
    lang = 'de-DE'; // German special chars detected
  } else if (/\p{Script=Latin}/u.test(text) && /[éèêçàùâîôûëïüœæ]/i.test(text)) {
    lang = 'fr-FR'; // French special chars detected
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.pitch = 1;
  utterance.rate = 1;
  utterance.volume = 1;
  speechSynthesis.speak(utterance);
}

function searchOnGoogle(query) {
  const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
  window.open(url, '_blank');
}

function startRecognition() {
  if (recognition) {
    recognition.abort();
    recognition = null;
  }
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
    const transcript = event.results[0][0].transcript;
    document.getElementById("userText").textContent = transcript;

    fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: transcript })
    })
    .then(response => response.json())
    .then(data => {
      loader.style.display = "none";
      document.getElementById('stopBtn').disabled = true;
      if (data.response) {
        document.getElementById("responseText").textContent = data.response;
        speak(data.response);
        // Always open a new tab with Google search for the user's query
        searchOnGoogle(transcript);
      } else {
        document.getElementById("responseText").textContent = "Error: " + data.error;
      }
    })
    .catch(error => {
      loader.style.display = "none";
      document.getElementById('stopBtn').disabled = true;
      document.getElementById("responseText").textContent = "Request failed.";
      console.error("Error:", error);
    });
  };

  recognition.onerror = (event) => {
    loader.style.display = "none";
    document.getElementById('stopBtn').disabled = true;
    alert("Speech recognition error: " + event.error);
  };

  recognition.onend = () => {
    document.getElementById('stopBtn').disabled = true;
  };
}

function stopRecognition() {
  if (recognition) {
    recognition.stop();
    document.getElementById('stopBtn').disabled = true;
  }
}

function sendChat() {
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;
  document.getElementById('userText').textContent = message;
  document.getElementById('loader').style.display = 'block';
  document.getElementById('responseText').textContent = '';
  fetch('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: message })
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById('loader').style.display = 'none';
      if (data.response) {
        document.getElementById('responseText').textContent = data.response;
        speak(data.response);
        searchOnGoogle(message);
      } else {
        document.getElementById('responseText').textContent = 'Error: ' + data.error;
      }
    })
    .catch(error => {
      document.getElementById('loader').style.display = 'none';
      document.getElementById('responseText').textContent = 'Request failed.';
      console.error('Error:', error);
    });
  input.value = '';
}

document.getElementById('chatInput').addEventListener('keydown', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    sendChat();
  }
});
