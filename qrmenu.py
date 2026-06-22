"""
Modern QR Menu Management System with Material Design Inspired UI

Features:
- Material Design inspired interface with animations
- Real-time updates via Firebase
- Advanced UI components with modern styling
- Responsive layout with dynamic scaling
- Interactive notifications and feedback
- Advanced order management system
- Multi-language support (Turkish/English)
- Light/Dark theme switching
- QR code generation for tables

Requirements:
- PyQt6
- PyQt6-WebEngine
- firebase-admin
- pyrebase4

Install dependencies:
    pip install PyQt6 PyQt6-WebEngine firebase-admin pyrebase4
"""
import re
import sys
import json
import qrcode
from io import BytesIO
import pyrebase
from datetime import datetime
from pathlib import Path
from PIL import Image  # Resim işleme için Pillow kütüphanesi
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QInputDialog,
    QHeaderView, QLabel, QFrame, QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect,
    QStackedWidget, QScrollArea, QToolButton, QMenu, QProgressBar, QToolBar,
    QSpinBox, QFileDialog, QMessageBox, QCheckBox, QRubberBand, QProgressDialog
)
from PyQt6.QtCore import (
    QUrl, QObject, pyqtSignal, Qt, QPropertyAnimation, QEasingCurve,
    QTimer, QSize, QPoint, QSettings, QBuffer, QRect
)
from PyQt6.QtGui import (
    QIcon, QFont, QPalette, QColor, QLinearGradient, QGradient,
    QPainter, QPainterPath, QBrush, QPen, QAction, QImage, QPixmap
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import firebase_admin
from firebase_admin import credentials, db, storage
from google.cloud import storage as cloud_storage
import os

# Application settings
APP_NAME = 'QR Menu Manager'
ORGANIZATION_NAME = 'QR Menu System'
DEFAULT_LANGUAGE = 'tr'  # Turkish by default

# Load translations
TRANSLATIONS = {
    'en': {
        'app_title': 'QR Menu Management Panel',
        'app_subtitle': 'Easily manage your menu and orders',
        'preview_tab': 'Preview',
        'menu_tab': 'Edit Menu',
        'orders_tab': 'Orders',
        'new_category': 'New Category',
        'new_item': 'New Item',
        'edit': 'Edit',
        'delete': 'Delete',
        'cancel': 'Cancel',
        'save': 'Save',
        'category': 'Category',
        'item_name': 'Item Name',
        'price': 'Price',
        'status': 'Status',
        'table': 'Table',
        'action': 'Action',
        'active_orders': 'Active Orders',
        'old_orders': 'Past Orders',
        'confirm': 'Confirm',
        'prepare': 'Prepare',
        'deliver': 'Deliver',
        'created_at': 'Created at',
        'updated_at': 'Updated at',
        'fill_all_fields': 'Please fill all fields',
        'invalid_price': 'Please enter a valid price',
        'dark_theme': 'Dark Theme',
        'light_theme': 'Light Theme',
        'language': 'Language',
        'refresh': 'Refresh',
        'table_management': 'Table Management',
        'generate_qr': 'Generate QR',
        'add_table': 'Add Table',
        'edit_table': 'Edit Table',
        'remove_table': 'Remove Table',
        'table_number': 'Table Number',
        'table_name': 'Table Name',
        'table_capacity': 'Capacity',
        'table_location': 'Location',
        'table_status': 'Status',
        'status_available': 'Available',
        'status_occupied': 'Occupied',
        'status_reserved': 'Reserved',
        'save_qr': 'Save QR Code',
        'qr_saved': 'QR Code saved successfully',
        'select_save_location': 'Select where to save QR code',
        'table_added': 'Table added successfully',
        'table_updated': 'Table updated successfully',
        'table_removed': 'Table removed successfully',
        'category_management': 'Category Management',
        'item_management': 'Item Management',
        'order_management': 'Order Management',
        'settings': 'Settings',
        'add_category': 'Add Category',
        'edit_category': 'Edit Category',
        'remove_category': 'Remove Category',
        'category_name': 'Category Name',
        'category_order': 'Display Order',
        'category_image': 'Category Image',
        'item_name': 'Item Name',
        'item_price': 'Price',
        'item_description': 'Description',
        'item_image': 'Item Image',
        'item_count': 'Item Count',
        'item_ingredients': 'Ingredients',
        'item_allergens': 'Allergens',
        'item_available': 'Available',
        'item_featured': 'Featured',
        'order_status': 'Order Status',
        'order_items': 'Items',
        'order_total': 'Total',
        'order_created': 'Created',
        'order_updated': 'Updated',
        'order_completed': 'Completed',
        'status_pending': 'Pending',
        'status_preparing': 'Preparing',
        'status_ready': 'Ready',
        'status_delivered': 'Delivered',
        'status_cancelled': 'Cancelled',
        'currency_symbol': 'Currency Symbol',
        'restaurant_name': 'Restaurant Name',
        'contact_info': 'Contact Information',
        'working_hours': 'Working Hours',
        'save_settings': 'Save Settings',
        'category_added': 'Category added successfully',
        'category_updated': 'Category updated successfully',
        'category_removed': 'Category removed successfully',
        'item_added': 'Item added successfully',
        'item_updated': 'Item updated successfully',
        'item_removed': 'Item removed successfully',
        'settings_saved': 'Settings saved successfully',
        'back': 'Back',
        'forward': 'Forward',
        'zoom_in': 'Zoom In',
        'zoom_out': 'Zoom Out',
        'zoom_reset': 'Reset Zoom',
        'waiting': 'Waiting',
        'preparing': 'Preparing',
        'ready': 'Ready',
        'delivered': 'Delivered',
        'add_item': 'Add Item',
        'edit_item': 'Edit Item',
        'remove_item': 'Remove Item',
        'generate_all_qr': 'Generate All QR',
        'qr_generation': 'QR Generation',
        'no_tables_found': 'No tables found in database!',
        'generating_qr_codes': 'Generating QR codes...',
        'qr_generation_success': 'QR codes successfully generated for {count} tables.\nCodes saved to \'qr_codes\' folder.',
    },
    'tr': {
        'app_title': 'QR Menü Yönetim Paneli',
        'app_subtitle': 'Menü ve siparişlerinizi kolayca yönetin',
        'preview_tab': 'Önizleme',
        'menu_tab': 'Menü Düzenle',
        'orders_tab': 'Siparişler',
        'new_category': 'Yeni Kategori',
        'new_item': 'Yeni Ürün',
        'edit': 'Düzenle',
        'delete': 'Sil',
        'cancel': 'İptal',
        'save': 'Kaydet',
        'category': 'Kategori',
        'item_name': 'Ürün Adı',
        'price': 'Fiyat',
        'status': 'Durum',
        'table': 'Masa',
        'action': 'İşlem',
        'active_orders': 'Aktif Siparişler',
        'old_orders': 'Eski Siparişler',
        'confirm': 'Onayla',
        'prepare': 'Hazırla',
        'deliver': 'Teslim Et',
        'created_at': 'Oluşturulma',
        'updated_at': 'Güncelleme',
        'fill_all_fields': 'Tüm alanları doldurunuz',
        'invalid_price': 'Geçerli bir fiyat giriniz',
        'dark_theme': 'Koyu Tema',
        'light_theme': 'Açık Tema',
        'language': 'Dil',
        'refresh': 'Yenile',
        'table_management': 'Masa Yönetimi',
        'generate_qr': 'QR Oluştur',
        'add_table': 'Masa Ekle',
        'edit_table': 'Masa Düzenle',
        'remove_table': 'Masa Sil',
        'table_number': 'Masa Numarası',
        'table_name': 'Masa Adı',
        'table_capacity': 'Kapasite',
        'table_location': 'Konum',
        'table_status': 'Durum',
        'status_available': 'Müsait',
        'status_occupied': 'Dolu',
        'status_reserved': 'Rezerve',
        'save_qr': 'QR Kodu Kaydet',
        'qr_saved': 'QR Kod başarıyla kaydedildi',
        'select_save_location': 'QR kodu kaydetmek için konum seçin',
        'table_added': 'Masa başarıyla eklendi',
        'table_updated': 'Masa başarıyla güncellendi',
        'table_removed': 'Masa başarıyla silindi',
        'category_management': 'Kategori Yönetimi',
        'item_management': 'Ürün Yönetimi',
        'order_management': 'Sipariş Yönetimi',
        'settings': 'Ayarlar',
        'add_category': 'Kategori Ekle',
        'edit_category': 'Kategori Düzenle',
        'remove_category': 'Kategori Sil',
        'category_name': 'Kategori Adı',
        'category_order': 'Görüntüleme Sırası',
        'item_count': 'Ürün Sayısı',
        'category_image': 'Kategori Görseli',
        'item_name': 'Ürün Adı',
        'item_price': 'Fiyat',
        'item_description': 'Açıklama',
        'item_image': 'Ürün Görseli',
        'item_ingredients': 'İçindekiler',
        'item_allergens': 'Alerjenler',
        'item_available': 'Mevcut',
        'item_featured': 'Öne Çıkan',
        'order_status': 'Sipariş Durumu',
        'order_items': 'Ürünler',
        'order_total': 'Toplam',
        'order_created': 'Oluşturulma',
        'order_updated': 'Güncelleme',
        'order_completed': 'Tamamlanma',
        'status_pending': 'Beklemede',
        'status_preparing': 'Hazırlanıyor',
        'status_ready': 'Hazır',
        'status_delivered': 'Teslim Edildi',
        'status_cancelled': 'İptal Edildi',
        'currency_symbol': 'Para Birimi',
        'restaurant_name': 'Restoran Adı',
        'contact_info': 'İletişim Bilgileri',
        'working_hours': 'Çalışma Saatleri',
        'save_settings': 'Ayarları Kaydet',
        'category_added': 'Kategori başarıyla eklendi',
        'category_updated': 'Kategori başarıyla güncellendi',
        'category_removed': 'Kategori başarıyla silindi',
        'item_added': 'Ürün başarıyla eklendi',
        'item_updated': 'Ürün başarıyla güncellendi',
        'item_removed': 'Ürün başarıyla silindi',
        'settings_saved': 'Ayarlar başarıyla kaydedildi',
        'back': 'Geri',
        'forward': 'İleri',
        'zoom_in': 'Yakınlaştır',
        'zoom_out': 'Uzaklaştır',
        'zoom_reset': 'Varsayılan Zoom',
        'waiting': 'Beklemede',
        'preparing': 'Hazırlanıyor',
        'ready': 'Hazır',
        'delivered': 'Teslim Edildi',
        'add_item': 'Ürün Ekle',
        'edit_item': 'Ürün Düzenle',
        'remove_item': 'Ürün Sil',
        'generate_all_qr': 'Tümünü Oluştur',
        'qr_generation': 'QR Kod Oluşturma',
        'no_tables_found': 'Veritabanında masa bulunamadı!',
        'generating_qr_codes': 'QR Kodları oluşturuluyor...',
        'qr_generation_success': 'Toplam {count} masa için QR kodları başarıyla oluşturuldu.\nKodlar \'qr_codes\' klasörüne kaydedildi.',
    }
}

# Color schemes
THEMES = {
    'dark': {
        'primary': '#2196F3',
        'primary_dark': '#1976D2',
        'primary_light': '#BBDEFB',
        'accent': '#FF4081',
        'accent_dark': '#F50057',
        'success': '#4CAF50',
        'warning': '#FFC107',
        'error': '#F44336',
        'surface': '#121212',
        'background': '#000000',
        'on_surface': '#FFFFFF',
        'on_surface_medium': 'rgba(255,255,255,0.74)',
        'on_surface_disabled': 'rgba(255,255,255,0.38)',
        'divider': 'rgba(255,255,255,0.12)'
    },
    'light': {
        'primary': '#2196F3',
        'primary_dark': '#1976D2',
        'primary_light': '#BBDEFB',
        'accent': '#FF4081',
        'accent_dark': '#F50057',
        'success': '#4CAF50',
        'warning': '#FFC107',
        'error': '#F44336',
        'surface': '#FFFFFF',
        'background': '#F5F5F5',
        'on_surface': '#000000',
        'on_surface_medium': 'rgba(0,0,0,0.74)',
        'on_surface_disabled': 'rgba(0,0,0,0.38)',
        'divider': 'rgba(0,0,0,0.12)'
    }
}

# Signals for thread-safe updates
class FirebaseSignalHandler(QObject):
    menu_changed = pyqtSignal()
    orders_changed = pyqtSignal()
    settings_changed = pyqtSignal(str, str)  # (key, value)

sig_handler = FirebaseSignalHandler()

class AppSettings:
    def __init__(self):
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        self.current_language = self.settings.value('language', DEFAULT_LANGUAGE)
        self.current_theme = self.settings.value('theme', 'dark')
    
    def get_text(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
    
    def get_theme(self):
        return THEMES[self.current_theme]
    
    def set_language(self, language):
        if language in TRANSLATIONS:
            self.current_language = language
            self.settings.setValue('language', language)
            sig_handler.settings_changed.emit('language', language)
    
    def set_theme(self, theme):
        if theme in THEMES:
            self.current_theme = theme
            self.settings.setValue('theme', theme)
            sig_handler.settings_changed.emit('theme', theme)
    
    def generate_stylesheet(self):
        colors = self.get_theme()
        return f"""
        QMainWindow, QDialog {{
            background-color: {colors['background']};
        }}
        
        QWidget {{
            color: {colors['on_surface']};
        }}
        
        QTabWidget::pane {{
            border: none;
            background-color: {colors['surface']};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: transparent;
            color: {colors['on_surface_medium']};
            padding: 12px 16px;
            margin-right: 4px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            color: {colors['primary']};
            border-bottom: 2px solid {colors['primary']};
        }}
        
        QTabBar::tab:hover:!selected {{
            color: {colors['on_surface']};
        }}
        
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary_dark']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['on_surface_disabled']};
        }}
        
        QPushButton#accent {{
            background-color: {colors['accent']};
        }}
        
        QPushButton#accent:hover {{
            background-color: {colors['accent_dark']};
        }}
        
        QPushButton#success {{
            background-color: {colors['success']};
        }}
        
        QPushButton#warning {{
            background-color: {colors['warning']};
        }}
        
        QPushButton#error {{
            background-color: {colors['error']};
        }}
        
        QTreeWidget {{
            background-color: {colors['surface']};
            border: none;
            border-radius: 8px;
            padding: 8px;
        }}
        
        QTreeWidget::item {{
            padding: 8px;
            margin: 2px 0;
            border-radius: 4px;
        }}
        
        QTreeWidget::item:selected {{
            background-color: rgba(33, 150, 243, 0.12);
            color: {colors['primary']};
        }}
        
        QTreeWidget::item:hover {{
            background-color: rgba(255, 255, 255, 0.08);
        }}
        
        QHeaderView::section {{
            background-color: {colors['surface']};
            color: {colors['on_surface_medium']};
            padding: 8px;
            border: none;
        }}
        
        QLineEdit, QComboBox {{
            background-color: {colors['surface']};
            color: {colors['on_surface']};
            border: 2px solid {colors['divider']};
            border-radius: 4px;
            padding: 8px;
            min-height: 20px;
        }}
        
        QLineEdit:focus, QComboBox:focus {{
            border: 2px solid {colors['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: url(down_arrow.png);
        }}
        
        QScrollBar:vertical {{
            border: none;
            background-color: {colors['surface']};
            width: 8px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['primary']};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QLabel#header {{
            color: {colors['on_surface']};
            font-size: 24px;
            font-weight: bold;
        }}
        
        QLabel#subheader {{
            color: {colors['on_surface_medium']};
            font-size: 16px;
        }}
        
        QFrame#card {{
            background-color: {colors['surface']};
            border-radius: 8px;
            padding: 16px;
        }}
        
        QProgressBar {{
            background-color: {colors['surface']};
            border: none;
            border-radius: 4px;
            height: 8px;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 4px;
        }}
        """

# Global settings instance
app_settings = AppSettings()

# Modern Color Palette
COLORS = {
    'primary': '#2196F3',      # Blue
    'primary_dark': '#1976D2',
    'primary_light': '#BBDEFB',
    'accent': '#FF4081',       # Pink
    'accent_dark': '#F50057',
    'success': '#4CAF50',      # Green
    'warning': '#FFC107',      # Amber
    'error': '#F44336',        # Red
    'surface': '#121212',      # Dark surface
    'background': '#000000',   # Dark background
    'on_surface': '#FFFFFF',   # White text
    'on_surface_medium': 'rgba(255,255,255,0.74)',
    'on_surface_disabled': 'rgba(255,255,255,0.38)',
    'divider': 'rgba(255,255,255,0.12)',
}

# Material Design Inspired StyleSheet
STYLE_SHEET = f"""
QMainWindow, QDialog {{
    background-color: {COLORS['background']};
}}

QWidget {{
    color: {COLORS['on_surface']};
}}

QTabWidget::pane {{
    border: none;
    background-color: {COLORS['surface']};
    border-radius: 8px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['on_surface_medium']};
    padding: 12px 16px;
    margin-right: 4px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    color: {COLORS['primary']};
    border-bottom: 2px solid {COLORS['primary']};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS['on_surface']};
}}

QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary']};
}}

QPushButton:disabled {{
    background-color: {COLORS['on_surface_disabled']};
}}

QPushButton#accent {{
    background-color: {COLORS['accent']};
}}

QPushButton#accent:hover {{
    background-color: {COLORS['accent_dark']};
}}

QPushButton#success {{
    background-color: {COLORS['success']};
}}

QPushButton#warning {{
    background-color: {COLORS['warning']};
}}

QPushButton#error {{
    background-color: {COLORS['error']};
}}

QTreeWidget {{
    background-color: {COLORS['surface']};
    border: none;
    border-radius: 8px;
    padding: 8px;
}}

QTreeWidget::item {{
    padding: 8px;
    margin: 2px 0;
    border-radius: 4px;
}}

QTreeWidget::item:selected {{
    background-color: rgba(33, 150, 243, 0.12);
    color: {COLORS['primary']};
}}

QTreeWidget::item:hover {{
    background-color: rgba(255, 255, 255, 0.08);
}}

QHeaderView::section {{
    background-color: {COLORS['surface']};
    color: {COLORS['on_surface_medium']};
    padding: 8px;
    border: none;
}}

QLineEdit, QComboBox {{
    background-color: {COLORS['surface']};
    color: {COLORS['on_surface']};
    border: 2px solid {COLORS['divider']};
    border-radius: 4px;
    padding: 8px;
    min-height: 20px;
}}

QLineEdit:focus, QComboBox:focus {{
    border: 2px solid {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: url(down_arrow.png);
}}

QScrollBar:vertical {{
    border: none;
    background-color: {COLORS['surface']};
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['primary']};
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QLabel#header {{
    color: {COLORS['on_surface']};
    font-size: 24px;
    font-weight: bold;
}}

QLabel#subheader {{
    color: {COLORS['on_surface_medium']};
    font-size: 16px;
}}

QFrame#card {{
    background-color: {COLORS['surface']};
    border-radius: 8px;
    padding: 16px;
}}

QProgressBar {{
    background-color: {COLORS['surface']};
    border: none;
    border-radius: 4px;
    height: 8px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 4px;
}}
"""

# Status styling with Material Design colors
STATUS_STYLES = {
    'Beklemede': {
        'color': COLORS['warning'],
        'background': 'rgba(255, 193, 7, 0.12)',
        'icon': '⏳'
    },
    'Hazırlanıyor': {
        'color': COLORS['primary'],
        'background': 'rgba(33, 150, 243, 0.12)',
        'icon': '👨‍🍳'
    },
    'Hazırlandı': {
        'color': COLORS['success'],
        'background': 'rgba(76, 175, 80, 0.12)',
        'icon': '✅'
    },
    'Teslim Edildi': {
        'color': COLORS['on_surface_disabled'],
        'background': 'rgba(255, 255, 255, 0.12)',
        'icon': '🏁'
    }
}

# Configuration
SERVICE_ACCOUNT_PATH = r'C:\Users\Muhammet AYYILDIZ\Desktop\qr\qr-menu-23-firebase-adminsdk-fbsvc-a0ca7f93ea.json'
FIREBASE_DB_URL = 'https://qr-menu-23-default-rtdb.firebaseio.com'
FIREBASE_STORAGE_BUCKET = 'qr-menu-23.firebasestorage.app'
PYREBASE_CONFIG = {
    "apiKey": "AIzaSyDGQJgSVpKPFn-zQEXrq_-y3uaqkLM8GJ8",
    "authDomain": "qr-menu-23.firebaseapp.com",
    "databaseURL": FIREBASE_DB_URL,
    "storageBucket": FIREBASE_STORAGE_BUCKET,
    "serviceAccount": SERVICE_ACCOUNT_PATH
}
GITHUB_MENU_URL = 'https://muhammetayldz.github.io/qr/'

# Image handling utilities
def process_image_for_upload(file_path, target_type='item'):
    """
    Resmi işleyip upload için hazırlar
    target_type: 'item' veya 'category' olabilir
    Returns: Geçici dosya yolu
    """
    try:
        # Hedef boyutlar ve oranlar
        if target_type == 'item':
            # Ürün resimleri için 16:9 oranında
            TARGET_WIDTH = 800
            TARGET_HEIGHT = 450  # 16:9 oranı
            MOBILE_WIDTH = 360
            MOBILE_HEIGHT = 203  # 16:9 oranı korunuyor
        else:  # category
            # Kategori resimleri için 16:9 oranında
            TARGET_WIDTH = 1200
            TARGET_HEIGHT = 675  # 16:9 oranı
            MOBILE_WIDTH = 360
            MOBILE_HEIGHT = 203  # 16:9 oranı korunuyor
        
        # Resmi aç
        with Image.open(file_path) as img:
            # RGBA modundaysa RGB'ye çevir
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # En boy oranını hesapla
            width, height = img.size
            aspect_ratio = width / height
            target_ratio = 16/9  # Sabit 16:9 oranı
            
            # Kırpma koordinatlarını hesapla
            if aspect_ratio > target_ratio:
                # Resim çok geniş, yanlardan kırp
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                img = img.crop((left, 0, left + new_width, height))
            else:
                # Resim çok uzun, üst ve alttan kırp
                new_height = int(width / target_ratio)
                top = (height - new_height) // 2
                img = img.crop((0, top, width, top + new_height))
            
            # Masaüstü versiyonu için yeniden boyutlandır
            desktop_img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            
            # Mobil versiyonu için yeniden boyutlandır
            mobile_img = img.resize((MOBILE_WIDTH, MOBILE_HEIGHT), Image.Resampling.LANCZOS)
            
            # Her iki versiyonu da optimize et
            temp_path = f"{file_path}.processed.jpg"
            desktop_img.save(temp_path, 'JPEG', quality=85, optimize=True)
            
            # Mobil versiyonu farklı bir dosyaya kaydet
            mobile_path = f"{file_path}.mobile.jpg"
            mobile_img.save(mobile_path, 'JPEG', quality=85, optimize=True)
            
            return temp_path
            
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

def upload_image_to_firebase(file_path, destination):
    try:
        print(f"Uploading image from {file_path} to {destination}")
        
        if not os.path.exists(file_path):
            print(f"Error: File does not exist at {file_path}")
            return None

        # Resmi işle
        target_type = 'category' if 'categories/' in destination else 'item'
        processed_path = process_image_for_upload(file_path, target_type)
        if not processed_path:
            return None

        try:
            # Get bucket reference
            bucket = storage.bucket()
            
            # Create blob and upload processed file
            blob = bucket.blob(destination)
            blob.upload_from_filename(processed_path)
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Get public URL - Firebase Storage URL formatını kullan
            url = f"https://firebasestorage.googleapis.com/v0/b/{FIREBASE_STORAGE_BUCKET}/o/{destination.replace('/', '%2F')}?alt=media"
            print(f"Upload successful. URL: {url}")
            return url
            
        finally:
            # Geçici dosyayı temizle
            if processed_path and os.path.exists(processed_path):
                try:
                    os.remove(processed_path)
                except:
                    pass
        
    except Exception as e:
        print(f"Error in upload_image_to_firebase: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def select_image_file():
    file_name, _ = QFileDialog.getOpenFileName(
        None,
        "Resim Seç",
        "",
        "Image Files (*.png *.jpg *.jpeg)"
    )
    if not file_name:
        return None
        
    # Resim boyutlarını kontrol et ve kullanıcıyı bilgilendir
    try:
        with Image.open(file_name) as img:
            width, height = img.size
            aspect_ratio = width / height
            
            if abs(aspect_ratio - 16/9) > 0.1:  # 16:9'dan farklıysa
                QMessageBox.information(
                    None,
                    "Resim Oranı",
                    "Seçtiğiniz resim otomatik olarak 16:9 oranına getirilecek ve gerekirse kırpılacaktır. "
                    "En iyi sonuç için 16:9 oranında resimler yüklemeniz önerilir."
                )
    except:
        pass
        
    return file_name

class MaterialLineEdit(QLineEdit):
    def __init__(self, placeholder='', parent=None):
        super().__init__(parent)
        self.setPlaceholderText('')  # Clear default placeholder
        self.setMinimumHeight(45)  # Adjusted height
        self.setProperty('class', 'material')
        
        # Create and setup the floating label
        self.label = QLabel(placeholder, self)
        self.label.setStyleSheet(f"""
            color: {COLORS["on_surface_medium"]};
            font-size: 14px;
            background: transparent;
        """)
        self.label.move(12, 12)  # Initial position
        
        # Set base style
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['divider']};
                border-radius: 4px;
                padding: 8px 12px;
                padding-top: 12px;
                color: {COLORS['on_surface']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        
        # Animation setup
        self.animation = QPropertyAnimation(self.label, b'pos')
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.setDuration(200)
        
        # Connect signals
        self.textChanged.connect(self._handle_text_changed)
        self.focusInEvent = self._focus_in
        self.focusOutEvent = self._focus_out
    
    def _handle_text_changed(self, text):
        if text and not self.label.property('floating'):
            self._float_label()
        elif not text and self.label.property('floating'):
            self._sink_label()
    
    def _focus_in(self, event):
        if not self.label.property('floating'):
            self._float_label()
        super().focusInEvent(event)
    
    def _focus_out(self, event):
        if not self.text() and self.label.property('floating'):
            self._sink_label()
        super().focusOutEvent(event)
    
    def _float_label(self):
        self.animation.setStartValue(self.label.pos())
        self.animation.setEndValue(QPoint(12, 4))  # Adjusted float position
        self.label.setStyleSheet(f"""
            color: {COLORS['primary']};
            font-size: 12px;
            background: transparent;
        """)
        self.label.setProperty('floating', True)
        self.animation.start()
    
    def _sink_label(self):
        self.animation.setStartValue(self.label.pos())
        self.animation.setEndValue(QPoint(12, 12))  # Adjusted sink position
        self.label.setStyleSheet(f"""
            color: {COLORS['on_surface_medium']};
            font-size: 14px;
            background: transparent;
        """)
        self.label.setProperty('floating', False)
        self.animation.start()

class MaterialDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName('header')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)
        
        # Content frame
        self.content = QFrame()
        self.content.setObjectName('card')
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(16)
        self.main_layout.addWidget(self.content)
        
        # Button container
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setSpacing(8)
        self.button_layout.addStretch()
        self.main_layout.addWidget(self.button_container)
        
        # Progress bar for loading states
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()
        self.main_layout.addWidget(self.progress)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet(f'color: {COLORS["error"]}')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        self.main_layout.addWidget(self.error_label)

class AddItemDialog(MaterialDialog):
    def __init__(self, db_ref):
        super().__init__('Yeni Ürün Ekle')
        self.db_ref = db_ref
        
        # Mevcut kategorileri al
        menu = self.db_ref.child('menu').get() or {}
        categories = []
        self.category_map = {}  # Kategori adı -> kategori ID eşleşmesi
        
        for cat_id, cat_data in menu.items():
            if isinstance(cat_data, dict) and 'name' in cat_data:
                categories.append(cat_data['name'])
                self.category_map[cat_data['name']] = cat_id
        
        # Category selection
        self.cat_combo = QComboBox()
        self.cat_combo.addItems(sorted(categories))  # Kategorileri alfabetik sırala
        self.cat_combo.setMinimumHeight(45)
        self.content_layout.addWidget(QLabel('Kategori'))
        self.content_layout.addWidget(self.cat_combo)
        
        # Name input
        self.name_edit = MaterialLineEdit('Ürün Adı')
        self.content_layout.addWidget(self.name_edit)
        
        # Price input
        self.price_edit = MaterialLineEdit('Fiyat (TL)')
        self.content_layout.addWidget(self.price_edit)
        
        # Description input
        self.desc_edit = MaterialLineEdit('Açıklama')
        self.content_layout.addWidget(self.desc_edit)
        
        # Buttons
        cancel_btn = QPushButton('İptal')
        cancel_btn.setObjectName('error')
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton('Kaydet')
        save_btn.setObjectName('success')
        save_btn.clicked.connect(self.accept)
        
        self.button_layout.addWidget(cancel_btn)
        self.button_layout.addWidget(save_btn)

    def accept(self):
        cat = self.cat_combo.currentText().strip()
        name = self.name_edit.text().strip()
        price = self.price_edit.text().strip()
        description = self.desc_edit.text().strip()
        
        if not all([cat, name, price]):
            self.error_label.setText('Tüm alanları doldurunuz!')
            self.error_label.show()
            return
        
        try:
            self.progress.show()
            price_float = float(price)
            
            # Kategori ID'sini al
            category_id = self.category_map[cat]
            
            # Yeni ürün ID'si oluştur
            item_id = name.lower().replace(' ', '_').replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
            
            # Yeni ürünü ekle
            self.db_ref.child('menu').child(category_id).child('items').child(item_id).set({
                'name': name,
                'price': price_float,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'available': True,
                'featured': False
            })
            super().accept()
        except ValueError:
            self.error_label.setText('Geçerli bir fiyat giriniz!')
            self.error_label.show()
        finally:
            self.progress.hide()

class EditItemDialog(MaterialDialog):
    def __init__(self, db_ref, category, old_name, old_price):
        super().__init__(f'"{old_name}" Düzenle')
        self.db_ref = db_ref
        self.category = category
        self.old_name = old_name
        
        # Category info
        cat_label = QLabel(f'Kategori: {category}')
        cat_label.setObjectName('subheader')
        self.content_layout.addWidget(cat_label)
        
        # Name input
        self.name_edit = MaterialLineEdit('Yeni Ürün Adı')
        self.name_edit.setText(old_name)
        self.content_layout.addWidget(self.name_edit)
        
        # Price input
        self.price_edit = MaterialLineEdit('Yeni Fiyat (TL)')
        self.price_edit.setText(str(old_price))
        self.content_layout.addWidget(self.price_edit)
        
        # Buttons
        delete_btn = QPushButton('Sil')
        delete_btn.setObjectName('error')
        delete_btn.clicked.connect(self._delete_item)
        
        cancel_btn = QPushButton('İptal')
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton('Kaydet')
        save_btn.setObjectName('success')
        save_btn.clicked.connect(self.accept)
        
        self.button_layout.addWidget(delete_btn)
        self.button_layout.addWidget(cancel_btn)
        self.button_layout.addWidget(save_btn)

    def _delete_item(self):
        self.progress.show()
        try:
            self.db_ref.child('menu').child(self.category).child(self.old_name).delete()
            super().accept()
        finally:
            self.progress.hide()

    def accept(self):
        new_name = self.name_edit.text().strip()
        new_price = self.price_edit.text().strip()
        
        if not all([new_name, new_price]):
            self.error_label.setText('Tüm alanları doldurunuz!')
            self.error_label.show()
            return
        
        try:
            self.progress.show()
            price_float = float(new_price)
            cat_ref = self.db_ref.child('menu').child(self.category)
            
            if new_name != self.old_name:
                # Move item to new name
                data = cat_ref.child(self.old_name).get() or {}
                cat_ref.child(new_name).set({
                    'name': new_name,
                    'price': price_float,
                    'updated_at': datetime.now().isoformat(),
                    'created_at': data.get('created_at', datetime.now().isoformat())
                })
                cat_ref.child(self.old_name).delete()
            else:
                # Update existing item
                cat_ref.child(self.old_name).update({
                    'price': price_float,
                    'updated_at': datetime.now().isoformat()
                })
            
            super().accept()
        except ValueError:
            self.error_label.setText('Geçerli bir fiyat giriniz!')
            self.error_label.show()
        finally:
            self.progress.hide()

class StatusBadge(QFrame):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)  # Yüksekliği azalttık
        self.setFixedWidth(140)  # Genişliği sabitledik
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)
        
        style = STATUS_STYLES.get(status, {
            'color': COLORS['on_surface_disabled'],
            'background': 'rgba(255,255,255,0.12)',
            'icon': '❓'
        })
        
        # Icon
        icon = QLabel(style['icon'])
        icon.setFixedWidth(20)
        layout.addWidget(icon)
        
        # Text
        text = QLabel(status)
        text.setStyleSheet(f"""
            color: {style['color']};
            font-weight: bold;
            font-size: 13px;
        """)
        layout.addWidget(text)
        
        # Set frame style
        self.setStyleSheet(f"""
            StatusBadge {{
                background-color: {style['background']};
                border-radius: 16px;
                border: 1px solid {style['color']};
            }}
        """)

    def _advance_order(self, order_id):
        order_ref = self.db_ref.child('orders').child('active').child(order_id)
        order = order_ref.get() or {}
        current_status = order.get('status', 'Beklemede')
        
        next_status = {
            'Beklemede': 'Hazırlanıyor',
            'Hazırlanıyor': 'Hazırlandı',
            'Hazırlandı': 'Teslim Edildi'
        }.get(current_status)
        
        if next_status == 'Teslim Edildi':
            # Move to history
            history_ref = self.db_ref.child('orders').child('history')
            order['status'] = next_status
            order['completed_at'] = datetime.now().isoformat()
            history_ref.push(order)
            # Remove from active orders
            order_ref.delete()
        else:
            # Update status
            order_ref.update({
                'status': next_status,
                'updated_at': datetime.now().isoformat()
            })
        
        # Buton container'ı güncelle
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(4, 0, 4, 0)
        btn_layout.setSpacing(0)
        
        # Create button with updated style
        btn = QPushButton(app_settings.get_text(next_status.lower()))
        btn.setObjectName('success' if next_status == 'Hazırlandı' else 'primary')
        btn.setFixedSize(110, 32)  # Buton boyutunu küçülttük
        
        # Style the button
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success'] if next_status == 'Hazırlandı' else COLORS['primary']};
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 16px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success'] if next_status == 'Hazırlandı' else COLORS['primary_dark']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['success'] if next_status == 'Hazırlandı' else COLORS['primary']};
                padding: 6px 4px 2px 4px;
            }}
        """)
        
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        
        return btn_container

class MaterialCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('card')
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

class TableDialog(MaterialDialog):
    def __init__(self, parent=None, table_data=None):
        super().__init__(
            app_settings.get_text('edit_table') if table_data else app_settings.get_text('add_table')
        )
        self.table_data = table_data or {}
        
        # Table number
        self.number_input = QSpinBox()
        self.number_input.setMinimum(1)
        self.number_input.setMaximum(999)
        self.number_input.setValue(int(table_data.get('number', 1)) if table_data else 1)
        self.content_layout.addWidget(QLabel(app_settings.get_text('table_number')))
        self.content_layout.addWidget(self.number_input)
        
        # Table name
        self.name_input = MaterialLineEdit(app_settings.get_text('table_name'))
        if table_data:
            self.name_input.setText(table_data.get('name', ''))
        self.content_layout.addWidget(self.name_input)
        
        # Capacity
        self.capacity_input = QSpinBox()
        self.capacity_input.setMinimum(1)
        self.capacity_input.setMaximum(50)
        self.capacity_input.setValue(int(table_data.get('capacity', 4)) if table_data else 4)
        self.content_layout.addWidget(QLabel(app_settings.get_text('table_capacity')))
        self.content_layout.addWidget(self.capacity_input)
        
        # Location
        self.location_input = MaterialLineEdit(app_settings.get_text('table_location'))
        if table_data:
            self.location_input.setText(table_data.get('location', ''))
        self.content_layout.addWidget(self.location_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            app_settings.get_text('status_available'),
            app_settings.get_text('status_occupied'),
            app_settings.get_text('status_reserved')
        ])
        if table_data and 'status' in table_data:
            index = {
                'available': 0,
                'occupied': 1,
                'reserved': 2
            }.get(table_data['status'], 0)
            self.status_combo.setCurrentIndex(index)
        self.content_layout.addWidget(QLabel(app_settings.get_text('table_status')))
        self.content_layout.addWidget(self.status_combo)
        
        # Buttons
        cancel_btn = QPushButton(app_settings.get_text('cancel'))
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton(app_settings.get_text('save'))
        save_btn.setObjectName('success')
        save_btn.clicked.connect(self.accept)
        
        self.button_layout.addWidget(cancel_btn)
        self.button_layout.addWidget(save_btn)
    
    def get_table_data(self):
        status_map = {
            app_settings.get_text('status_available'): 'available',
            app_settings.get_text('status_occupied'): 'occupied',
            app_settings.get_text('status_reserved'): 'reserved'
        }
        return {
            'number': self.number_input.value(),
            'name': self.name_input.text().strip(),
            'capacity': self.capacity_input.value(),
            'location': self.location_input.text().strip(),
            'status': status_map[self.status_combo.currentText()],
            'qr_url': f"{GITHUB_MENU_URL}?table={self.number_input.value()}"
        }

class QRCodeDialog(MaterialDialog):
    def __init__(self, table_number, parent=None):
        super().__init__(f"QR Code - {app_settings.get_text('table')} {table_number}")
        self.table_number = table_number
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"{GITHUB_MENU_URL}?table={table_number}")
        qr.make(fit=True)
        
        # Convert to QPixmap
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qimage = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qimage)
        
        # Display QR code
        qr_label = QLabel()
        qr_label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(qr_label)
        
        # Save button
        save_btn = QPushButton(app_settings.get_text('save_qr'))
        save_btn.setObjectName('success')
        save_btn.clicked.connect(self.save_qr)
        
        close_btn = QPushButton(app_settings.get_text('cancel'))
        close_btn.clicked.connect(self.reject)
        
        self.button_layout.addWidget(close_btn)
        self.button_layout.addWidget(save_btn)
        
        self.qr_image = img
    
    def save_qr(self):
        file_name = f"table_{self.table_number}_qr.png"
        path, _ = QFileDialog.getSaveFileName(
            self,
            app_settings.get_text('select_save_location'),
            file_name,
            "PNG Files (*.png)"
        )
        if path:
            self.qr_image.save(path)
            QMessageBox.information(
                self,
                app_settings.get_text('save_qr'),
                app_settings.get_text('qr_saved')
            )

class TableManagementTab(QWidget):
    def __init__(self, db_ref, parent=None):
        super().__init__(parent)
        self.db_ref = db_ref
        
        # Initialize Pyrebase
        pb = pyrebase.initialize_app(PYREBASE_CONFIG)
        self.pb_db = pb.database()
        
        # Store buttons for language updates
        self.buttons = []
        
        # Setup UI
        self._init_ui()
        
        # Load initial data
        self.load_tables()
        
        # Setup Firebase listener
        self.pb_db.child('tables').stream(self.on_table_change)
        
        # Connect to settings changes
        sig_handler.settings_changed.connect(self._handle_settings_change)
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(20)
        
        # Category list card
        cat_card = MaterialCard()
        cat_layout = QVBoxLayout(cat_card)
        cat_layout.setContentsMargins(20, 20, 20, 20)
        
        # Category tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            app_settings.get_text('table_number'),
            app_settings.get_text('table_name'),
            app_settings.get_text('table_capacity'),
            app_settings.get_text('table_location'),
            app_settings.get_text('table_status')
        ])
        self.tree.setAlternatingRowColors(True)
        
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        cat_layout.addWidget(self.tree)
        
        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(12)
        
        buttons = [
            ('add_table', self.add_table, 'success'),
            ('edit_table', self.edit_table, 'primary'),
            ('remove_table', self.remove_table, 'error'),
            ('generate_qr', self.generate_qr, 'accent'),
            ('generate_all_qr', self.generate_all_qr, 'primary')  # Yeni buton eklendi
        ]
        
        for key, func, style in buttons:
            btn = QPushButton(app_settings.get_text(key))
            btn.setObjectName(style)
            btn.setFixedWidth(130)
            btn.setMinimumHeight(40)
            btn.clicked.connect(func)
            btn.setProperty('text_key', key)  # Store text key for updates
            button_layout.addWidget(btn)
            self.buttons.append(btn)
        
        cat_layout.addWidget(button_container)
        layout.addWidget(cat_card)

    def generate_all_qr(self):
        """Tüm masalar için QR kodları oluştur"""
        # QR codes klasörünü oluştur
        if not os.path.exists('qr_codes'):
            os.makedirs('qr_codes')
        
        # Tüm masaları al
        tables = self.db_ref.child('tables').get() or {}
        
        if not tables:
            QMessageBox.warning(
                self,
                app_settings.get_text('qr_generation'),
                app_settings.get_text('no_tables_found')
            )
            return
        
        progress = QProgressDialog(
            app_settings.get_text('generating_qr_codes'),
            None, 0, len(tables), self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        success_count = 0
        for table_id, table_data in tables.items():
            table_number = table_data.get('number')
            if not table_number:
                continue
            
            try:
                # QR kodu oluştur
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                
                # Menü URL'sini ekle
                qr.add_data(f"{GITHUB_MENU_URL}?table={table_number}")
                qr.make(fit=True)
                
                # QR görselini oluştur
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                # QR kodunu kaydet
                file_name = f"qr_codes/table_{table_number}_qr.png"
                qr_image.save(file_name)
                
                # Firebase'de QR URL'sini güncelle
                self.db_ref.child('tables').child(table_id).update({
                    'qr_url': f"table_{table_number}_qr.png"
                })
                
                success_count += 1
                
            except Exception as e:
                print(f"Error generating QR for table {table_number}: {str(e)}")
            
            progress.setValue(progress.value() + 1)
        
        progress.close()
        
        QMessageBox.information(
            self,
            app_settings.get_text('qr_generation'),
            app_settings.get_text('qr_generation_success').format(count=success_count)
        )
        
        # Dosya gezginini aç
        os.startfile('qr_codes') if os.name == 'nt' else os.system('xdg-open qr_codes')

    def _handle_settings_change(self, key, value):
        if key == 'language':
            # Update button texts
            for btn in self.buttons:
                text_key = btn.property('text_key')
                if text_key:
                    btn.setText(app_settings.get_text(text_key))
            
            # Update tree headers
            self.tree.setHeaderLabels([
                app_settings.get_text('table_number'),
                app_settings.get_text('table_name'),
                app_settings.get_text('table_capacity'),
                app_settings.get_text('table_location'),
                app_settings.get_text('table_status')
            ])

    def on_table_change(self, message):
        # Ensure we're on the main thread when updating UI
        QTimer.singleShot(0, self.load_tables)
    
    def load_tables(self):
        self.tree.clear()
        tables = self.db_ref.child('tables').get() or {}
        
        # Convert to list and sort by table number
        table_list = []
        for table_id, table_data in tables.items():
            if isinstance(table_data, dict):
                table_data['id'] = table_id
                table_list.append(table_data)
        
        table_list.sort(key=lambda x: x.get('number', 0))
        
        status_map = {
            'available': app_settings.get_text('status_available'),
            'occupied': app_settings.get_text('status_occupied'),
            'reserved': app_settings.get_text('status_reserved')
        }
        
        for table_data in table_list:
            item = QTreeWidgetItem([
                str(table_data.get('number', '')),
                table_data.get('name', ''),
                str(table_data.get('capacity', '')),
                table_data.get('location', ''),
                status_map.get(table_data.get('status', 'available'), 
                             app_settings.get_text('status_available'))
            ])
            
            # Set status color
            status_colors = {
                'available': COLORS['success'],
                'occupied': COLORS['error'],
                'reserved': COLORS['warning']
            }
            status_color = status_colors.get(table_data.get('status', 'available'), COLORS['success'])
            item.setForeground(4, QColor(status_color))
            
            # Store table ID in item data
            item.setData(0, Qt.ItemDataRole.UserRole, table_data['id'])
            
            self.tree.addTopLevelItem(item)
    
    def add_table(self):
        dialog = TableDialog(self)
        if dialog.exec():
            table_data = dialog.get_table_data()
            # Generate proper table ID
            table_id = f"table{table_data['number']}"
            self.db_ref.child('tables').child(table_id).set(table_data)
            
            # Generate QR code for new table
            self.generate_qr_for_table(table_data['number'])
            
            QMessageBox.information(
                self,
                app_settings.get_text('add_table'),
                app_settings.get_text('table_added')
            )
    
    def edit_table(self):
        current = self.tree.currentItem()
        if not current:
            return
        
        table_id = current.data(0, Qt.ItemDataRole.UserRole)
        table_data = self.db_ref.child('tables').child(table_id).get()
        
        if table_data:
            dialog = TableDialog(self, table_data)
            if dialog.exec():
                new_data = dialog.get_table_data()
                self.db_ref.child('tables').child(table_id).update(new_data)
                
                # Regenerate QR code if table number changed
                if new_data['number'] != table_data.get('number'):
                    self.generate_qr_for_table(new_data['number'])
                
                QMessageBox.information(
                    self,
                    app_settings.get_text('edit_table'),
                    app_settings.get_text('table_updated')
                )
    
    def remove_table(self):
        current = self.tree.currentItem()
        if not current:
            return
        
        table_id = current.data(0, Qt.ItemDataRole.UserRole)
        table_number = current.text(0)
        
        reply = QMessageBox.question(
            self,
            app_settings.get_text('remove_table'),
            f"Masa {table_number}'yi silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_ref.child('tables').child(table_id).delete()
            
            # Remove QR code file if exists
            qr_file = f"qr_codes/table_{table_number}_qr.png"
            if os.path.exists(qr_file):
                os.remove(qr_file)
            
            QMessageBox.information(
                self,
                app_settings.get_text('remove_table'),
                app_settings.get_text('table_removed')
            )
    
    def generate_qr(self):
        current = self.tree.currentItem()
        if not current:
            return
        
        table_number = int(current.text(0))
        self.generate_qr_for_table(table_number)
        
        QMessageBox.information(
            self,
            app_settings.get_text('generate_qr'),
            f"Masa {table_number} için QR kod oluşturuldu"
        )
    
    def generate_qr_for_table(self, table_number):
        # Create QR codes directory if it doesn't exist
        if not os.path.exists('qr_codes'):
            os.makedirs('qr_codes')
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add menu URL with table parameter
        qr.add_data(f"https://muhammetayldz.github.io/qr/?table={table_number}")
        qr.make(fit=True)
        
        # Create QR image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        file_name = f"qr_codes/table_{table_number}_qr.png"
        qr_image.save(file_name)
        
        # Show QR code dialog
        dialog = QRCodeDialog(table_number, self)
        dialog.exec()

class CategoryDialog(MaterialDialog):
    def __init__(self, parent=None, category_data=None):
        super().__init__(
            app_settings.get_text('edit_category') if category_data else app_settings.get_text('add_category')
        )
        self.category_data = category_data or {}
        self.selected_image = None
        
        # Category name
        self.name_input = MaterialLineEdit(app_settings.get_text('category_name'))
        if category_data:
            self.name_input.setText(category_data.get('name', ''))
        self.content_layout.addWidget(self.name_input)
        
        # Display order
        self.order_input = QSpinBox()
        self.order_input.setMinimum(1)
        self.order_input.setMaximum(999)
        self.order_input.setValue(int(category_data.get('order', 1)) if category_data else 1)
        self.content_layout.addWidget(QLabel(app_settings.get_text('category_order')))
        self.content_layout.addWidget(self.order_input)
        
        # Image selection
        image_container = QWidget()
        image_layout = QHBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(100, 100)
        self.image_preview.setStyleSheet("border: 1px solid gray; border-radius: 4px;")
        if category_data and category_data.get('image'):
            # TODO: Load and display existing image
            self.image_preview.setText("Mevcut\nGörsel")
        else:
            self.image_preview.setText("Görsel\nYok")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        select_btn = QPushButton("Görsel Seç")
        select_btn.clicked.connect(self._select_image)
        
        image_layout.addWidget(self.image_preview)
        image_layout.addWidget(select_btn)
        image_layout.addStretch()
        
        self.content_layout.addWidget(QLabel(app_settings.get_text('category_image')))
        self.content_layout.addWidget(image_container)
        
        # Buttons
        cancel_btn = QPushButton(app_settings.get_text('cancel'))
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton(app_settings.get_text('save'))
        save_btn.setObjectName('success')
        save_btn.clicked.connect(self.accept)
        
        self.button_layout.addWidget(cancel_btn)
        self.button_layout.addWidget(save_btn)
    
    def _select_image(self):
        file_path = select_image_file()
        if file_path:
            self.selected_image = file_path
            pixmap = QPixmap(file_path)
            self.image_preview.setPixmap(pixmap.scaled(
                100, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
    
    def get_category_data(self):
        data = {
            'name': self.name_input.text().strip(),
            'order': self.order_input.value()
        }
        
        if self.selected_image:
            try:
                # Upload image and get URL
                image_path = f"categories/{data['name'].lower().replace(' ', '_')}.jpg"
                image_url = upload_image_to_firebase(self.selected_image, image_path)
                if image_url:
                    data['image'] = image_url
                    data['picture'] = image_url  # Add picture URL
            except Exception as e:
                print(f"Error uploading category image: {e}")
        
        return data

class ItemDialog(MaterialDialog):
    def __init__(self, db_ref, parent=None, item_data=None):
        super().__init__(
            app_settings.get_text('edit_item') if item_data else app_settings.get_text('add_item')
        )
        self.db_ref = db_ref
        self.item_data = item_data or {}
        self.selected_image = None
        
        # Mevcut kategorileri al
        menu = self.db_ref.child('menu').get() or {}
        categories = []
        self.category_map = {}  # Kategori adı -> kategori ID eşleşmesi
        current_category = None
        
        for cat_id, cat_data in menu.items():
            if isinstance(cat_data, dict) and 'name' in cat_data:
                categories.append(cat_data['name'])
                self.category_map[cat_data['name']] = cat_id
                
                # Düzenlenen ürünün kategorisini bul
                if item_data:
                    items = cat_data.get('items', {})
                    for item_id, item in items.items():
                        if isinstance(item, dict) and item.get('name') == item_data.get('name'):
                            current_category = cat_data['name']
        
        # Category selection
        self.cat_combo = QComboBox()
        self.cat_combo.addItems(sorted(categories))  # Kategorileri alfabetik sırala
        if current_category:
            self.cat_combo.setCurrentText(current_category)
        self.cat_combo.setMinimumHeight(45)
        self.content_layout.addWidget(QLabel(app_settings.get_text('category')))
        self.content_layout.addWidget(self.cat_combo)
        
        # Item name
        self.name_input = MaterialLineEdit(app_settings.get_text('item_name'))
        if item_data:
            self.name_input.setText(item_data.get('name', ''))
        self.content_layout.addWidget(self.name_input)
        
        # Price
        self.price_input = MaterialLineEdit(app_settings.get_text('item_price'))
        if item_data:
            self.price_input.setText(str(item_data.get('price', '')))
        self.content_layout.addWidget(self.price_input)
        
        # Description
        self.desc_input = MaterialLineEdit(app_settings.get_text('item_description'))
        if item_data:
            self.desc_input.setText(item_data.get('description', ''))
        self.content_layout.addWidget(self.desc_input)
        
        # Image selection
        image_container = QWidget()
        image_layout = QHBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(100, 100)
        self.image_preview.setStyleSheet("border: 1px solid gray; border-radius: 4px;")
        if item_data and item_data.get('image'):
            # TODO: Load and display existing image
            self.image_preview.setText("Mevcut\nGörsel")
        else:
            self.image_preview.setText("Görsel\nYok")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        select_btn = QPushButton("Görsel Seç")
        select_btn.clicked.connect(self._select_image)
        
        image_layout.addWidget(self.image_preview)
        image_layout.addWidget(select_btn)
        image_layout.addStretch()
        
        self.content_layout.addWidget(QLabel(app_settings.get_text('item_image')))
        self.content_layout.addWidget(image_container)
        
        # Ingredients
        self.ingredients_input = MaterialLineEdit(app_settings.get_text('item_ingredients'))
        if item_data:
            self.ingredients_input.setText(','.join(item_data.get('ingredients', [])))
        self.content_layout.addWidget(self.ingredients_input)
        
        # Allergens
        self.allergens_input = MaterialLineEdit(app_settings.get_text('item_allergens'))
        if item_data:
            self.allergens_input.setText(','.join(item_data.get('allergens', [])))
        self.content_layout.addWidget(self.allergens_input)
        
        # Available
        self.available_check = QCheckBox(app_settings.get_text('item_available'))
        self.available_check.setChecked(item_data.get('available', True) if item_data else True)
        self.content_layout.addWidget(self.available_check)
        
        # Featured
        self.featured_check = QCheckBox(app_settings.get_text('item_featured'))
        self.featured_check.setChecked(item_data.get('featured', False) if item_data else False)
        self.content_layout.addWidget(self.featured_check)
        
        # Buttons
        cancel_btn = QPushButton(app_settings.get_text('cancel'))
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton(app_settings.get_text('save'))
        save_btn.setObjectName('success')
        save_btn.clicked.connect(self.accept)
        
        self.button_layout.addWidget(cancel_btn)
        self.button_layout.addWidget(save_btn)
    
    def _select_image(self):
        file_path = select_image_file()
        if file_path:
            self.selected_image = file_path
            pixmap = QPixmap(file_path)
            self.image_preview.setPixmap(pixmap.scaled(
                100, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
    
    def get_item_data(self):
        cat = self.cat_combo.currentText().strip()
        category_id = self.category_map[cat]
        
        data = {
            'name': self.name_input.text().strip(),
            'price': float(self.price_input.text().strip() or 0),
            'description': self.desc_input.text().strip(),
            'ingredients': [i.strip() for i in self.ingredients_input.text().split(',') if i.strip()],
            'allergens': [a.strip() for a in self.allergens_input.text().split(',') if a.strip()],
            'available': self.available_check.isChecked(),
            'featured': self.featured_check.isChecked(),
            'updated_at': datetime.now().isoformat(),
            'category_id': category_id
        }
        
        # Eğer düzenleme modundaysa ve yeni resim seçilmediyse, eski resmi koru
        if self.item_data and self.item_data.get('image') and not self.selected_image:
            data['image'] = self.item_data['image']
            if self.item_data.get('picture'):
                data['picture'] = self.item_data['picture']
        
        # Yeni resim seçildiyse
        if self.selected_image:
            try:
                # Önce eski resmi storage'dan sil (eğer varsa)
                if self.item_data and self.item_data.get('image'):
                    try:
                        old_image_path = self.item_data['image'].split('/')[-1].split('?')[0]
                        bucket = storage.bucket()
                        old_blob = bucket.blob(f"items/{old_image_path}")
                        old_blob.delete()
                    except Exception as e:
                        print(f"Error deleting old image: {e}")

                # Yeni resmi yükle
                image_path = f"items/{data['name'].lower().replace(' ', '_')}.jpg"
                image_url = upload_image_to_firebase(self.selected_image, image_path)
                if image_url:
                    print(f"New image URL: {image_url}")  # Debug için URL'yi yazdır
                    data['image'] = image_url
                    data['picture'] = image_url
            except Exception as e:
                print(f"Error uploading item image: {e}")
        
        # Eğer düzenleme modundaysa, oluşturulma tarihini koru
        if self.item_data and 'created_at' in self.item_data:
            data['created_at'] = self.item_data['created_at']
        else:
            data['created_at'] = datetime.now().isoformat()
        
        return data

class MenuManagementTab(QWidget):
    def __init__(self, db_ref, parent=None):
        super().__init__(parent)
        self.db_ref = db_ref
        self._is_closing = False
        
        # Initialize Pyrebase
        pb = pyrebase.initialize_app(PYREBASE_CONFIG)
        self.pb_db = pb.database()
        
        # Store stream handler for cleanup
        self._stream_handler = None
        
        # Store buttons for language updates
        self.buttons = []
        
        # Setup UI
        self._init_ui()
        
        # Load initial data
        self.load_menu()
        
        # Setup Firebase listener
        self._setup_firebase_listener()
        
        # Connect to settings changes
        sig_handler.settings_changed.connect(self._handle_settings_change)
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(20)
        
        # Category list card
        cat_card = MaterialCard()
        cat_layout = QVBoxLayout(cat_card)
        cat_layout.setContentsMargins(20, 20, 20, 20)
        
        # Category tree widget
        self.cat_tree = QTreeWidget()
        self.cat_tree.setHeaderLabels([
            app_settings.get_text('category_name'),
            app_settings.get_text('category_order'),
            app_settings.get_text('item_count')
        ])
        self.cat_tree.setAlternatingRowColors(True)
        self.cat_tree.setMinimumHeight(250)
        
        header = self.cat_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 150)
        header.resizeSection(2, 100)
        
        cat_layout.addWidget(self.cat_tree)
        layout.addWidget(cat_card)
        
        # Item list card
        item_card = MaterialCard()
        item_layout = QVBoxLayout(item_card)
        item_layout.setContentsMargins(20, 20, 20, 20)
        
        # Item tree widget
        self.item_tree = QTreeWidget()
        self.item_tree.setHeaderLabels([
            app_settings.get_text('item_name'),
            app_settings.get_text('item_price'),
            app_settings.get_text('item_available')
        ])
        self.item_tree.setAlternatingRowColors(True)
        self.item_tree.setMinimumHeight(300)
        
        header = self.item_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 100)
        header.resizeSection(2, 100)
        
        item_layout.addWidget(self.item_tree)
        layout.addWidget(item_card)
        
        # Button container at the bottom
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(12)
        
        # Category buttons
        cat_buttons = [
            ('add_category', self.add_category, 'success'),
            ('edit_category', self.edit_category, 'primary'),
            ('remove_category', self.remove_category, 'error')
        ]
        
        for key, func, style in cat_buttons:
            btn = QPushButton(app_settings.get_text(key))
            btn.setObjectName(style)
            btn.setFixedWidth(130)
            btn.setMinimumHeight(40)
            btn.clicked.connect(func)
            btn.setProperty('text_key', key)  # Store text key for updates
            btn_layout.addWidget(btn)
            self.buttons.append(btn)
        
        btn_layout.addStretch()
        
        # Item buttons
        item_buttons = [
            ('add_item', self.add_item, 'success'),
            ('edit_item', self.edit_item, 'primary'),
            ('remove_item', self.remove_item, 'error')
        ]
        
        for key, func, style in item_buttons:
            btn = QPushButton(app_settings.get_text(key))
            btn.setObjectName(style)
            btn.setFixedWidth(130)
            btn.setMinimumHeight(40)
            btn.clicked.connect(func)
            btn.setProperty('text_key', key)  # Store text key for updates
            btn_layout.addWidget(btn)
            self.buttons.append(btn)
        
        layout.addWidget(btn_container)
        
        # Connect category selection change
        self.cat_tree.currentItemChanged.connect(self.on_category_selected)
    
    def _setup_firebase_listener(self):
        # Store the stream handler for cleanup
        self._stream_handler = self.pb_db.child('menu').stream(self._on_menu_change)
    
    def _on_menu_change(self, message):
        if not self._is_closing:
            QTimer.singleShot(0, self.load_menu)
    
    def closeEvent(self, event):
        self._is_closing = True
        if self._stream_handler:
            self._stream_handler.close()
        super().closeEvent(event)

    def load_menu(self):
        self.cat_tree.clear()
        self.item_tree.clear()
        
        menu = self.db_ref.child('menu').get() or {}
        categories = []
        
        for cat_data in menu.values():
            if isinstance(cat_data, dict) and 'name' in cat_data:
                categories.append(cat_data)
        
        # Sort categories by order
        categories.sort(key=lambda x: x.get('order', 999))
        
        for cat_data in categories:
            cat_item = QTreeWidgetItem([
                cat_data['name'],
                str(cat_data.get('order', 1)),
                str(len(cat_data.get('items', {})))
            ])
            self.cat_tree.addTopLevelItem(cat_item)
            
            # Load items if this was the previously selected category
            if (self.cat_tree.currentItem() and 
                self.cat_tree.currentItem().text(0) == cat_data['name']):
                self.load_items(cat_data.get('items', {}))

    def load_items(self, items):
        self.item_tree.clear()
        
        for item_data in items.values():
            if isinstance(item_data, dict) and 'name' in item_data:
                item = QTreeWidgetItem([
                    item_data['name'],
                    f"{item_data.get('price', 0)} ₺",
                    '✓' if item_data.get('available', True) else '✗'
                ])
                
                # Set color based on availability
                if not item_data.get('available', True):
                    item.setForeground(2, QColor(COLORS['error']))
                else:
                    item.setForeground(2, QColor(COLORS['success']))
                
                self.item_tree.addTopLevelItem(item)
        
        self.item_tree.sortItems(0, Qt.SortOrder.AscendingOrder)

    def add_category(self):
        dialog = CategoryDialog(self)
        if dialog.exec():
            cat_data = dialog.get_category_data()
            cat_data['items'] = {}
            self.db_ref.child('menu').child(cat_data['name'].lower().replace(' ', '_')).set(cat_data)
            QMessageBox.information(
                self,
                app_settings.get_text('add_category'),
                app_settings.get_text('category_added')
            )
    
    def edit_category(self):
        current = self.cat_tree.currentItem()
        if not current:
            return
        
        cat_name = current.text(0)
        cat_data = None
        
        menu = self.db_ref.child('menu').get() or {}
        for cat_id, data in menu.items():
            if isinstance(data, dict) and data.get('name') == cat_name:
                cat_data = data
                break
        
        if cat_data:
            dialog = CategoryDialog(self, cat_data)
            if dialog.exec():
                new_data = dialog.get_category_data()
                # Preserve items when updating
                new_data['items'] = cat_data.get('items', {})
                self.db_ref.child('menu').child(cat_name.lower().replace(' ', '_')).set(new_data)
                QMessageBox.information(
                    self,
                    app_settings.get_text('edit_category'),
                    app_settings.get_text('category_updated')
                )
    
    def remove_category(self):
        current = self.cat_tree.currentItem()
        if not current:
            return
        
        cat_name = current.text(0)
        self.db_ref.child('menu').child(cat_name.lower().replace(' ', '_')).delete()
        QMessageBox.information(
            self,
            app_settings.get_text('remove_category'),
            app_settings.get_text('category_removed')
        )
    
    def add_item(self):
        dialog = ItemDialog(self.db_ref)
        if dialog.exec():
            item_data = dialog.get_item_data()
            category_id = item_data.pop('category_id')  # Kategori ID'sini al ve data'dan çıkar
            
            # Yeni ürün ID'si oluştur
            item_id = item_data['name'].lower().replace(' ', '_').replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
            
            # Ürünü doğru kategoriye ekle
            self.db_ref.child('menu').child(category_id).child('items').child(item_id).set(item_data)
            
            QMessageBox.information(
                self,
                app_settings.get_text('add_item'),
                app_settings.get_text('item_added')
            )
            
            self.load_menu()  # Menüyü yenile
    
    def edit_item(self):
        current_cat = self.cat_tree.currentItem()
        current_item = self.item_tree.currentItem()
        if not current_cat or not current_item:
            return
        
        cat_name = current_cat.text(0)
        item_name = current_item.text(0)
        
        menu = self.db_ref.child('menu').get() or {}
        for cat_id, cat_data in menu.items():
            if isinstance(cat_data, dict) and cat_data.get('name') == cat_name:
                items = cat_data.get('items', {})
                for item_id, item_data in items.items():
                    if isinstance(item_data, dict) and item_data.get('name') == item_name:
                        dialog = ItemDialog(self.db_ref, self, item_data)
                        if dialog.exec():
                            new_data = dialog.get_item_data()
                            category_id = new_data.pop('category_id')  # Kategori ID'sini al
                            
                            # Yeni item ID oluştur
                            new_item_id = new_data['name'].lower().replace(' ', '_').replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
                            
                            # Eğer kategori değiştiyse
                            if category_id != cat_id:
                                # Eski konumdan sil
                                self.db_ref.child('menu').child(cat_id).child('items').child(item_id).delete()
                                
                                # Yeni konuma ekle
                                self.db_ref.child('menu').child(category_id).child('items').child(new_item_id).set(new_data)
                            else:
                                # Aynı konumda güncelle
                                if item_id != new_item_id:
                                    # Eski item'ı sil ve yeni ID ile ekle
                                    self.db_ref.child('menu').child(cat_id).child('items').child(item_id).delete()
                                    self.db_ref.child('menu').child(cat_id).child('items').child(new_item_id).set(new_data)
                                else:
                                    # Aynı ID'de güncelle
                                    self.db_ref.child('menu').child(cat_id).child('items').child(item_id).update(new_data)
                            
                            QMessageBox.information(
                                self,
                                app_settings.get_text('edit_item'),
                                app_settings.get_text('item_updated')
                            )
                            self.load_menu()
                        break
                break
    
    def remove_item(self):
        current_cat = self.cat_tree.currentItem()
        current_item = self.item_tree.currentItem()
        if not current_cat or not current_item:
            return
        
        cat_name = current_cat.text(0)
        item_name = current_item.text(0)
        
        # Kullanıcıya silme onayı sor
        reply = QMessageBox.question(
            self,
            app_settings.get_text('remove_item'),
            f"{item_name} ürününü silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Kategori ID'sini bul
            menu = self.db_ref.child('menu').get() or {}
            for cat_id, cat_data in menu.items():
                if isinstance(cat_data, dict) and cat_data.get('name') == cat_name:
                    # Item ID'sini bul
                    items = cat_data.get('items', {})
                    for item_id, item_data in items.items():
                        if isinstance(item_data, dict) and item_data.get('name') == item_name:
                            # Resmi storage'dan sil
                            if item_data.get('image'):
                                try:
                                    # URL'den dosya adını çıkar
                                    image_path = item_data['image'].split('/')[-1].split('?')[0]
                                    bucket = storage.bucket()
                                    blob = bucket.blob(f"items/{image_path}")
                                    blob.delete()
                                except Exception as e:
                                    print(f"Error deleting image: {e}")
                            
                            # Ürünü database'den sil
                            self.db_ref.child('menu').child(cat_id).child('items').child(item_id).delete()
                            
                            QMessageBox.information(
                                self,
                                app_settings.get_text('remove_item'),
                                app_settings.get_text('item_removed')
                            )
                            self.load_menu()
                            return
                    break

    def on_category_selected(self, current, previous):
        if current:
            category_name = current.text(0)
            menu = self.db_ref.child('menu').get() or {}
            for cat_data in menu.values():
                if isinstance(cat_data, dict) and cat_data.get('name') == category_name:
                    self.load_items(cat_data.get('items', {}))
                    break

    def _handle_settings_change(self, key, value):
        if key == 'language':
            # Update button texts
            for btn in self.buttons:
                text_key = btn.property('text_key')
                if text_key:
                    btn.setText(app_settings.get_text(text_key))
            
            # Update tree headers
            self.cat_tree.setHeaderLabels([
                app_settings.get_text('category_name'),
                app_settings.get_text('category_order'),
                app_settings.get_text('item_count')
            ])
            
            self.item_tree.setHeaderLabels([
                app_settings.get_text('item_name'),
                app_settings.get_text('item_price'),
                app_settings.get_text('item_available')
            ])

class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tree_active = None
        self.tree_old = None
        self.setWindowTitle(app_settings.get_text('app_title'))
        self.resize(1200, 800)
        
        # Connect to settings changes
        sig_handler.settings_changed.connect(self._handle_settings_change)
        
        # Create toolbar
        self.create_toolbar()
        
        # Apply stylesheet
        self.update_theme()
        
        # init firebase admin
        self._init_firebase()
        # build UI
        self._init_ui()
        # init streaming after UI ready
        self._init_pyrebase()
        # connect signals
        sig_handler.orders_changed.connect(self.load_orders)
    
    def _handle_settings_change(self, key, value):
        if key == 'language':
            self.update_texts()
        elif key == 'theme':
            self.update_theme()
    
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Theme switcher
        theme_menu = QMenu()
        dark_action = QAction(app_settings.get_text('dark_theme'), self)
        light_action = QAction(app_settings.get_text('light_theme'), self)
        dark_action.triggered.connect(lambda: self.change_theme('dark'))
        light_action.triggered.connect(lambda: self.change_theme('light'))
        theme_menu.addAction(dark_action)
        theme_menu.addAction(light_action)
        
        theme_btn = QToolButton()
        theme_btn.setText('🎨')
        theme_btn.setMenu(theme_menu)
        theme_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(theme_btn)
        
        # Language switcher
        lang_menu = QMenu()
        en_action = QAction('English', self)
        tr_action = QAction('Türkçe', self)
        en_action.triggered.connect(lambda: self.change_language('en'))
        tr_action.triggered.connect(lambda: self.change_language('tr'))
        lang_menu.addAction(en_action)
        lang_menu.addAction(tr_action)
        
        lang_btn = QToolButton()
        lang_btn.setText('🌐')
        lang_btn.setMenu(lang_menu)
        lang_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(lang_btn)

    def change_theme(self, theme):
        app_settings.set_theme(theme)
        self.update_theme()

    def change_language(self, language):
        app_settings.set_language(language)
        self.update_texts()

    def update_theme(self):
        self.setStyleSheet(app_settings.generate_stylesheet())

    def update_texts(self):
        """Update all text elements when language changes"""
        # Update window title
        self.setWindowTitle(app_settings.get_text('app_title'))
        
        # Update tab texts
        self.tabs.setTabText(0, app_settings.get_text('preview_tab'))
        self.tabs.setTabText(1, app_settings.get_text('menu_tab'))
        self.tabs.setTabText(2, app_settings.get_text('orders_tab'))
        self.tabs.setTabText(3, app_settings.get_text('table_management'))
        
        # Update tree headers
        if self.tree_active:
            self.tree_active.setHeaderLabels([
                app_settings.get_text('table'),
                app_settings.get_text('status'),
                app_settings.get_text('action')
            ])
        
        if self.tree_old:
            self.tree_old.setHeaderLabels([
                app_settings.get_text('table'),
                app_settings.get_text('status'),
                app_settings.get_text('created_at')
            ])
        
        # Refresh orders to update button texts
        self.load_orders()
        
        # Update toolbar tooltips
        if hasattr(self, 'webview'):
            for action in self.findChildren(QToolButton):
                if action.toolTip() == "Geri":
                    action.setToolTip(app_settings.get_text('back'))
                elif action.toolTip() == "İleri":
                    action.setToolTip(app_settings.get_text('forward'))
                elif action.toolTip() == "Yenile":
                    action.setToolTip(app_settings.get_text('refresh'))
                elif action.toolTip() == "Yakınlaştır":
                    action.setToolTip(app_settings.get_text('zoom_in'))
                elif action.toolTip() == "Uzaklaştır":
                    action.setToolTip(app_settings.get_text('zoom_out'))
                elif action.toolTip() == "Varsayılan Zoom":
                    action.setToolTip(app_settings.get_text('zoom_reset'))

    def _init_firebase(self):
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL,
            'storageBucket': FIREBASE_STORAGE_BUCKET
        })
        self.db_ref = db.reference()

    def _init_pyrebase(self):
        pb = pyrebase.initialize_app(PYREBASE_CONFIG)
        self.pb_db = pb.database()
        self.pb_db.child('orders').stream(lambda m: sig_handler.orders_changed.emit())

    def _init_ui(self):
        # Create central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Header card
        header_card = MaterialCard()
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel(app_settings.get_text('app_title'))
        title.setObjectName('header')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel(app_settings.get_text('app_subtitle'))
        subtitle.setObjectName('subheader')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header_card)
        
        # Create and style tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._build_preview_tab(), app_settings.get_text('preview_tab'))
        self.tabs.addTab(MenuManagementTab(self.db_ref), app_settings.get_text('menu_tab'))
        self.tabs.addTab(self._build_orders_tab(), app_settings.get_text('orders_tab'))
        self.tabs.addTab(TableManagementTab(self.db_ref), app_settings.get_text('table_management'))
        
        # Add tab change animation
        self.tab_animation = QPropertyAnimation(self.tabs, b'currentIndex')
        self.tab_animation.setDuration(200)
        self.tab_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.tabs.currentChanged.connect(self._handle_tab_change)
        main_layout.addWidget(self.tabs)

    def _handle_tab_change(self, index):
        if index == 0:
            self.webview.reload()

    def _build_preview_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)  # Kenar boşluklarını kaldır
        layout.setSpacing(0)  # Boşlukları kaldır
        
        # WebView container
        preview_card = QWidget()
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)
        
        # Create WebView with settings
        self.webview = QWebEngineView()
        
        # WebView ayarlarını yapılandır
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, True)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(2)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: transparent;
                border: none;
            }
            QProgressBar::chunk {
                background: #2196F3;
            }
        """)
        
        # Progress bar sinyallerini bağla
        self.webview.loadStarted.connect(lambda: self.progress_bar.setVisible(True))
        self.webview.loadProgress.connect(self.progress_bar.setValue)
        self.webview.loadFinished.connect(lambda: self.progress_bar.setVisible(False))
        
        # Layout'a ekle
        preview_layout.addWidget(self.progress_bar)
        preview_layout.addWidget(self.webview)
        
        layout.addWidget(preview_card)
        
        # Menü URL'sini yükle
        self.webview.setUrl(QUrl(GITHUB_MENU_URL))
        
        # WebView'ı tam boyuta ayarla
        self.webview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        return tab

    def _build_orders_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(20)
        
        orders_tabs = QTabWidget()
        orders_tabs.setDocumentMode(True)
        
        # Active orders
        active_tab = QWidget()
        a_layout = QVBoxLayout(active_tab)
        a_layout.setContentsMargins(0, 20, 0, 0)
        a_layout.setSpacing(20)
        
        active_card = MaterialCard()
        active_layout = QVBoxLayout(active_card)
        active_layout.setContentsMargins(20, 20, 20, 20)
        
        self.tree_active = QTreeWidget()
        self.tree_active.setHeaderLabels(['Masa', 'Durum', 'İşlem'])
        self.tree_active.setAlternatingRowColors(True)
        self.tree_active.setMinimumHeight(400)
        
        # Sütun genişliklerini ayarla
        header_active = self.tree_active.header()
        header_active.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Masa sütunu sabit
        header_active.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Durum sütunu sabit
        header_active.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # İşlem sütunu sabit
        header_active.resizeSection(0, 120)  # Masa sütunu genişliği
        header_active.resizeSection(1, 150)  # Durum sütunu genişliği
        header_active.resizeSection(2, 120)  # İşlem sütunu genişliği
        
        # Satır yüksekliğini ayarla
        self.tree_active.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
            }
            QTreeWidget::item {
                height: 40px;  /* Satır yüksekliği */
                padding: 4px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: rgba(33, 150, 243, 0.12);
            }
        """)
        
        active_layout.addWidget(self.tree_active)
        a_layout.addWidget(active_card)
        orders_tabs.addTab(active_tab, app_settings.get_text('active_orders'))
        
        # Old orders tab benzer şekilde güncelleniyor
        old_tab = QWidget()
        o_layout = QVBoxLayout(old_tab)
        o_layout.setContentsMargins(0, 20, 0, 0)
        o_layout.setSpacing(20)
        
        old_card = MaterialCard()
        old_layout = QVBoxLayout(old_card)
        old_layout.setContentsMargins(20, 20, 20, 20)
        
        self.tree_old = QTreeWidget()
        self.tree_old.setHeaderLabels(['Masa', 'Durum', 'Tarih'])
        self.tree_old.setAlternatingRowColors(True)
        self.tree_old.setMinimumHeight(400)
        
        # Sütun genişliklerini ayarla
        header_old = self.tree_old.header()
        header_old.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header_old.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header_old.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header_old.resizeSection(0, 120)
        header_old.resizeSection(1, 150)
        header_old.resizeSection(2, 180)  # Tarih sütunu biraz daha geniş
        
        # Aynı satır yüksekliği ayarı
        self.tree_old.setStyleSheet(self.tree_active.styleSheet())
        
        old_layout.addWidget(self.tree_old)
        o_layout.addWidget(old_card)
        orders_tabs.addTab(old_tab, app_settings.get_text('old_orders'))
        
        layout.addWidget(orders_tabs)
        return tab

    def load_orders(self):
        if not self.tree_active or not self.tree_old:
            return
            
        self.tree_active.clear()
        self.tree_old.clear()
        
        # Load active orders
        active_orders = self.db_ref.child('orders').child('active').get() or {}
        for order_id, order in active_orders.items():
            table_no = order.get('table', '')
            status = order.get('status', 'Beklemede')
            total = order.get('total', 0)
            items = order.get('items', [])
            created_at = order.get('created_at', '')
            
            btn_text = {
                'Beklemede': app_settings.get_text('confirm'),
                'Hazırlanıyor': app_settings.get_text('prepare'),
                'Hazırlandı': app_settings.get_text('deliver')
            }.get(status, '—')
            
            parent = QTreeWidgetItem([
                f"Masa {table_no}",
                '',
                ''  # Empty column for button
            ])
            parent.setFont(0, QFont('Arial', 11, QFont.Weight.Bold))
            self.tree_active.addTopLevelItem(parent)
            
            # Add status badge
            status_badge = StatusBadge(status)
            self.tree_active.setItemWidget(parent, 1, status_badge)
            
            if btn_text != '—':
                btn_container = QWidget()
                btn_layout = QHBoxLayout(btn_container)
                btn_layout.setContentsMargins(4, 0, 4, 0)
                btn_layout.setSpacing(0)
                
                # Create button
                btn = QPushButton(btn_text)
                btn.setObjectName('success' if status == 'Hazırlandı' else 'primary')
                btn.setMinimumWidth(120)
                btn.setFixedHeight(40)
                
                # Style the button
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['success'] if status == 'Hazırlandı' else COLORS['primary']};
                        color: white;
                        font-weight: bold;
                        font-size: 12px;
                        border: none;
                        border-radius: 8px;
                        padding: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['success'] if status == 'Hazırlandı' else COLORS['primary_dark']};
                    }}
                    QPushButton:pressed {{
                        background-color: {COLORS['success'] if status == 'Hazırlandı' else COLORS['primary']};
                        padding: 6px 4px 2px 4px;
                    }}
                """)
                
                btn.clicked.connect(lambda _, x=order_id: self._advance_order(x))
                btn_layout.addWidget(btn)
                btn_layout.addStretch()
                
                self.tree_active.setItemWidget(parent, 2, btn_container)
            
            for item in items:
                child = QTreeWidgetItem(parent, [
                    f"- {item['name']}",
                    f"x{item['quantity']}",
                    f"{item['price'] * item['quantity']} ₺"
                ])
                child.setForeground(0, QColor(COLORS['on_surface_medium']))
        
        self.tree_active.expandAll()
        
        # Load completed orders
        completed_orders = self.db_ref.child('orders').child('history').get() or {}
        for order_id, order in completed_orders.items():
            table_no = order.get('table', '')
            status = order.get('status', '')
            completed_at = order.get('completed_at', '')
            items = order.get('items', [])
            
            # Format date
            try:
                completed_date = datetime.fromisoformat(completed_at).strftime('%d/%m/%Y %H:%M')
            except:
                completed_date = completed_at
            
            parent = QTreeWidgetItem([
                f"Masa {table_no}",
                '',  # Status will be added as badge
                completed_date
            ])
            parent.setFont(0, QFont('Arial', 11, QFont.Weight.Bold))
            self.tree_old.addTopLevelItem(parent)
            
            # Add status badge
            status_badge = StatusBadge(status)
            self.tree_old.setItemWidget(parent, 1, status_badge)
            
            # Add items
            for item in items:
                child = QTreeWidgetItem(parent, [
                    f"- {item['name']}",
                    f"x{item['quantity']}",
                    f"{item['price'] * item['quantity']} ₺"
                ])
                child.setForeground(0, QColor(COLORS['on_surface_medium']))
        
        self.tree_old.expandAll()
        
        # Sort old orders by date (newest first)
        self.tree_old.sortItems(2, Qt.SortOrder.DescendingOrder)

    def _advance_order(self, order_id):
        order_ref = self.db_ref.child('orders').child('active').child(order_id)
        order = order_ref.get() or {}
        current_status = order.get('status', 'Beklemede')
        
        next_status = {
            'Beklemede': 'Hazırlanıyor',
            'Hazırlanıyor': 'Hazırlandı',
            'Hazırlandı': 'Teslim Edildi'
        }.get(current_status)
        
        if next_status == 'Teslim Edildi':
            # Move to history
            history_ref = self.db_ref.child('orders').child('history')
            order['status'] = next_status
            order['completed_at'] = datetime.now().isoformat()
            history_ref.push(order)
            # Remove from active orders
            order_ref.delete()
        else:
            # Update status
            order_ref.update({
                'status': next_status,
                'updated_at': datetime.now().isoformat()
            })
        
        self.load_orders()

    def run(self):
        # Show window in fullscreen
        self.showMaximized()
        # Set window state to maximize
        self.setWindowState(Qt.WindowState.WindowMaximized)

    def generate_menu_html(self):
        # ... existing code ...
        
        # CSS styles
        styles = """
            <style>
                .menu-item {
                    position: relative;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    background: white;
                }
                
                .menu-item-image {
                    position: relative;
                    width: 100%;
                    padding-top: 56.25%;  /* 16:9 aspect ratio */
                    overflow: hidden;
                }
                
                .menu-item-image img {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }
                
                .menu-item-details {
                    padding: 15px;
                    position: relative;
                }
                
                .add-to-cart {
                    position: absolute;
                    bottom: 15px;
                    right: 15px;
                    background: #ff4757;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: bold;
                    z-index: 2;
                }
                
                @media (max-width: 768px) {
                    .menu-item {
                        margin-bottom: 15px;
                    }
                    
                    .menu-item-details {
                        padding: 12px;
                        padding-bottom: 50px;  /* Sepete Ekle butonu için alan */
                    }
                    
                    .add-to-cart {
                        position: absolute;
                        bottom: 10px;
                        right: 10px;
                        width: calc(100% - 20px);  /* Tam genişlik - padding */
                        text-align: center;
                    }
                }
            </style>
        """
        
        # Menu item template
        item_template = """
            <div class="menu-item">
                <div class="menu-item-image">
                    <img src="{image_url}" alt="{name}" loading="lazy">
                </div>
                <div class="menu-item-details">
                    <h3>{name}</h3>
                    <p class="price">{price:.2f} TL</p>
                    <p class="description">{description}</p>
                    <a href="#" class="add-to-cart" onclick="addToCart('{id}')">Sepete Ekle</a>
                </div>
            </div>
        """
        # ... existing code ...

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdminApp()
    window.run()
    sys.exit(app.exec())
    print("Admin app closed.")