const recordButton = document.getElementById('record');
const stopButton = document.getElementById('stop');
const uploadForm = document.getElementById('uploadForm');
const timerDisplay = document.getElementById('timer');

let mediaRecorder;
let audioChunks = [];
let timerInterval;

function formatTime(seconds) {
    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    return `${m}:${s}`;
}

recordButton.onclick = () => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        audioChunks = [];
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio_data', blob, 'recorded.wav');

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(res => res.text())
            .then(msg => {
                alert(msg);
                location.reload();
            });
        };

        recordButton.disabled = true;
        stopButton.disabled = false;

        let seconds = 0;
        timerInterval = setInterval(() => {
            seconds++;
            timerDisplay.textContent = formatTime(seconds);
        }, 1000);
    });
};

stopButton.onclick = () => {
    mediaRecorder.stop();
    recordButton.disabled = false;
    stopButton.disabled = true;
    clearInterval(timerInterval);
};
