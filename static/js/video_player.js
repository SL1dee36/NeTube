// Get references to DOM elements
const video = document.getElementById('NeTubeVideoPlayer');
const playPauseButton = document.getElementById('playPause');
const muteUnmuteButton = document.getElementById('muteUnmute');
const fullscreenButton = document.getElementById('fullscreen');
const videoPlayerContainer = document.getElementById('videoPlayerContainer');
const seekBar = document.getElementById('seekBar');
const volumeSlider = document.getElementById('volume');
const volumeText = document.getElementById('volumeText');
const currentTimeDisplay = document.getElementById('currentTime');
const durationDisplay = document.getElementById('duration');
const pipButton = document.getElementById('pip');
const settingsButton = document.getElementById('settings');
const settingsMenu = document.getElementById('settingsMenu');
const speedSelect = document.getElementById('speed');
const autoplayCheckbox = document.getElementById('autoplay');

// Play or pause video
const updatePlayPauseButton = () => {
    playPauseButton.innerHTML = video.paused ? '<i class="fas fa-play"></i>' : '<i class="fas fa-pause"></i>';
};

playPauseButton.addEventListener('click', () => {
    video.paused ? video.play() : video.pause();
});


video.addEventListener('click', () => {
    if (video.paused) {
        video.play();
        playPauseButton.innerHTML = '<i class="fas fa-pause"></i>';
    } else {
        video.pause();
        playPauseButton.innerHTML = '<i class="fas fa-play"></i>';
    }
});


video.addEventListener('play', updatePlayPauseButton);
video.addEventListener('pause', updatePlayPauseButton);

// Mute or unmute video
muteUnmuteButton.addEventListener('click', () => {
    video.muted = !video.muted;
    muteUnmuteButton.innerHTML = video.muted ? '<i class="fas fa-volume-mute"></i>' : '<i class="fas fa-volume-up"></i>';
    volumeSlider.value = video.muted ? 0 : video.volume;
    volumeText.innerText = Math.round(video.volume * 100);
});

// Fullscreen mode
fullscreenButton.addEventListener('click', () => {
    if (!document.fullscreenElement) {
        videoPlayerContainer.requestFullscreen().catch(err => {
            console.log("Error attempting to enable full-screen mode:", err);
        });
        fullscreenButton.innerHTML = '<i class="fas fa-compress"></i>'; // Иконка для выхода из полноэкранного режима
    } else {
        document.exitFullscreen();
        fullscreenButton.innerHTML = '<i class="fas fa-expand"></i>'; // Иконка для входа в полноэкранный режим
    }
});

document.addEventListener('fullscreenchange', () => {
    if (document.fullscreenElement) {
        videoPlayerContainer.classList.add('fullscreen');
        document.body.style.overflow = 'hidden'; // Предотвращение прокрутки
    } else {
        videoPlayerContainer.classList.remove('fullscreen');
        document.body.style.overflow = ''; // Восстановление прокрутки
    }
});
// Picture-in-Picture mode
pipButton.addEventListener('click', async () => {
    if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
    } else if (video.requestPictureInPicture) {
        await video.requestPictureInPicture();
    }
});

// Toggle visibility of settings menu
settingsButton.addEventListener('click', () => {
    settingsMenu.classList.toggle('hidden');
});

// Change playback speed
speedSelect.addEventListener('change', (event) => {
    video.playbackRate = parseFloat(event.target.value);
});

// Toggle autoplay
autoplayCheckbox.addEventListener('change', (event) => {
    video.loop = event.target.checked;
});

// Update seek bar and current time
video.addEventListener('timeupdate', () => {
    seekBar.value = (video.currentTime / video.duration) * 100;
    currentTimeDisplay.textContent = formatTime(video.currentTime);
});

// Seek video when seek bar changes
seekBar.addEventListener('input', () => {
    video.currentTime = (seekBar.value / 100) * video.duration;
});

// Update volume
volumeSlider.addEventListener('input', () => {
    video.volume = volumeSlider.value;
    muteUnmuteButton.innerHTML = video.volume === 0 ? '<i class="fas fa-volume-mute"></i>' : '<i class="fas fa-volume-up"></i>';
    volumeText.innerText = Math.round(video.volume * 100);
});

// Display video duration
video.addEventListener('loadedmetadata', () => {
    durationDisplay.textContent = formatTime(video.duration);
});

// Format time in MM:SS
function formatTime(time) {
    const minutes = Math.floor(time / 60).toString().padStart(2, '0');
    const seconds = Math.floor(time % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
}
