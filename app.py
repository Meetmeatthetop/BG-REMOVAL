import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QSlider, QHBoxLayout
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from rembg import remove
from PIL import Image, ImageEnhance
import io

class BackgroundRemoverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Background Remover')

        layout = QVBoxLayout()

        # Upload button
        self.upload_btn = QPushButton('Upload Image', self)
        self.upload_btn.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_btn)

        # Image display
        self.image_label = QLabel('Original Image', self)
        layout.addWidget(self.image_label)

        # Pre-processing sliders
        self.brightness_slider = self.create_slider('Brightness', layout)
        self.contrast_slider = self.create_slider('Contrast', layout)
        self.sharpness_slider = self.create_slider('Sharpness', layout)

        # Remove background button
        self.remove_bg_btn = QPushButton('Remove Background', self)
        self.remove_bg_btn.clicked.connect(self.remove_background)
        layout.addWidget(self.remove_bg_btn)

        # Processed image display
        self.result_label = QLabel('Processed Image', self)
        layout.addWidget(self.result_label)

        # Save button
        self.save_btn = QPushButton('Save Image', self)
        self.save_btn.clicked.connect(self.save_image)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def create_slider(self, name, layout):
        hbox = QHBoxLayout()
        label = QLabel(f'{name}:', self)
        hbox.addWidget(label)
        slider = QSlider(Qt.Orientation.Horizontal, self)
        slider.setRange(0, 200)
        slider.setValue(100)
        hbox.addWidget(slider)
        layout.addLayout(hbox)
        return slider

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Images (*.png *.xpm *.jpg)')
        if file_path:
            self.image = Image.open(file_path)
            self.image_label.setPixmap(QPixmap(file_path))

    def remove_background(self):
        # Apply pre-processing
        image = self.image
        image = self.apply_preprocessing(image)

        # Remove background
        output = remove(image)

        # Convert to QImage for display
        bio = io.BytesIO()
        output.save(bio, format="PNG")
        qimage = QImage.fromData(bio.getvalue())
        self.result_label.setPixmap(QPixmap.fromImage(qimage))

    def apply_preprocessing(self, image):
        brightness = self.brightness_slider.value() / 100.0
        contrast = self.contrast_slider.value() / 100.0
        sharpness = self.sharpness_slider.value() / 100.0

        image = ImageEnhance.Brightness(image).enhance(brightness)
        image = ImageEnhance.Contrast(image).enhance(contrast)
        image = ImageEnhance.Sharpness(image).enhance(sharpness)

        return image

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'PNG Files (*.png)')
        if file_path:
            self.result_label.pixmap().save(file_path, 'PNG')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BackgroundRemoverApp()
    window.show()
    sys.exit(app.exec())
