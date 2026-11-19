"""
seed_data.py — Nạp Dữ Liệu Khởi Tạo Chuẩn Mẫu (Seed Data) Thông Qua SQLAlchemy ORM
Tạo và liên kết toàn bộ 23 Bảng qua Python thuần & SQLAlchemy Session — 100% không dùng raw SQL.
Cách chạy:
    cd backend
    python seed_data.py
"""

import os
import sys
from datetime import datetime, timezone, timedelta, date

# Thêm đường dẫn backend vào sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app.database import engine, Base, SessionLocal, DB_PATH
from app.models import (
    User, KYCVerification, UserAddress, BankAccount,
    Category, Brand, Product, ProductImage, ProductSpec,
    ProductOffer, Voucher,
    Order, OrderParcel, OrderItem, OrderTrackingEvent,
    EscrowWallet, EscrowTransaction,
    Dispute, DisputeEvidence, DisputeMessage,
    ProductReview, Wishlist, Notification
)


def seed():
    print("=" * 68)
    print("🌱 BẮT ĐẦU NẠP DỮ LIỆU SEED DATA QUA PYTHON & SQLALCHEMY ORM")
    print(f"📁 Database: {DB_PATH}")
    print("=" * 68)

    # Đảm bảo 23 bảng đã được tạo
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Kiểm tra nếu đã có dữ liệu cũ thì làm mới
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️ Dữ liệu cũ đã tồn tại. Đang dọn dẹp để nạp mới...")
            for model in [
                DisputeMessage, DisputeEvidence, Dispute,
                OrderTrackingEvent, OrderItem, OrderParcel, Order,
                EscrowTransaction, EscrowWallet,
                ProductReview, Wishlist, Notification, ProductOffer,
                ProductSpec, ProductImage, Product, Brand, Category, Voucher,
                BankAccount, UserAddress, KYCVerification, User
            ]:
                db.query(model).delete()
            db.commit()
            print("🧹 Đã dọn dẹp dữ liệu cũ thành công.")

        # ==============================================================
        # 1. USERS & E-KYC & ADDRESSES & BANK ACCOUNTS
        # ==============================================================
        print("👤 Đang tạo Users, eKYC và Tài khoản ngân hàng...")
        admin = User(
            id="usr-admin",
            email="admin@hybridstore.vn",
            phone="0900000001",
            password_hash="pbkdf2:sha256:admin123456",
            full_name="Quản Trị Viên Hệ Thống (Admin)",
            username="admin",
            role="admin",
            avatar_url="assets/images/products/set-nam-techwear-all-black.png",
            membership_title="ADMIN MASTER",
            bio="Quản trị viên cấp cao phụ trách vận hành và trọng tài sàn TMĐT Hybrid Store.",
            is_active=True,
            vip_points=5000
        )

        inspector = User(
            id="usr-inspector",
            email="inspector@hybridstore.vn",
            phone="0900000002",
            password_hash="pbkdf2:sha256:inspect123456",
            full_name="Kiểm Định Viên Trung Tâm Quốc Gia",
            username="inspector",
            role="inspector",
            avatar_url="assets/images/products/may-anh-ky-thuat-so-mirrorless.png",
            membership_title="SENIOR INSPECTOR",
            bio="Kiểm định viên phụ trách soi kính lúp, đo pin và niêm phong hàng C2C.",
            is_active=True,
            vip_points=2000
        )

        seller_techzone = User(
            id="usr-techzone",
            email="techzone@hybridstore.vn",
            phone="0900000003",
            password_hash="pbkdf2:sha256:seller123456",
            full_name="TechZone Official Store",
            username="techzone",
            role="seller",
            avatar_url="assets/images/products/may-tinh-laptop-mong-nhe.png",
            membership_title="OFFICIAL MALL",
            bio="Phân phối chính hãng Apple, Samsung, Sony 100% Brand Mall bảo hành toàn quốc.",
            is_active=True,
            vip_points=12000
        )

        seller_minh = User(
            id="usr-minh",
            email="minhhoang@gmail.com",
            phone="0912345678",
            password_hash="pbkdf2:sha256:minh123456",
            full_name="Trần Minh Hoàng",
            username="minhhoang",
            role="seller",
            avatar_url="assets/images/products/dien-thoai-smartphone-flagship.png",
            membership_title="PRO SELLER",
            bio="Chuyên hàng công nghệ lướt 99% nguyên bản zin áp suất, hỗ trợ kiểm định tận mắt.",
            is_active=True,
            vip_points=3500
        )

        buyer_tuan = User(
            id="usr-tuan",
            email="tuananh@gmail.com",
            phone="0988888888",
            password_hash="pbkdf2:sha256:tuan123456",
            full_name="Nguyễn Tuấn Anh",
            username="tuananh",
            role="buyer",
            avatar_url="assets/images/products/dong-ho-thong-minh-smartwatch.png",
            membership_title="VIP BUYER",
            bio="Tín đồ công nghệ yêu thích đồ hi-tech và săn deal giá hời.",
            is_active=True,
            vip_points=1850
        )

        db.add_all([admin, inspector, seller_techzone, seller_minh, buyer_tuan])
        db.flush()

        # eKYC cho Seller Minh
        kyc_minh = KYCVerification(
            id="kyc-minh",
            user_id=seller_minh.id,
            id_card_number="001098012345",
            full_name_on_card="TRẦN MINH HOÀNG",
            date_of_birth=date(1995, 10, 24),
            gender="Nam",
            permanent_address="Số 88 Cầu Giấy, P. Dịch Vọng, Q. Cầu Giấy, Hà Nội",
            front_image_url="assets/images/products/images.jpg",
            back_image_url="assets/images/products/images (1).jpg",
            selfie_image_url="assets/images/products/images (4).jpg",
            status="approved",
            reviewed_by=inspector.id,
            reviewed_at=datetime.now(timezone.utc) - timedelta(days=30)
        )
        db.add(kyc_minh)

        # Địa chỉ người mua
        addr_tuan1 = UserAddress(
            id="addr-1",
            user_id=buyer_tuan.id,
            recipient_name="Nguyễn Tuấn Anh",
            phone="0988888888",
            province="Thành phố Hà Nội",
            district="Quận Cầu Giấy",
            ward="Phường Dịch Vọng Hậu",
            street_address="Toà nhà FPT Tower, Số 10 Phạm Văn Bạch",
            full_address="Toà nhà FPT Tower, Số 10 Phạm Văn Bạch, P. Dịch Vọng Hậu, Q. Cầu Giấy, Hà Nội",
            is_default=True,
            address_type="office"
        )
        addr_tuan2 = UserAddress(
            id="addr-2",
            user_id=buyer_tuan.id,
            recipient_name="Nguyễn Tuấn Anh (Nhà riêng)",
            phone="0988888888",
            province="Thành phố Hà Nội",
            district="Quận Nam Từ Liêm",
            ward="Phường Mỹ Đình 1",
            street_address="Căn hộ 1208, Toà CT1 Sudico Mỹ Đình",
            full_address="Căn hộ 1208, Toà CT1 Sudico Mỹ Đình, P. Mỹ Đình 1, Q. Nam Từ Liêm, Hà Nội",
            is_default=False,
            address_type="home"
        )
        db.add_all([addr_tuan1, addr_tuan2])

        # Tài khoản ngân hàng Napas 24/7
        bank_minh = BankAccount(
            id="bank-1",
            user_id=seller_minh.id,
            bank_code="TCB",
            bank_name="Techcombank",
            account_number="19034567890123",
            account_holder="TRAN MINH HOANG",
            is_default=True
        )
        bank_techzone = BankAccount(
            id="bank-2",
            user_id=seller_techzone.id,
            bank_code="VCB",
            bank_name="Vietcombank",
            account_number="0011004567890",
            account_holder="CTY CP CONG NGHE TECHZONE",
            is_default=True
        )
        db.add_all([bank_minh, bank_techzone])
        db.flush()

        # ==============================================================
        # 2. CATEGORIES & BRANDS
        # ==============================================================
        print("📦 Đang tạo Danh mục ngành hàng và Thương hiệu chính hãng...")
        categories_data = [
            ("cat-tech", "tech", "Điện Thoại & Laptop Flagship", "devices", "tertiary", "HYBRID TECH", "Flagship Apple, Samsung & Laptop đồ hoạ mỏng nhẹ", 1),
            ("cat-audio", "audio", "Âm Thanh & Tai Nghe Hi-Res", "headphones", "accent", "HI-FI AUDIO", "Tai nghe Sony WH-1000XM5, loa bluetooth bass trầm", 2),
            ("cat-gaming", "gaming", "Gaming Gear & Bàn Phím Cơ", "sports_esports", "primary", "ESPORTS READY", "Bàn phím cơ AULA F75, chuột gaming không dây", 3),
            ("cat-camera", "camera", "Máy Ảnh & Thiết Bị Quay Chụp", "photo_camera", "purple", "PHOTO & CINEMA", "Máy ảnh Mirrorless Sony, lens tele và gimbal chống rung", 4),
            ("cat-watches", "watches", "Đồng Hồ & Phụ Kiện Cao Cấp", "watch", "cyan", "LUXURY TIME", "Đồng hồ cơ Automatic, smartwatch thể thao GPS", 5),
            ("cat-appliances", "appliances", "Đồ Gia Dụng Thông Minh", "home_mini", "warning", "SMART HOME", "Nồi chiên không dầu Philips, máy hút bụi cầm tay Dyson", 6),
            ("cat-sneakers", "sneakers", "Sneakers & Giày Dép Hype", "steps", "secondary", "OFFICIAL SEAL", "Giày thể thao nam nữ sneaker đế dày phong cách streetwear", 7),
            ("cat-fashion", "fashion", "Thời Trang & Streetwear Mall", "checkroom", "primary", "MALL NEW 100%", "Set đồ techwear, áo jacket blazer runway nam cao cấp", 8),
        ]
        for cat_id, slug, name, icon, tone, badge, desc, order in categories_data:
            cat = Category(
                id=cat_id,
                slug=slug,
                name=name,
                icon=icon,
                tone=tone,
                badge=badge,
                desc=desc,
                display_order=order,
                is_active=True
            )
            db.add(cat)

        brands_data = [
            ("br-apple", "apple", "Apple", "assets/images/products/may-tinh-laptop-mong-nhe.png", True),
            ("br-samsung", "samsung", "Samsung", "assets/images/products/dien-thoai-smartphone-flagship.png", True),
            ("br-sony", "sony", "Sony", "assets/images/products/tai-nghe-sony-wh-ch520.png", True),
            ("br-logitech", "logitech", "Logitech G", "assets/images/products/chuot-logitech-g-pro-x-superlight-pink.png", True),
            ("br-razer", "razer", "Razer", "assets/images/products/tai-nghe-razer-blackshark-v2-gold.png", True),
            ("br-dyson", "dyson", "Dyson", "assets/images/products/may-hut-bui-cam-tay.png", True),
            ("br-nike", "nike", "Nike", "assets/images/products/giay-the-thao-nam-fashion-3-mau.png", True),
            ("br-philips", "philips", "Philips", "assets/images/products/noi-chien-khong-dau.png", True),
        ]
        for b_id, slug, name, logo, is_mall in brands_data:
            b = Brand(
                id=b_id,
                slug=slug,
                name=name,
                logo_url=logo,
                is_official_mall=is_mall
            )
            db.add(b)

        db.flush()

        # ==============================================================
        # 3. PRODUCTS & SPECS & IMAGES
        # ==============================================================
        print("🛍️ Đang tạo Sản phẩm Hybrid (Mall & C2C), Thông số kỹ thuật & Thư viện ảnh...")
        products_data = [
            {
                "id": "p-1",
                "sku": "IP15PM-256-NT",
                "name": "iPhone 15 Pro Max 256GB Natural Titanium (Like New 99%)",
                "short_name": "iPhone 15 Pro Max",
                "slug": "iphone-15-pro-max-256gb-natural-titanium",
                "category_id": "cat-tech",
                "brand_id": "br-apple",
                "seller_id": seller_minh.id,
                "product_type": "c2c",
                "condition_pct": 99,
                "condition_label": "Like New 99%",
                "original_price": 29990000,
                "selling_price": 23490000,
                "stock_quantity": 2,
                "thumbnail_url": "assets/images/products/dien-thoai-smartphone-flagship.png",
                "description": "Máy zin áp suất, pin 98%, ngoại hình không cấn móp, còn bảo hành Apple Care+ 6 tháng.",
                "accessories_included": "Hộp zin, cáp C to C bện dù, ốp lưng UAG",
                "warranty_months": 6,
                "warranty_policy_note": "Bảo hành 1 đổi 1 trong 30 ngày tại trung tâm Hybrid Store",
                "inspection_passed": True,
                "inspection_score": 9.8,
                "allow_offers": True,
                "is_flash_sale": True,
                "rating_average": 4.95,
                "rating_count": 48,
                "status": "active",
                "specs": [
                    ("Chipset", "Apple A17 Pro 3nm 6 nhân"),
                    ("Bộ nhớ trong", "256 GB NVMe"),
                    ("Màn hình", "6.7 inch Super Retina XDR OLED 120Hz ProMotion"),
                    ("Dung lượng pin", "4.422 mAh (Độ chai 2%)"),
                    ("Kiểm định", "Đạt chuẩn 9.8/10 chứng nhận bởi Hybrid Inspector"),
                ],
                "images": [
                    "assets/images/products/dien-thoai-smartphone-flagship.png",
                    "assets/images/products/dong-ho-thong-minh-smartwatch.png",
                ]
            },
            {
                "id": "p-2",
                "sku": "MBP14-M3P-18-512",
                "name": "MacBook Pro 14 inch M3 Pro (18GB Unified RAM, 512GB SSD) Space Black",
                "short_name": "MacBook Pro M3 Pro",
                "slug": "macbook-pro-14-m3-pro-space-black",
                "category_id": "cat-tech",
                "brand_id": "br-apple",
                "seller_id": seller_techzone.id,
                "product_type": "mall",
                "condition_pct": 100,
                "condition_label": "Mới 100% Brand Mall",
                "original_price": 49990000,
                "selling_price": 44890000,
                "stock_quantity": 10,
                "thumbnail_url": "assets/images/products/may-tinh-laptop-mong-nhe.png",
                "description": "Hàng mới chính hãng Brand Mall 100% nguyên seal hộp tem Apple Việt Nam.",
                "accessories_included": "Hộp trùng serial, củ sạc 70W MagSafe 3, cáp bện dù chính hãng",
                "warranty_months": 12,
                "warranty_policy_note": "Bảo hành 12 tháng tại các Trung tâm bảo hành uỷ quyền Apple toàn quốc",
                "inspection_passed": True,
                "inspection_score": 10.0,
                "allow_offers": False,
                "is_flash_sale": True,
                "rating_average": 5.0,
                "rating_count": 112,
                "status": "active",
                "specs": [
                    ("Vi xử lý", "Apple M3 Pro (11-core CPU, 14-core GPU)"),
                    ("RAM", "18GB Unified Memory"),
                    ("SSD", "512GB siêu tốc độ 5000MB/s"),
                    ("Màn hình", "Liquid Retina XDR 14.2 inch 3024x1964 mini-LED 120Hz"),
                ],
                "images": [
                    "assets/images/products/may-tinh-laptop-mong-nhe.png",
                ]
            },
            {
                "id": "p-3",
                "sku": "WH1000XM5-SLV",
                "name": "Tai nghe chống ồn Sony WH-1000XM5 Silver (Đầy đủ phụ kiện 98%)",
                "short_name": "Sony WH-1000XM5",
                "slug": "tai-nghe-sony-wh-1000xm5-silver",
                "category_id": "cat-audio",
                "brand_id": "br-sony",
                "seller_id": seller_minh.id,
                "product_type": "c2c",
                "condition_pct": 98,
                "condition_label": "Gần như mới 98%",
                "original_price": 8990000,
                "selling_price": 5490000,
                "stock_quantity": 3,
                "thumbnail_url": "assets/images/products/tai-nghe-sony-wh-ch520.png",
                "description": "Đệm tai êm ái chưa bong tróc, pin nghe liên tục 30 giờ, chống ồn đỉnh cao.",
                "accessories_included": "Bao đựng cứng cao cấp, dây 3.5mm, adapter máy bay, cáp sạc C",
                "warranty_months": 3,
                "warranty_policy_note": "Bảo hành 3 tháng phần cứng và cảm ứng",
                "inspection_passed": True,
                "inspection_score": 9.6,
                "allow_offers": True,
                "is_flash_sale": False,
                "rating_average": 4.9,
                "rating_count": 35,
                "status": "active",
                "specs": [
                    ("Driver", "30mm màng carbon tổng hợp"),
                    ("Bluetooth", "5.2 hỗ trợ codec LDAC, AAC, SBC"),
                    ("Thời lượng pin", "Lên đến 30 tiếng bật ANC"),
                ],
                "images": [
                    "assets/images/products/tai-nghe-sony-wh-ch520.png",
                ]
            },
            {
                "id": "p-4",
                "sku": "GPX-PINK",
                "name": "Chuột Gaming Logitech G Pro X Superlight Wireless Pink Edition",
                "short_name": "Logitech G Pro X",
                "slug": "chuot-logitech-g-pro-x-superlight-pink",
                "category_id": "cat-gaming",
                "brand_id": "br-logitech",
                "seller_id": seller_techzone.id,
                "product_type": "mall",
                "condition_pct": 100,
                "condition_label": "Mới 100% Brand Mall",
                "original_price": 3490000,
                "selling_price": 2890000,
                "stock_quantity": 15,
                "thumbnail_url": "assets/images/products/chuot-logitech-g-pro-x-superlight-pink.png",
                "description": "Hàng mới chính hãng 100% nguyên seal hộp tem Digiworld phân phối.",
                "accessories_included": "Receiver Lightspeed, cáp sạc, grip tape dán chống trượt",
                "warranty_months": 24,
                "warranty_policy_note": "Đổi mới 24 tháng theo chính sách Logitech Việt Nam",
                "inspection_passed": True,
                "inspection_score": 10.0,
                "allow_offers": False,
                "is_flash_sale": False,
                "rating_average": 4.88,
                "rating_count": 87,
                "status": "active",
                "specs": [
                    ("Cân nặng", "Siêu nhẹ dưới 63 gram"),
                    ("Cảm biến", "HERO 25K (100 - 25,600 DPI, 400+ IPS)"),
                ],
                "images": [
                    "assets/images/products/chuot-logitech-g-pro-x-superlight-pink.png",
                ]
            },
            {
                "id": "p-5",
                "sku": "HD9880-90",
                "name": "Nồi chiên không dầu Philips XXL Connected 7.2L Smart Sense",
                "short_name": "Nồi chiên Philips XXL",
                "slug": "noi-chien-khong-dau-philips-xxl-7-2l",
                "category_id": "cat-appliances",
                "brand_id": "br-philips",
                "seller_id": seller_techzone.id,
                "product_type": "mall",
                "condition_pct": 100,
                "condition_label": "Mới 100% Brand Mall",
                "original_price": 8990000,
                "selling_price": 6490000,
                "stock_quantity": 8,
                "thumbnail_url": "assets/images/products/noi-chien-khong-dau.png",
                "description": "Hàng mới 100% chính hãng phân phối, bảo hành 2 năm toàn quốc.",
                "accessories_included": "Giỏ chiên QuickClean, khay nướng chống dính",
                "warranty_months": 24,
                "warranty_policy_note": "Bảo hành 2 năm chính hãng Philips",
                "inspection_passed": True,
                "inspection_score": 10.0,
                "allow_offers": False,
                "is_flash_sale": False,
                "rating_average": 4.92,
                "rating_count": 64,
                "status": "active",
                "specs": [
                    ("Thể tích", "7.2 Lít (chiên nguyên con gà 1.4kg)"),
                    ("Công suất", "2000W công nghệ Rapid Air Twin TurboStar"),
                ],
                "images": [
                    "assets/images/products/noi-chien-khong-dau.png",
                ]
            },
            {
                "id": "p-6",
                "sku": "ILCE-7M4-USED",
                "name": "Máy ảnh Sony Alpha A7 Mark IV Body (Like New 99%, 1.200 Shots)",
                "short_name": "Sony Alpha A7 IV",
                "slug": "sony-alpha-a7-mark-iv-body",
                "category_id": "cat-camera",
                "brand_id": "br-sony",
                "seller_id": seller_minh.id,
                "product_type": "c2c",
                "condition_pct": 99,
                "condition_label": "Like New 99%",
                "original_price": 54990000,
                "selling_price": 43500000,
                "stock_quantity": 1,
                "thumbnail_url": "assets/images/products/may-anh-ky-thuat-so-mirrorless.png",
                "description": "Máy chụp test 1200 shots, sensor đẹp tuyệt đối không hạt bụi, đầy đủ hộp sạc cáp zin.",
                "accessories_included": "Hộp zin, pin FZ100, sạc cáp, dây đeo Sony chính hãng",
                "warranty_months": 12,
                "warranty_policy_note": "Bảo hành trách nhiệm 12 tháng tại shop",
                "inspection_passed": True,
                "inspection_score": 9.9,
                "allow_offers": True,
                "is_flash_sale": True,
                "rating_average": 5.0,
                "rating_count": 18,
                "status": "active",
                "specs": [
                    ("Cảm biến", "33.0 Megapixels Full-Frame Exmor R CMOS BSI"),
                    ("Quay phim", "4K 60p 10-bit 4:2:2 All-Intra"),
                    ("Số shot đã chụp", "1,200 shots (Đã kiểm tra qua tool chính hãng)"),
                ],
                "images": [
                    "assets/images/products/may-anh-ky-thuat-so-mirrorless.png",
                    "assets/images/products/images (8).jpg",
                ]
            }
        ]

        for p_data in products_data:
            specs = p_data.pop("specs", [])
            images = p_data.pop("images", [])
            prod = Product(**p_data)
            db.add(prod)
            db.flush()

            for idx, img_url in enumerate(images):
                img = ProductImage(
                    id=f"img-{prod.id}-{idx+1}",
                    product_id=prod.id,
                    image_url=img_url,
                    display_order=idx,
                    is_cover=(idx == 0)
                )
                db.add(img)

            for idx, (k, val) in enumerate(specs):
                sp = ProductSpec(
                    id=f"sp-{prod.id}-{idx+1}",
                    product_id=prod.id,
                    spec_key=k,
                    spec_value=val,
                    display_order=idx
                )
                db.add(sp)

        db.flush()

        # ==============================================================
        # 4. VOUCHERS
        # ==============================================================
        print("🎟️ Đang tạo Vouchers khuyến mãi...")
        now = datetime.now(timezone.utc)
        vouchers = [
            Voucher(
                id="vch-1",
                code="HYBRID100K",
                title="Giảm 100K cho đơn hàng công nghệ từ 1 triệu",
                voucher_type="fixed",
                discount_value=100000,
                min_order_value=1000000,
                usage_limit=500,
                usage_count=42,
                start_date=now - timedelta(days=5),
                end_date=now + timedelta(days=30),
                is_active=True
            ),
            Voucher(
                id="vch-2",
                code="FREESHIPMAX",
                title="Miễn phí vận chuyển toàn quốc tối đa 50K",
                voucher_type="freeship",
                discount_value=50000,
                min_order_value=300000,
                usage_limit=1000,
                usage_count=180,
                start_date=now - timedelta(days=10),
                end_date=now + timedelta(days=60),
                is_active=True
            ),
            Voucher(
                id="vch-3",
                code="VIPMALL10",
                title="Giảm 10% tối đa 500K cho gian hàng Brand Mall",
                voucher_type="percent",
                discount_value=10,
                min_order_value=2000000,
                max_discount_amount=500000,
                usage_limit=200,
                usage_count=18,
                start_date=now - timedelta(days=2),
                end_date=now + timedelta(days=15),
                is_active=True
            )
        ]
        db.add_all(vouchers)
        db.flush()

        # ==============================================================
        # 5. C2C PRODUCT OFFERS (TRẢ GIÁ 24H)
        # ==============================================================
        print("🤝 Đang tạo Lịch sử trả giá C2C 24h...")
        offer1 = ProductOffer(
            id="off-1",
            product_id="p-1",
            buyer_id=buyer_tuan.id,
            seller_id=seller_minh.id,
            original_price=23490000,
            offered_price=21800000,
            discount_pct=7,
            buyer_message="Em có thiện chí mua ngay trong chiều nay tại Hà Nội, anh bớt em 21.8tr nhé!",
            seller_note="Giá 21.8tr hơi thấp bạn nhé, mình bớt tối đa chốt 22.5tr bao ship tận nơi.",
            status="pending",
            expires_at=now + timedelta(hours=18)
        )
        offer2 = ProductOffer(
            id="off-2",
            product_id="p-3",
            buyer_id=buyer_tuan.id,
            seller_id=seller_minh.id,
            original_price=5490000,
            offered_price=5000000,
            discount_pct=9,
            buyer_message="Bác để em 5 triệu tròn qua lấy liền nhé!",
            seller_note="Đồng ý bán, bạn hoàn tất đặt đơn trong 12 giờ tới nhé.",
            status="accepted",
            expires_at=now + timedelta(hours=12)
        )
        db.add_all([offer1, offer2])
        db.flush()

        # ==============================================================
        # 6. ORDERS & PARCELS & ITEMS & TRACKING
        # ==============================================================
        print("🛒 Đang tạo Đơn hàng Multi-Vendor, Tách kiện & Nhật ký hành trình...")
        order1 = Order(
            id="ord-1",
            order_code="ORD-20261119-001",
            buyer_id=buyer_tuan.id,
            subtotal=23490000,
            shipping_fee=40000,
            discount_amount=100000,
            total_amount=23430000,
            voucher_id="vch-1",
            payment_method="COD",
            payment_status="held_in_escrow",
            shipping_method="standard",
            recipient_name="Nguyễn Tuấn Anh",
            recipient_phone="0988888888",
            shipping_address="Toà nhà FPT Tower, Số 10 Phạm Văn Bạch, P. Dịch Vọng Hậu, Q. Cầu Giấy, Hà Nội",
            buyer_note="Giao giờ hành chính, gọi trước 15 phút.",
            status="shipping",
            step_index=3
        )
        db.add(order1)
        db.flush()

        parcel1 = OrderParcel(
            id="pkg-1",
            order_id=order1.id,
            seller_id=seller_minh.id,
            parcel_code="PARCEL-001-MINH",
            parcel_type="c2c_seller",
            carrier_name="Giao Hàng Nhanh (GHN)",
            tracking_code="GHN882947192VN",
            shipping_fee=40000,
            estimated_delivery="19/11/2026 - 20/11/2026",
            status="in_transit"
        )
        db.add(parcel1)
        db.flush()

        item1 = OrderItem(
            id="item-1",
            order_id=order1.id,
            parcel_id=parcel1.id,
            product_id="p-1",
            product_name="iPhone 15 Pro Max 256GB Natural Titanium (Like New 99%)",
            product_type="c2c",
            condition_pct=99,
            unit_price=23490000,
            quantity=1,
            total_price=23490000,
            variant_info="Titan Tự Nhiên, 256GB",
            thumbnail_url="assets/images/products/dien-thoai-smartphone-flagship.png"
        )
        db.add(item1)

        tracking_events = [
            OrderTrackingEvent(
                id="tr-1",
                parcel_id=parcel1.id,
                status_title="Đơn hàng được khởi tạo",
                status_description="Đơn hàng được khởi tạo thành công trên hệ thống sàn Hybrid.Store",
                location="Hà Nội",
                shipper_name="",
                event_time=now - timedelta(hours=24)
            ),
            OrderTrackingEvent(
                id="tr-2",
                parcel_id=parcel1.id,
                status_title="Đã đóng gói & Niêm phong",
                status_description="Người bán đã đóng gói và dán niêm phong kiểm định chất lượng",
                location="Kho Minh Hoàng C2C Tech, Cầu Giấy",
                shipper_name="Trần Minh Hoàng",
                event_time=now - timedelta(hours=18)
            ),
            OrderTrackingEvent(
                id="tr-3",
                parcel_id=parcel1.id,
                status_title="Bưu tá đã nhận kiện",
                status_description="Shipper GHN đã lấy kiện hàng thành công và đang chuyển về bưu cục trung chuyển",
                location="Bưu cục GHN Cầu Giấy, Hà Nội",
                shipper_name="Nguyễn Văn Giao",
                shipper_phone="0911222333",
                event_time=now - timedelta(hours=8)
            ),
            OrderTrackingEvent(
                id="tr-4",
                parcel_id=parcel1.id,
                status_title="Đang phân loại trung chuyển",
                status_description="Kiện hàng đang được phân loại tự động và xuất kho giao đến người nhận",
                location="Trung tâm khai thác GHN Kho Mê Linh, Hà Nội",
                shipper_name="Bưu tá phát GHN",
                event_time=now - timedelta(hours=2)
            ),
        ]
        db.add_all(tracking_events)
        db.flush()

        # ==============================================================
        # 7. ESCROW WALLETS & TRANSACTIONS
        # ==============================================================
        print("💳 Đang tạo Ví Ký Quỹ Escrow & Sổ cái đối soát 24/7...")
        wallet_techzone = EscrowWallet(
            id="wal-techzone",
            user_id=seller_techzone.id,
            available_balance=45800000,
            locked_balance=15000000,
            total_withdrawn=120000000
        )
        wallet_minh = EscrowWallet(
            id="wal-minh",
            user_id=seller_minh.id,
            available_balance=18500000,
            locked_balance=23430000,  # Khoá tiền đơn iPhone 15 Pro Max
            total_withdrawn=45000000
        )
        db.add_all([wallet_techzone, wallet_minh])
        db.flush()

        tx_escrow = EscrowTransaction(
            id="tx-1",
            wallet_id=wallet_minh.id,
            order_id=order1.id,
            transaction_code="TX-ESC-2026-001",
            transaction_type="hold_order",
            amount=23430000,
            balance_after=18500000,
            memo="Tạm giữ tiền thanh toán đơn hàng ORD-20261119-001 qua cơ chế Escrow",
            status="completed"
        )
        db.add(tx_escrow)
        db.flush()

        # ==============================================================
        # 8. TRIPARTITE DISPUTE (PHÒNG TRỌNG TÀI KHIẾU NẠI 3 BÊN)
        # ==============================================================
        print("⚖️ Đang tạo Vụ án Trọng tài Tranh chấp Khiếu nại 3 Bên...")
        dispute1 = Dispute(
            id="dsp-1",
            dispute_code="DSP-2026-001",
            order_id=order1.id,
            buyer_id=buyer_tuan.id,
            seller_id=seller_minh.id,
            arbitrator_admin_id=admin.id,
            reason="Hàng có vết xước viền sâu không giống mô tả 99%",
            description="Lúc bóc hộp phát hiện vết xước cạnh viền dưới loa máy, người mua yêu cầu bồi thường 500k hoặc đổi trả.",
            requested_refund=500000,
            approved_refund=0,
            status="in_arbitration"
        )
        db.add(dispute1)
        db.flush()

        evid1 = DisputeEvidence(
            id="ev-1",
            dispute_id=dispute1.id,
            uploaded_by_user_id=buyer_tuan.id,
            media_type="image",
            media_url="assets/images/products/images (6).jpg",
            title="xuoc_loa_iphone.jpg",
            file_size_kb=450
        )
        db.add(evid1)

        msg1 = DisputeMessage(
            id="msg-1",
            dispute_id=dispute1.id,
            sender_id=buyer_tuan.id,
            sender_role="buyer",
            message_text="Em nhận máy lúc 14h, bóc hộp quay video 4K có thấy vết xước này, anh xem hỗ trợ giảm giá giúp em."
        )
        msg2 = DisputeMessage(
            id="msg-2",
            dispute_id=dispute1.id,
            sender_id=seller_minh.id,
            sender_role="seller",
            message_text="Chào Tuấn Anh, máy trước khi gửi bên mình đã soi kính lúp rất kỹ. Bạn gửi lại video bóc seal giúp mình nhé!"
        )
        msg3 = DisputeMessage(
            id="msg-3",
            dispute_id=dispute1.id,
            sender_id=admin.id,
            sender_role="admin",
            message_text="[Trọng tài viên sàn]: Đã tiếp nhận yêu cầu. Sàn đang tạm dừng giải ngân 23.430.000đ từ ví Escrow cho đến khi 2 bên đồng thuận."
        )
        db.add_all([msg1, msg2, msg3])
        db.flush()

        # ==============================================================
        # 9. REVIEWS & WISHLISTS & NOTIFICATIONS
        # ==============================================================
        print("⭐ Đang tạo Đánh giá 5 sao, Wishlist & Trung tâm Thông báo...")
        rev1 = ProductReview(
            id="rev-1",
            product_id="p-2",
            user_id=buyer_tuan.id,
            order_id=None,
            rating=5,
            comment="Máy MacBook Pro M3 mới tinh nguyên seal xịn sò, giao hỏa tốc 2 giờ rất uy tín!",
            has_photo=True,
            is_verified_buyer=True,
            seller_reply="TechZone chân thành cảm ơn anh Tuấn Anh đã tin tưởng và ủng hộ gian hàng chính hãng!"
        )
        wish1 = Wishlist(id="wish-1", user_id=buyer_tuan.id, product_id="p-6")
        wish2 = Wishlist(id="wish-2", user_id=buyer_tuan.id, product_id="p-3")

        notif1 = Notification(
            id="notif-1",
            user_id=buyer_tuan.id,
            type="order",
            title="Đơn hàng đang giao đến bạn",
            message="Kiện hàng GHN882947192VN đang được vận chuyển đến địa chỉ của bạn.",
            link_url="pages/order/tracking.html?orderId=ORD-20261119-001"
        )
        notif2 = Notification(
            id="notif-2",
            user_id=seller_minh.id,
            type="dispute",
            title="Phòng trọng tài khiếu nại đã mở",
            message="Vụ việc DSP-2026-001 đang được Trọng tài viên sàn phân xử.",
            link_url="pages/dispute/arbitration_room.html?disputeId=DSP-2026-001"
        )
        db.add_all([rev1, wish1, wish2, notif1, notif2])

        db.commit()
        print("=" * 68)
        print("🎉 NẠP SEED DATA THÀNH CÔNG 100% VÀO CƠ SỞ DỮ LIỆU QUA SQLALCHEMY!")
        print("=" * 68)

    except Exception as e:
        db.rollback()
        print(f"❌ Có lỗi trong quá trình nạp seed data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
