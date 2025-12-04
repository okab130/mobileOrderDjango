from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from order.models import User, Table, MenuItem
from PIL import Image
import io


class Command(BaseCommand):
    help = '初期データを投入します'

    def handle(self, *args, **options):
        self.stdout.write('初期データ投入を開始します...')
        
        # ユーザー作成
        self._create_users()
        
        # テーブル作成
        self._create_tables()
        
        # メニュー商品作成
        self._create_menu_items()
        
        self.stdout.write(self.style.SUCCESS('初期データ投入が完了しました'))
    
    def _create_users(self):
        """ユーザー作成"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='ADMIN'
            )
            self.stdout.write('管理者ユーザーを作成しました (admin/admin123)')
        
        if not User.objects.filter(username='staff').exists():
            User.objects.create_user(
                username='staff',
                email='staff@example.com',
                password='staff123',
                role='STAFF'
            )
            self.stdout.write('スタッフユーザーを作成しました (staff/staff123)')
    
    def _create_tables(self):
        """テーブル作成（1-10）"""
        for i in range(1, 11):
            Table.objects.get_or_create(
                table_number=i,
                defaults={'seat_count': 4}
            )
        self.stdout.write('テーブル10卓を作成しました')
    
    def _create_menu_items(self):
        """メニュー商品作成"""
        menu_data = [
            {'name': 'ハンバーグステーキ', 'price': 1200, 'color': '#8B4513'},
            {'name': 'カルボナーラ', 'price': 980, 'color': '#FFD700'},
            {'name': 'シーザーサラダ', 'price': 680, 'color': '#32CD32'},
            {'name': 'フライドポテト', 'price': 480, 'color': '#FFA500'},
            {'name': 'マルゲリータピザ', 'price': 1400, 'color': '#DC143C'},
            {'name': 'ティラミス', 'price': 580, 'color': '#D2691E'},
            {'name': 'アイスコーヒー', 'price': 380, 'color': '#654321'},
            {'name': 'オレンジジュース', 'price': 350, 'color': '#FF8C00'},
        ]
        
        for item_data in menu_data:
            if not MenuItem.objects.filter(name=item_data['name']).exists():
                # プレースホルダー画像を作成
                img = Image.new('RGB', (800, 600), color=item_data['color'])
                
                # 画像にテキストを追加（簡易版）
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG', quality=95)
                img_file = ContentFile(img_io.getvalue(), name=f"{item_data['name']}.jpg")
                
                # MenuItemを作成
                menu_item = MenuItem(
                    name=item_data['name'],
                    price=item_data['price'],
                    is_available=True
                )
                menu_item.image.save(f"{item_data['name']}.jpg", img_file, save=False)
                menu_item.save()
                
                self.stdout.write(f"商品「{item_data['name']}」を作成しました")
