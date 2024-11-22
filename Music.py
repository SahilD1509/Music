import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QSlider, QListWidget, QHBoxLayout, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from pygame import mixer
from mutagen.mp3 import MP3


class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player")
        self.setGeometry(100, 100, 800, 600)

        # Initialize pygame mixer
        mixer.init()

        # Player state
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.song_length = 0  # Total duration of the current song
        self.timer = QTimer()  # Timer to update the progress bar
        self.timer.timeout.connect(self.update_progress_bar)

        # Layouts and Widgets
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel("Welcome to SD Music Player", self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Playlist
        self.playlist_widget = QListWidget(self)
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_song)
        main_layout.addWidget(self.playlist_widget)

        # Song Info
        self.song_info_label = QLabel("No song playing", self)
        self.song_info_label.setStyleSheet("font-size: 14px; color: gray;")
        main_layout.addWidget(self.song_info_label)

        # Progress Bar Layout
        progress_layout = QHBoxLayout()

        self.progress_label_start = QLabel("0:00", self)
        self.progress_label_start.setStyleSheet("font-size: 12px;")
        progress_layout.addWidget(self.progress_label_start)

        self.progress_bar = QSlider(Qt.Horizontal, self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.sliderReleased.connect(self.seek_music)  # User can seek the song
        progress_layout.addWidget(self.progress_bar)

        self.progress_label_end = QLabel("0:00", self)
        self.progress_label_end.setStyleSheet("font-size: 12px;")
        progress_layout.addWidget(self.progress_label_end)

        main_layout.addLayout(progress_layout)

        # Controls Layout
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.play_music)
        controls_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("⏸ Pause")
        self.pause_button.clicked.connect(self.pause_music)
        controls_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_music)
        controls_layout.addWidget(self.stop_button)

        self.next_button = QPushButton("⏭ Next")
        self.next_button.clicked.connect(self.next_music)
        controls_layout.addWidget(self.next_button)

        self.prev_button = QPushButton("⏮ Previous")
        self.prev_button.clicked.connect(self.previous_music)
        controls_layout.addWidget(self.prev_button)

        main_layout.addLayout(controls_layout)

        # Volume Slider
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 Volume:")
        volume_layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)

        main_layout.addLayout(volume_layout)

        # Add Song Button
        self.add_song_button = QPushButton("➕ Add Songs")
        self.add_song_button.clicked.connect(self.add_songs)
        main_layout.addWidget(self.add_song_button)

        # Container widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Music Files", "", "Music Files (*.mp3)")
        if files:
            for file in files:
                self.playlist.append(file)
                self.playlist_widget.addItem(os.path.basename(file))

    def play_music(self):
        if self.current_index == -1 and self.playlist:
            self.current_index = 0
        if self.current_index >= 0 and not self.is_playing:
            self.load_and_play(self.playlist[self.current_index])

    def pause_music(self):
        if self.is_playing:
            mixer.music.pause()
            self.is_playing = False
        else:
            mixer.music.unpause()
            self.is_playing = True

    def stop_music(self):
        mixer.music.stop()
        self.is_playing = False
        self.timer.stop()
        self.reset_progress_bar()

    def next_music(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.load_and_play(self.playlist[self.current_index])

    def previous_music(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.load_and_play(self.playlist[self.current_index])

    def set_volume(self, value):
        mixer.music.set_volume(value / 100)

    def load_and_play(self, file_path):
        mixer.music.stop()
        mixer.music.load(file_path)
        mixer.music.play()
        self.is_playing = True
        self.update_song_info(file_path)

        # Get song duration
        audio = MP3(file_path)
        self.song_length = int(audio.info.length)
        self.progress_bar.setRange(0, self.song_length)
        self.progress_label_end.setText(self.format_time(self.song_length))

        # Start timer for progress bar
        self.timer.start(1000)

    def play_selected_song(self):
        selected_index = self.playlist_widget.currentRow()
        if selected_index != -1:
            self.current_index = selected_index
            self.load_and_play(self.playlist[self.current_index])

    def update_song_info(self, file_path):
        audio = MP3(file_path)
        title = os.path.basename(file_path)
        artist = audio.tags.get("TPE1", "Unknown Artist")
        album = audio.tags.get("TALB", "Unknown Album")
        self.song_info_label.setText(f"Playing: {title}\nArtist: {artist}\nAlbum: {album}")

    def update_progress_bar(self):
        if self.is_playing:
            current_time = mixer.music.get_pos() // 1000  # Convert milliseconds to seconds
            self.progress_bar.setValue(current_time)
            self.progress_label_start.setText(self.format_time(current_time))

    def seek_music(self):
        seek_time = self.progress_bar.value()
        mixer.music.play(start=seek_time)

    def reset_progress_bar(self):
        self.progress_bar.setValue(0)
        self.progress_label_start.setText("0:00")
        self.progress_label_end.setText("0:00")

    @staticmethod
    def format_time(seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())
