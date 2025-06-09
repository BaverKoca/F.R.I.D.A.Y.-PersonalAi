// static/script.js

let recognition = null;

function speak(text) {
  const lang = document.getElementById('langSelect').value;
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
  // Get selected language
  const lang = document.getElementById('langSelect').value;
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
