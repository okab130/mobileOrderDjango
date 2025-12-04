from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
import os


class User(AbstractUser):
    """ユーザーモデル（管理者・スタッフ）"""
    ROLE_CHOICES = [
        ('ADMIN', '管理者'),
        ('STAFF', 'スタッフ'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STAFF')

    class Meta:
        db_table = 'users'


class Table(models.Model):
    """テーブルモデル"""
    table_number = models.IntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    seat_count = models.IntegerField(default=4)
    
    class Meta:
        db_table = 'tables'
        ordering = ['table_number']
    
    def __str__(self):
        return f'テーブル{self.table_number}'
    
    @property
    def qr_code_url(self):
        return f'/order?table={self.table_number}'


class MenuItem(models.Model):
    """メニュー商品モデル"""
    name = models.CharField(max_length=100)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='menu/original/')
    thumbnail = models.ImageField(upload_to='menu/thumbnail/', blank=True, null=True)
    large_image = models.ImageField(upload_to='menu/large/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['id']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # 初回保存
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # 画像リサイズは初回保存後のみ実行
        if self.image and is_new:
            self._create_resized_images()
            # リサイズ後に再度保存（フィールド更新のため）
            super().save(update_fields=['thumbnail', 'large_image'])
    
    def _create_resized_images(self):
        """画像リサイズ処理"""
        # サムネイル作成 (300x300)
        thumbnail_path = self._resize_image(self.image.path, 'thumbnail', 300, 300)
        self.thumbnail.name = thumbnail_path
        
        # 大サイズ画像作成 (1200x900)
        large_path = self._resize_image(self.image.path, 'large', 1200, 900)
        self.large_image.name = large_path
    
    def _resize_image(self, source_path, size_type, width, height):
        """画像リサイズ処理"""
        img = Image.open(source_path)
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        # ファイル名とパスを生成
        base_name = os.path.basename(source_path)
        output_dir = os.path.join(os.path.dirname(os.path.dirname(source_path)), size_type)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, base_name)
        
        # 保存
        img.save(output_path)
        
        # 相対パスを返す
        return f'menu/{size_type}/{base_name}'


class Session(models.Model):
    """注文セッションモデル"""
    STATUS_CHOICES = [
        ('ACTIVE', 'アクティブ'),
        ('COMPLETED', '会計済み'),
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='sessions')
    guest_count = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f'{self.table} - {self.started_at.strftime("%Y-%m-%d %H:%M")}'
    
    @property
    def total_amount(self):
        """合計金額を計算"""
        return sum(order.menu_item.price * order.quantity for order in self.orders.all())


class Order(models.Model):
    """注文モデル"""
    STATUS_CHOICES = [
        ('PENDING', '未着手'),
        ('COOKING', '調理中'),
        ('COMPLETED', '完成'),
        ('SERVED', '提供済'),
    ]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='orders')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name='orders')
    quantity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['ordered_at']
    
    def __str__(self):
        return f'{self.session.table} - {self.menu_item.name} x {self.quantity}'
    
    @property
    def subtotal(self):
        """小計を計算"""
        return self.menu_item.price * self.quantity


class StaffCall(models.Model):
    """店員呼び出しモデル"""
    REASON_CHOICES = [
        ('WATER', 'お水'),
        ('PAYMENT', '会計'),
        ('QUESTION', '質問'),
        ('COMPLAINT', '苦情'),
        ('OTHER', 'その他'),
    ]
    STATUS_CHOICES = [
        ('PENDING', '未対応'),
        ('RESOLVED', '対応済'),
    ]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='staff_calls')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='staff_calls')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    called_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'staff_calls'
        ordering = ['called_at']
    
    def __str__(self):
        return f'{self.table} - {self.get_reason_display()}'

